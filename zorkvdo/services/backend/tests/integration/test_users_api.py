"""Integration tests for user + settings + subscription + analytics endpoints."""
from __future__ import annotations

import pytest


async def test_get_update_profile(authed_client):
    client, _ = authed_client

    resp = await client.get("/api/v1/users/me/profile")
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Tester"

    resp = await client.patch(
        "/api/v1/users/me/profile",
        json={"display_name": "Updated Name", "bio": "creator"},
    )
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Updated Name"
    assert resp.json()["bio"] == "creator"


async def test_get_update_settings(authed_client):
    client, _ = authed_client

    # Defaults
    resp = await client.get("/api/v1/users/me/settings")
    assert resp.status_code == 200
    assert resp.json()["theme"] == "system"

    # Update
    resp = await client.patch(
        "/api/v1/users/me/settings",
        json={"theme": "dark", "language": "fr"},
    )
    assert resp.status_code == 200
    assert resp.json()["theme"] == "dark"
    assert resp.json()["language"] == "fr"

    # Persistent
    resp = await client.get("/api/v1/users/me/settings")
    assert resp.json()["theme"] == "dark"


async def test_list_plans(authed_client):
    client, _ = authed_client
    resp = await client.get("/api/v1/users/plans")
    assert resp.status_code == 200
    plans = resp.json()
    codes = {p["code"] for p in plans}
    assert {"free", "creator", "pro"} <= codes


async def test_subscribe_and_cancel(authed_client):
    client, user = authed_client

    # Subscribe
    resp = await client.post(
        "/api/v1/users/me/subscription",
        json={"plan_code": "creator", "period": "monthly"},
    )
    assert resp.status_code == 200
    assert resp.json()["plan_code"] == "creator"
    assert resp.json()["status"] == "active"

    # Get current
    resp = await client.get("/api/v1/users/me/subscription")
    assert resp.status_code == 200
    assert resp.json()["plan_code"] == "creator"

    # Cancel
    resp = await client.delete("/api/v1/users/me/subscription")
    assert resp.status_code == 200
    assert resp.json()["cancelled"] is True

    # Get again → none
    resp = await client.get("/api/v1/users/me/subscription")
    assert resp.status_code == 200
    # Cancelled subscription is still returned (history) — but our impl just shows
    # the latest row, which is now cancelled. Accept either null or cancelled status.
    if resp.json():
        assert resp.json()["status"] == "cancelled"


async def test_analytics(authed_client):
    client, _ = authed_client

    # Create a project so analytics isn't empty
    await client.post("/api/v1/projects", json={"name": "x"})

    resp = await client.get("/api/v1/users/me/analytics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["projects_count"] >= 1
    assert "recent_activity" in data


async def test_history(authed_client):
    client, _ = authed_client
    await client.post("/api/v1/projects", json={"name": "x"})
    resp = await client.get("/api/v1/users/me/history")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


async def test_feedback_submission(authed_client):
    client, _ = authed_client
    resp = await client.post(
        "/api/v1/feedback",
        json={
            "category": "bug",
            "subject": "App crashes on upload",
            "message": "Steps to reproduce: ...",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "received"


async def test_help_center(authed_client):
    client, _ = authed_client
    resp = await client.get("/api/v1/help")
    assert resp.status_code == 200
    assert "categories" in resp.json()
