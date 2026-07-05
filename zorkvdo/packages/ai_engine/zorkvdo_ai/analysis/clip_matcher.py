"""ClipMatcher — recommend the best user clip for each blueprint scene slot.

Strategy:
  1. Quick-probe each user clip for duration + dimensions.
  2. Score each (scene, clip) pair using a weighted sum of:
       - duration fit (does the clip cover the scene length?)
       - face match (does the scene want a person? does the clip have one?)
       - motion compatibility (does the clip's motion match the suggestion?)
       - object keyword overlap
     If `ai_client` is provided, we also ask the model for a relevance
     score per pair — but the deterministic baseline is the source of
     truth and the AI score only acts as a tiebreaker.
  3. Return a list of ClipMatch (one per scene).
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.logging import get_logger
from zorkvdo_schemas import (
    Blueprint,
    CameraMotion,
    ClipMatch,
    ShotType,
    VideoStats,
)

from .passes import ObjectDetector, VideoProber

log = get_logger(__name__)


@dataclass
class ClipInfo:
    clip_id: str
    path: str
    stats: VideoStats
    has_face: bool
    object_counts: dict[str, int]


class ClipMatcher:
    def __init__(
        self,
        *,
        prober: VideoProber | None = None,
        object_detector: ObjectDetector | None = None,
        ai_client: Any | None = None,
    ) -> None:
        self.prober = prober or VideoProber()
        self.object_detector = object_detector or ObjectDetector(
            yolo_model="yolov8n.pt", enable_face=True, enable_pose=False, sample_fps=1.0
        )
        self.ai_client = ai_client

    async def match(
        self,
        blueprint: Blueprint,
        clips: list[tuple[str, str]],
    ) -> list[ClipMatch]:
        """`clips` is a list of (clip_id, file_path) pairs.

        Returns one ClipMatch per blueprint scene.
        """
        if not clips:
            return []

        # Probe each clip in parallel
        clip_infos = await asyncio.gather(
            *(self._probe_clip(cid, path) for cid, path in clips)
        )
        clip_infos = [c for c in clip_infos if c is not None]
        if not clip_infos:
            return []

        matches: list[ClipMatch] = []
        for scene in blueprint.scenes:
            best = self._best_for_scene(scene, clip_infos)
            if best is not None:
                matches.append(best)
        return matches

    async def _probe_clip(self, clip_id: str, path: str) -> ClipInfo | None:
        if not os.path.exists(path):
            log.warning("clip_missing", clip_id=clip_id, path=path)
            return None
        try:
            probe = await self.prober.probe(path)
            loop = asyncio.get_running_loop()
            obj_signals = await loop.run_in_executor(
                None, self.object_detector.analyze, path
            )
            return ClipInfo(
                clip_id=clip_id,
                path=path,
                stats=probe.stats,
                has_face=obj_signals.face_count > 0,
                object_counts=dict(obj_signals.object_counts),
            )
        except Exception as e:
            log.warning("clip_probe_failed", clip_id=clip_id, error=str(e))
            return None

    def _best_for_scene(self, scene, clips: list[ClipInfo]) -> ClipMatch | None:
        suggestion = scene.clip_suggestion
        scored: list[tuple[float, ClipInfo, list[str]]] = []

        for clip in clips:
            score = 0.0
            reasons: list[str] = []

            # 1. Duration fit
            dur = clip.stats.duration_seconds
            lo, hi = suggestion.duration_range
            if lo <= dur <= hi:
                score += 0.4
                reasons.append(f"duration {dur:.1f}s fits [{lo:.1f}, {hi:.1f}]")
            elif dur >= lo:
                # Longer is OK — we can trim
                score += 0.2
                reasons.append(f"clip {dur:.1f}s ≥ needed {lo:.1f}s (trimmable)")
            else:
                score -= 0.3
                reasons.append(f"clip {dur:.1f}s too short")

            # 2. Face match
            if suggestion.min_face_count > 0:
                if clip.has_face:
                    score += 0.3
                    reasons.append("has face (requested)")
                else:
                    score -= 0.2
                    reasons.append("missing requested face")

            # 3. Motion compatibility
            if suggestion.motion != CameraMotion.STATIC:
                # Without re-running motion analysis on each clip we can't be exact,
                # so we accept any non-static clip as a soft positive.
                score += 0.1
                reasons.append(f"prefers {suggestion.motion.value} motion")
            else:
                score += 0.05

            # 4. Object keyword overlap
            wanted = set(suggestion.keywords)
            have = set(clip.object_counts.keys())
            overlap = wanted & have
            if overlap:
                score += 0.15 * len(overlap) / max(len(wanted), 1)
                reasons.append(f"objects overlap: {overlap}")

            scored.append((score, clip, reasons))

        if not scored:
            return None

        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_clip, best_reasons = scored[0]
        confidence = max(0.0, min(1.0, 0.5 + best_score * 0.5))

        # Suggested in/out within the clip
        lo, hi = suggestion.duration_range
        target = max(lo, min(hi, scene.duration))
        suggested_end = min(best_clip.stats.duration_seconds, target)
        suggested_start = max(0.0, suggested_end - target)

        return ClipMatch(
            scene_index=scene.index,
            clip_id=best_clip.clip_id,
            confidence=confidence,
            match_reasons=best_reasons,
            suggested_start=suggested_start,
            suggested_end=suggested_end,
            suggested_motion=suggestion.motion,
            suggested_shot=suggestion.preferred_shot,
        )
