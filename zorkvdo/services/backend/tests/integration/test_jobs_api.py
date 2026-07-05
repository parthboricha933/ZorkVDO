"""Tests for the analysis service — exercises the inline (sync) path."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import NotFoundError
from app.services.analysis_service import AnalysisService


async def _upload_video(client) -> str:
    """Helper: upload a video via the authed client and return its id."""
    resp = await client.post(
        "/api/v1/videos/upload",
        files={"file": ("test.mp4", b"\x00\x00\x00\x18ftypmp42", "video/mp4")},
        data={"kind": "source"},
    )
    return resp.json()["id"]


async def test_start_analysis_unknown_video_raises(authed_client):
    client, _ = authed_client
    resp = await client.post("/api/v1/jobs/analyze/does-not-exist?sync=true")
    assert resp.status_code == 404


async def test_start_analysis_with_inline_runner(authed_client, monkeypatch):
    """Patch the analysis task to a stub and verify the job pipeline."""
    client, user = authed_client
    vid = await _upload_video(client)

    # Patch the inline runner so we don't need a real video file
    async def fake_run(job_id, video_id, owner_id, blueprint_name):
        from app.api import deps as _deps
        from app.db import build_repositories
        from app.core.config import get_settings
        s = get_settings()
        repos = _deps._repos_cache or build_repositories(s)
        job_doc = await repos.get("jobs").get(job_id)
        job_doc["status"] = "succeeded"
        job_doc["progress"] = 1.0
        job_doc["finished_at"] = "2025-01-01T00:00:00Z"
        job_doc["result"] = {
            "video_id": video_id,
            "blueprint_id": "bp_fake",
            "scene_count": 5,
            "detected_bpm": 120.0,
        }
        await repos.get("jobs").put(job_id, job_doc)
        return job_doc["result"]

    monkeypatch.setattr("app.workers.tasks.run_analysis_job", fake_run)
    # Also patch the import inside analysis_service
    import app.services.analysis_service as _svc
    original = _svc.AnalysisService.start_analysis

    async def patched_start(self, owner_id, video_id, *, blueprint_name="x", sync=False):
        # Just call the original — it'll dispatch to run_analysis_job
        return await original(self, owner_id, video_id=video_id, blueprint_name=blueprint_name, sync=True)

    monkeypatch.setattr(_svc.AnalysisService, "start_analysis", patched_start)

    resp = await client.post(
        f"/api/v1/jobs/analyze/{vid}?sync=true",
        json={"blueprint_name": "My Blueprint"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["status"] == "succeeded"
    assert data["result"]["scene_count"] == 5


async def test_get_job_unknown_returns_404(authed_client):
    client, _ = authed_client
    resp = await client.get("/api/v1/jobs/does-not-exist")
    assert resp.status_code == 404


async def test_list_jobs_empty(authed_client):
    client, _ = authed_client
    resp = await client.get("/api/v1/jobs")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_cancel_unknown_job_returns_404(authed_client):
    client, _ = authed_client
    resp = await client.post("/api/v1/jobs/does-not-exist/cancel")
    assert resp.status_code == 404


async def test_cancel_already_finished_job_returns_false(authed_client, monkeypatch):
    """A job that's already succeeded cannot be cancelled."""
    client, user = authed_client

    # Insert a fake succeeded job
    from app.api import deps as _deps
    repos = _deps._repos_cache
    job_id = "fake-job-id"
    await repos.get("jobs").put(job_id, {
        "id": job_id,
        "user_id": user["id"],
        "project_id": None,
        "job_type": "analyze",
        "status": "succeeded",
        "progress": 1.0,
        "started_at": "2025-01-01T00:00:00Z",
        "finished_at": "2025-01-01T00:01:00Z",
        "error": None,
        "result": {},
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    })

    resp = await client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert resp.status_code == 200
    assert resp.json()["cancelled"] is False


async def test_cancel_queued_job(authed_client):
    client, user = authed_client
    from app.api import deps as _deps
    repos = _deps._repos_cache
    job_id = "queued-job"
    await repos.get("jobs").put(job_id, {
        "id": job_id,
        "user_id": user["id"],
        "project_id": None,
        "job_type": "analyze",
        "status": "queued",
        "progress": 0.0,
        "started_at": None,
        "finished_at": None,
        "error": None,
        "result": {},
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    })

    resp = await client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert resp.status_code == 200
    assert resp.json()["cancelled"] is True

    # Verify it's marked cancelled
    resp = await client.get(f"/api/v1/jobs/{job_id}")
    assert resp.json()["status"] == "cancelled"


async def test_job_isolation_between_users(authed_client):
    """A job owned by one user should not be visible to another.

    We register the second user via the API on the same client/app so they
    share the same in-memory repository cache.
    """
    c1, u1 = authed_client
    # Register a second user via the same app
    resp = await c1.post(
        "/api/v1/auth/register",
        json={
            "email": "other2@zorkvdo.example.com",
            "password": "supersecret123",
            "display_name": "Other2",
        },
    )
    assert resp.status_code == 201
    u2_token = resp.json()["access_token"]

    from app.api import deps as _deps
    repos = _deps._repos_cache
    job_id = "u1-job"
    await repos.get("jobs").put(job_id, {
        "id": job_id,
        "user_id": u1["id"],
        "project_id": None,
        "job_type": "analyze",
        "status": "queued",
        "progress": 0.0,
        "started_at": None,
        "finished_at": None,
        "error": None,
        "result": {},
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    })

    # u2 (using u2_token) can't see u1's job
    resp = await c1.get(
        f"/api/v1/jobs/{job_id}",
        headers={"Authorization": f"Bearer {u2_token}"},
    )
    assert resp.status_code == 404

    # u2 can't cancel u1's job
    resp = await c1.post(
        f"/api/v1/jobs/{job_id}/cancel",
        headers={"Authorization": f"Bearer {u2_token}"},
    )
    assert resp.status_code == 404
