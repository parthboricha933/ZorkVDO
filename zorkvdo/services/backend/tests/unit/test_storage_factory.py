"""Tests for the storage factory + S3 fallback."""
from __future__ import annotations

import pytest

from app.core.config import Settings
from app.storage import build_storage
from app.storage.local import LocalStorage


def test_build_storage_local_default():
    s = Settings(storage_backend="local", storage_local_root="/tmp/zorkvdo_test", storage_bucket="t")
    storage = build_storage(s)
    assert isinstance(storage, LocalStorage)
    assert storage.bucket == "t"


def test_build_storage_s3_falls_back_when_no_creds():
    """When S3 is requested but boto3 init fails, we fall back to local."""
    s = Settings(
        storage_backend="s3",
        storage_local_root="/tmp/zorkvdo_test",
        storage_bucket="t",
        s3_endpoint="http://localhost:9999",  # nothing there
        s3_access_key="",
        s3_secret_key="",  # empty → S3Storage.__init__ should error
    )
    storage = build_storage(s)
    # Should fall back to local
    assert isinstance(storage, LocalStorage)


def test_build_storage_firebase_falls_back_to_local():
    """Firebase storage isn't implemented yet → falls back to local."""
    s = Settings(
        storage_backend="firebase",
        storage_local_root="/tmp/zorkvdo_test",
        storage_bucket="t",
    )
    storage = build_storage(s)
    assert isinstance(storage, LocalStorage)
