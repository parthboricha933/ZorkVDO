"""Camera motion + zoom estimation via sparse optical flow (Lucas-Kanade).

For each sampled frame pair we compute:
  - mean flow vector (→ pan / tilt)
  - flow divergence (→ zoom in/out)
  - flow variance (→ handheld shake)
  - per-scene zoom direction (zoom_in / zoom_out)

Enhanced zoom detection:
  - Positive radial divergence > threshold → zoom_in
  - Negative radial divergence < -threshold → zoom_out
  - Per-scene zoom tracking for the blueprint
"""
from __future__ import annotations

from dataclasses import dataclass, field
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
    zoom_direction: str  # "in" | "out" | "none"
    zoom_speed: float  # 0.0 - 1.0


@dataclass
class MotionSignals:
    frames: list[MotionFrame]
    dominant_motion: CameraMotion
    avg_zoom: float
    avg_shake: float
    zoom_events: list[dict] = field(default_factory=list)
    # zoom_events: [{"time": float, "direction": "in"/"out", "speed": float, "duration": float}]


class MotionAnalyzer:
    ZOOM_THRESHOLD = 0.015  # radial divergence ratio to count as zoom

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
        zoom_events: list[dict] = []
        current_zoom: dict | None = None  # tracking ongoing zoom event

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
                            h, w = gray.shape
                            cx, cy = w / 2.0, h / 2.0
                            radial_old = good_old - np.array([cx, cy])
                            radial_new = good_new - np.array([cx, cy])
                            r_old = np.linalg.norm(radial_old, axis=1) + 1e-6
                            r_new = np.linalg.norm(radial_new, axis=1)
                            zoom = float(np.mean((r_new - r_old) / r_old))
                            shake = float(np.std(good_new - good_old))

                            # Determine zoom direction
                            zoom_dir = "none"
                            zoom_speed = 0.0
                            if abs(zoom) > self.ZOOM_THRESHOLD:
                                zoom_dir = "in" if zoom > 0 else "out"
                                zoom_speed = min(1.0, abs(zoom) * 20.0)

                            # Track zoom events (consecutive frames with same direction)
                            t = idx / fps
                            if zoom_dir != "none":
                                if current_zoom and current_zoom["direction"] == zoom_dir:
                                    # Extend current event
                                    current_zoom["end_time"] = t
                                    current_zoom["speed"] = max(current_zoom["speed"], zoom_speed)
                                else:
                                    # Close previous event if exists
                                    if current_zoom:
                                        current_zoom["duration"] = current_zoom["end_time"] - current_zoom["time"]
                                        zoom_events.append(current_zoom)
                                    # Start new event
                                    current_zoom = {
                                        "time": t,
                                        "end_time": t,
                                        "direction": zoom_dir,
                                        "speed": zoom_speed,
                                    }
                            else:
                                # No zoom — close current event if exists
                                if current_zoom:
                                    current_zoom["duration"] = current_zoom["end_time"] - current_zoom["time"]
                                    if current_zoom["duration"] > 0.2:  # min 0.2s
                                        zoom_events.append(current_zoom)
                                    current_zoom = None

                            frames.append(MotionFrame(
                                time=t,
                                motion=self._classify(dx, dy, zoom, shake),
                                pan_x=dx,
                                pan_y=dy,
                                zoom=zoom,
                                shake=shake,
                                zoom_direction=zoom_dir,
                                zoom_speed=zoom_speed,
                            ))
                prev_gray = gray
                prev_pts = cv2.goodFeaturesToTrack(gray, mask=None, **feature_params)
            idx += 1

        cap.release()

        # Close final zoom event
        if current_zoom:
            current_zoom["duration"] = current_zoom["end_time"] - current_zoom["time"]
            if current_zoom["duration"] > 0.2:
                zoom_events.append(current_zoom)

        if not frames:
            return MotionSignals(
                frames=[],
                dominant_motion=CameraMotion.STATIC,
                avg_zoom=0.0,
                avg_shake=0.0,
                zoom_events=[],
            )

        motions = [f.motion for f in frames]
        dominant = max(set(motions), key=motions.count)
        return MotionSignals(
            frames=frames,
            dominant_motion=dominant,
            avg_zoom=float(np.mean([f.zoom for f in frames])),
            avg_shake=float(np.mean([f.shake for f in frames])),
            zoom_events=zoom_events,
        )

    @staticmethod
    def _classify(dx: float, dy: float, zoom: float, shake: float) -> CameraMotion:
        if shake > 4.0:
            return CameraMotion.HANDHELD
        if abs(zoom) > 0.015:
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
            "zoom_events": signals.zoom_events,
            "frames": [
                {
                    "time": f.time,
                    "motion": f.motion.value,
                    "pan_x": f.pan_x,
                    "pan_y": f.pan_y,
                    "zoom": f.zoom,
                    "shake": f.shake,
                    "zoom_direction": f.zoom_direction,
                    "zoom_speed": f.zoom_speed,
                }
                for f in signals.frames
            ],
        }
