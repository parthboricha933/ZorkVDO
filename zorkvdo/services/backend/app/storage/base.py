"""Storage protocol + value objects."""
from __future__ import annotations

from dataclasses import dataclass
from typing import IO, Protocol, runtime_checkable


@dataclass
class StoredObject:
    """Metadata returned after a successful upload."""

    key: str          # logical key, e.g. "users/{uid}/videos/{vid}.mp4"
    backend: str      # local | s3 | firebase
    size: int         # bytes
    content_type: str
    url: str          # presigned or public URL (depends on backend)
    bucket: str | None = None


@runtime_checkable
class Storage(Protocol):
    backend: str

    async def put(
        self,
        *,
        key: str,
        stream: IO[bytes] | bytes,
        content_type: str,
    ) -> StoredObject: ...

    async def get(self, key: str) -> bytes: ...

    async def delete(self, key: str) -> bool: ...

    async def presigned_url(self, key: str, expires_seconds: int = 3600) -> str: ...
