"""Template routes: /api/v1/templates/*."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserId, get_template_service
from app.models.projects import TemplatePublic
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TemplatePublic])
async def list_templates(
    user_id: CurrentUserId,
    category: str | None = Query(None),
    is_premium: bool | None = Query(None),
    svc: TemplateService = Depends(get_template_service),
) -> list[TemplatePublic]:
    return await svc.list(category=category, is_premium=is_premium)


@router.get("/{template_id}", response_model=TemplatePublic)
async def get_template(
    template_id: str,
    user_id: CurrentUserId,
    svc: TemplateService = Depends(get_template_service),
) -> TemplatePublic:
    return await svc.get(template_id)
