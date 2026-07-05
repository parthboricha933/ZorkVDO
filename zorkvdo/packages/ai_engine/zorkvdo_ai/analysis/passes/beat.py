"""Beat detection via librosa.

Extracts BPM + onset frames (beat times in seconds). If the video has
no audio track or librosa can't decode it, returns an empty result
rather than raising — beats are optional metadata for the blueprint.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class BeatSignals:
    bpm: float | None
    beat_times: list[float]
    onset_times: list[float]
    energy: float


class BeatDetector:
    def __init__(self, *, extract_audio_bin: str = "ffmpeg") -> None:
        self._ffmpeg = extract_audio_bin

    def analyze(self, video_path: str | Path) -> BeatSignals:
        import asyncio
        import os
        import tempfile

        path = str(video_path)
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        # Extract audio to a temp WAV (mono, 22050 Hz — librosa default)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_path = tmp.name

        try:
            proc = asyncio.run(self._extract_audio(path, audio_path))
            if proc != 0:
                return BeatSignals(bpm=None, beat_times=[], onset_times=[], energy=0.0)

            return self._analyze_audio(audio_path)
        finally:
            try:
                os.unlink(audio_path)
            except OSError:
                pass

    async def _extract_audio(self, video_path: str, audio_path: str) -> int:
        proc = await asyncio.create_subprocess_exec(
            self._ffmpeg,
            "-y", "-i", video_path,
            "-vn", "-ac", "1", "-ar", "22050",
            "-f", "wav", audio_path,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        return proc.returncode or 0

    def _analyze_audio(self, audio_path: str) -> BeatSignals:
        import librosa
        import numpy as np

        try:
            y, sr = librosa.load(audio_path, sr=22050, mono=True)
        except Exception:
            return BeatSignals(bpm=None, beat_times=[], onset_times=[], energy=0.0)

        if len(y) == 0 or float(np.max(np.abs(y))) < 1e-4:
            return BeatSignals(bpm=None, beat_times=[], onset_times=[], energy=0.0)

        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beats, sr=sr).tolist()
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
        onset_times = librosa.frames_to_time(onset_frames, sr=sr).tolist()
        energy = float(np.sqrt(np.mean(y**2)))

        bpm = float(tempo) if np.isscalar(tempo) else float(tempo[0])
        return BeatSignals(
            bpm=bpm,
            beat_times=[float(t) for t in beat_times],
            onset_times=[float(t) for t in onset_times],
            energy=energy,
        )

    def to_dict(self, signals: BeatSignals) -> dict[str, Any]:
        return {
            "bpm": signals.bpm,
            "beat_times": signals.beat_times,
            "onset_times": signals.onset_times,
            "energy": signals.energy,
        }
