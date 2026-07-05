"""Job routes: /api/v1/jobs/* — analysis + rendering queue."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserId, get_analysis_service
from app.models.jobs import JobPublic
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/jobs", tags=["jobs"])


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
