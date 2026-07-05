"""Tests for the UserService — settings, subscription, notifications, analytics."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.core.exceptions import NotFoundError
from app.models.user import (
    UserSettings,
    UserSettingsUpdate,
    UserProfileUpdate,
)
from app.services.user_service import UserService


@pytest.fixture
async def user_service(repos):
    return UserService(repos.registry)


async def _create_user(repos, user_id="u1") -> str:
    now = datetime.now(timezone.utc).isoformat()
    await repos.get("users").put(user_id, {
        "id": user_id,
        "email": f"{user_id}@example.com",
        "display_name": user_id.upper(),
        "plan": "free",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    })
    return user_id


async def test_get_settings_returns_defaults(user_service, repos):
    uid = await _create_user(repos)
    s = await user_service.get_settings(uid)
    assert isinstance(s, UserSettings)
    assert s.theme == "system"
    assert s.language == "en"


async def test_update_settings_partial(user_service, repos):
    uid = await _create_user(repos)
    s = await user_service.update_settings(uid, UserSettingsUpdate(theme="dark"))
    assert s.theme == "dark"
    # Other fields stay at default
    assert s.language == "en"


async def test_update_settings_persistent(user_service, repos):
    uid = await _create_user(repos)
    await user_service.update_settings(uid, UserSettingsUpdate(theme="dark", language="fr"))
    s = await user_service.get_settings(uid)
    assert s.theme == "dark"
    assert s.language == "fr"


async def test_list_plans(user_service):
    plans = await user_service.list_plans()
    codes = {p.code for p in plans}
    assert {"free", "creator", "pro"} <= codes
    # Pro should be more expensive than creator
    creator = next(p for p in plans if p.code == "creator")
    pro = next(p for p in plans if p.code == "pro")
    assert pro.price_monthly_usd > creator.price_monthly_usd


async def test_subscribe_creates_active_subscription(user_service, repos):
    uid = await _create_user(repos)
    sub = await user_service.subscribe(uid, "creator", "monthly")
    assert sub.status == "active"
    assert sub.plan_code == "creator"
    # User's plan should be updated
    user = await repos.get("users").get(uid)
    assert user["plan"] == "creator"


async def test_subscribe_replaces_existing(user_service, repos):
    uid = await _create_user(repos)
    s1 = await user_service.subscribe(uid, "creator", "monthly")
    s2 = await user_service.subscribe(uid, "pro", "yearly")
    assert s2.status == "active"
    # Old subscription should be cancelled
    old = await repos.get("subscriptions").get(s1.id)
    assert old["status"] == "cancelled"


async def test_cancel_subscription(user_service, repos):
    uid = await _create_user(repos)
    await user_service.subscribe(uid, "creator", "monthly")
    cancelled = await user_service.cancel_subscription(uid)
    assert cancelled is True
    # User plan reverts to free
    user = await repos.get("users").get(uid)
    assert user["plan"] == "free"


async def test_cancel_when_no_subscription_returns_false(user_service, repos):
    uid = await _create_user(repos)
    assert await user_service.cancel_subscription(uid) is False


async def test_create_and_list_notifications(user_service, repos):
    uid = await _create_user(repos)
    await user_service.create_notification(
        uid, kind="info", title="Welcome", body="Hello!"
    )
    await user_service.create_notification(
        uid, kind="success", title="Done", body="Task complete"
    )
    notifs = await user_service.list_notifications(uid)
    assert len(notifs) == 2


async def test_mark_notification_read(user_service, repos):
    uid = await _create_user(repos)
    n = await user_service.create_notification(uid, kind="info", title="x")
    ok = await user_service.mark_notification_read(uid, n.id)
    assert ok is True
    notifs = await user_service.list_notifications(uid)
    assert notifs[0].read is True


async def test_mark_read_other_user_fails(user_service, repos):
    uid1 = await _create_user(repos, "u1")
    uid2 = await _create_user(repos, "u2")
    n = await user_service.create_notification(uid1, kind="info", title="x")
    with pytest.raises(Exception):
        await user_service.mark_notification_read(uid2, n.id)


async def test_filter_unread_notifications(user_service, repos):
    uid = await _create_user(repos)
    n1 = await user_service.create_notification(uid, kind="info", title="one")
    n2 = await user_service.create_notification(uid, kind="info", title="two")
    await user_service.mark_notification_read(uid, n1.id)
    unread = await user_service.list_notifications(uid, unread_only=True)
    assert len(unread) == 1
    assert unread[0].title == "two"


async def test_history_tracking(user_service, repos):
    """When a project is created, history should be logged."""
    from app.services.project_service import ProjectService
    from app.models.projects import ProjectCreate
    uid = await _create_user(repos)
    project_service = ProjectService(repos.registry)
    await project_service.create(uid, ProjectCreate(name="My Project"))
    history = await user_service.list_history(uid)
    assert len(history) == 1
    assert history[0]["action"] == "create"
    assert history[0]["entity_type"] == "project"


async def test_analytics_summary(user_service, repos):
    from app.services.project_service import ProjectService
    from app.models.projects import ProjectCreate
    uid = await _create_user(repos)
    project_service = ProjectService(repos.registry)
    await project_service.create(uid, ProjectCreate(name="P1"))
    await project_service.create(uid, ProjectCreate(name="P2"))
    summary = await user_service.analytics(uid)
    assert summary.projects_count == 2
    assert summary.videos_count == 0
    assert summary.blueprints_count == 0
    assert summary.recent_activity  # not empty


async def test_submit_feedback(user_service, repos):
    uid = await _create_user(repos)
    fid = await user_service.submit_feedback(
        uid, category="bug", subject="crash", message="steps to repro",
        contact_email="user@example.com",
    )
    assert fid
    # Stored under the notifications collection with kind=feedback
    stored = await repos.get("notifications").get(f"feedback:{fid}")
    assert stored["kind"] == "feedback"
    assert stored["title"] == "crash"


async def test_update_profile(user_service, repos):
    uid = await _create_user(repos)
    await user_service.update_profile(uid, UserProfileUpdate(
        display_name="New Name",
        bio="creator bio",
    ))
    user = await repos.get("users").get(uid)
    assert user["display_name"] == "New Name"
    assert user["bio"] == "creator bio"


async def test_get_profile_unknown_user(user_service):
    with pytest.raises(NotFoundError):
        await user_service.get_profile("nonexistent")
