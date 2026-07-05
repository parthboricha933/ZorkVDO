"""Integration tests for project endpoints."""
from __future__ import annotations

import pytest


async def test_create_list_get_update_delete_project(authed_client):
    client, user = authed_client

    # Create
    resp = await client.post(
        "/api/v1/projects",
        json={"name": "My First Project", "description": "Test desc"},
    )
    assert resp.status_code == 201, resp.text
    proj = resp.json()
    assert proj["name"] == "My First Project"
    assert proj["owner_id"] == user["id"]
    pid = proj["id"]

    # List
    resp = await client.get("/api/v1/projects")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == pid

    # Get
    resp = await client.get(f"/api/v1/projects/{pid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == pid

    # Update
    resp = await client.patch(
        f"/api/v1/projects/{pid}",
        json={"name": "Renamed Project", "status": "archived"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed Project"
    assert resp.json()["status"] == "archived"

    # Delete
    resp = await client.delete(f"/api/v1/projects/{pid}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    # Get after delete → 404
    resp = await client.get(f"/api/v1/projects/{pid}")
    assert resp.status_code == 404


async def test_project_isolation_between_users(authed_client, second_authed_client):
    c1, u1 = authed_client
    c2, u2 = second_authed_client

    # u1 creates a project
    resp = await c1.post("/api/v1/projects", json={"name": "u1's project"})
    pid = resp.json()["id"]

    # u2 cannot see it
    resp = await c2.get(f"/api/v1/projects/{pid}")
    assert resp.status_code == 404

    # u2 cannot delete it
    resp = await c2.delete(f"/api/v1/projects/{pid}")
    assert resp.status_code == 404


async def test_create_project_requires_auth(client):
    resp = await client.post("/api/v1/projects", json={"name": "x"})
    assert resp.status_code == 401


async def test_list_projects_pagination(authed_client):
    client, _ = authed_client
    # Create 5 projects
    for i in range(5):
        await client.post("/api/v1/projects", json={"name": f"P{i}"})

    # Limit
    resp = await client.get("/api/v1/projects?limit=2")
    assert len(resp.json()) == 2

    # Offset
    resp = await client.get("/api/v1/projects?limit=2&offset=2")
    assert len(resp.json()) == 2
