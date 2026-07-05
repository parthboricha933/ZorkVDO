"""The Blueprint contract — the central reusable artifact.

A Blueprint fully describes the editing style of an analysed viral video
in a serialisable form, and is consumed by:

  1. The clip matcher — to map user clips into scene slots.
  2. The renderer    — to assemble a new video following the same style.
  3. The Flutter UI  — to render a timeline editor.

Stability guarantees:
  - Field names are part of the public API; never rename without bumping
    `BlueprintMeta.schema_version`.
  - New optional fields may be added freely.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import (
    CameraMotion,
    CaptionAnimation,
    CaptionPosition,
    ColorGrade,
    EffectType,
    Pace,
    ShotType,
    TransitionType,
)


class CaptionStyle(BaseModel):
    """Visual + temporal style of one caption block."""

    text: str
    start: float = Field(..., description="seconds from scene start", ge=0)
    end: float = Field(..., description="seconds from scene start", ge=0)
    position: CaptionPosition = CaptionPosition.BOTTOM_THIRD
    animation: CaptionAnimation = CaptionAnimation.POP
    font_family: str = "Inter"
    font_size: float = 48.0
    color_hex: str = "#FFFFFF"
    stroke_color_hex: str | None = "#000000"
    stroke_width: float = 2.0
    background_color_hex: str | None = None
    background_opacity: float = 0.0
    bold: bool = True
    italic: bool = False
    uppercase: bool = True
    highlight_words: list[int] = Field(
        default_factory=list,
        description="indices of words to highlight (e.g. for karaoke)",
    )


class Effect(BaseModel):
    type: EffectType = EffectType.NONE
    intensity: float = Field(0.5, ge=0.0, le=1.0)
    duration: float = Field(0.0, ge=0.0, description="seconds, 0 = whole scene")


class Transition(BaseModel):
    """Transition *into* this scene from the previous one."""

    type: TransitionType = TransitionType.CUT
    duration: float = Field(0.2, ge=0.0, le=5.0, description="seconds")


class ClipSuggestion(BaseModel):
    """What kind of user clip should fill this scene slot."""

    role: str = "any"
    preferred_shot: ShotType = ShotType.UNKNOWN
    duration_range: tuple[float, float] = (0.5, 3.0)
    motion: CameraMotion = CameraMotion.STATIC
    description: str = ""
    keywords: list[str] = Field(default_factory=list)
    min_face_count: int = 0
    allow_text_overlay: bool = True


class Scene(BaseModel):
    """One slot in the timeline. Order matters."""

    index: int = Field(..., ge=0)
    start: float = Field(..., ge=0, description="seconds from clip start")
    end: float = Field(..., gt=0, description="seconds from clip start")
    duration: float = Field(..., gt=0)
    shot_type: ShotType = ShotType.MEDIUM
    camera_motion: CameraMotion = CameraMotion.STATIC
    zoom_factor: float = Field(1.0, ge=0.1, le=20.0)
    effects: list[Effect] = Field(default_factory=list)
    transition_in: Transition = Field(default_factory=Transition)
    captions: list[CaptionStyle] = Field(default_factory=list)
    clip_suggestion: ClipSuggestion = Field(default_factory=ClipSuggestion)
    dominant_colors_hex: list[str] = Field(default_factory=list)
    audio_peak_db: float | None = None
    bpm_sync: float | None = Field(None, description="beats-per-minute if detected")


class MusicTrack(BaseModel):
    """Music metadata detected or selected for the blueprint."""

    title: str = ""
    artist: str = ""
    bpm: float | None = None
    key: str | None = None
    energy: float = Field(0.5, ge=0.0, le=1.0)
    beat_times: list[float] = Field(default_factory=list, description="seconds")
    source_url: str | None = None
    license: str | None = None


class BlueprintMeta(BaseModel):
    schema_version: str = "1.0.0"
    generator: str = "zorkvdo-analyzer"
    generated_at: datetime
    source_video_id: str
    source_duration_seconds: float
    fps: float
    width: int
    height: int


class Blueprint(BaseModel):
    """Top-level container — the full reusable editing style."""

    id: str
    name: str
    meta: BlueprintMeta
    pace: Pace = Pace.MEDIUM
    overall_duration: float
    scenes: list[Scene]
    music: MusicTrack | None = None
    color_grade: ColorGrade = ColorGrade.NATURAL
    tags: list[str] = Field(default_factory=list)
    notes: str = ""

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialise to a Firestore-friendly dict (datetime → iso str)."""
        data = self.model_dump(mode="json")
        return data

    @classmethod
    def from_storage_dict(cls, data: dict[str, Any]) -> "Blueprint":
        return cls.model_validate(data)
