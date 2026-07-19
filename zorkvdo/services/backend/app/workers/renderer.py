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
# Reduced for Railway free tier memory constraints
QUALITY_BITRATES: dict[str, dict[str, int]] = {
    "low":    {"video_k": 800,  "audio_k": 96,  "scale": 360},
    "medium": {"video_k": 1500, "audio_k": 128, "scale": 540},
    "high":   {"video_k": 2500, "audio_k": 128, "scale": 720},
}


# Aspect ratio → scale target (reduced for memory)
ASPECT_RATIOS: dict[str, tuple[int, int]] = {
    "9:16":  (720, 1280),
    "16:9":  (1280, 720),
    "1:1":   (720, 720),
    "4:5":   (720, 900),
}


async def render_video(
    *,
    blueprint: Blueprint,
    clip_mapping: list[dict],
    clip_paths: dict[str, str],
    quality: str = "high",
    aspect_ratio: str | None = None,
    source_audio_path: str | None = None,
) -> str:
    """Render the final video. Returns path to the output MP4.

    Args:
        source_audio_path: If provided, this audio file is muxed into the
            output instead of a silent track (extracted from the original
            viral video).
    """
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

            # Check if this is an image file (convert to video with Ken Burns)
            is_image = src_path.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp"))
            if is_image:
                await _image_to_video(
                    image_path=src_path,
                    dst_path=seg_path,
                    duration=max(0.5, end - start),
                    width=width,
                    height=height,
                    bitrate_v=bitrate_v,
                )
            else:
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
        await _concat(
            concat_list_path=str(concat_list),
            output_path=output_path,
            bitrate_v=bitrate_v,
            bitrate_a=bitrate_a,
            audio_path=source_audio_path,
        )

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


async def _image_to_video(
    *,
    image_path: str,
    dst_path: str,
    duration: float,
    width: int,
    height: int,
    bitrate_v: int,
) -> None:
    """Convert a still image to a short video clip with Ken Burns zoom effect."""
    filter = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"zoompan=z='min(zoom+0.0015,1.5)':d={int(duration*30)}:s={width}x{height}:fps=30,setsar=1"
    )
    cmd = [
        "ffmpeg", "-y", "-loglevel", "warning",
        "-loop", "1", "-i", image_path,
        "-t", f"{duration:.3f}",
        "-vf", filter,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-an",
        "-threads", "1",
        dst_path,
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        err_msg = stderr.decode(errors='ignore')[:500] if stderr else "(no stderr)"
        raise RuntimeError(f"ffmpeg image-to-video failed (exit {proc.returncode}): {err_msg}")


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
    """Trim a clip to [start, start+duration] and scale to target dims.

    Applies detected effects:
    - Zoom in/out: animated zoom via zoompan filter
    - Flash transition: white frame at start
    - Slow motion: if effect detected
    """
    # Check for zoom effects in the scene
    has_zoom_in = any(e.type.value == "zoom_bump" for e in scene.effects if hasattr(e, 'type'))
    zoom_factor = scene.zoom_factor if scene.zoom_factor > 1.0 else 1.0

    # Check for flash transition
    is_flash = scene.transition_in.type.value == "flash" if hasattr(scene.transition_in, 'type') else False

    # Build filter chain
    if has_zoom_in or zoom_factor > 1.05:
        # Animated zoom in via zoompan
        total_frames = int(duration * 30)
        start_zoom = 1.0
        end_zoom = zoom_factor if zoom_factor > 1.0 else 1.3
        filter_complex = (
            f"scale={width * 2}:{height * 2}:force_original_aspect_ratio=decrease,"
            f"pad={width * 2}:{height * 2}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"zoompan=z='min(zoom+{(end_zoom - start_zoom) / max(total_frames, 1):.6f},{end_zoom})':"
            f"d={total_frames}:s={width}x{height}:fps=30,setsar=1"
        )
    elif is_flash:
        # Flash transition: white frame for 0.1s at start, then normal
        flash_frames = 3  # ~0.1s at 30fps
        filter_complex = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"format=yuv420p,"
            f"geq=r='if(lt(n,{flash_frames}),255,r)':"
            f"g='if(lt(n,{flash_frames}),255,g)':"
            f"b='if(lt(n,{flash_frames}),255,b)',setsar=1"
        )
    else:
        # Standard scale + pad
        filter_complex = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1"
        )

    cmd = [
        "ffmpeg", "-y", "-loglevel", "warning",
        "-ss", f"{start:.3f}",
        "-i", src_path,
        "-t", f"{duration:.3f}",
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-preset", "ultrafast",  # lowest memory usage
        "-crf", "28",  # constant quality (higher = smaller file, lower quality)
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-an",
        "-threads", "1",  # limit to 1 thread to reduce memory
        dst_path,
    ]
    log.info("ffmpeg_trim", cmd=" ".join(cmd), src_exists=os.path.exists(src_path), src_size=os.path.getsize(src_path) if os.path.exists(src_path) else 0)
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        err_msg = stderr.decode(errors='ignore')[:500] if stderr else "(no stderr)"
        out_msg = stdout.decode(errors='ignore')[:200] if stdout else ""
        raise RuntimeError(
            f"ffmpeg trim failed (exit {proc.returncode}): stderr={err_msg} stdout={out_msg}"
        )


async def _concat(
    *, concat_list_path: str, output_path: str, bitrate_v: int, bitrate_a: int,
    audio_path: str | None = None,
) -> None:
    """Concatenate segments and add audio (original track or silent)."""
    if audio_path and os.path.exists(audio_path):
        # Use the original audio track from the viral video
        cmd = [
            "ffmpeg", "-y", "-loglevel", "warning",
            "-f", "concat", "-safe", "0",
            "-i", concat_list_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", f"{bitrate_a}k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            "-movflags", "+faststart",
            "-threads", "1",
            output_path,
        ]
    else:
        # No original audio — use silent track
        cmd = [
            "ffmpeg", "-y", "-loglevel", "warning",
            "-f", "concat", "-safe", "0",
            "-i", concat_list_path,
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", f"{bitrate_a}k",
            "-shortest",
            "-movflags", "+faststart",
            "-threads", "1",
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
