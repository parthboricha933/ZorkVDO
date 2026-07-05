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


class RenderRequest(BaseModel):
    project_id: str
    output_format: str = "mp4"
    quality: str = "high"  # low | medium | high
    aspect_ratio: str | None = None  # e.g. "9:16", "16:9", "1:1"
    blueprint_overrides: dict[str, Any] = {}
