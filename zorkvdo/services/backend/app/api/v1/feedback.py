"""Feedback + Help routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUserId, get_user_service
from app.models.user import FeedbackRequest
from app.services.user_service import UserService

router = APIRouter(tags=["feedback"])


@router.post("/feedback")
async def submit_feedback(
    req: FeedbackRequest,
    user_id: CurrentUserId,
    svc: UserService = Depends(get_user_service),
) -> dict:
    fid = await svc.submit_feedback(
        user_id,
        category=req.category,
        subject=req.subject,
        message=req.message,
        contact_email=req.contact_email,
    )
    return {"id": fid, "status": "received"}


@router.get("/help")
async def help_center() -> dict:
    """Static help-centre catalog. In production this would come from a CMS."""
    return {
        "categories": [
            {
                "id": "getting-started",
                "title": "Getting Started",
                "articles": [
                    {"id": "upload-first-video", "title": "Upload your first viral video"},
                    {"id": "first-blueprint", "title": "Generate your first blueprint"},
                    {"id": "first-render", "title": "Render your first video"},
                ],
            },
            {
                "id": "blueprints",
                "title": "Blueprints & Analysis",
                "articles": [
                    {"id": "what-is-blueprint", "title": "What is a Blueprint?"},
                    {"id": "blueprint-quality", "title": "Improving blueprint accuracy"},
                    {"id": "manual-mapping", "title": "Manually remapping clips"},
                ],
            },
            {
                "id": "account",
                "title": "Account & Billing",
                "articles": [
                    {"id": "plans", "title": "Plan comparison"},
                    {"id": "cancel", "title": "Cancel subscription"},
                    {"id": "data-export", "title": "Export your data"},
                ],
            },
        ],
        "contact_email": "support@zorkvdo.example",
    }
