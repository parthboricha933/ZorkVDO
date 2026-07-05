"""Storage key conventions.

Layout (per the project spec):

    users/{uid}/uploads/{video_id}.mp4      ← source videos + user clips
    users/{uid}/renders/{video_id}.mp4      ← final rendered outputs
    users/{uid}/audio/{audio_id}.wav        ← extracted audio tracks
    users/{uid}/thumbnails/{thumb_id}.jpg   ← video thumbnails
    templates/{template_id}/...             ← global template assets
    cache/{cache_key}                       ← global cache (analysis intermediates)

All functions are pure — they don't touch the storage backend, just
compute the correct key. This keeps the path layout in one place.
"""
from __future__ import annotations

from pathlib import PurePosixPath


def user_upload(uid: str, video_id: str, ext: str = ".mp4") -> str:
    """Path for a user-uploaded source video or clip."""
    ext = ext if ext.startswith(".") else f".{ext}"
    return f"users/{uid}/uploads/{video_id}{ext}"


def user_render(uid: str, video_id: str, ext: str = ".mp4") -> str:
    """Path for a final rendered output video."""
    ext = ext if ext.startswith(".") else f".{ext}"
    return f"users/{uid}/renders/{video_id}{ext}"


def user_audio(uid: str, audio_id: str, ext: str = ".wav") -> str:
    """Path for an extracted audio track."""
    ext = ext if ext.startswith(".") else f".{ext}"
    return f"users/{uid}/audio/{audio_id}{ext}"


def user_thumbnail(uid: str, thumb_id: str, ext: str = ".jpg") -> str:
    """Path for a video thumbnail image."""
    ext = ext if ext.startswith(".") else f".{ext}"
    return f"users/{uid}/thumbnails/{thumb_id}{ext}"


def template_asset(template_id: str, filename: str) -> str:
    """Path for a global template asset."""
    return f"templates/{template_id}/{filename}"


def cache_key(*parts: str) -> str:
    """Path for a global cache entry. Parts are joined with /."""
    return "cache/" + "/".join(PurePosixPath(p).as_posix().lstrip("/") for p in parts)


def parse_user_from_key(key: str) -> str | None:
    """Extract the uid from a `users/{uid}/...` key. Returns None otherwise."""
    parts = key.strip("/").split("/")
    if len(parts) >= 2 and parts[0] == "users":
        return parts[1]
    return None


def parse_kind_from_key(key: str) -> str | None:
    """Extract the kind (uploads/renders/audio/thumbnails) from a user key."""
    parts = key.strip("/").split("/")
    if len(parts) >= 3 and parts[0] == "users":
        return parts[2]
    return None
