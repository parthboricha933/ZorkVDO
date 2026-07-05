"""ZorkVDO shared schemas.

Pydantic models for the Blueprint JSON contract — the central artifact
produced by video analysis and consumed by the renderer / clip matcher.
Used by both the FastAPI backend and (later) the Flutter app via
`pyscaffold`-style JSON serialization.
"""
from .blueprint import (
    Blueprint,
    BlueprintMeta,
    CaptionStyle,
    ClipSuggestion,
    Effect,
    MusicTrack,
    Scene,
    Transition,
)
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
from .analysis import AnalysisResult, ClipMatch, VideoStats

__all__ = [
    "Blueprint",
    "BlueprintMeta",
    "CaptionStyle",
    "ClipSuggestion",
    "Effect",
    "MusicTrack",
    "Scene",
    "Transition",
    "CameraMotion",
    "CaptionAnimation",
    "CaptionPosition",
    "ColorGrade",
    "EffectType",
    "Pace",
    "ShotType",
    "TransitionType",
    "AnalysisResult",
    "ClipMatch",
    "VideoStats",
]

__version__ = "0.1.0"
