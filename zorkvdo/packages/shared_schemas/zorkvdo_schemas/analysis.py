"""Video analysis + clip-matching schemas."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .blueprint import Blueprint
from .enums import CameraMotion, ShotType


class VideoStats(BaseModel):
    """Raw technical metadata extracted from a video file."""

    duration_seconds: float
    fps: float
    width: int
    height: int
    codec: str = ""
    bitrate: int | None = None
    has_audio: bool = True
    audio_sample_rate: int | None = None
    audio_channels: int | None = None


class AnalysisResult(BaseModel):
    """Everything the analysis pipeline produces for one video.

    The `blueprint` field is the user-facing artifact; the rest is kept
    for debugging / re-running the blueprint generator without re-doing
    expensive CV passes.
    """

    video_id: str
    stats: VideoStats
    scene_count: int
    detected_objects: dict[str, int] = Field(default_factory=dict)
    detected_faces: int = 0
    detected_pose: bool = False
    dominant_colors_hex: list[str] = Field(default_factory=list)
    detected_bpm: float | None = None
    caption_count: int = 0
    raw_signals: dict[str, Any] = Field(
        default_factory=dict,
        description="intermediate signals (scene boundaries, beat times, ...)",
    )
    blueprint: Blueprint

    def to_storage_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class ClipMatch(BaseModel):
    """A user clip mapped into a blueprint scene slot."""

    scene_index: int
    clip_id: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    match_reasons: list[str] = Field(default_factory=list)
    suggested_start: float = Field(0.0, ge=0.0)
    suggested_end: float | None = None
    suggested_motion: CameraMotion = CameraMotion.STATIC
    suggested_shot: ShotType = ShotType.UNKNOWN
