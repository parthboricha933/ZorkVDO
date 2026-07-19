"""Video service — uploads, listing, deletion, storage delegation.

Storage layout (per project spec):
  - source videos → users/{uid}/uploads/{video_id}.mp4
  - user clips    → users/{uid}/uploads/{video_id}.mp4  (kind=user_clip)
  - rendered output → users/{uid}/renders/{video_id}.mp4 (kind=output)
"""
from __future__ import annotations

import mimetypes
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.db.base import RepositoryRegistry
from app.models.projects import VideoPublic
from app.storage import Storage, paths
from app.storage.base import StoredObject

log = get_logger(__name__)


class VideoService:
    def __init__(
        self,
        repos: RepositoryRegistry,
        storage: Storage,
        settings: Settings,
    ) -> None:
        self.repos = repos
        self.storage = storage
        self.settings = settings

    async def upload(
        self,
        owner_id: str,
        *,
        filename: str,
        content_type: str,
        size_bytes: int,
        kind: str,
        stream,
    ) -> VideoPublic:
        # Validate
        if kind not in ("source", "user_clip", "output"):
            raise ValidationError("kind must be source|user_clip|output")
        if size_bytes > self.settings.upload_max_bytes:
            raise ValidationError(
                "file too large",
                details={"max_bytes": self.settings.upload_max_bytes},
            )

        # If the content type is generic, try to infer from filename extension
        if content_type in ("application/octet-stream", ""):
            import mimetypes
            inferred = mimetypes.guess_type(filename)[0]
            if inferred:
                content_type = inferred

        # Accept both video AND image files (images are converted to clips)
        allowed = self.settings.allowed_video_mimes | self.settings.allowed_image_mimes
        if content_type not in allowed:
            raise ValidationError(
                "unsupported content type",
                details={"allowed": sorted(allowed), "got": content_type},
            )

        # Track whether this is an image (for renderer to convert)
        is_image = content_type in self.settings.allowed_image_mimes

        vid = uuid.uuid4().hex
        ext = Path(filename).suffix or mimetypes.guess_extension(content_type) or ""

        # Pick the right path helper based on kind
        if kind == "output":
            key = paths.user_render(owner_id, vid, ext)
        else:
            # Both `source` and `user_clip` go under uploads/
            key = paths.user_upload(owner_id, vid, ext)

        stored: StoredObject = await self.storage.put(
            key=key, stream=stream, content_type=content_type
        )
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "id": vid,
            "owner_id": owner_id,
            "kind": kind,
            "filename": filename,
            "content_type": content_type,
            "size_bytes": stored.size,
            "storage_key": stored.key,
            "storage_url": stored.url,
            "duration_seconds": None,
            "width": None,
            "height": None,
            "fps": None,
            "analysis_id": None,
            "is_image": is_image,
            "created_at": now,
            "updated_at": now,
        }
        await self.repos.get("videos").put(vid, doc)
        log.info(
            "video_uploaded",
            video_id=vid,
            owner_id=owner_id,
            size=stored.size,
            kind=kind,
            key=stored.key,
        )
        return VideoPublic(**doc)

    async def get(self, owner_id: str, video_id: str) -> VideoPublic:
        doc = await self._get_owned(owner_id, video_id)
        return VideoPublic(**doc)

    async def list(
        self,
        owner_id: str,
        *,
        kind: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[VideoPublic]:
        where = {"owner_id": owner_id}
        if kind:
            where["kind"] = kind
        rows = await self.repos.get("videos").query(
            where=where, order_by="created_at", limit=limit, offset=offset
        )
        return [VideoPublic(**r) for r in rows]

    async def delete(self, owner_id: str, video_id: str) -> bool:
        """Delete a video. Raises NotFoundError if not found or not owned."""
        doc = await self._get_owned(owner_id, video_id)
        try:
            await self.storage.delete(doc["storage_key"])
        except Exception as e:
            log.warning("storage_delete_failed", error=str(e))
        ok = await self.repos.get("videos").delete(video_id)
        return ok

    async def get_bytes(self, owner_id: str, video_id: str) -> tuple[bytes, VideoPublic]:
        video = await self.get(owner_id, video_id)
        data = await self.storage.get(video.storage_key)
        return data, video

    async def update_metadata(
        self, video_id: str, *, duration: float, width: int, height: int, fps: float, analysis_id: str | None = None
    ) -> None:
        """Called by the analysis worker after probing the file."""
        doc = await self.repos.get("videos").get(video_id)
        if not doc:
            raise NotFoundError("video not found")
        doc.update({
            "duration_seconds": duration,
            "width": width,
            "height": height,
            "fps": fps,
        })
        if analysis_id:
            doc["analysis_id"] = analysis_id
        await self.repos.get("videos").put(video_id, doc)

    async def _get_owned(self, owner_id: str, video_id: str) -> dict:
        doc = await self.repos.get("videos").get(video_id)
        if not doc:
            raise NotFoundError("video not found")
        if doc["owner_id"] != owner_id:
            raise NotFoundError("video not found")
        return doc
