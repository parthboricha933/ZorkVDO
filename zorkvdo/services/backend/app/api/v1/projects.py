"""Project routes: /api/v1/projects/*."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserId, get_project_service
from app.models.projects import ProjectCreate, ProjectPublic, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectPublic, status_code=201)
async def create_project(
    req: ProjectCreate,
    user_id: CurrentUserId,
    svc: ProjectService = Depends(get_project_service),
) -> ProjectPublic:
    return await svc.create(user_id, req)


@router.get("", response_model=list[ProjectPublic])
async def list_projects(
    user_id: CurrentUserId,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: ProjectService = Depends(get_project_service),
) -> list[ProjectPublic]:
    return await svc.list(user_id, limit=limit, offset=offset)


@router.get("/{project_id}", response_model=ProjectPublic)
async def get_project(
    project_id: str,
    user_id: CurrentUserId,
    svc: ProjectService = Depends(get_project_service),
) -> ProjectPublic:
    return await svc.get(user_id, project_id)


@router.patch("/{project_id}", response_model=ProjectPublic)
async def update_project(
    project_id: str,
    req: ProjectUpdate,
    user_id: CurrentUserId,
    svc: ProjectService = Depends(get_project_service),
) -> ProjectPublic:
    return await svc.update(user_id, project_id, req)


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    user_id: CurrentUserId,
    svc: ProjectService = Depends(get_project_service),
) -> dict:
    return {"deleted": await svc.delete(user_id, project_id)}
