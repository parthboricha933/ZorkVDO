"""Caption detection via OCR.

Sample frames at `sample_fps`, run OCR (easyocr), and group overlapping
detections across consecutive frames into discrete caption blocks with
start/end timestamps.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from zorkvdo_schemas import CaptionAnimation, CaptionPosition


@dataclass
class CaptionBlock:
    text: str
    start: float
    end: float
    position: CaptionPosition
    box: tuple[int, int, int, int]  # x, y, w, h
    font_size_hint: float
    color_hex: str


@dataclass
class CaptionSignals:
    blocks: list[CaptionBlock]
    default_font: str = "Inter"
    default_animation: CaptionAnimation = CaptionAnimation.POP


class CaptionDetector:
    """Lazily initialises easyocr on first use (heavy import)."""

    def __init__(
        self,
        *,
        languages: list[str] | None = None,
        sample_fps: float = 1.0,
    ) -> None:
        self.languages = languages or ["en"]
        self.sample_fps = float(sample_fps)
        self._reader: Any | None = None

    def _get_reader(self) -> Any:
        if self._reader is None:
            try:
                import easyocr
            except ImportError as e:
                raise RuntimeError(
                    "easyocr is not installed. Install with: pip install easyocr"
                ) from e
            self._reader = easyocr.Reader(self.languages, gpu=False, verbose=False)
        return self._reader

    def analyze(self, video_path: str | Path) -> CaptionSignals:
        path = str(video_path)
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise RuntimeError(f"cannot open video: {path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        step = max(1, int(round(fps / self.sample_fps)))

        reader = self._get_reader()
        raw: list[dict[str, Any]] = []  # {time, text, box, font_size, color}
        idx = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if idx % step == 0:
                t = idx / fps
                # Focus on the bottom 40% of the frame (typical caption area)
                h, w = frame.shape[:2]
                crop = frame[int(h * 0.55):, :]
                try:
                    results = reader.readtext(crop)
                except Exception:
                    results = []
                for (box, text, conf) in results:
                    if conf < 0.4 or not text.strip():
                        continue
                    box_pts = np.array(box, dtype=int)
                    x = int(box_pts[:, 0].min())
                    y = int(box_pts[:, 1].min()) + int(h * 0.55)
                    bw = int(box_pts[:, 0].max() - x)
                    bh = int(box_pts[:, 1].max() - box_pts[:, 1].min())
                    color = self._avg_color(frame, (x, y, bw, bh))
                    raw.append({
                        "time": t,
                        "text": text.strip(),
                        "box": (x, y, bw, bh),
                        "font_size": float(bh),
                        "color": color,
                    })
            idx += 1
        cap.release()

        blocks = self._group_blocks(raw)
        return CaptionSignals(blocks=blocks)

    @staticmethod
    def _avg_color(frame: np.ndarray, box: tuple[int, int, int, int]) -> str:
        x, y, w, h = box
        if w <= 0 or h <= 0:
            return "#FFFFFF"
        crop = frame[max(0, y):y + h, max(0, x):x + w]
        if crop.size == 0:
            return "#FFFFFF"
        avg = cv2.mean(crop)[:3]
        return "#{:02X}{:02X}{:02X}".format(
            int(avg[0]), int(avg[1]), int(avg[2])
        )

    def _group_blocks(self, raw: list[dict[str, Any]]) -> list[CaptionBlock]:
        """Merge consecutive OCR hits with similar text + position."""
        if not raw:
            return []
        raw.sort(key=lambda r: r["time"])
        blocks: list[CaptionBlock] = []
        current: dict[str, Any] | None = None

        def _similar(a: dict, b: dict) -> bool:
            if abs(a["time"] - b["time"]) > 1.5:
                return False
            # Normalise whitespace + case for text comparison
            ta = "".join(c for c in a["text"] if c.isalnum()).lower()
            tb = "".join(c for c in b["text"] if c.isalnum()).lower()
            if not ta or not tb:
                return False
            # Levenshtein-ish: at least 60% char overlap
            common = sum(1 for c in ta if c in tb)
            return common / max(len(ta), len(tb)) >= 0.6

        for r in raw:
            if current and _similar(current, r):
                current["end"] = r["time"]
                # Prefer the longer text
                if len(r["text"]) > len(current["text"]):
                    current["text"] = r["text"]
                    current["box"] = r["box"]
                    current["font_size"] = r["font_size"]
                    current["color"] = r["color"]
            else:
                if current:
                    blocks.append(self._finalize(current))
                current = {**r, "end": r["time"] + 0.5}
        if current:
            blocks.append(self._finalize(current))

        return blocks

    def _finalize(self, r: dict[str, Any]) -> CaptionBlock:
        x, y, w, h = r["box"]
        # Position from y coordinate
        # (we cropped bottom 40%, so any y > 0 in our offset means bottom)
        position = CaptionPosition.BOTTOM_THIRD
        return CaptionBlock(
            text=r["text"],
            start=float(r["time"]),
            end=float(r["end"]),
            position=position,
            box=(x, y, w, h),
            font_size_hint=r["font_size"],
            color_hex=r["color"],
        )

    def to_dict(self, signals: CaptionSignals) -> dict[str, Any]:
        return {
            "blocks": [
                {
                    "text": b.text,
                    "start": b.start,
                    "end": b.end,
                    "position": b.position.value,
                    "box": list(b.box),
                    "font_size_hint": b.font_size_hint,
                    "color_hex": b.color_hex,
                }
                for b in signals.blocks
            ],
            "default_font": signals.default_font,
            "default_animation": signals.default_animation.value,
        }
