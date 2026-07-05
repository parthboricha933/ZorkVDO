"""Pytest configuration + shared fixtures.

Tests are hermetic: each test gets a fresh in-memory repository, a
temporary storage root, and an isolated FastAPI client. No real Redis,
no real Firebase, no real S3.
"""
from __future__ import annotations

import asyncio
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio

# Ensure backend root + packages on path
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_MONOREPO = _BACKEND_ROOT.parent.parent
sys.path.insert(0, str(_BACKEND_ROOT))
sys.path.insert(0, str(_MONOREPO / "packages" / "shared_schemas"))
sys.path.insert(0, str(_MONOREPO / "packages" / "ai_engine"))


@pytest.fixture(scope="session")
def event_loop():
    """Single event loop for the whole test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def settings(tmp_path):
    """Fresh Settings with everything pinned to dev/test values."""
    # Force settings module to refresh
    from app.core.config import get_settings
    get_settings.cache_clear()

    # Set env vars for the duration of this test
    env = {
        "APP_ENV": "development",
        "APP_LOG_LEVEL": "WARNING",
        "DATABASE_BACKEND": "memory",
        "STORAGE_BACKEND": "local",
        "STORAGE_LOCAL_ROOT": str(tmp_path / "storage"),
        "AI_PROVIDER": "mock",
        "JWT_SECRET": "test_secret_64_chars_long_enough_for_testing_purposes_only",
        "JWT_ACCESS_TTL_MINUTES": "30",
        "JWT_REFRESH_TTL_DAYS": "14",
        "PASSWORD_MIN_LENGTH": "8",
        "ANALYSIS_SCENE_THRESHOLD": "27.0",
        "ANALYSIS_SAMPLE_FPS": "2.0",
        "ANALYSIS_MAX_VIDEO_SECONDS": "600",
        "UPLOAD_MAX_BYTES": "524288000",
    }
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        yield get_settings()
    finally:
        # Restore
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        get_settings.cache_clear()


@pytest_asyncio.fixture
async def repos(settings):
    """Fresh repository registry for each test (isolated state)."""
    from app.db import build_repositories
    from app.api import deps as _deps
    rs = build_repositories(settings)
    _deps._repos_cache = rs  # warm the deps cache
    yield rs
    _deps._repos_cache = None


@pytest_asyncio.fixture
async def storage(settings):
    from app.storage import build_storage
    from app.api import deps as _deps
    st = build_storage(settings)
    _deps._storage_cache = st
    yield st
    _deps._storage_cache = None


@pytest_asyncio.fixture
async def ai_client(settings):
    from zorkvdo_ai import build_ai_client
    from app.api import deps as _deps
    ai = build_ai_client(settings)
    _deps._ai_client_cache = ai
    yield ai
    _deps._ai_client_cache = None


@pytest_asyncio.fixture
async def client(settings, repos, storage, ai_client):
    """Isolated TestClient with all caches warmed."""
    from httpx import ASGITransport, AsyncClient

    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def authed_client(client):
    """A client that's already registered + logged in."""
    from app.core.config import get_settings
    s = get_settings()
    # Register
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "tester@zorkvdo.example.com",
            "password": "test1234password",
            "display_name": "Tester",
        },
    )
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    yield client, resp.json()["user"]


@pytest_asyncio.fixture
async def second_authed_client(client):
    """A second authed client (different user) for permission tests."""
    # Register another user via the same app
    from httpx import ASGITransport, AsyncClient
    from app.main import create_app
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "other@zorkvdo.example.com",
                "password": "test1234password",
                "display_name": "Other",
            },
        )
        assert resp.status_code == 201, resp.text
        token = resp.json()["access_token"]
        ac.headers["Authorization"] = f"Bearer {token}"
        yield ac, resp.json()["user"]
