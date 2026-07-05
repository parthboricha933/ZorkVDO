"""Health + readiness endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Request

from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "zorkvdo-backend", "version": "0.1.0"}


@router.get("/ready")
async def ready(request: Request) -> dict:
    """Check critical dependencies are wired."""
    settings: Settings = get_settings()
    checks: dict[str, str] = {"app": "ok"}

    # Check both app.state (set by lifespan) AND the deps cache (set by tests)
    from app.api import deps as _deps
    repos = getattr(request.app.state, "repositories", None) or _deps._repos_cache
    storage = getattr(request.app.state, "storage", None) or _deps._storage_cache
    ai = getattr(request.app.state, "ai_client", None) or _deps._ai_client_cache

    checks["db"] = "ok" if repos else "degraded"
    checks["storage"] = "ok" if storage else "degraded"
    checks["ai_provider"] = ai.provider_name if ai else "mock"
    return {
        "status": "ok" if all(v in ("ok", "mock") for v in checks.values()) else "degraded",
        "checks": checks,
        "env": settings.app_env,
    }
