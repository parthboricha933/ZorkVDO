"""Filesystem storage backend (default for dev/test)."""
from __future__ import annotations

from pathlib import Path
from typing import IO

from app.storage.base import StoredObject, Storage


class LocalStorage(Storage):
    backend = "local"

    def __init__(self, root: Path | str, bucket: str) -> None:
        self.root = Path(root)
        self.bucket = bucket
        self.base = self.root / bucket
        self.base.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        # Strip leading slashes — every key is relative to bucket root.
        safe = key.lstrip("/")
        path = (self.base / safe).resolve()
        # Prevent path traversal outside base.
        if not str(path).startswith(str(self.base.resolve())):
            raise ValueError(f"unsafe key: {key}")
        return path

    async def put(
        self,
        *,
        key: str,
        stream: IO[bytes] | bytes,
        content_type: str,
    ) -> StoredObject:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = stream if isinstance(stream, bytes) else stream.read()
        path.write_bytes(data)
        return StoredObject(
            key=key,
            backend=self.backend,
            size=len(data),
            content_type=content_type,
            url=f"/storage/{self.bucket}/{key.lstrip('/')}",
            bucket=self.bucket,
        )

    async def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    async def delete(self, key: str) -> bool:
        path = self._path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    async def presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        # Local backend serves via /storage/{bucket}/... route — no signing.
        return f"/storage/{self.bucket}/{key.lstrip('/')}"
