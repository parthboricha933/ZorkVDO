"""Blueprint routes: /api/v1/blueprints/*."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserId, get_blueprint_service
from app.models.projects import BlueprintPublic, BlueprintSummary
from app.services.blueprint_service import BlueprintService

router = APIRouter(prefix="/blueprints", tags=["blueprints"])


@router.get("", response_model=list[BlueprintSummary])
async def list_blueprints(
    user_id: CurrentUserId,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: BlueprintService = Depends(get_blueprint_service),
) -> list[BlueprintSummary]:
    return await svc.list(user_id, limit=limit, offset=offset)


@router.get("/{blueprint_id}", response_model=BlueprintPublic)
async def get_blueprint(
    blueprint_id: str,
    user_id: CurrentUserId,
    svc: BlueprintService = Depends(get_blueprint_service),
) -> BlueprintPublic:
    return await svc.get(user_id, blueprint_id)


@router.delete("/{blueprint_id}")
async def delete_blueprint(
    blueprint_id: str,
    user_id: CurrentUserId,
    svc: BlueprintService = Depends(get_blueprint_service),
) -> dict:
    return {"deleted": await svc.delete(user_id, blueprint_id)}
