"""User service — profile, settings, subscription, notifications, analytics."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.exceptions import NotFoundError, PermissionError
from app.db.base import RepositoryRegistry
from app.models.user import (
    AnalyticsSummary,
    NotificationPublic,
    SubscriptionPlan,
    SubscriptionPublic,
    UserSettings,
    UserSettingsUpdate,
    UserProfileUpdate,
)

# Static catalog of subscription plans. In production this would live
# in the database, but a small constant list is fine for v1.
PLANS: list[SubscriptionPlan] = [
    SubscriptionPlan(
        code="free",
        name="Free",
        price_monthly_usd=0.0,
        price_yearly_usd=0.0,
        features=[
            "3 projects",
            "720p rendering",
            "Watermark on export",
            "Community templates",
        ],
    ),
    SubscriptionPlan(
        code="creator",
        name="Creator",
        price_monthly_usd=12.0,
        price_yearly_usd=120.0,
        features=[
            "Unlimited projects",
            "1080p rendering",
            "No watermark",
            "Premium templates",
            "Priority queue",
            "10 GB storage",
        ],
    ),
    SubscriptionPlan(
        code="pro",
        name="Pro",
        price_monthly_usd=29.0,
        price_yearly_usd=290.0,
        features=[
            "Everything in Creator",
            "4K rendering",
            "Cloud rendering (2x GPU)",
            "Team workspace (5 seats)",
            "100 GB storage",
            "Early access features",
        ],
    ),
]


class UserService:
    def __init__(self, repos: RepositoryRegistry) -> None:
        self.repos = repos

    # ── Profile ──────────────────────────────────────────────
    async def update_profile(self, user_id: str, req: UserProfileUpdate) -> dict:
        users = self.repos.get("users")
        user = await users.get(user_id)
        if not user:
            raise NotFoundError("user not found")
        if req.display_name is not None:
            user["display_name"] = req.display_name
        if req.avatar_url is not None:
            user["avatar_url"] = req.avatar_url
        if req.bio is not None:
            user["bio"] = req.bio
        await users.put(user_id, user)
        return user

    async def get_profile(self, user_id: str) -> dict:
        user = await self.repos.get("users").get(user_id)
        if not user:
            raise NotFoundError("user not found")
        return user

    # ── Settings ─────────────────────────────────────────────
    async def get_settings(self, user_id: str) -> UserSettings:
        doc = await self.repos.get("settings").get(user_id)
        if not doc:
            return UserSettings()
        return UserSettings(**{k: v for k, v in doc.items() if k in UserSettings.model_fields})

    async def update_settings(self, user_id: str, req: UserSettingsUpdate) -> UserSettings:
        settings_repo = self.repos.get("settings")
        doc = (await settings_repo.get(user_id)) or {"id": user_id}
        updates = req.model_dump(exclude_none=True)
        doc.update(updates)
        await settings_repo.put(user_id, doc)
        return await self.get_settings(user_id)

    # ── Subscription ─────────────────────────────────────────
    async def list_plans(self) -> list[SubscriptionPlan]:
        return list(PLANS)

    async def get_subscription(self, user_id: str) -> SubscriptionPublic | None:
        rows = await self.repos.get("subscriptions").query(where={"user_id": user_id})
        if not rows:
            return None
        return SubscriptionPublic(**rows[0])

    async def subscribe(self, user_id: str, plan_code: str, period: str) -> SubscriptionPublic:
        plan = next((p for p in PLANS if p.code == plan_code), None)
        if not plan:
            raise NotFoundError(f"plan not found: {plan_code}")
        sub_repo = self.repos.get("subscriptions")
        # Cancel existing active subscription
        existing = await sub_repo.query(where={"user_id": user_id, "status": "active"})
        now = datetime.now(timezone.utc)
        for s in existing:
            s["status"] = "cancelled"
            s["cancelled_at"] = now.isoformat()
            await sub_repo.put(s["id"], s)
        sid = uuid.uuid4().hex
        renews_at = (now.replace(year=now.year + 1) if period == "yearly"
                     else now.replace(month=(now.month % 12) + 1, year=now.year + (1 if now.month == 12 else 0)))
        doc = {
            "id": sid,
            "user_id": user_id,
            "plan_code": plan_code,
            "status": "active",
            "started_at": now.isoformat(),
            "renews_at": renews_at.isoformat(),
            "cancelled_at": None,
        }
        await sub_repo.put(sid, doc)
        # Update user plan
        users = self.repos.get("users")
        user = await users.get(user_id)
        if user:
            user["plan"] = plan_code
            await users.put(user_id, user)
        return SubscriptionPublic(**doc)

    async def cancel_subscription(self, user_id: str) -> bool:
        sub_repo = self.repos.get("subscriptions")
        rows = await sub_repo.query(where={"user_id": user_id, "status": "active"})
        if not rows:
            return False
        for s in rows:
            s["status"] = "cancelled"
            s["cancelled_at"] = datetime.now(timezone.utc).isoformat()
            await sub_repo.put(s["id"], s)
        users = self.repos.get("users")
        user = await users.get(user_id)
        if user:
            user["plan"] = "free"
            await users.put(user_id, user)
        return True

    # ── Notifications ────────────────────────────────────────
    async def list_notifications(self, user_id: str, unread_only: bool = False) -> list[NotificationPublic]:
        rows = await self.repos.get("notifications").query(
            where={"user_id": user_id}, order_by="created_at"
        )
        if unread_only:
            rows = [r for r in rows if not r.get("read", False)]
        return [NotificationPublic(**r) for r in rows]

    async def mark_notification_read(self, user_id: str, notif_id: str) -> bool:
        notif_repo = self.repos.get("notifications")
        doc = await notif_repo.get(notif_id)
        if not doc or doc["user_id"] != user_id:
            raise PermissionError("not your notification")
        doc["read"] = True
        await notif_repo.put(notif_id, doc)
        return True

    async def create_notification(
        self,
        user_id: str,
        *,
        kind: str,
        title: str,
        body: str = "",
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> NotificationPublic:
        nid = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "id": nid,
            "user_id": user_id,
            "kind": kind,
            "title": title,
            "body": body,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "read": False,
            "created_at": now,
        }
        await self.repos.get("notifications").put(nid, doc)
        return NotificationPublic(**doc)

    # ── History ──────────────────────────────────────────────
    async def list_history(self, user_id: str, limit: int = 50) -> list[dict]:
        rows = await self.repos.get("history").query(
            where={"owner_id": user_id}, order_by="created_at", limit=limit
        )
        return rows

    # ── Analytics ────────────────────────────────────────────
    async def analytics(self, user_id: str) -> AnalyticsSummary:
        projects = await self.repos.get("projects").query(where={"owner_id": user_id})
        videos = await self.repos.get("videos").query(where={"owner_id": user_id})
        blueprints = await self.repos.get("blueprints").query(where={"owner_id": user_id})
        renders = [v for v in videos if v.get("kind") == "output"]
        history = await self.list_history(user_id, limit=10)
        storage_used = sum(v.get("size_bytes", 0) for v in videos)
        total_render_seconds = sum(v.get("duration_seconds") or 0 for v in renders)
        return AnalyticsSummary(
            projects_count=len(projects),
            videos_count=len(videos),
            blueprints_count=len(blueprints),
            renders_count=len(renders),
            total_render_seconds=total_render_seconds,
            storage_used_bytes=storage_used,
            recent_activity=[
                {
                    "action": h["action"],
                    "entity_type": h["entity_type"],
                    "entity_id": h["entity_id"],
                    "summary": h["summary"],
                    "created_at": h["created_at"],
                }
                for h in history
            ],
        )

    # ── Feedback ─────────────────────────────────────────────
    async def submit_feedback(
        self, user_id: str, category: str, subject: str, message: str, contact_email: str | None
    ) -> str:
        fid = uuid.uuid4().hex
        # We reuse the `notifications` collection as a simple feedback store;
        # in production this would be a dedicated collection + email dispatch.
        await self.repos.get("notifications").put(
            f"feedback:{fid}",
            {
                "id": fid,
                "user_id": user_id,
                "kind": "feedback",
                "title": subject,
                "body": message,
                "category": category,
                "contact_email": contact_email,
                "read": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return fid
