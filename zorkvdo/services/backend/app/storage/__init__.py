"""Storage abstractions for user uploads (videos, clips, thumbnails).

Backends:
  - `local`  → filesystem (default for dev/tests)
  - `s3`     → S3 / MinIO via boto3
  - `firebase` → Firebase Storage (placeholder; activated when configured)

The backend is selected via `STORAGE_PROVIDER` in env. Each backend
implements the same `Storage` protocol so business logic doesn't care.

Path layout is centralised in `storage.paths` — never construct keys
manually in business code.
"""
from __future__ import annotations

from .base import Storage, StoredObject
from .factory import build_storage
from .local import LocalStorage
from . import paths

__all__ = ["Storage", "StoredObject", "LocalStorage", "build_storage", "paths"]
