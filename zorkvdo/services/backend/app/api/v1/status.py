"""Developer Settings / API Status page routes: /api/v1/status/*.

Hidden behind authentication. Returns the live status of every external
integration: connected / missing_key / invalid / offline / disabled.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserId
from app.core.config import Settings, get_settings
from app.integrations import get_integration_status

router = APIRouter(prefix="/status", tags=["developer"])


@router.get("")
async def get_status(
    user_id: CurrentUserId,
    refresh: bool = Query(False, description="Force re-run of all probes"),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Full status report for every integration."""
    registry = get_integration_status()
    if refresh or not registry.all_reports():
        await registry.refresh(settings)
    return {
        "summary": registry.summary(),
        "integrations": [r.to_dict() for r in registry.all_reports()],
    }


@router.get("/{name}")
async def get_one_status(
    name: str,
    user_id: CurrentUserId,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Status for a single integration by name (e.g. `gemini`, `redis`)."""
    registry = get_integration_status()
    if not registry.all_reports():
        await registry.refresh(settings)
    report = registry.get(name)
    if not report:
        from app.core.exceptions import NotFoundError
        raise NotFoundError(f"unknown integration: {name}")
    return report.to_dict()


@router.post("/refresh")
async def refresh_status(
    user_id: CurrentUserId,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Force re-run every probe (e.g. after dropping in a new API key)."""
    registry = get_integration_status()
    await registry.refresh(settings)
    return {
        "refreshed": True,
        "summary": registry.summary(),
    }
