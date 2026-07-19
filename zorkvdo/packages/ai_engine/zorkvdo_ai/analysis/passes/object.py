"""Object + face + pose detection.

Default path uses YOLO (via `ultralytics`). If `ultralytics` is not
installed, falls back to a Haar-cascade-based face detector shipped with
OpenCV — so the analysis pipeline always produces *something* useful
even in a minimal install.

MediaPipe pose is optional; it's only loaded when
`ANALYSIS_ENABLE_POSE=true` AND the package is importable.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np


@dataclass
class ObjectSignals:
    object_counts: dict[str, int] = field(default_factory=dict)
    face_count: int = 0
    pose_detected: bool = False
    frames_with_objects: int = 0


class ObjectDetector:
    def __init__(
        self,
        *,
        yolo_model: str = "yolo11n.pt",
        enable_face: bool = True,
        enable_pose: bool = True,
        sample_fps: float = 1.0,
    ) -> None:
        self.yolo_model = yolo_model
        self.enable_face = enable_face
        self.enable_pose = enable_pose
        self.sample_fps = float(sample_fps)
        self._yolo: Any | None = None
        self._face_cascade: Any | None = None
        self._pose: Any | None = None

    def _get_yolo(self) -> Any | None:
        if self._yolo is None:
            try:
                from ultralytics import YOLO
                self._yolo = YOLO(self.yolo_model)
            except Exception:
                # YOLO not available — fall back to OpenCV Haar only
                self._yolo = False
        return self._yolo if self._yolo is not False else None

    def _get_face_cascade(self) -> Any:
        if self._face_cascade is None:
            try:
                # cv2.data haarcascades ship with opencv-python (not -headless)
                cascade_path = os.path.join(
                    cv2.data.haarcascades, "haarcascade_frontalface_default.xml"
                )
                self._face_cascade = cv2.CascadeClassifier(cascade_path)
            except (AttributeError, Exception):
                # CascadeClassifier not available in opencv-python-headless
                # Fall back to None — face detection will be skipped
                self._face_cascade = False
        return self._face_cascade if self._face_cascade is not False else None

    def _get_pose(self) -> Any | None:
        if not self.enable_pose:
            return None
        if self._pose is None:
            try:
                import mediapipe as mp
                self._pose = mp.solutions.pose.Pose(
                    static_image_mode=False,
                    model_complexity=0,
                    enable_segmentation=False,
                    min_detection_confidence=0.5,
                )
            except Exception:
                self._pose = False
        return self._pose if self._pose is not False else None

    def analyze(self, video_path: str | Path) -> ObjectSignals:
        path = str(video_path)
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise RuntimeError(f"cannot open video: {path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(1, int(round(fps / self.sample_fps)))

        object_counts: dict[str, int] = {}
        max_faces = 0
        pose_detected = False
        frames_with_objects = 0
        idx = 0

        yolo = self._get_yolo()
        face_cascade = self._get_face_cascade() if self.enable_face else None
        pose = self._get_pose()

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % step == 0:
                frame_had_object = False
                if yolo is not None:
                    try:
                        results = yolo(frame, verbose=False)
                        for r in results:
                            for cls_id in (r.boxes.cls or []):
                                name = yolo.names.get(int(cls_id), f"cls{int(cls_id)}")
                                object_counts[name] = object_counts.get(name, 0) + 1
                                frame_had_object = True
                    except Exception:
                        pass
                if face_cascade is not None:
                    try:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(
                            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                        )
                        if len(faces) > max_faces:
                            max_faces = len(faces)
                        if len(faces) > 0:
                            frame_had_object = True
                            object_counts["face"] = object_counts.get("face", 0) + len(faces)
                    except Exception:
                        pass
                if pose is not None:
                    try:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        res = pose.process(rgb)
                        if res.pose_landmarks is not None:
                            pose_detected = True
                    except Exception:
                        pass
                if frame_had_object:
                    frames_with_objects += 1
            idx += 1

        cap.release()
        if pose is not None:
            try:
                pose.close()
            except Exception:
                pass

        return ObjectSignals(
            object_counts=object_counts,
            face_count=max_faces,
            pose_detected=pose_detected,
            frames_with_objects=frames_with_objects,
        )

    def to_dict(self, signals: ObjectSignals) -> dict[str, Any]:
        return {
            "object_counts": signals.object_counts,
            "face_count": signals.face_count,
            "pose_detected": signals.pose_detected,
            "frames_with_objects": signals.frames_with_objects,
        }
