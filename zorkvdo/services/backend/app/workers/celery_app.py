"""Celery app definition.

The Celery worker is a separate process from the FastAPI app but shares
the same codebase. It reads from Redis and processes long-running jobs:
  - run_analysis  : video → AnalysisResult + Blueprint
  - run_match_clips: blueprint + user clips → list[ClipMatch]
  - run_render    : blueprint + clip mapping → output video file
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Ensure local packages are importable in worker process too
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND_ROOT))
sys.path.insert(0, str(_BACKEND_ROOT.parent.parent / "packages" / "shared_schemas"))
sys.path.insert(0, str(_BACKEND_ROOT.parent.parent / "packages" / "ai_engine"))

from celery import Celery  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.logging import configure_logging, get_logger  # noqa: E402

log = get_logger(__name__)

settings = get_settings()

celery_app = Celery(
    "zorkvdo",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=60 * 30,           # 30 min hard limit
    task_soft_time_limit=60 * 25,      # 25 min soft limit
    worker_max_tasks_per_child=10,     # recycle to release CV memory
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=60 * 60 * 24,       # 24h
    task_default_queue="zorkvdo",
)


@celery_app.task(name="zorkvdo.ping")
def ping() -> str:
    return "pong"


def run_worker() -> None:  # pragma: no cover - CLI entry
    configure_logging(level=settings.app_log_level, json_logs=settings.is_prod)
    log.info("celery_worker_starting", broker=settings.celery_broker_url)
    celery_app.start()


def _run_async(coro):
    """Helper to bridge sync Celery tasks → async functions."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
