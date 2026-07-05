"""Integration tests for the /health and /ready endpoints."""
from __future__ import annotations

import pytest


async def test_health_endpoint(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "zorkvdo-backend"


async def test_ready_endpoint(client):
    resp = await client.get("/api/v1/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "db" in data["checks"]
    assert "storage" in data["checks"]
    assert "ai_provider" in data["checks"]


async def test_root_endpoint(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "ZorkVDO API"
    assert data["docs"] == "/docs"


async def test_openapi_schema_available(client):
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["info"]["title"] == "ZorkVDO API"
    assert "/api/v1/auth/register" in data["paths"]
