"""Scene-cut detection via OpenCV histogram difference.

A new scene boundary is recorded when the mean HSV-histogram difference
between consecutive sampled frames exceeds `threshold`. Output is a list
of (start_time, end_time) tuples covering the whole video.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


@dataclass
class SceneSignals:
    boundaries: list[float]   # timestamps (s) at which a new scene begins
    shot_durations: list[float]
    avg_shot_duration: float


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
        frame_idx = 0
        last_boundary_frame = 0

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_idx % step == 0:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                if prev_hist is not None:
                    diff = float(cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)) * 100
                    if diff > self.threshold:
                        t = frame_idx / fps
                        # Merge very-close boundaries (<0.3s apart)
                        if t - boundaries[-1] > 0.3:
                            boundaries.append(t)
                            last_boundary_frame = frame_idx
                prev_hist = hist
            frame_idx += 1

        cap.release()

        # Build shot durations from boundaries
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
        )

    def to_dict(self, signals: SceneSignals) -> dict[str, Any]:
        return {
            "boundaries": signals.boundaries,
            "shot_durations": signals.shot_durations,
            "avg_shot_duration": signals.avg_shot_duration,
        }
