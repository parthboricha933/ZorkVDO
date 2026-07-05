"""FFprobe wrapper — extracts container-level stats (no CV needed)."""
from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path

from zorkvdo_schemas import VideoStats


@dataclass
class ProbeResult:
    stats: VideoStats
    raw: dict


class VideoProber:
    """Wraps ffprobe (ships with ffmpeg) to read container metadata."""

    def __init__(self, ffprobe_path: str = "ffprobe") -> None:
        self._bin = ffprobe_path

    async def probe(self, video_path: str | Path) -> ProbeResult:
        path = str(video_path)
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        cmd = [
            self._bin,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            path,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(
                f"ffprobe failed: {stderr.decode(errors='ignore')[:500]}"
            )

        data = json.loads(stdout.decode())
        return ProbeResult(stats=self._parse(data, path), raw=data)

    def _parse(self, data: dict, path: str) -> VideoStats:
        fmt = data.get("format", {})
        streams = data.get("streams", [])
        video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})

        duration = float(fmt.get("duration") or video_stream.get("duration") or 0.0)
        # Average frame rate is "30000/1001" style — evaluate safely.
        avg_fps = 0.0
        fr_str = video_stream.get("avg_frame_rate", "0/1")
        try:
            num, _, den = fr_str.partition("/")
            avg_fps = float(num) / max(float(den or 1), 1e-9)
        except (ValueError, ZeroDivisionError):
            avg_fps = 0.0

        return VideoStats(
            duration_seconds=duration,
            fps=avg_fps,
            width=int(video_stream.get("width") or 0),
            height=int(video_stream.get("height") or 0),
            codec=video_stream.get("codec_name", ""),
            bitrate=int(fmt.get("bit_rate") or 0) or None,
            has_audio=bool(audio_stream),
            audio_sample_rate=int(audio_stream.get("sample_rate") or 0) or None,
            audio_channels=int(audio_stream.get("channels") or 0) or None,
        )
