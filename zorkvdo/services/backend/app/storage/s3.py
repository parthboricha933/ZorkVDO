"""S3 / MinIO storage backend."""
from __future__ import annotations

import asyncio
import time
from typing import IO

from app.core.exceptions import StorageError
from app.core.logging import get_logger
from app.storage.base import StoredObject, Storage

log = get_logger(__name__)


class S3Storage(Storage):
    backend = "s3"

    def __init__(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
        region: str,
        bucket: str,
        use_path_style: bool = True,
    ) -> None:
        if not access_key or not secret_key:
            raise StorageError(
                "S3 credentials missing",
                details={"hint": "set S3_ACCESS_KEY and S3_SECRET_KEY"},
            )
        try:
            import boto3
            from botocore.client import Config
        except ImportError as e:  # pragma: no cover
            raise StorageError("boto3 not installed") from e

        self.bucket = bucket
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(s3={"addressing_style": "path" if use_path_style else "auto"}),
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self._client.head_bucket(Bucket=self.bucket)
        except Exception:
            try:
                self._client.create_bucket(Bucket=self.bucket)
                log.info("s3_bucket_created", bucket=self.bucket)
            except Exception as e:  # pragma: no cover
                log.warning("s3_bucket_create_failed", bucket=self.bucket, error=str(e))

    async def put(
        self,
        *,
        key: str,
        stream: IO[bytes] | bytes,
        content_type: str,
    ) -> StoredObject:
        data = stream if isinstance(stream, bytes) else stream.read()
        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return StoredObject(
            key=key,
            backend=self.backend,
            size=len(data),
            content_type=content_type,
            url=f"/storage/{self.bucket}/{key.lstrip('/')}",
            bucket=self.bucket,
        )

    async def get(self, key: str) -> bytes:
        resp = await asyncio.to_thread(
            self._client.get_object, Bucket=self.bucket, Key=key
        )
        return resp["Body"].read()

    async def delete(self, key: str) -> bool:
        await asyncio.to_thread(self._client.delete_object, Bucket=self.bucket, Key=key)
        return True

    async def presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        return await asyncio.to_thread(
            self._client.generate_presigned_url,
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_seconds,
        )
