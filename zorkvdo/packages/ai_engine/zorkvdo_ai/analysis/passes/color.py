"""Dominant-color analysis via k-means clustering.

Samples frames at `sample_fps`, clusters all sampled pixels in RGB space
with k-means (k=5), and returns the cluster centroids as hex colors
sorted by prevalence.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


@dataclass
class ColorSignals:
    dominant_hex: list[str]
    palette_hex: list[str]
    brightness: float
    saturation: float


class ColorAnalyzer:
    def __init__(self, *, sample_fps: float = 1.0, k: int = 5) -> None:
        self.sample_fps = float(sample_fps)
        self.k = int(k)

    def analyze(self, video_path: str | Path) -> ColorSignals:
        path = str(video_path)
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise RuntimeError(f"cannot open video: {path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(1, int(round(fps / self.sample_fps)))

        pixels: list[np.ndarray] = []
        brightness_vals: list[float] = []
        saturation_vals: list[float] = []
        idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % step == 0:
                # Downsample for speed
                small = cv2.resize(frame, (160, 90))
                hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
                brightness_vals.append(float(np.mean(hsv[..., 2]) / 255.0))
                saturation_vals.append(float(np.mean(hsv[..., 1]) / 255.0))
                rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB).reshape(-1, 3)
                pixels.append(rgb)
            idx += 1
        cap.release()

        if not pixels:
            return ColorSignals(dominant_hex=[], palette_hex=[], brightness=0.0, saturation=0.0)

        all_pixels = np.vstack(pixels).astype(np.float32)
        # k-means
        n_init = 3
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(
            all_pixels, self.k, None, criteria, n_init, cv2.KMEANS_PP_CENTERS
        )
        # Count labels for prevalence
        counts = np.bincount(labels.flatten())
        order = np.argsort(-counts)
        centers = centers[order]
        counts = counts[order]
        palette = ["#%02X%02X%02X" % tuple(int(c) for c in center) for center in centers]
        return ColorSignals(
            dominant_hex=palette[:3],
            palette_hex=palette,
            brightness=float(np.mean(brightness_vals)),
            saturation=float(np.mean(saturation_vals)),
        )

    def to_dict(self, signals: ColorSignals) -> dict[str, Any]:
        return {
            "dominant_hex": signals.dominant_hex,
            "palette_hex": signals.palette_hex,
            "brightness": signals.brightness,
            "saturation": signals.saturation,
        }
