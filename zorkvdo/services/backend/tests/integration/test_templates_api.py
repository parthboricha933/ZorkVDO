"""Integration tests for templates + blueprints endpoints."""
from __future__ import annotations

import pytest


async def test_list_templates_seeds_catalog(authed_client):
    client, _ = authed_client
    resp = await client.get("/api/v1/templates")
    assert resp.status_code == 200
    templates = resp.json()
    names = {t["name"] for t in templates}
    assert "Hook → Punchline" in names
    assert "Hype Reel" in names


async def test_get_template_by_id(authed_client):
    client, _ = authed_client
    resp = await client.get("/api/v1/templates/tpl_hook_punchline")
    assert resp.status_code == 200
    assert resp.json()["id"] == "tpl_hook_punchline"


async def test_filter_templates_by_category(authed_client):
    client, _ = authed_client
    resp = await client.get("/api/v1/templates?category=action")
    assert resp.status_code == 200
    for t in resp.json():
        assert t["category"] == "action"


async def test_filter_templates_by_premium(authed_client):
    client, _ = authed_client
    resp = await client.get("/api/v1/templates?is_premium=true")
    assert resp.status_code == 200
    for t in resp.json():
        assert t["is_premium"] is True


async def test_get_missing_template_returns_404(authed_client):
    client, _ = authed_client
    resp = await client.get("/api/v1/templates/does_not_exist")
    assert resp.status_code == 404


async def test_list_blueprints_empty(authed_client):
    client, _ = authed_client
    resp = await client.get("/api/v1/blueprints")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_get_missing_blueprint_404(authed_client):
    client, _ = authed_client
    resp = await client.get("/api/v1/blueprints/missing")
    assert resp.status_code == 404
