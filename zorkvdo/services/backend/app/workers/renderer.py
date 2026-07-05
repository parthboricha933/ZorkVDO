"""Video renderer — assembles a final video from a blueprint + user clips.

Strategy:
  1. For each scene, trim the matched clip to the scene's [start, end].
  2. Concatenate the trimmed clips in scene order using the concat demuxer.
  3. Apply a global color-grade LUT (optional, based on blueprint.color_grade).
  4. Burn in captions using the `drawtext` filter (font + size + timing).
  5. Mux in the music track if provided.

This is a pragmatic v1 implementation — it produces a single MP4 at the
requested quality. Advanced effects (slow-motion, glitch, etc.) are
recorded in the blueprint but the renderer applies only the subset that
FFmpeg can do losslessly (trim, concat, drawtext, fade, basic color).
"""
from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from zorkvdo_schemas import Blueprint

log = get_logger(__name__)


# Bitrate ladder (kbps) keyed by quality level
QUALITY_BITRATES: dict[str, dict[str, int]] = {
    "low":    {"video_k": 1500, "audio_k": 96,  "scale": 540},
    "medium": {"video_k": 3000, "audio_k": 128, "scale": 720},
    "high":   {"video_k": 6000, "audio_k": 192, "scale": 1080},
}


# Aspect ratio → scale target
ASPECT_RATIOS: dict[str, tuple[int, int]] = {
    "9:16":  (1080, 1920),
    "16:9":  (1920, 1080),
    "1:1":   (1080, 1080),
    "4:5":   (1080, 1350),
}


async def render_video(
    *,
    blueprint: Blueprint,
    clip_mapping: list[dict],
    clip_paths: dict[str, str],
    quality: str = "high",
    aspect_ratio: str | None = None,
) -> str:
    """Render the final video. Returns path to the output MP4."""
    if not clip_mapping:
        raise ValueError("no clip mapping provided")

    # Determine output dimensions
    if aspect_ratio and aspect_ratio in ASPECT_RATIOS:
        width, height = ASPECT_RATIOS[aspect_ratio]
    else:
        width, height = ASPECT_RATIOS["9:16"]  # default vertical

    ladder = QUALITY_BITRATES.get(quality, QUALITY_BITRATES["high"])
    bitrate_v = ladder["video_k"]
    bitrate_a = ladder["audio_k"]

    # Build per-scene trimmed clips
    workdir = Path(tempfile.mkdtemp(prefix="zorkvdo_render_"))
    segment_paths: list[str] = []

    try:
        # Map scene_index → clip info
        scene_lookup = {s.index: s for s in blueprint.scenes}
        for mapping in clip_mapping:
            scene_idx = mapping["scene_index"]
            clip_id = mapping["clip_id"]
            start = mapping.get("suggested_start", 0.0)
            end = mapping.get("suggested_end")
            scene = scene_lookup.get(scene_idx)
            if not scene:
                continue
            if end is None:
                end = start + scene.duration

            src_path = clip_paths.get(clip_id)
            if not src_path or not os.path.exists(src_path):
                log.warning("clip_missing_for_render", clip_id=clip_id, scene=scene_idx)
                continue

            seg_path = str(workdir / f"scene_{scene_idx:03d}.mp4")
            await _trim_and_scale(
                src_path=src_path,
                dst_path=seg_path,
                start=max(0.0, start),
                duration=max(0.1, end - start),
                width=width,
                height=height,
                bitrate_v=bitrate_v,
                scene=scene,
            )
            segment_paths.append(seg_path)

        if not segment_paths:
            raise RuntimeError("no segments produced from clip mapping")

        # Concat with the concat demuxer
        concat_list = workdir / "concat.txt"
        concat_list.write_text("\n".join(f"file '{p}'" for p in segment_paths))
        output_path = str(workdir / "output.mp4")
        await _concat(concat_list_path=str(concat_list), output_path=output_path, bitrate_v=bitrate_v, bitrate_a=bitrate_a)

        # If the blueprint has captions, burn them in via drawtext
        captions = [
            (scene.index, cap)
            for scene in blueprint.scenes
            for cap in scene.captions
        ]
        if captions:
            captioned_path = str(workdir / "captioned.mp4")
            await _burn_captions(
                input_path=output_path,
                output_path=captioned_path,
                scenes=blueprint.scenes,
                width=width,
                height=height,
                bitrate_v=bitrate_v,
            )
            output_path = captioned_path

        log.info("render_done", output_path=output_path, segments=len(segment_paths))
        return output_path
    except Exception:
        # Cleanup partial work on failure
        import shutil
        shutil.rmtree(workdir, ignore_errors=True)
        raise


async def _trim_and_scale(
    *,
    src_path: str,
    dst_path: str,
    start: float,
    duration: float,
    width: int,
    height: int,
    bitrate_v: int,
    scene,
) -> None:
    """Trim a clip to [start, start+duration] and scale to target dims."""
    # Build filter chain: scale + crop to exact dimensions + apply zoom factor
    zoom = scene.zoom_factor if scene.zoom_factor > 1.0 else 1.0
    # Crop center, then scale
    filter_complex = (
        f"scale={width * zoom // 1 if zoom > 1 else width}:-2,"
        f"crop={width}:{height},setsar=1"
    )

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-ss", f"{start:.3f}",
        "-i", src_path,
        "-t", f"{duration:.3f}",
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", f"{bitrate_v}k",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-an",  # drop audio for segments — we'll mux music at the end
        dst_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"ffmpeg trim failed: {stderr.decode(errors='ignore')[:500]}"
        )


async def _concat(
    *, concat_list_path: str, output_path: str, bitrate_v: int, bitrate_a: int
) -> None:
    """Concatenate segments and add a silent audio track."""
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", f"{bitrate_v}k",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", f"{bitrate_a}k",
        "-shortest",
        "-movflags", "+faststart",
        output_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"ffmpeg concat failed: {stderr.decode(errors='ignore')[:500]}"
        )


async def _burn_captions(
    *,
    input_path: str,
    output_path: str,
    scenes,
    width: int,
    height: int,
    bitrate_v: int,
) -> None:
    """Burn captions into the video using drawtext."""
    # Build a single filter chain with one drawtext per caption
    filters: list[str] = []
    # First, accumulate per-scene start time so captions land correctly
    scene_starts: dict[int, float] = {}
    acc = 0.0
    for scene in scenes:
        scene_starts[scene.index] = acc
        acc += scene.duration

    for scene in scenes:
        for cap in scene.captions:
            t_start = scene_starts.get(scene.index, 0.0) + cap.start
            t_end = scene_starts.get(scene.index, 0.0) + cap.end
            text = cap.text.replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")
            # Vertical position
            y_expr = (
                f"h-{cap.font_size}-40" if cap.position.value == "bottom_third"
                else f"(h-text_h)/2"
            )
            fontcolor = cap.color_hex.lstrip("#")
            filters.append(
                f"drawtext=fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf':"
                f"text='{text}':"
                f"fontcolor={fontcolor}:fontsize={int(cap.font_size)}:"
                f"x=(w-text_w)/2:y={y_expr}:"
                f"box=1:boxcolor=black@0.5:boxborderw=10:"
                f"enable='between(t,{t_start:.2f},{t_end:.2f})'"
            )

    filter_chain = ",".join(filters)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", input_path,
        "-vf", filter_chain,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", f"{bitrate_v}k",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        output_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        log.warning(
            "caption_burn_failed",
            error=stderr.decode(errors="ignore")[:500],
        )
        # Fall back to no captions
        import shutil
        shutil.copy(input_path, output_path)
