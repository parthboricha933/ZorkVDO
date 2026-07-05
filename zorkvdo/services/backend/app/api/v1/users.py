"""User routes: /api/v1/users/* — profile, settings, subscription, notifications, history, analytics."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserId, get_user_service
from app.models.user import (
    AnalyticsSummary,
    NotificationPublic,
    SubscriptionPlan,
    SubscriptionPublic,
    UserSettings,
    UserSettingsUpdate,
    UserProfileUpdate,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


# ── Profile ───────────────────────────────────────────────────────────
@router.get("/me/profile")
async def get_profile(
    user_id: CurrentUserId,
    svc: UserService = Depends(get_user_service),
) -> dict:
    user = await svc.get_profile(user_id)
    return {
        "id": user["id"],
        "email": user["email"],
        "display_name": user["display_name"],
        "avatar_url": user.get("avatar_url"),
        "bio": user.get("bio", ""),
        "plan": user.get("plan", "free"),
        "created_at": user["created_at"],
    }


@router.patch("/me/profile")
async def update_profile(
    req: UserProfileUpdate,
    user_id: CurrentUserId,
    svc: UserService = Depends(get_user_service),
) -> dict:
    user = await svc.update_profile(user_id, req)
    return {
        "id": user["id"],
        "display_name": user["display_name"],
        "avatar_url": user.get("avatar_url"),
        "bio": user.get("bio", ""),
    }


# ── Settings ──────────────────────────────────────────────────────────
@router.get("/me/settings", response_model=UserSettings)
async def get_settings(
    user_id: CurrentUserId,
    svc: UserService = Depends(get_user_service),
) -> UserSettings:
    return await svc.get_settings(user_id)


@router.patch("/me/settings", response_model=UserSettings)
async def update_settings(
    req: UserSettingsUpdate,
    user_id: CurrentUserId,
    svc: UserService = Depends(get_user_service),
) -> UserSettings:
    return await svc.update_settings(user_id, req)


# ── Subscription ──────────────────────────────────────────────────────
@router.get("/me/subscription", response_model=SubscriptionPublic | None)
async def get_subscription(
    user_id: CurrentUserId,
    svc: UserService = Depends(get_user_service),
) -> SubscriptionPublic | None:
    return await svc.get_subscription(user_id)


@router.get("/plans", response_model=list[SubscriptionPlan])
async def list_plans(
    user_id: CurrentUserId,
    svc: UserService = Depends(get_user_service),
) -> list[SubscriptionPlan]:
    return await svc.list_plans()


@router.post("/me/subscription", response_model=SubscriptionPublic)
async def subscribe(
    body: dict,
    user_id: CurrentUserId,
    svc: UserService = Depends(get_user_service),
) -> SubscriptionPublic:
    plan_code = body.get("plan_code", "free")
    period = body.get("period", "monthly")
    return await svc.subscribe(user_id, plan_code, period)


@router.delete("/me/subscription")
async def cancel_subscription(
    user_id: CurrentUserId,
    svc: UserService = Depends(get_user_service),
) -> dict:
    return {"cancelled": await svc.cancel_subscription(user_id)}


# ── Notifications ─────────────────────────────────────────────────────
@router.get("/me/notifications", response_model=list[NotificationPublic])
async def list_notifications(
    user_id: CurrentUserId,
    unread_only: bool = Query(False),
    svc: UserService = Depends(get_user_service),
) -> list[NotificationPublic]:
    return await svc.list_notifications(user_id, unread_only=unread_only)


@router.post("/me/notifications/{notif_id}/read")
async def mark_notification_read(
    notif_id: str,
    user_id: CurrentUserId,
    svc: UserService = Depends(get_user_service),
) -> dict:
    return {"read": await svc.mark_notification_read(user_id, notif_id)}


# ── History ───────────────────────────────────────────────────────────
@router.get("/me/history")
async def list_history(
    user_id: CurrentUserId,
    limit: int = Query(50, ge=1, le=200),
    svc: UserService = Depends(get_user_service),
) -> list[dict]:
    return await svc.list_history(user_id, limit=limit)


# ── Analytics ─────────────────────────────────────────────────────────
@router.get("/me/analytics", response_model=AnalyticsSummary)
async def analytics(
    user_id: CurrentUserId,
    svc: UserService = Depends(get_user_service),
) -> AnalyticsSummary:
    return await svc.analytics(user_id)
