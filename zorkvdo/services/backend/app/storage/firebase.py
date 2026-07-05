"""Firebase Storage backend.

Uses firebase-admin's bucket API to upload/download/delete files in
Firebase Storage. Activated when:
  - STORAGE_PROVIDER=firebase
  - FIREBASE_PROJECT_ID is set
  - A service-account JSON is present at FIREBASE_CREDENTIALS_PATH

Until then, the factory falls back to LocalStorage.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import IO

from app.core.exceptions import StorageError
from app.core.logging import get_logger
from app.storage.base import StoredObject, Storage

log = get_logger(__name__)


class FirebaseStorage(Storage):
    backend = "firebase"

    def __init__(self, *, bucket_name: str, credentials_path: str, project_id: str) -> None:
        if not credentials_path or not Path(credentials_path).exists():
            raise StorageError(
                "firebase credentials missing for storage",
                details={"expected_path": credentials_path},
            )
        try:
            import firebase_admin
            from firebase_admin import credentials
        except ImportError as e:
            raise StorageError("firebase-admin not installed") from e

        if not firebase_admin._apps.get("[DEFAULT]"):  # type: ignore[attr-defined]
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred, {
                "projectId": project_id,
                "storageBucket": bucket_name,
            })

        self._bucket_name = bucket_name
        self._project_id = project_id
        self._bucket = firebase_admin.storage().bucket()
        log.info("firebase_storage_initialised", bucket=bucket_name, project=project_id)

    async def put(
        self,
        *,
        key: str,
        stream: IO[bytes] | bytes,
        content_type: str,
    ) -> StoredObject:
        data = stream if isinstance(stream, bytes) else stream.read()
        blob = self._bucket.blob(key)

        def _upload():
            blob.upload_from_string(data, content_type=content_type)

        await asyncio.to_thread(_upload)
        log.info("firebase_storage_uploaded", key=key, size=len(data))
        return StoredObject(
            key=key,
            backend=self.backend,
            size=len(data),
            content_type=content_type,
            url=f"gs://{self._bucket_name}/{key}",
            bucket=self._bucket_name,
        )

    async def get(self, key: str) -> bytes:
        blob = self._bucket.blob(key)

        def _download():
            return blob.download_as_bytes()

        return await asyncio.to_thread(_download)

    async def delete(self, key: str) -> bool:
        blob = self._bucket.blob(key)

        def _delete():
            if blob.exists():
                blob.delete()
                return True
            return False

        return await asyncio.to_thread(_delete)

    async def presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        """Generate a signed URL for downloading the file."""
        blob = self._bucket.blob(key)
        expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_seconds)

        def _sign():
            return blob.generate_signed_url(expiration=expiry, version="v4")

        return await asyncio.to_thread(_sign)
