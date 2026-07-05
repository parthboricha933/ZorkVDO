"""Tests for the VideoService — uploads, retrieval, ownership."""
from __future__ import annotations

import io
from datetime import datetime, timezone

import pytest

from app.core.config import Settings
from app.core.exceptions import NotFoundError, ValidationError
from app.services.video_service import VideoService
from app.storage.local import LocalStorage


@pytest.fixture
def settings():
    return Settings(
        storage_backend="local",
        storage_local_root="/tmp/zorkvdo_video_test",
        storage_bucket="test",
        upload_max_bytes=1024 * 1024,  # 1 MB
        upload_allowed_video_mimes="video/mp4,video/quicktime",
    )


@pytest.fixture
def storage(settings):
    return LocalStorage(root=settings.storage_local_root, bucket=settings.storage_bucket)


@pytest.fixture
async def video_service(repos, storage, settings):
    return VideoService(repos.registry, storage, settings)


async def _create_user(repos, user_id="u1") -> str:
    now = datetime.now(timezone.utc).isoformat()
    await repos.get("users").put(user_id, {
        "id": user_id, "email": f"{user_id}@x.com", "display_name": user_id,
        "password_hash": "x", "plan": "free", "is_active": True,
        "created_at": now, "updated_at": now,
    })
    return user_id


async def test_upload_creates_video(video_service, repos):
    uid = await _create_user(repos)
    payload = b"video data"  # 10 bytes
    video = await video_service.upload(
        owner_id=uid,
        filename="test.mp4",
        content_type="video/mp4",
        size_bytes=len(payload),
        kind="source",
        stream=payload,
    )
    assert video.filename == "test.mp4"
    assert video.kind == "source"
    assert video.owner_id == uid
    assert video.size_bytes == len(payload)


async def test_upload_rejects_invalid_kind(video_service, repos):
    uid = await _create_user(repos)
    with pytest.raises(ValidationError):
        await video_service.upload(
            owner_id=uid, filename="x", content_type="video/mp4",
            size_bytes=10, kind="invalid", stream=b"x",
        )


async def test_upload_rejects_invalid_mime(video_service, repos):
    uid = await _create_user(repos)
    with pytest.raises(ValidationError):
        await video_service.upload(
            owner_id=uid, filename="x.exe", content_type="application/x-msdownload",
            size_bytes=10, kind="source", stream=b"x",
        )


async def test_upload_rejects_oversize(video_service, repos):
    uid = await _create_user(repos)
    # Try to upload 2 MB but max is 1 MB
    with pytest.raises(ValidationError):
        await video_service.upload(
            owner_id=uid, filename="big.mp4", content_type="video/mp4",
            size_bytes=2 * 1024 * 1024, kind="source", stream=b"x" * (2 * 1024 * 1024),
        )


async def test_get_video(video_service, repos):
    uid = await _create_user(repos)
    v = await video_service.upload(
        owner_id=uid, filename="a.mp4", content_type="video/mp4",
        size_bytes=10, kind="source", stream=b"x",
    )
    fetched = await video_service.get(uid, v.id)
    assert fetched.id == v.id


async def test_get_other_user_video_404(video_service, repos):
    uid = await _create_user(repos, "u1")
    await _create_user(repos, "u2")
    v = await video_service.upload(
        owner_id="u1", filename="a.mp4", content_type="video/mp4",
        size_bytes=10, kind="source", stream=b"x",
    )
    with pytest.raises(NotFoundError):
        await video_service.get("u2", v.id)


async def test_list_videos_by_kind(video_service, repos):
    uid = await _create_user(repos)
    await video_service.upload(
        owner_id=uid, filename="s.mp4", content_type="video/mp4",
        size_bytes=10, kind="source", stream=b"x",
    )
    await video_service.upload(
        owner_id=uid, filename="c.mp4", content_type="video/mp4",
        size_bytes=10, kind="user_clip", stream=b"x",
    )
    sources = await video_service.list(uid, kind="source")
    clips = await video_service.list(uid, kind="user_clip")
    assert len(sources) == 1
    assert len(clips) == 1


async def test_delete_video(video_service, repos):
    uid = await _create_user(repos)
    v = await video_service.upload(
        owner_id=uid, filename="a.mp4", content_type="video/mp4",
        size_bytes=10, kind="source", stream=b"x",
    )
    assert await video_service.delete(uid, v.id) is True
    with pytest.raises(NotFoundError):
        await video_service.get(uid, v.id)


async def test_get_bytes(video_service, repos):
    uid = await _create_user(repos)
    v = await video_service.upload(
        owner_id=uid, filename="a.mp4", content_type="video/mp4",
        size_bytes=10, kind="source", stream=b"hello world",
    )
    data, video = await video_service.get_bytes(uid, v.id)
    assert data == b"hello world"


async def test_update_metadata(video_service, repos):
    uid = await _create_user(repos)
    v = await video_service.upload(
        owner_id=uid, filename="a.mp4", content_type="video/mp4",
        size_bytes=10, kind="source", stream=b"x",
    )
    await video_service.update_metadata(
        v.id, duration=12.5, width=1080, height=1920, fps=30.0, analysis_id="job1",
    )
    fetched = await video_service.get(uid, v.id)
    assert fetched.duration_seconds == 12.5
    assert fetched.width == 1080
    assert fetched.height == 1920
    assert fetched.analysis_id == "job1"
