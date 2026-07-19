"""Celery tasks — the actual work the worker performs.

Each task is exposed as both:
  - A Celery task (decorated)         → for asynchronous dispatch
  - An async function (undecorated)   → for inline / test invocation

The decorated task wraps the async function via `_run_async`.
"""
from __future__ import annotations

import asyncio
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import get_settings
from app.core.logging import bind_task, configure_logging, get_logger
from app.db import build_repositories
from app.storage import build_storage
from zorkvdo_ai import VideoAnalyzer
from zorkvdo_ai.analysis import AnalyzerConfig

log = get_logger(__name__)

# Lazy import celery_app + _run_async — only needed when dispatching
# async Celery tasks. The inline task variants (used by the API in dev
# mode) don't need celery at all.
def _get_celery():
    from app.workers.celery_app import celery_app, _run_async
    return celery_app, _run_async


# ──────────────────────────────────────────────────────────────────────
# Analysis
# ──────────────────────────────────────────────────────────────────────
async def run_analysis_job(
    job_id: str, video_id: str, owner_id: str, blueprint_name: str
) -> dict:
    """Run the full video analysis pipeline and persist results."""
    configure_logging(level="INFO")
    bind_task(job_id)
    log.info("analysis_job_start", job_id=job_id, video_id=video_id)

    settings = get_settings()
    repos = build_repositories(settings)
    storage = build_storage(settings)
    return await _run_analysis_impl(job_id, video_id, owner_id, blueprint_name, settings, repos, storage)


async def run_analysis_job_inline(
    job_id: str,
    video_id: str,
    owner_id: str,
    blueprint_name: str,
    *,
    repos,
    storage,
) -> dict:
    """Inline version that reuses the caller's repos + storage (no new
    in-memory store). Used by the /jobs/analyze?sync=true endpoint so the
    job results are visible to the API immediately.
    """
    configure_logging(level="INFO")
    bind_task(job_id)
    log.info("analysis_job_start_inline", job_id=job_id, video_id=video_id)
    settings = get_settings()
    return await _run_analysis_impl(job_id, video_id, owner_id, blueprint_name, settings, repos, storage)


async def _run_analysis_impl(
    job_id: str,
    video_id: str,
    owner_id: str,
    blueprint_name: str,
    settings,
    repos,
    storage,
) -> dict:
    """Shared implementation between the Celery task and the inline runner."""
    # repos may be a RepositoryRegistry (inline) or Repositories wrapper (Celery)
    registry = repos.registry if hasattr(repos, "registry") else repos

    # Mark job running
    jobs_repo = repos.get("jobs")
    job_doc = await jobs_repo.get(job_id)
    if not job_doc:
        log.error("job_not_found", job_id=job_id)
        return {"error": "job not found"}

    job_doc["status"] = "running"
    job_doc["started_at"] = datetime.now(timezone.utc).isoformat()
    await jobs_repo.put(job_id, job_doc)

    try:
        # Fetch video metadata
        videos_repo = repos.get("videos")
        video_doc = await videos_repo.get(video_id)
        if not video_doc:
            raise FileNotFoundError(f"video {video_id} not found")

        # Download the file to a temp path for analysis
        data = await storage.get(video_doc["storage_key"])
        suffix = Path(video_doc["filename"]).suffix or ".mp4"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        try:
            cfg = AnalyzerConfig(
                scene_threshold=settings.analysis_scene_threshold,
                sample_fps=settings.analysis_sample_fps,
                ocr_languages=settings.analysis_ocr_languages.split(","),
                yolo_model=settings.yolo_model_path,
                enable_face=settings.analysis_enable_face,
                enable_pose=settings.analysis_enable_pose,
                max_video_seconds=settings.analysis_max_video_seconds,
            )
            analyzer = VideoAnalyzer(config=cfg)
            result = await analyzer.analyze(
                tmp_path,
                video_id=video_id,
                blueprint_id=uuid.uuid4().hex,
                blueprint_name=blueprint_name,
            )
        finally:
            try:
                Path(tmp_path).unlink()
            except OSError:
                pass

        # Persist blueprint
        from app.services.blueprint_service import BlueprintService
        bp_service = BlueprintService(registry)
        await bp_service.save(owner_id, result.blueprint)

        # Update video metadata with probe results
        await videos_repo.put(video_id, {
            "duration_seconds": result.stats.duration_seconds,
            "width": result.stats.width,
            "height": result.stats.height,
            "fps": result.stats.fps,
            "analysis_id": job_id,
        })

        # Mark job succeeded
        job_doc = await jobs_repo.get(job_id)
        job_doc["status"] = "succeeded"
        job_doc["progress"] = 1.0
        job_doc["finished_at"] = datetime.now(timezone.utc).isoformat()
        job_doc["result"] = {
            "video_id": video_id,
            "blueprint_id": result.blueprint.id,
            "scene_count": result.scene_count,
            "detected_bpm": result.detected_bpm,
        }
        await jobs_repo.put(job_id, job_doc)

        # Notify the user
        from app.services.user_service import UserService
        user_svc = UserService(registry)
        await user_svc.create_notification(
            owner_id,
            kind="success",
            title="Analysis complete",
            body=f"Generated blueprint '{blueprint_name}' with {result.scene_count} scenes.",
            entity_type="blueprint",
            entity_id=result.blueprint.id,
        )

        log.info("analysis_job_done", job_id=job_id, blueprint_id=result.blueprint.id)
        return job_doc["result"]

    except Exception as e:
        log.exception("analysis_job_failed", job_id=job_id, error=str(e))
        job_doc = await jobs_repo.get(job_id) or {}
        job_doc["status"] = "failed"
        job_doc["error"] = str(e)
        job_doc["finished_at"] = datetime.now(timezone.utc).isoformat()
        await jobs_repo.put(job_id, job_doc)
        raise


def run_analysis_task(job_id: str, video_id: str, owner_id: str, blueprint_name: str) -> dict:
    """Celery task wrapper — only registered if celery is installed."""
    celery_app, _run_async = _get_celery()
    return _run_async(run_analysis_job(job_id, video_id, owner_id, blueprint_name))


def _register_celery_tasks():
    """Register tasks with celery. Called lazily only when celery is needed."""
    celery_app, _ = _get_celery()
    celery_app.task(name="zorkvdo.run_analysis", bind=True)(run_analysis_task)


# ──────────────────────────────────────────────────────────────────────
# Clip matching
# ──────────────────────────────────────────────────────────────────────
async def run_match_clips_job(
    job_id: str, blueprint_id: str, owner_id: str, clip_ids: list[str]
) -> dict:
    from zorkvdo_ai import ClipMatcher
    from app.services.blueprint_service import BlueprintService

    configure_logging(level="INFO")
    bind_task(job_id)
    settings = get_settings()
    repos = build_repositories(settings)
    storage = build_storage(settings)

    jobs_repo = repos.get("jobs")
    job_doc = await jobs_repo.get(job_id) or {}
    job_doc["status"] = "running"
    job_doc["started_at"] = datetime.now(timezone.utc).isoformat()
    await jobs_repo.put(job_id, job_doc)

    try:
        bp_service = BlueprintService(registry)
        blueprint = await bp_service.get_raw(blueprint_id)

        # Resolve clip paths
        clips_repo = repos.get("videos")
        clip_pairs: list[tuple[str, str]] = []
        for cid in clip_ids:
            doc = await clips_repo.get(cid)
            if not doc or doc.get("owner_id") != owner_id:
                continue
            # Download to a temp file
            data = await storage.get(doc["storage_key"])
            suffix = Path(doc["filename"]).suffix or ".mp4"
            tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            tmp.write(data)
            tmp.close()
            clip_pairs.append((cid, tmp.name))

        try:
            matcher = ClipMatcher()
            matches = await matcher.match(blueprint, clip_pairs)
        finally:
            for _, path in clip_pairs:
                try:
                    Path(path).unlink()
                except OSError:
                    pass

        # Persist matches into the job result
        job_doc = await jobs_repo.get(job_id)
        job_doc["status"] = "succeeded"
        job_doc["progress"] = 1.0
        job_doc["finished_at"] = datetime.now(timezone.utc).isoformat()
        job_doc["result"] = {
            "blueprint_id": blueprint_id,
            "matches": [m.model_dump(mode="json") for m in matches],
        }
        await jobs_repo.put(job_id, job_doc)
        return job_doc["result"]

    except Exception as e:
        log.exception("match_clips_job_failed", job_id=job_id, error=str(e))
        job_doc = await jobs_repo.get(job_id) or {}
        job_doc["status"] = "failed"
        job_doc["error"] = str(e)
        job_doc["finished_at"] = datetime.now(timezone.utc).isoformat()
        await jobs_repo.put(job_id, job_doc)
        raise


def run_match_clips_task(job_id: str, blueprint_id: str, owner_id: str, clip_ids: list[str]) -> dict:
    celery_app, _run_async = _get_celery()
    return _run_async(run_match_clips_job(job_id, blueprint_id, owner_id, clip_ids))


# ──────────────────────────────────────────────────────────────────────
# Rendering
# ──────────────────────────────────────────────────────────────────────
async def run_render_job(
    job_id: str,
    project_id: str,
    owner_id: str,
    blueprint_id: str,
    clip_mapping: list[dict],
    quality: str,
    aspect_ratio: str | None,
) -> dict:
    """Render a final video from a blueprint + user clips (Celery entry)."""
    configure_logging(level="INFO")
    bind_task(job_id)
    settings = get_settings()
    repos = build_repositories(settings)
    storage = build_storage(settings)
    return await _run_render_impl(
        job_id, project_id, owner_id, blueprint_id, clip_mapping,
        quality, aspect_ratio, settings, repos, storage,
    )


async def run_render_job_inline(
    job_id: str,
    project_id: str,
    owner_id: str,
    blueprint_id: str,
    clip_mapping: list[dict],
    quality: str,
    aspect_ratio: str | None,
    *,
    repos,
    storage,
) -> dict:
    """Inline render — reuses caller's repos + storage."""
    configure_logging(level="INFO")
    bind_task(job_id)
    settings = get_settings()
    return await _run_render_impl(
        job_id, project_id, owner_id, blueprint_id, clip_mapping,
        quality, aspect_ratio, settings, repos, storage,
    )


async def _run_render_impl(
    job_id: str,
    project_id: str,
    owner_id: str,
    blueprint_id: str,
    clip_mapping: list[dict],
    quality: str,
    aspect_ratio: str | None,
    settings,
    repos,
    storage,
) -> dict:
    """Shared render implementation."""
    from app.services.blueprint_service import BlueprintService
    from app.services.video_service import VideoService
    from app.workers.renderer import render_video

    # repos may be a RepositoryRegistry (inline) or Repositories wrapper (Celery)
    registry = repos.registry if hasattr(repos, "registry") else repos

    jobs_repo = repos.get("jobs")
    job_doc = await jobs_repo.get(job_id) or {}
    job_doc["status"] = "running"
    job_doc["started_at"] = datetime.now(timezone.utc).isoformat()
    await jobs_repo.put(job_id, job_doc)

    try:
        bp_service = BlueprintService(registry)
        blueprint = await bp_service.get_raw(blueprint_id)

        # Extract audio from the SOURCE video (for song reuse)
        source_audio_path = None
        source_video_id = blueprint.meta.source_video_id
        videos_repo = repos.get("videos")
        if source_video_id:
            source_doc = await videos_repo.get(source_video_id)
            if source_doc:
                try:
                    src_data = await storage.get(source_doc["storage_key"])
                    src_suffix = Path(source_doc["filename"]).suffix or ".mp4"
                    src_tmp = tempfile.NamedTemporaryFile(suffix=src_suffix, delete=False)
                    src_tmp.write(src_data)
                    src_tmp.close()

                    # Extract audio
                    audio_tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                    audio_tmp.close()
                    audio_extract = await asyncio.create_subprocess_exec(
                        "ffmpeg", "-y", "-loglevel", "warning",
                        "-i", src_tmp.name,
                        "-vn", "-acodec", "libmp3lame", "-ab", "128k",
                        audio_tmp.name,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                    await audio_extract.communicate()
                    if audio_extract.returncode == 0:
                        source_audio_path = audio_tmp.name
                        log.info("source_audio_extracted", job_id=job_id)
                    try:
                        Path(src_tmp.name).unlink()
                    except OSError:
                        pass
                except Exception as e:
                    log.warning("source_audio_extract_failed", error=str(e))

        # Resolve + download clips
        clip_paths: dict[str, str] = {}  # clip_id → local path
        for mapping in clip_mapping:
            cid = mapping["clip_id"]
            doc = await videos_repo.get(cid)
            if not doc:
                continue
            data = await storage.get(doc["storage_key"])
            suffix = Path(doc["filename"]).suffix or ".mp4"
            tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            tmp.write(data)
            tmp.close()
            clip_paths[cid] = tmp.name

        try:
            output_path = await render_video(
                blueprint=blueprint,
                clip_mapping=clip_mapping,
                clip_paths=clip_paths,
                quality=quality,
                aspect_ratio=aspect_ratio,
                source_audio_path=source_audio_path,
            )

            # Upload the rendered file
            video_svc = VideoService(registry, storage, settings)
            with open(output_path, "rb") as f:
                video_pub = await video_svc.upload(
                    owner_id=owner_id,
                    filename=f"{project_id}_render.mp4",
                    content_type="video/mp4",
                    size_bytes=Path(output_path).stat().st_size,
                    kind="output",
                    stream=f.read(),
                )
        finally:
            for p in clip_paths.values():
                try:
                    Path(p).unlink()
                except OSError:
                    pass
            if source_audio_path:
                try:
                    Path(source_audio_path).unlink()
                except OSError:
                    pass
            try:
                Path(output_path).unlink()
            except (OSError, UnboundLocalError):
                pass

        # Update project
        proj_repo = repos.get("projects")
        proj = await proj_repo.get(project_id)
        if proj:
            proj["output_video_id"] = video_pub.id
            proj["status"] = "rendered"
            await proj_repo.put(project_id, proj)

        # Mark job done
        job_doc = await jobs_repo.get(job_id)
        job_doc["status"] = "succeeded"
        job_doc["progress"] = 1.0
        job_doc["finished_at"] = datetime.now(timezone.utc).isoformat()
        job_doc["result"] = {
            "project_id": project_id,
            "output_video_id": video_pub.id,
        }
        await jobs_repo.put(job_id, job_doc)

        # Notify
        from app.services.user_service import UserService
        user_svc = UserService(registry)
        await user_svc.create_notification(
            owner_id,
            kind="success",
            title="Render complete",
            body=f"Your video is ready: {video_pub.filename}",
            entity_type="video",
            entity_id=video_pub.id,
        )
        return job_doc["result"]

    except Exception as e:
        log.exception("render_job_failed", job_id=job_id, error=str(e))
        job_doc = await jobs_repo.get(job_id) or {}
        job_doc["status"] = "failed"
        job_doc["error"] = str(e)
        job_doc["finished_at"] = datetime.now(timezone.utc).isoformat()
        await jobs_repo.put(job_id, job_doc)
        raise


def run_render_task(
    job_id: str,
    project_id: str,
    owner_id: str,
    blueprint_id: str,
    clip_mapping: list[dict],
    quality: str = "high",
    aspect_ratio: str | None = None,
) -> dict:
    celery_app, _run_async = _get_celery()
    return _run_async(
        run_render_job(
            job_id, project_id, owner_id, blueprint_id, clip_mapping, quality, aspect_ratio
        )
    )
