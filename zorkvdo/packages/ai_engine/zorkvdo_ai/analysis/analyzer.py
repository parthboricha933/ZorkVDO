"""VideoAnalyzer — orchestrates all CV/audio passes into a single AnalysisResult.

This is the public entry point the Celery worker calls. It:
  1. Probes the video for container-level stats.
  2. Runs all analysis passes (scene, motion, beat, caption, color, object).
  3. Passes raw signals to `BlueprintBuilder` to produce the reusable Blueprint.
  4. Returns an `AnalysisResult` containing everything (raw signals + blueprint).
"""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from zorkvdo_schemas import AnalysisResult

from .blueprint_builder import BlueprintBuilder
from .passes import (
    BeatDetector,
    CaptionDetector,
    ColorAnalyzer,
    MotionAnalyzer,
    ObjectDetector,
    SceneDetector,
    VideoProber,
)

log = get_logger(__name__)


@dataclass
class AnalyzerConfig:
    scene_threshold: float = 27.0
    sample_fps: float = 2.0
    ocr_languages: list[str] | None = None
    yolo_model: str = "yolov8n.pt"
    enable_face: bool = True
    enable_pose: bool = True
    max_video_seconds: int = 600


class VideoAnalyzer:
    def __init__(
        self,
        *,
        config: AnalyzerConfig | None = None,
        prober: VideoProber | None = None,
        scene: SceneDetector | None = None,
        motion: MotionAnalyzer | None = None,
        beat: BeatDetector | None = None,
        caption: CaptionDetector | None = None,
        color: ColorAnalyzer | None = None,
        objects: ObjectDetector | None = None,
        builder: BlueprintBuilder | None = None,
    ) -> None:
        cfg = config or AnalyzerConfig()
        self.cfg = cfg
        self.prober = prober or VideoProber()
        self.scene = scene or SceneDetector(
            threshold=cfg.scene_threshold, sample_fps=cfg.sample_fps
        )
        self.motion = motion or MotionAnalyzer(sample_fps=cfg.sample_fps)
        self.beat = beat or BeatDetector()
        self.caption = caption or CaptionDetector(
            languages=cfg.ocr_languages or ["en"], sample_fps=1.0
        )
        self.color = color or ColorAnalyzer(sample_fps=1.0)
        self.objects = objects or ObjectDetector(
            yolo_model=cfg.yolo_model,
            enable_face=cfg.enable_face,
            enable_pose=cfg.enable_pose,
            sample_fps=1.0,
        )
        self.builder = builder or BlueprintBuilder()

    async def analyze(
        self,
        video_path: str | Path,
        *,
        video_id: str | None = None,
        blueprint_id: str | None = None,
        blueprint_name: str = "Untitled Blueprint",
    ) -> AnalysisResult:
        """Run the full pipeline. CPU-bound passes run in a thread pool."""
        path = str(video_path)
        if not Path(path).exists():
            raise FileNotFoundError(path)

        vid = video_id or uuid.uuid4().hex
        bid = blueprint_id or uuid.uuid4().hex
        log.info("analysis_start", video_id=vid, path=path)

        started = time.perf_counter()

        # 1. Probe (fast, async subprocess)
        probe = await self.prober.probe(path)
        if probe.stats.duration_seconds > self.cfg.max_video_seconds:
            raise ValueError(
                f"video too long: {probe.stats.duration_seconds:.1f}s > "
                f"max {self.cfg.max_video_seconds}s"
            )

        # 2. Run CV/audio passes in a thread pool (they're synchronous, CPU-bound)
        loop = asyncio.get_running_loop()
        scene_signals, motion_signals, beat_signals, color_signals, object_signals = (
            await asyncio.gather(
                loop.run_in_executor(None, self.scene.analyze, path, probe.stats.duration_seconds),
                loop.run_in_executor(None, self.motion.analyze, path),
                loop.run_in_executor(None, self.beat.analyze, path),
                loop.run_in_executor(None, self.color.analyze, path),
                loop.run_in_executor(None, self.objects.analyze, path),
            )
        )

        # Caption OCR is the slowest pass — run it last so its failure doesn't
        # block the other signals. Wrap in try/except so a missing easyocr
        # install doesn't kill the whole pipeline.
        try:
            caption_signals = await loop.run_in_executor(None, self.caption.analyze, path)
        except Exception as e:
            log.warning("caption_analysis_failed", error=str(e))
            from .passes.caption import CaptionSignals
            caption_signals = CaptionSignals(blocks=[])

        # 3. Build the blueprint from signals
        blueprint = self.builder.build(
            blueprint_id=bid,
            blueprint_name=blueprint_name,
            video_id=vid,
            stats=probe.stats,
            scene=scene_signals,
            motion=motion_signals,
            beat=beat_signals,
            caption=caption_signals,
            color=color_signals,
            objects=object_signals,
        )

        elapsed = time.perf_counter() - started
        log.info(
            "analysis_done",
            video_id=vid,
            elapsed=elapsed,
            scenes=len(blueprint.scenes),
            bpm=blueprint.music.bpm if blueprint.music else None,
        )

        return AnalysisResult(
            video_id=vid,
            stats=probe.stats,
            scene_count=len(blueprint.scenes),
            detected_objects=object_signals.object_counts,
            detected_faces=object_signals.face_count,
            detected_pose=object_signals.pose_detected,
            dominant_colors_hex=color_signals.dominant_hex,
            detected_bpm=beat_signals.bpm,
            caption_count=len(caption_signals.blocks),
            raw_signals={
                "probe": {"duration": probe.stats.duration_seconds, "fps": probe.stats.fps},
                "scene": self.scene.to_dict(scene_signals),
                "motion": self.motion.to_dict(motion_signals),
                "beat": self.beat.to_dict(beat_signals),
                "caption": self.caption.to_dict(caption_signals),
                "color": self.color.to_dict(color_signals),
                "objects": self.objects.to_dict(object_signals),
            },
            blueprint=blueprint,
        )
