"""Camera motion + zoom estimation via sparse optical flow (Lucas-Kanade).

For each sampled frame pair we compute:
  - mean flow vector (→ pan / tilt)
  - flow divergence (→ zoom in/out)
  - flow variance (→ handheld shake)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from zorkvdo_schemas import CameraMotion


@dataclass
class MotionFrame:
    time: float
    motion: CameraMotion
    pan_x: float
    pan_y: float
    zoom: float
    shake: float


@dataclass
class MotionSignals:
    frames: list[MotionFrame]
    dominant_motion: CameraMotion
    avg_zoom: float
    avg_shake: float


class MotionAnalyzer:
    def __init__(self, sample_fps: float = 2.0) -> None:
        self.sample_fps = float(sample_fps)

    def analyze(self, video_path: str | Path) -> MotionSignals:
        path = str(video_path)
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise RuntimeError(f"cannot open video: {path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(1, int(round(fps / self.sample_fps)))

        prev_gray: np.ndarray | None = None
        prev_pts: np.ndarray | None = None
        frames: list[MotionFrame] = []
        idx = 0

        # Lukas-Kanade params
        lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
        )
        feature_params = dict(
            maxCorners=200, qualityLevel=0.3, minDistance=7, blockSize=7
        )

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % step == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if prev_gray is not None and prev_pts is not None and len(prev_pts) >= 8:
                    next_pts, status, _ = cv2.calcOpticalFlowPyrLK(
                        prev_gray, gray, prev_pts, None, **lk_params
                    )
                    if next_pts is not None and status is not None:
                        good_old = prev_pts[status.flatten() == 1]
                        good_new = next_pts[status.flatten() == 1]
                        if len(good_old) >= 8 and good_new.ndim == 2 and good_new.shape[1] >= 2:
                            dx = float(np.mean(good_new[:, 0] - good_old[:, 0]))
                            dy = float(np.mean(good_new[:, 1] - good_old[:, 1]))
                            # Zoom: radial divergence from frame centre
                            h, w = gray.shape
                            cx, cy = w / 2.0, h / 2.0
                            radial_old = good_old - np.array([cx, cy])
                            radial_new = good_new - np.array([cx, cy])
                            r_old = np.linalg.norm(radial_old, axis=1) + 1e-6
                            r_new = np.linalg.norm(radial_new, axis=1)
                            zoom = float(np.mean((r_new - r_old) / r_old))
                            shake = float(np.std(good_new - good_old))
                            frames.append(
                                MotionFrame(
                                    time=idx / fps,
                                    motion=self._classify(dx, dy, zoom, shake),
                                    pan_x=dx,
                                    pan_y=dy,
                                    zoom=zoom,
                                    shake=shake,
                                )
                            )
                prev_gray = gray
                prev_pts = cv2.goodFeaturesToTrack(gray, mask=None, **feature_params)
            idx += 1

        cap.release()

        if not frames:
            return MotionSignals(
                frames=[],
                dominant_motion=CameraMotion.STATIC,
                avg_zoom=0.0,
                avg_shake=0.0,
            )

        # Dominant motion = mode across frames
        motions = [f.motion for f in frames]
        dominant = max(set(motions), key=motions.count)
        return MotionSignals(
            frames=frames,
            dominant_motion=dominant,
            avg_zoom=float(np.mean([f.zoom for f in frames])),
            avg_shake=float(np.mean([f.shake for f in frames])),
        )

    @staticmethod
    def _classify(dx: float, dy: float, zoom: float, shake: float) -> CameraMotion:
        if shake > 4.0:
            return CameraMotion.HANDHELD
        if abs(zoom) > 0.02:
            return CameraMotion.ZOOM_IN if zoom > 0 else CameraMotion.ZOOM_OUT
        if abs(dx) > abs(dy) and abs(dx) > 1.5:
            return CameraMotion.PAN_LEFT if dx < 0 else CameraMotion.PAN_RIGHT
        if abs(dy) > 1.5:
            return CameraMotion.TILT_UP if dy < 0 else CameraMotion.TILT_DOWN
        return CameraMotion.STATIC

    def to_dict(self, signals: MotionSignals) -> dict[str, Any]:
        return {
            "dominant_motion": signals.dominant_motion.value,
            "avg_zoom": signals.avg_zoom,
            "avg_shake": signals.avg_shake,
            "frames": [
                {
                    "time": f.time,
                    "motion": f.motion.value,
                    "pan_x": f.pan_x,
                    "pan_y": f.pan_y,
                    "zoom": f.zoom,
                    "shake": f.shake,
                }
                for f in signals.frames
            ],
        }
