"""Analysis service — bridges the API surface to the AI engine + Celery.

For synchronous (small) videos the analysis can run inline; for anything
else we enqueue a Celery task and return a job ID immediately.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import NotFoundError, PermissionError, ValidationError
from app.core.logging import get_logger
from app.db.base import RepositoryRegistry
from app.models.jobs import JobPublic
from app.storage.base import Storage
from zorkvdo_ai import VideoAnalyzer
from zorkvdo_ai.analysis import AnalyzerConfig

log = get_logger(__name__)


class AnalysisService:
    def __init__(
        self,
        repos: RepositoryRegistry,
        storage: Storage,
        settings: Settings,
        analyzer: VideoAnalyzer | None = None,
    ) -> None:
        self.repos = repos
        self.storage = storage
        self.settings = settings
        self._analyzer = analyzer

    def _build_analyzer(self) -> VideoAnalyzer:
        if self._analyzer is None:
            cfg = AnalyzerConfig(
                scene_threshold=settings.analysis_scene_threshold,
                sample_fps=settings.analysis_sample_fps,
                ocr_languages=settings.analysis_ocr_languages.split(","),
                yolo_model=settings.yolo_model_path,
                enable_face=settings.analysis_enable_face,
                enable_pose=settings.analysis_enable_pose,
                max_video_seconds=settings.analysis_max_video_seconds,
            )
            self._analyzer = VideoAnalyzer(config=cfg)
        return self._analyzer

    async def start_analysis(
        self,
        owner_id: str,
        video_id: str,
        *,
        blueprint_name: str = "Untitled Blueprint",
        sync: bool = False,
    ) -> JobPublic:
        # Verify ownership
        video = await self.repos.get("videos").get(video_id)
        if not video:
            raise NotFoundError("video not found")
        if video["owner_id"] != owner_id:
            raise NotFoundError("video not found")

        job_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        job_doc = {
            "id": job_id,
            "user_id": owner_id,
            "project_id": None,
            "job_type": "analyze",
            "status": "queued",
            "progress": 0.0,
            "started_at": None,
            "finished_at": None,
            "error": None,
            "result": {"video_id": video_id, "blueprint_name": blueprint_name},
            "created_at": now,
            "updated_at": now,
        }
        await self.repos.get("jobs").put(job_id, job_doc)

        if sync:
            # Run inline (dev/test only). Pass the existing repos so the
            # worker writes to the same in-memory store the API reads from.
            from app.workers.tasks import run_analysis_job_inline
            await run_analysis_job_inline(
                job_id, video_id, owner_id, blueprint_name,
                repos=self.repos,
                storage=self.storage,
            )
            doc = await self.repos.get("jobs").get(job_id)
            if doc is None:
                raise RuntimeError("job doc missing after inline run")
            return JobPublic(**doc)

        # Enqueue Celery task
        try:
            from app.workers.celery_app import celery_app
            celery_app.send_task(
                "zorkvdo.run_analysis",
                kwargs={
                    "job_id": job_id,
                    "video_id": video_id,
                    "owner_id": owner_id,
                    "blueprint_name": blueprint_name,
                },
            )
        except Exception as e:
            log.warning("celery_unavailable_using_background", error=str(e))
            # No Celery — run in a background asyncio task so the API
            # returns immediately. The browser polls /jobs/{id} for status.
            import asyncio
            from app.workers.tasks import run_analysis_job_inline

            async def _run_bg():
                try:
                    await run_analysis_job_inline(
                        job_id, video_id, owner_id, blueprint_name,
                        repos=self.repos, storage=self.storage,
                    )
                except Exception as bg_exc:
                    log.exception("bg_analysis_failed", job_id=job_id, error=str(bg_exc))
                    from datetime import datetime, timezone
                    jd = await self.repos.get("jobs").get(job_id)
                    if jd:
                        jd["status"] = "failed"
                        jd["error"] = str(bg_exc)
                        jd["finished_at"] = datetime.now(timezone.utc).isoformat()
                        await self.repos.get("jobs").put(job_id, jd)

            asyncio.ensure_future(_run_bg())

        # Return immediately with the queued job
        doc = await self.repos.get("jobs").get(job_id)
        if doc is None:
            raise NotFoundError("job not found")
        return JobPublic(**doc)

    async def get_job(self, owner_id: str, job_id: str) -> JobPublic:
        doc = await self.repos.get("jobs").get(job_id)
        if not doc:
            raise NotFoundError("job not found")
        if doc["user_id"] != owner_id:
            raise NotFoundError("job not found")
        return JobPublic(**doc)

    async def list_jobs(self, owner_id: str, limit: int = 50) -> list[JobPublic]:
        rows = await self.repos.get("jobs").query(
            where={"user_id": owner_id}, order_by="created_at", limit=limit
        )
        return [JobPublic(**r) for r in rows]

    async def cancel_job(self, owner_id: str, job_id: str) -> bool:
        doc = await self.repos.get("jobs").get(job_id)
        if not doc:
            raise NotFoundError("job not found")
        if doc["user_id"] != owner_id:
            raise NotFoundError("job not found")
        if doc["status"] in ("succeeded", "failed", "cancelled"):
            return False
        doc["status"] = "cancelled"
        doc["finished_at"] = datetime.now(timezone.utc).isoformat()
        await self.repos.get("jobs").put(job_id, doc)
        return True
