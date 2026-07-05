"""Background job DTOs."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class JobPublic(BaseModel):
    id: str
    user_id: str
    project_id: str | None = None
    job_type: str  # analyze | generate_blueprint | match_clips | render
    status: str   # queued | running | succeeded | failed | cancelled
    progress: float = 0.0
    started_at: str | None = None
    finished_at: str | None = None
    error: str | None = None
    result: dict[str, Any] | None = None
    created_at: str
    updated_at: str


class ClipMappingItem(BaseModel):
    """One entry in the render clip mapping."""

    scene_index: int
    clip_id: str
    suggested_start: float = 0.0
    suggested_end: float | None = None


class RenderRequest(BaseModel):
    """Body for POST /jobs/render."""

    project_id: str
    blueprint_id: str
    clip_mapping: list[ClipMappingItem]
    quality: str = "high"  # low | medium | high
    aspect_ratio: str | None = None  # e.g. "9:16", "16:9", "1:1"
    blueprint_overrides: dict[str, Any] = {}
