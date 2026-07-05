"""Unit tests for the BlueprintBuilder — pure, no video needed."""
from __future__ import annotations

from datetime import datetime, timezone

from zorkvdo_schemas import VideoStats
from zorkvdo_ai.analysis.blueprint_builder import BlueprintBuilder
from zorkvdo_ai.analysis.passes.beat import BeatSignals
from zorkvdo_ai.analysis.passes.caption import CaptionBlock, CaptionSignals
from zorkvdo_ai.analysis.passes.color import ColorSignals
from zorkvdo_ai.analysis.passes.motion import MotionFrame, MotionSignals
from zorkvdo_ai.analysis.passes.object import ObjectSignals
from zorkvdo_ai.analysis.passes.scene import SceneSignals


def _stats(**kw) -> VideoStats:
    defaults = dict(
        duration_seconds=12.0,
        fps=30.0,
        width=1080,
        height=1920,
        codec="h264",
        bitrate=2000000,
        has_audio=True,
        audio_sample_rate=48000,
        audio_channels=2,
    )
    defaults.update(kw)
    return VideoStats(**defaults)


def _scene_signals(durations: list[float]) -> SceneSignals:
    boundaries = [0.0]
    for d in durations[:-1]:
        boundaries.append(boundaries[-1] + d)
    return SceneSignals(
        boundaries=boundaries,
        shot_durations=durations,
        avg_shot_duration=sum(durations) / len(durations) if durations else 0.0,
    )


def _motion_signals(motion) -> MotionSignals:
    return MotionSignals(
        frames=[MotionFrame(time=0.5, motion=motion, pan_x=0, pan_y=0, zoom=0, shake=0)],
        dominant_motion=motion,
        avg_zoom=0.0,
        avg_shake=0.0,
    )


def _beat_signals(bpm=120.0) -> BeatSignals:
    return BeatSignals(
        bpm=bpm,
        beat_times=[0.5, 1.0, 1.5, 2.0],
        onset_times=[0.5, 1.0, 1.5, 2.0],
        energy=0.4,
    )


def _caption_signals() -> CaptionSignals:
    return CaptionSignals(
        blocks=[
            CaptionBlock(
                text="WOW THIS IS INSANE",
                start=0.5,
                end=2.0,
                position=__import__("zorkvdo_schemas").CaptionPosition.BOTTOM_THIRD,
                box=(100, 1800, 800, 60),
                font_size_hint=48.0,
                color_hex="#FFFFFF",
            )
        ]
    )


def _color_signals() -> ColorSignals:
    return ColorSignals(
        dominant_hex=["#FF8800", "#004488", "#222222"],
        palette_hex=["#FF8800", "#004488", "#222222", "#FFFFFF", "#000000"],
        brightness=0.55,
        saturation=0.65,
    )


def _object_signals(faces=1, objects=None) -> ObjectSignals:
    return ObjectSignals(
        object_counts=objects or ({"person": 2} if faces else {}),
        face_count=faces,
        pose_detected=False,
        frames_with_objects=5,
    )


def test_builder_produces_one_scene_per_shot():
    builder = BlueprintBuilder()
    bp = builder.build(
        blueprint_id="bp1",
        blueprint_name="Test",
        video_id="v1",
        stats=_stats(duration_seconds=12.0),
        scene=_scene_signals([2.0, 3.0, 4.0, 3.0]),
        motion=_motion_signals(__import__("zorkvdo_schemas").CameraMotion.STATIC),
        beat=_beat_signals(),
        caption=_caption_signals(),
        color=_color_signals(),
        objects=_object_signals(),
    )
    assert len(bp.scenes) == 4
    assert bp.scenes[0].duration == 2.0
    assert bp.scenes[1].duration == 3.0
    assert bp.overall_duration == 12.0


def test_builder_assigns_pace_from_avg_shot():
    builder = BlueprintBuilder()
    from zorkvdo_schemas import Pace

    # Hyper: avg < 1s
    bp = builder.build(
        blueprint_id="bp1", blueprint_name="x", video_id="v1",
        stats=_stats(duration_seconds=4.0),
        scene=_scene_signals([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]),
        motion=_motion_signals(__import__("zorkvdo_schemas").CameraMotion.STATIC),
        beat=_beat_signals(), caption=CaptionSignals(blocks=[]),
        color=_color_signals(), objects=_object_signals(),
    )
    assert bp.pace == Pace.HYPER

    # Slow: avg >= 4s
    bp = builder.build(
        blueprint_id="bp2", blueprint_name="x", video_id="v1",
        stats=_stats(duration_seconds=12.0),
        scene=_scene_signals([6.0, 6.0]),
        motion=_motion_signals(__import__("zorkvdo_schemas").CameraMotion.STATIC),
        beat=_beat_signals(), caption=CaptionSignals(blocks=[]),
        color=_color_signals(), objects=_object_signals(),
    )
    assert bp.pace == Pace.SLOW


def test_builder_first_scene_is_hook_last_is_cta():
    builder = BlueprintBuilder()
    bp = builder.build(
        blueprint_id="bp1", blueprint_name="x", video_id="v1",
        stats=_stats(duration_seconds=12.0),
        scene=_scene_signals([2.0, 3.0, 4.0, 3.0]),
        motion=_motion_signals(__import__("zorkvdo_schemas").CameraMotion.STATIC),
        beat=_beat_signals(), caption=_caption_signals(),
        color=_color_signals(), objects=_object_signals(faces=1),
    )
    assert bp.scenes[0].clip_suggestion.role == "hook"
    assert bp.scenes[-1].clip_suggestion.role == "cta"


def test_builder_color_grade_classifications():
    from zorkvdo_schemas import ColorGrade
    builder = BlueprintBuilder()

    # Bright + saturated → NEON
    bp = builder.build(
        blueprint_id="bp1", blueprint_name="x", video_id="v1",
        stats=_stats(),
        scene=_scene_signals([12.0]),
        motion=_motion_signals(__import__("zorkvdo_schemas").CameraMotion.STATIC),
        beat=_beat_signals(),
        caption=CaptionSignals(blocks=[]),
        color=ColorSignals(
            dominant_hex=["#FF00FF"], palette_hex=["#FF00FF"],
            brightness=0.8, saturation=0.9,
        ),
        objects=_object_signals(),
    )
    assert bp.color_grade == ColorGrade.NEON

    # Dark → NOIR
    bp = builder.build(
        blueprint_id="bp2", blueprint_name="x", video_id="v1",
        stats=_stats(),
        scene=_scene_signals([12.0]),
        motion=_motion_signals(__import__("zorkvdo_schemas").CameraMotion.STATIC),
        beat=_beat_signals(),
        caption=CaptionSignals(blocks=[]),
        color=ColorSignals(
            dominant_hex=["#000000"], palette_hex=["#000000"],
            brightness=0.1, saturation=0.1,
        ),
        objects=_object_signals(),
    )
    assert bp.color_grade == ColorGrade.NOIR


def test_builder_captions_landed_in_correct_scene():
    builder = BlueprintBuilder()
    bp = builder.build(
        blueprint_id="bp1", blueprint_name="x", video_id="v1",
        stats=_stats(duration_seconds=12.0),
        scene=_scene_signals([3.0, 3.0, 3.0, 3.0]),
        motion=_motion_signals(__import__("zorkvdo_schemas").CameraMotion.STATIC),
        beat=_beat_signals(),
        caption=_caption_signals(),  # caption at 0.5-2.0s → scene 0
        color=_color_signals(),
        objects=_object_signals(),
    )
    # The caption at 0.5-2.0 should land in scene 0
    assert any(c.text == "WOW THIS IS INSANE" for c in bp.scenes[0].captions)
    # And not in scene 1+
    for s in bp.scenes[1:]:
        assert not any(c.text == "WOW THIS IS INSANE" for c in s.captions)


def test_builder_music_attached_when_bpm_present():
    builder = BlueprintBuilder()
    bp = builder.build(
        blueprint_id="bp1", blueprint_name="x", video_id="v1",
        stats=_stats(),
        scene=_scene_signals([12.0]),
        motion=_motion_signals(__import__("zorkvdo_schemas").CameraMotion.STATIC),
        beat=_beat_signals(bpm=140.0),
        caption=CaptionSignals(blocks=[]),
        color=_color_signals(),
        objects=_object_signals(),
    )
    assert bp.music is not None
    assert bp.music.bpm == 140.0


def test_builder_music_omitted_when_no_bpm():
    builder = BlueprintBuilder()
    bp = builder.build(
        blueprint_id="bp1", blueprint_name="x", video_id="v1",
        stats=_stats(),
        scene=_scene_signals([12.0]),
        motion=_motion_signals(__import__("zorkvdo_schemas").CameraMotion.STATIC),
        beat=BeatSignals(bpm=None, beat_times=[], onset_times=[], energy=0.0),
        caption=CaptionSignals(blocks=[]),
        color=_color_signals(),
        objects=_object_signals(),
    )
    assert bp.music is None


def test_builder_tags_include_pace_and_motion():
    from zorkvdo_schemas import CameraMotion
    builder = BlueprintBuilder()
    bp = builder.build(
        blueprint_id="bp1", blueprint_name="x", video_id="v1",
        stats=_stats(),
        scene=_scene_signals([2.0, 2.0]),
        motion=_motion_signals(CameraMotion.PAN_LEFT),
        beat=_beat_signals(),
        caption=CaptionSignals(blocks=[]),
        color=_color_signals(),
        objects=_object_signals(faces=1, objects={"person": 1}),
    )
    assert any(t.startswith("pace:") for t in bp.tags)
    assert any(t.startswith("motion:") for t in bp.tags)
    assert any(t.startswith("mood:") for t in bp.tags)
    assert "subject:person" in bp.tags


def test_builder_handles_empty_scenes_gracefully():
    builder = BlueprintBuilder()
    bp = builder.build(
        blueprint_id="bp1", blueprint_name="x", video_id="v1",
        stats=_stats(duration_seconds=10.0),
        scene=SceneSignals(boundaries=[0.0], shot_durations=[10.0], avg_shot_duration=10.0),
        motion=MotionSignals(frames=[], dominant_motion=__import__("zorkvdo_schemas").CameraMotion.STATIC, avg_zoom=0, avg_shake=0),
        beat=_beat_signals(),
        caption=CaptionSignals(blocks=[]),
        color=_color_signals(),
        objects=_object_signals(faces=0, objects={}),
    )
    assert len(bp.scenes) == 1
    assert bp.scenes[0].duration == 10.0
