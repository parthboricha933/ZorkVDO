"""Build the Storage backend from settings."""
from __future__ import annotations

from app.core.config import Settings
from app.core.logging import get_logger
from app.storage.base import Storage
from app.storage.local import LocalStorage

log = get_logger(__name__)


def build_storage(settings: Settings) -> Storage:
    backend = settings.storage_provider

    if backend == "s3":
        try:
            from app.storage.s3 import S3Storage

            return S3Storage(
                endpoint=settings.s3_endpoint,
                access_key=settings.s3_access_key,
                secret_key=settings.s3_secret_key.get_secret_value(),
                region=settings.s3_region,
                bucket=settings.storage_bucket,
                use_path_style=settings.s3_use_path_style,
            )
        except Exception as e:
            log.warning("s3_storage_unavailable_falling_back", error=str(e))

    if backend == "firebase":
        # Placeholder: Firebase Storage backend uses the same SDK as Firestore.
        # Implementation deferred until FIREBASE_PROJECT_ID is provided.
        log.warning("firebase_storage_not_implemented_using_local")
        return LocalStorage(root=settings.storage_local_root, bucket=settings.storage_bucket)

    # default
    return LocalStorage(root=settings.storage_local_root, bucket=settings.storage_bucket)
