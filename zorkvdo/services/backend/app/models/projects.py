"""Project + Video + Blueprint + History DTOs."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str = ""
    source_video_id: str | None = None
    blueprint_id: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


class ProjectPublic(BaseModel):
    id: str
    name: str
    description: str = ""
    status: str = "active"
    owner_id: str
    source_video_id: str | None = None
    blueprint_id: str | None = None
    output_video_id: str | None = None
    created_at: str
    updated_at: str


class VideoPublic(BaseModel):
    id: str
    owner_id: str
    kind: str  # source | user_clip | output
    filename: str
    content_type: str
    size_bytes: int
    storage_key: str
    storage_url: str
    duration_seconds: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    analysis_id: str | None = None
    created_at: str
    updated_at: str


class VideoUploadInit(BaseModel):
    """Client tells the server what it's about to upload."""
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str
    size_bytes: int = Field(..., gt=0)
    kind: str = Field("source", pattern="^(source|user_clip|output)$")


class VideoUploadAck(BaseModel):
    upload_url: str
    upload_method: str = "PUT"
    headers: dict[str, str] = {}
    expires_in_seconds: int
    video_id: str


class VideoUploadComplete(BaseModel):
    """Client confirms the upload finished."""
    storage_key: str | None = None


class BlueprintPublic(BaseModel):
    id: str
    owner_id: str
    name: str
    source_video_id: str
    pace: str = "medium"
    overall_duration: float
    scenes: list[dict[str, Any]]
    music: dict[str, Any] | None = None
    color_grade: str = "natural"
    tags: list[str] = []
    notes: str = ""
    schema_version: str = "1.0.0"
    created_at: str
    updated_at: str


class BlueprintSummary(BaseModel):
    id: str
    name: str
    source_video_id: str
    pace: str
    scene_count: int
    overall_duration: float
    created_at: str
    updated_at: str


class HistoryEntry(BaseModel):
    id: str
    owner_id: str
    project_id: str | None = None
    action: str
    entity_type: str  # project | video | blueprint | render
    entity_id: str
    summary: str = ""
    created_at: str


class TemplatePublic(BaseModel):
    id: str
    name: str
    description: str = ""
    category: str = "general"
    is_premium: bool = False
    preview_url: str | None = None
    blueprint_id: str | None = None
    tags: list[str] = []
    created_at: str
    updated_at: str
