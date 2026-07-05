"""Unit tests for the storage backend."""
from __future__ import annotations

import pytest

from app.storage.local import LocalStorage


@pytest.fixture
def storage(tmp_path):
    return LocalStorage(root=tmp_path / "storage", bucket="test-bucket")


async def test_put_and_get(storage):
    obj = await storage.put(
        key="users/u1/videos/v1.mp4",
        stream=b"hello world",
        content_type="video/mp4",
    )
    assert obj.size == 11
    assert obj.bucket == "test-bucket"

    data = await storage.get("users/u1/videos/v1.mp4")
    assert data == b"hello world"


async def test_delete(storage):
    await storage.put(key="a/b.txt", stream=b"x", content_type="text/plain")
    assert await storage.delete("a/b.txt") is True
    assert await storage.delete("a/b.txt") is False


async def test_presigned_url_returns_local_path(storage):
    url = await storage.presigned_url("some/key.mp4", expires_seconds=60)
    assert "test-bucket" in url
    assert "some/key.mp4" in url


async def test_path_traversal_blocked(storage):
    with pytest.raises(ValueError):
        await storage.put(
            key="../../etc/passwd",
            stream=b"x",
            content_type="text/plain",
        )


async def test_put_creates_nested_dirs(storage):
    await storage.put(
        key="very/deep/nested/path/file.dat",
        stream=b"data",
        content_type="application/octet-stream",
    )
    data = await storage.get("very/deep/nested/path/file.dat")
    assert data == b"data"
