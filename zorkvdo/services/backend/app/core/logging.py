"""Structured logging via structlog.

Produces JSON logs in production, pretty console logs in development.
A request_id is bound to every log line via middleware so a single
user request can be traced across the API + Celery worker.
"""
from __future__ import annotations

import logging
import sys
import uuid
from contextvars import ContextVar

import structlog
from structlog.types import EventDict, Processor

# ContextVars propagated across async tasks / Celery jobs.
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)
task_id_ctx: ContextVar[str | None] = ContextVar("task_id", default=None)


def _inject_context(_: logging.LogRecord, __: str, event_dict: EventDict) -> EventDict:
    """Attach request_id / user_id / task_id to every log event."""
    for ctx in (request_id_ctx, user_id_ctx, task_id_ctx):
        value = ctx.get()
        if value:
            event_dict.setdefault(ctx.name, value)
    return event_dict


def configure_logging(level: str = "INFO", json_logs: bool = False) -> None:
    """Configure structlog + stdlib logging once at startup."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        _inject_context,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_logs:
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

    # Bridge stdlib logging so uvicorn / celery logs flow through structlog.
    logging.basicConfig(level=log_level, stream=sys.stderr, force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "celery", "app"):
        target = logging.getLogger(name)
        target.setLevel(log_level)
        target.handlers = []


def new_request_id() -> str:
    rid = uuid.uuid4().hex
    request_id_ctx.set(rid)
    return rid


def bind_user(user_id: str | None) -> None:
    user_id_ctx.set(user_id)


def bind_task(task_id: str | None) -> None:
    task_id_ctx.set(task_id)


def get_logger(name: str = "app") -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
