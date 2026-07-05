"""Integration tests for video upload + retrieval."""
from __future__ import annotations

import io

import pytest


async def test_upload_list_get_delete_video(authed_client):
    client, user = authed_client

    # Upload
    resp = await client.post(
        "/api/v1/videos/upload",
        files={"file": ("test.mp4", b"\x00\x00\x00\x18ftypmp42", "video/mp4")},
        data={"kind": "source"},
    )
    assert resp.status_code == 201, resp.text
    video = resp.json()
    assert video["kind"] == "source"
    assert video["filename"] == "test.mp4"
    assert video["owner_id"] == user["id"]
    vid = video["id"]

    # List
    resp = await client.get("/api/v1/videos")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # Get
    resp = await client.get(f"/api/v1/videos/{vid}")
    assert resp.status_code == 200
    assert resp.json()["id"] == vid

    # Download
    resp = await client.get(f"/api/v1/videos/{vid}/download")
    assert resp.status_code == 200

    # Delete
    resp = await client.delete(f"/api/v1/videos/{vid}")
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    # Get after delete → 404
    resp = await client.get(f"/api/v1/videos/{vid}")
    assert resp.status_code == 404


async def test_upload_rejects_invalid_kind(authed_client):
    client, _ = authed_client
    resp = await client.post(
        "/api/v1/videos/upload",
        files={"file": ("test.mp4", b"data", "video/mp4")},
        data={"kind": "invalid"},
    )
    assert resp.status_code == 422


async def test_upload_rejects_invalid_content_type(authed_client):
    client, _ = authed_client
    resp = await client.post(
        "/api/v1/videos/upload",
        files={"file": ("test.exe", b"data", "application/x-msdownload")},
        data={"kind": "source"},
    )
    assert resp.status_code == 422


async def test_video_isolation_between_users(authed_client, second_authed_client):
    c1, _ = authed_client
    c2, _ = second_authed_client

    resp = await c1.post(
        "/api/v1/videos/upload",
        files={"file": ("a.mp4", b"data", "video/mp4")},
        data={"kind": "source"},
    )
    vid = resp.json()["id"]

    # u2 cannot fetch
    resp = await c2.get(f"/api/v1/videos/{vid}")
    assert resp.status_code == 404

    # u2 cannot delete
    resp = await c2.delete(f"/api/v1/videos/{vid}")
    assert resp.status_code == 404


async def test_filter_videos_by_kind(authed_client):
    client, _ = authed_client
    await client.post(
        "/api/v1/videos/upload",
        files={"file": ("s.mp4", b"data", "video/mp4")},
        data={"kind": "source"},
    )
    await client.post(
        "/api/v1/videos/upload",
        files={"file": ("c.mp4", b"data", "video/mp4")},
        data={"kind": "user_clip"},
    )

    resp = await client.get("/api/v1/videos?kind=source")
    assert len(resp.json()) == 1
    assert resp.json()[0]["kind"] == "source"

    resp = await client.get("/api/v1/videos?kind=user_clip")
    assert len(resp.json()) == 1
    assert resp.json()[0]["kind"] == "user_clip"
