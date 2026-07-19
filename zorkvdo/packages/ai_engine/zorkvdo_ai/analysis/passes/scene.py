"""Scene-cut detection + transition type detection via OpenCV.

Detects:
  - Scene boundaries (HSV histogram difference)
  - Flash/lightning transitions (sudden brightness spike)
  - Whip pan transitions (rapid horizontal motion at boundary)
  - Crossfade transitions (gradual blend)
  - Cut transitions (sharp boundary, no flash)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np


@dataclass
class TransitionEvent:
    """A transition detected at a scene boundary."""
    timestamp: float
    transition_type: str  # cut | flash | whip_pan | crossfade
    intensity: float  # 0.0 - 1.0


@dataclass
class SceneSignals:
    boundaries: list[float]
    shot_durations: list[float]
    avg_shot_duration: float
    transitions: list[TransitionEvent] = field(default_factory=list)
    flash_count: int = 0


class SceneDetector:
    def __init__(self, *, threshold: float = 27.0, sample_fps: float = 2.0) -> None:
        self.threshold = float(threshold)
        self.sample_fps = float(sample_fps)

    def analyze(self, video_path: str | Path, *, duration_seconds: float) -> SceneSignals:
        path = str(video_path)
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise RuntimeError(f"cannot open video: {path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(1, int(round(fps / self.sample_fps)))

        boundaries: list[float] = [0.0]
        prev_hist: np.ndarray | None = None
        prev_brightness: float | None = None
        prev_gray: np.ndarray | None = None
        frame_idx = 0
        transitions: list[TransitionEvent] = []
        flash_count = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_idx % step == 0:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = float(np.mean(gray))

                if prev_hist is not None:
                    diff = float(cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)) * 100
                    if diff > self.threshold:
                        t = frame_idx / fps
                        if t - boundaries[-1] > 0.3:
                            boundaries.append(t)

                            # Detect transition type
                            transition_type = "cut"
                            intensity = diff / 100.0

                            # Flash/lightning detection: sudden brightness spike
                            if prev_brightness is not None:
                                brightness_ratio = brightness / max(prev_brightness, 0.01)
                                if brightness_ratio > 1.8 or brightness > 220:
                                    transition_type = "flash"
                                    intensity = min(1.0, (brightness_ratio - 1.0) / 2.0)
                                    flash_count += 1
                                # Whip pan detection: high horizontal motion at boundary
                                elif prev_gray is not None:
                                    # Use phase correlation for shift detection
                                    try:
                                        (shift_x, shift_y), _ = cv2.phaseCorrelate(
                                            np.float64(prev_gray), np.float64(gray)
                                        )
                                        if abs(shift_x) > 15 or abs(shift_y) > 15:
                                            transition_type = "whip_pan"
                                            intensity = min(1.0, abs(shift_x) / 50.0)
                                    except Exception:
                                        pass

                                # Crossfade detection: moderate diff + brightness is smooth
                                if transition_type == "cut" and diff < 40 and prev_brightness is not None:
                                    if abs(brightness - prev_brightness) < 20:
                                        transition_type = "crossfade"
                                        intensity = diff / 60.0

                            transitions.append(TransitionEvent(
                                timestamp=t,
                                transition_type=transition_type,
                                intensity=intensity,
                            ))

                prev_hist = hist
                prev_brightness = brightness
                prev_gray = gray
            frame_idx += 1

        cap.release()

        boundaries.append(duration_seconds)
        shot_durations = [
            boundaries[i + 1] - boundaries[i]
            for i in range(len(boundaries) - 1)
        ]
        avg = float(np.mean(shot_durations)) if shot_durations else 0.0
        return SceneSignals(
            boundaries=boundaries[:-1],
            shot_durations=shot_durations,
            avg_shot_duration=avg,
            transitions=transitions,
            flash_count=flash_count,
        )

    def to_dict(self, signals: SceneSignals) -> dict[str, Any]:
        return {
            "boundaries": signals.boundaries,
            "shot_durations": signals.shot_durations,
            "avg_shot_duration": signals.avg_shot_duration,
            "flash_count": signals.flash_count,
            "transitions": [
                {"timestamp": t.timestamp, "type": t.transition_type, "intensity": t.intensity}
                for t in signals.transitions
            ],
        }
