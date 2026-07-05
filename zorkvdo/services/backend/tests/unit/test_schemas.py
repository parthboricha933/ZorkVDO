"""Unit tests for the Blueprint contract + enums."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from zorkvdo_schemas import (
    Blueprint,
    BlueprintMeta,
    CameraMotion,
    CaptionAnimation,
    CaptionStyle,
    ClipSuggestion,
    ColorGrade,
    Effect,
    EffectType,
    MusicTrack,
    Pace,
    Scene,
    ShotType,
    Transition,
    TransitionType,
)


def _build_blueprint(**overrides) -> Blueprint:
    meta = BlueprintMeta(
        schema_version="1.0.0",
        generator="zorkvdo-analyzer",
        generated_at=datetime.now(timezone.utc),
        source_video_id="vid1",
        source_duration_seconds=30.0,
        fps=30.0,
        width=1080,
        height=1920,
    )
    scene = Scene(
        index=0,
        start=0.0,
        end=2.0,
        duration=2.0,
        shot_type=ShotType.WIDE,
        camera_motion=CameraMotion.PAN_LEFT,
        zoom_factor=1.0,
        effects=[Effect(type=EffectType.SLOW_MOTION, intensity=0.5)],
        transition_in=Transition(type=TransitionType.CUT, duration=0.1),
        captions=[
            CaptionStyle(
                text="HELLO",
                start=0.0,
                end=1.5,
                position=__import__("zorkvdo_schemas").CaptionPosition.BOTTOM_THIRD,
                animation=CaptionAnimation.POP,
                font_size=48.0,
                color_hex="#FFFFFF",
                bold=True,
            )
        ],
        clip_suggestion=ClipSuggestion(role="hook", preferred_shot=ShotType.WIDE),
        dominant_colors_hex=["#FF0000", "#00FF00", "#0000FF"],
    )
    bp = Blueprint(
        id="bp1",
        name="Test Blueprint",
        meta=meta,
        pace=Pace.FAST,
        overall_duration=30.0,
        scenes=[scene],
        music=MusicTrack(title="Test", bpm=120.0, energy=0.7),
        color_grade=ColorGrade.TEAL_ORANGE,
        tags=["pace:fast", "mood:energetic"],
    )
    if overrides:
        bp = bp.model_copy(update=overrides)
    return bp


def test_blueprint_serializes_to_json():
    bp = _build_blueprint()
    s = bp.model_dump_json()
    data = json.loads(s)
    assert data["id"] == "bp1"
    assert data["pace"] == "fast"
    assert data["color_grade"] == "teal_orange"
    assert len(data["scenes"]) == 1
    assert data["scenes"][0]["camera_motion"] == "pan_left"


def test_blueprint_round_trips_through_storage():
    bp = _build_blueprint()
    d = bp.to_storage_dict()
    assert isinstance(d, dict)
    bp2 = Blueprint.from_storage_dict(d)
    assert bp2.id == bp.id
    assert bp2.pace == bp.pace
    assert len(bp2.scenes) == len(bp.scenes)
    assert bp2.scenes[0].captions[0].text == "HELLO"


def test_enums_serialize_as_strings():
    assert CameraMotion.PAN_LEFT.value == "pan_left"
    assert EffectType.SLOW_MOTION.value == "slow_motion"
    assert TransitionType.CUT.value == "cut"
    assert Pace.HYPER.value == "hyper"


def test_caption_position_values():
    from zorkvdo_schemas import CaptionPosition
    assert CaptionPosition.BOTTOM_THIRD.value == "bottom_third"
    assert CaptionPosition.CENTER.value == "center"


def test_blueprint_meta_schema_version_immutable_in_ctor():
    bp = _build_blueprint()
    assert bp.meta.schema_version == "1.0.0"


def test_clip_suggestion_defaults():
    cs = ClipSuggestion(role="any")
    assert cs.preferred_shot == ShotType.UNKNOWN
    assert cs.min_face_count == 0
    assert cs.allow_text_overlay is True


def test_effect_intensity_clamped():
    with pytest.raises(Exception):
        Effect(type=EffectType.BLUR, intensity=2.0)
    with pytest.raises(Exception):
        Effect(type=EffectType.BLUR, intensity=-0.1)


def test_scene_duration_must_be_positive():
    with pytest.raises(Exception):
        Scene(
            index=0, start=0.0, end=1.0,
            duration=0.0,  # invalid
        )


def test_blueprint_optional_music():
    bp = _build_blueprint(music=None)
    d = bp.to_storage_dict()
    assert d["music"] is None
    bp2 = Blueprint.from_storage_dict(d)
    assert bp2.music is None
