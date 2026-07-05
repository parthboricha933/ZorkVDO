"""Integration tests for the auth endpoints."""
from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_register_login_refresh_flow(client):
    # Register
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@test.com",
            "password": "supersecret123",
            "display_name": "Alice",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["user"]["email"] == "alice@test.com"

    # Me
    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "alice@test.com"

    # Refresh
    refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": data["refresh_token"]},
    )
    assert refresh.status_code == 200
    assert refresh.json()["access_token"] != data["access_token"]


@pytest.mark.asyncio
async def test_login_rejects_wrong_password(client):
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "bob@test.com",
            "password": "supersecret123",
            "display_name": "Bob",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "bob@test.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_token(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(authed_client):
    client, _ = authed_client
    # Try registering the same email again
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "tester@zorkvdo.example.com",
            "password": "anotherpass123",
            "display_name": "Other",
        },
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_change_password(client):
    # Register
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "carol@test.com",
            "password": "supersecret123",
            "display_name": "Carol",
        },
    )
    token = resp.json()["access_token"]

    # Change password
    resp2 = await client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={"old_password": "supersecret123", "new_password": "newpassword123"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["changed"] is True

    # Old password should fail
    resp3 = await client.post(
        "/api/v1/auth/login",
        json={"email": "carol@test.com", "password": "supersecret123"},
    )
    assert resp3.status_code == 401

    # New password should work
    resp4 = await client.post(
        "/api/v1/auth/login",
        json={"email": "carol@test.com", "password": "newpassword123"},
    )
    assert resp4.status_code == 200


@pytest.mark.asyncio
async def test_logout_invalidates_session(client):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dave@test.com",
            "password": "supersecret123",
            "display_name": "Dave",
        },
    )
    token = resp.json()["access_token"]

    # Logout
    out = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert out.status_code == 200

    # Token should be revoked
    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 401
