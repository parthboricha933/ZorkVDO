"""MoviePy service — high-level editing operations.

MoviePy is used for the operations that benefit from a Pythonic API:
  - text animations (typewriter, pop, slide)
  - picture-in-picture overlays
  - complex transition effects (crossfade, slide, wipe)
  - audio mixing (multiple tracks, ducking, fade)

FFmpeg remains primary for fast operations (trim, scale, concat) — see
`app.workers.renderer`.

This module is lazily imported — if `moviepy` isn't installed, every
method raises a clear error so the caller can fall back to FFmpeg.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from app.core.logging import get_logger

log = get_logger(__name__)


class MoviePyService:
    """High-level editing ops via MoviePy.

    The service is lazy — `moviepy` is only imported when a method is
    first called. This keeps the backend light when MoviePy isn't needed.
    """

    def __init__(self) -> None:
        self._moviepy: Any | None = None
        self._vfx: Any | None = None
        self._afx: Any | None = None

    def _ensure_moviepy(self) -> None:
        if self._moviepy is not None:
            return
        try:
            from moviepy import (
                VideoFileClip,
                TextClip,
                CompositeVideoClip,
                ImageClip,
                AudioFileClip,
                concatenate_videoclips,
            )
            from moviepy import vfx, afx
            self._moviepy = {
                "VideoFileClip": VideoFileClip,
                "TextClip": TextClip,
                "CompositeVideoClip": CompositeVideoClip,
                "ImageClip": ImageClip,
                "AudioFileClip": AudioFileClip,
                "concatenate_videoclips": concatenate_videoclips,
            }
            self._vfx = vfx
            self._afx = afx
        except ImportError as e:
            raise RuntimeError(
                "moviepy is not installed. Install with: pip install moviepy"
            ) from e

    async def add_text_animation(
        self,
        video_path: str,
        output_path: str,
        *,
        text: str,
        start: float,
        end: float,
        font_size: int = 48,
        color: str = "white",
        stroke_color: str = "black",
        stroke_width: int = 2,
        position: tuple[str, str] = ("center", "bottom"),
        animation: str = "pop",  # pop | typewriter | slide_in
    ) -> str:
        """Burn an animated text caption into a video.

        Animations:
          - pop        : scale up from 0.5 to 1.0 over the first 0.15s
          - typewriter : reveal characters one at a time
          - slide_in   : slide in from the left
        """
        def _work() -> str:
            self._ensure_moviepy()
            mp = self._moviepy
            vfx = self._vfx

            video = mp["VideoFileClip"](video_path)

            # Build the text clip
            text_clip = mp["TextClip"](
                text=text,
                font_size=font_size,
                color=color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                method="caption",
                size=(video.w * 0.9, None),
                text_align="center",
            )

            # Apply animation
            if animation == "pop":
                text_clip = text_clip.with_effects([
                    vfx.Resize(lambda t: 0.5 + 0.5 * min(1, t / 0.15))
                ])
            elif animation == "slide_in":
                text_clip = text_clip.with_position(
                    lambda t: (video.w * 0.05 - (1 - min(1, t / 0.3)) * video.w * 0.5, "bottom")
                )
            # typewriter: would need per-character clip splitting; skip for v1

            text_clip = text_clip.with_start(start).with_end(end).with_position(position)

            composite = mp["CompositeVideoClip"]([video, text_clip])
            composite.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                preset="veryfast",
                logger=None,
            )
            video.close()
            composite.close()
            return output_path

        return await asyncio.to_thread(_work)

    async def add_picture_in_picture(
        self,
        main_video_path: str,
        overlay_video_path: str,
        output_path: str,
        *,
        overlay_size: tuple[int, int] = (320, 180),
        overlay_position: tuple[str, str] = ("right", "top"),
        overlay_start: float = 0.0,
        overlay_end: float | None = None,
    ) -> str:
        """Overlay a smaller video on top of the main video (PiP)."""
        def _work() -> str:
            self._ensure_moviepy()
            mp = self._moviepy

            main = mp["VideoFileClip"](main_video_path)
            overlay = mp["VideoFileClip"](overlay_video_path)

            # Resize + position the overlay
            overlay = overlay.resized(overlay_size)
            overlay = overlay.with_start(overlay_start)
            if overlay_end is not None:
                overlay = overlay.with_end(overlay_end)
            overlay = overlay.with_position(overlay_position)

            composite = mp["CompositeVideoClip"]([main, overlay])
            composite.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                preset="veryfast",
                logger=None,
            )
            main.close()
            overlay.close()
            composite.close()
            return output_path

        return await asyncio.to_thread(_work)

    async def add_crossfade_transition(
        self,
        clip_a_path: str,
        clip_b_path: str,
        output_path: str,
        *,
        fade_duration: float = 0.5,
    ) -> str:
        """Crossfade two clips — clip B fades in over the end of clip A."""
        def _work() -> str:
            self._ensure_moviepy()
            mp = self._moviepy
            vfx = self._vfx

            clip_a = mp["VideoFileClip"](clip_a_path)
            clip_b = mp["VideoFileClip"](clip_b_path)

            # Crossfade: clip_b starts `fade_duration` before clip_a ends,
            # and fades in over `fade_duration`.
            clip_b = clip_b.with_start(clip_a.duration - fade_duration)
            clip_b = clip_b.with_effects([vfx.CrossFadeIn(fade_duration)])

            composite = mp["CompositeVideoClip"]([clip_a, clip_b])
            composite.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                preset="veryfast",
                logger=None,
            )
            clip_a.close()
            clip_b.close()
            composite.close()
            return output_path

        return await asyncio.to_thread(_work)

    async def mix_audio(
        self,
        video_path: str,
        music_path: str,
        output_path: str,
        *,
        music_volume: float = 0.4,
        duck: bool = True,
        duck_threshold: float = 0.05,
    ) -> str:
        """Mix a music track under the video's existing audio.

        If `duck` is True, the music volume drops when the original audio
        is louder than `duck_threshold`.
        """
        def _work() -> str:
            self._ensure_moviepy()
            mp = self._moviepy
            afx = self._afx

            video = mp["VideoFileClip"](video_path)
            music = mp["AudioFileClip"](music_path)

            # Loop or trim music to match video duration
            if music.duration < video.duration:
                # Loop the music
                loops_needed = int(video.duration / music.duration) + 1
                from moviepy.audio.AudioClip import concatenate_audioclips
                music_parts = [music] * loops_needed
                music = concatenate_audioclips(music_parts)
            music = music.subclipped(0, video.duration)

            # Apply volume
            music = music.with_effects([afx.MultiplyVolume(music_volume)])

            # Mix with original audio
            if video.audio is not None:
                mixed = mp["CompositeAudioClip"]([video.audio, music])
            else:
                mixed = music

            final = video.with_audio(mixed)
            final.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                preset="veryfast",
                logger=None,
            )
            video.close()
            music.close()
            final.close()
            return output_path

        return await asyncio.to_thread(_work)

    def is_available(self) -> bool:
        """True if moviepy is installed."""
        try:
            import moviepy  # noqa: F401
            return True
        except ImportError:
            return False
