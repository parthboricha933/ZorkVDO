"""Job routes: /api/v1/jobs/* — analysis + rendering queue."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserId, get_analysis_service, get_repositories
from app.core.exceptions import NotFoundError, PermissionError, ValidationError
from app.core.logging import get_logger
from app.models.jobs import JobPublic, RenderRequest
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/jobs", tags=["jobs"])
log = get_logger(__name__)


@router.get("", response_model=list[JobPublic])
async def list_jobs(
    user_id: CurrentUserId,
    limit: int = Query(50, ge=1, le=200),
    svc: AnalysisService = Depends(get_analysis_service),
) -> list[JobPublic]:
    return await svc.list_jobs(user_id, limit=limit)


@router.get("/{job_id}", response_model=JobPublic)
async def get_job(
    job_id: str,
    user_id: CurrentUserId,
    svc: AnalysisService = Depends(get_analysis_service),
) -> JobPublic:
    return await svc.get_job(user_id, job_id)


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    user_id: CurrentUserId,
    svc: AnalysisService = Depends(get_analysis_service),
) -> dict:
    return {"cancelled": await svc.cancel_job(user_id, job_id)}


@router.post("/analyze/{video_id}", response_model=JobPublic, status_code=201)
async def start_analysis(
    video_id: str,
    user_id: CurrentUserId,
    body: dict | None = None,
    sync: bool = Query(False),
    svc: AnalysisService = Depends(get_analysis_service),
) -> JobPublic:
    blueprint_name = (body or {}).get("blueprint_name", "Untitled Blueprint")
    return await svc.start_analysis(
        owner_id=user_id,
        video_id=video_id,
        blueprint_name=blueprint_name,
        sync=sync,
    )


@router.post("/render", response_model=JobPublic, status_code=201)
async def start_render(
    req: RenderRequest,
    user_id: CurrentUserId,
    repos=Depends(get_repositories),
) -> JobPublic:
    """Start a render job. Accepts a blueprint_id + clip_mapping.

    The clip_mapping is a list of {scene_index, clip_id, suggested_start, suggested_end}.
    The render worker downloads each clip, trims/scales/concats them per the
    blueprint, burns in captions, and uploads the result.
    """
    # Verify the project belongs to the user
    proj_repo = repos.get("projects")
    project = await proj_repo.get(req.project_id)
    if not project:
        raise NotFoundError("project not found")
    if project.get("owner_id") != user_id:
        raise NotFoundError("project not found")

    # Verify the blueprint belongs to the user
    bp_repo = repos.get("blueprints")
    bp = await bp_repo.get(req.blueprint_id)
    if not bp:
        raise NotFoundError("blueprint not found")
    if bp.get("owner_id") != user_id:
        raise NotFoundError("blueprint not found")

    # Verify all clips belong to the user
    videos_repo = repos.get("videos")
    for mapping in req.clip_mapping:
        clip_id = mapping.clip_id if hasattr(mapping, "clip_id") else mapping["clip_id"]
        clip = await videos_repo.get(clip_id)
        if not clip:
            raise ValidationError(f"clip {clip_id} not found")
        if clip.get("owner_id") != user_id:
            raise ValidationError(f"clip {clip_id} not owned by user")

    # Create the job
    job_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    job_doc = {
        "id": job_id,
        "user_id": user_id,
        "project_id": req.project_id,
        "job_type": "render",
        "status": "queued",
        "progress": 0.0,
        "started_at": None,
        "finished_at": None,
        "error": None,
        "result": {
            "blueprint_id": req.blueprint_id,
            "clip_mapping": [m.model_dump() if hasattr(m, "model_dump") else m for m in req.clip_mapping],
            "quality": req.quality,
            "aspect_ratio": req.aspect_ratio,
        },
        "created_at": now,
        "updated_at": now,
    }
    await repos.get("jobs").put(job_id, job_doc)

    # Try to enqueue the Celery task; fall back to inline if Celery is offline
    try:
        from app.workers.celery_app import celery_app
        celery_app.send_task(
            "zorkvdo.run_render",
            kwargs={
                "job_id": job_id,
                "project_id": req.project_id,
                "owner_id": user_id,
                "blueprint_id": req.blueprint_id,
                "clip_mapping": [m.model_dump() if hasattr(m, "model_dump") else m for m in req.clip_mapping],
                "quality": req.quality,
                "aspect_ratio": req.aspect_ratio,
            },
        )
    except Exception as e:
        log.warning("celery_unavailable_using_background", error=str(e))
        # No Celery — run in background so the API returns immediately
        import asyncio
        from app.api.deps import _storage_cache
        from app.workers.tasks import run_render_job_inline

        clip_mapping_list = [m.model_dump() if hasattr(m, "model_dump") else m for m in req.clip_mapping]

        async def _run_bg():
            try:
                await run_render_job_inline(
                    job_id, req.project_id, user_id, req.blueprint_id,
                    clip_mapping_list,
                    req.quality, req.aspect_ratio,
                    repos=repos.registry,
                    storage=_storage_cache,
                )
            except Exception as bg_exc:
                log.exception("bg_render_failed", job_id=job_id, error=str(bg_exc))
                from datetime import datetime, timezone
                jd = await repos.get("jobs").get(job_id)
                if jd:
                    jd["status"] = "failed"
                    jd["error"] = str(bg_exc)
                    jd["finished_at"] = datetime.now(timezone.utc).isoformat()
                    await repos.get("jobs").put(job_id, jd)

        asyncio.ensure_future(_run_bg())

    doc = await repos.get("jobs").get(job_id)
    if doc is None:
        raise NotFoundError("job not found after creation")
    return JobPublic(**doc)
