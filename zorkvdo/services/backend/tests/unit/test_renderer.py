"""Tests for the FFmpeg renderer — uses mocked subprocess calls."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app.workers.renderer import ASPECT_RATIOS, QUALITY_BITRATES, render_video
from zorkvdo_schemas import (
    Blueprint,
    BlueprintMeta,
    CaptionAnimation,
    CaptionPosition,
    CaptionStyle,
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


def _make_blueprint(num_scenes=3, with_captions=False) -> Blueprint:
    meta = BlueprintMeta(
        schema_version="1.0.0",
        generator="test",
        generated_at=datetime.now(timezone.utc),
        source_video_id="v1",
        source_duration_seconds=float(num_scenes * 2),
        fps=30.0,
        width=1080,
        height=1920,
    )
    scenes = []
    for i in range(num_scenes):
        captions = []
        if with_captions:
            captions.append(
                CaptionStyle(
                    text=f"Caption {i}",
                    start=0.0,
                    end=1.0,
                    position=CaptionPosition.BOTTOM_THIRD,
                    animation=CaptionAnimation.POP,
                    font_size=48.0,
                    color_hex="#FFFFFF",
                )
            )
        scenes.append(
            Scene(
                index=i,
                start=float(i * 2),
                end=float((i + 1) * 2),
                duration=2.0,
                shot_type=ShotType.MEDIUM,
                captions=captions,
                transition_in=Transition(type=TransitionType.CUT),
            )
        )
    return Blueprint(
        id="bp1",
        name="Test",
        meta=meta,
        pace=Pace.FAST,
        overall_duration=float(num_scenes * 2),
        scenes=scenes,
        music=None,
        color_grade=ColorGrade.NATURAL,
        tags=["test"],
    )


def _fake_subprocess_success(*args, **kwargs):
    """Mock for asyncio.create_subprocess_exec that succeeds."""
    proc = asyncio.Future()
    proc.set_result(None)

    class FakeProc:
        returncode = 0

        async def communicate(self):
            # Write the output file so subsequent reads work
            cmd = args[0] if args else []
            # Find -i input then the output is the last positional arg
            # Just write an empty file at the destination
            if cmd and isinstance(cmd, list) and len(cmd) > 1:
                # Last positional is the output file
                # Find it by skipping options
                output_path = None
                skip_next = False
                for j, arg in enumerate(cmd):
                    if skip_next:
                        skip_next = False
                        continue
                    if isinstance(arg, str) and arg.startswith("-"):
                        if arg in ("-i", "-ss", "-t", "-vf", "-c:v", "-c:a", "-b:v", "-b:a",
                                    "-preset", "-pix_fmt", "-r", "-f", "-safe", "-movflags"):
                            skip_next = True
                        continue
                    output_path = arg
                if output_path and output_path.endswith(".mp4"):
                    with open(output_path, "wb") as f:
                        f.write(b"\x00\x00\x00\x18ftypmp42")
            return b"", b""

    return FakeProc()


async def test_render_video_basic():
    """Mock FFmpeg and verify render_video produces an output path."""
    bp = _make_blueprint(num_scenes=3)
    clip_paths = {f"clip_{i}": f"/tmp/fake_clip_{i}.mp4" for i in range(3)}

    # Create fake source clips so the existence checks pass
    import os
    import tempfile
    tmp_files = []
    for cid, path in clip_paths.items():
        with open(path, "wb") as f:
            f.write(b"fake")
        tmp_files.append(path)

    try:
        with patch("app.workers.renderer.asyncio.create_subprocess_exec") as mock_subprocess:
            mock_subprocess.side_effect = lambda *a, **kw: _fake_subprocess_success(*a, **kw)
            output_path = await render_video(
                blueprint=bp,
                clip_mapping=[
                    {"scene_index": i, "clip_id": f"clip_{i}", "suggested_start": 0.0, "suggested_end": 2.0}
                    for i in range(3)
                ],
                clip_paths=clip_paths,
                quality="high",
                aspect_ratio="9:16",
            )
        assert output_path
        assert output_path.endswith(".mp4")
    finally:
        for p in tmp_files:
            try:
                os.unlink(p)
            except OSError:
                pass


async def test_render_video_with_captions():
    """Renderer should still produce output when captions are present."""
    bp = _make_blueprint(num_scenes=2, with_captions=True)
    clip_paths = {f"clip_{i}": f"/tmp/fake_clip_c_{i}.mp4" for i in range(2)}
    import os
    for p in clip_paths.values():
        with open(p, "wb") as f:
            f.write(b"fake")

    try:
        with patch("app.workers.renderer.asyncio.create_subprocess_exec") as mock_subprocess:
            mock_subprocess.side_effect = lambda *a, **kw: _fake_subprocess_success(*a, **kw)
            output_path = await render_video(
                blueprint=bp,
                clip_mapping=[
                    {"scene_index": i, "clip_id": f"clip_{i}", "suggested_start": 0.0, "suggested_end": 2.0}
                    for i in range(2)
                ],
                clip_paths=clip_paths,
                quality="medium",
                aspect_ratio="16:9",
            )
        assert output_path
    finally:
        for p in clip_paths.values():
            try:
                os.unlink(p)
            except OSError:
                pass


async def test_render_video_no_mapping_raises():
    bp = _make_blueprint(num_scenes=1)
    with pytest.raises(ValueError, match="no clip mapping"):
        await render_video(
            blueprint=bp,
            clip_mapping=[],
            clip_paths={},
            quality="high",
            aspect_ratio=None,
        )


async def test_render_video_missing_clip_skipped():
    """If a clip is missing from clip_paths, that scene is skipped —
    but if all are missing, render fails with RuntimeError."""
    bp = _make_blueprint(num_scenes=3)
    # Only provide one clip
    import os
    with open("/tmp/fake_partial_0.mp4", "wb") as f:
        f.write(b"fake")
    try:
        with patch("app.workers.renderer.asyncio.create_subprocess_exec") as mock_subprocess:
            mock_subprocess.side_effect = lambda *a, **kw: _fake_subprocess_success(*a, **kw)
            output_path = await render_video(
                blueprint=bp,
                clip_mapping=[
                    {"scene_index": 0, "clip_id": "clip_0", "suggested_start": 0.0, "suggested_end": 2.0},
                    {"scene_index": 1, "clip_id": "clip_1", "suggested_start": 0.0, "suggested_end": 2.0},
                    {"scene_index": 2, "clip_id": "clip_2", "suggested_start": 0.0, "suggested_end": 2.0},
                ],
                clip_paths={"clip_0": "/tmp/fake_partial_0.mp4"},  # only one
                quality="low",
                aspect_ratio="1:1",
            )
        assert output_path
    finally:
        try:
            os.unlink("/tmp/fake_partial_0.mp4")
        except OSError:
            pass


async def test_render_video_all_clips_missing_raises():
    bp = _make_blueprint(num_scenes=2)
    with patch("app.workers.renderer.asyncio.create_subprocess_exec"):
        with pytest.raises(RuntimeError, match="no segments produced"):
            await render_video(
                blueprint=bp,
                clip_mapping=[
                    {"scene_index": i, "clip_id": f"clip_{i}", "suggested_start": 0.0, "suggested_end": 2.0}
                    for i in range(2)
                ],
                clip_paths={},  # no clips available
                quality="high",
                aspect_ratio=None,
            )


def test_quality_ladder_keys():
    assert set(QUALITY_BITRATES.keys()) == {"low", "medium", "high"}
    for q, ladder in QUALITY_BITRATES.items():
        assert "video_k" in ladder
        assert "audio_k" in ladder
        assert "scale" in ladder


def test_aspect_ratios_keys():
    assert "9:16" in ASPECT_RATIOS
    assert "16:9" in ASPECT_RATIOS
    assert "1:1" in ASPECT_RATIOS
    for ratio, (w, h) in ASPECT_RATIOS.items():
        assert w > 0 and h > 0
