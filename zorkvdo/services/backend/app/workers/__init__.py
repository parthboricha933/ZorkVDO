"""Celery app + background tasks.

Imports are lazy — if celery isn't installed (e.g. minimal Docker image),
the app still boots and the API works (analysis runs inline via the
`*_inline` variants in tasks.py).
"""
# Don't import celery_app at module load — it requires celery to be installed.
# The API only needs the `*_inline` task variants which don't use celery.

__all__ = ["celery_app", "run_analysis_job", "run_render_job", "run_match_clips_job"]


def __getattr__(name):
    """Lazy imports — only loaded when actually accessed."""
    if name == "celery_app":
        from .celery_app import celery_app
        return celery_app
    if name in ("run_analysis_job", "run_render_job", "run_match_clips_job"):
        from . import tasks
        return getattr(tasks, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
