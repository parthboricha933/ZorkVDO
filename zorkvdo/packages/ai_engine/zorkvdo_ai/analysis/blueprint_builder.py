"""BlueprintBuilder — assembles a reusable Blueprint from raw analysis signals.

The builder is *pure*: given the typed signal objects, it always returns
the same Blueprint. This makes it trivially testable without any video
file or AI provider.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from zorkvdo_schemas import (
    Blueprint,
    BlueprintMeta,
    CameraMotion,
    CaptionAnimation,
    CaptionStyle,
    ClipSuggestion,
    ColorGrade,
    Effect,
    EffectType,
    MusicTrack,
    Pace,
    Scene,
    ShotType,
    Transition,
    TransitionType,
    VideoStats,
)

from .passes.beat import BeatSignals
from .passes.caption import CaptionSignals
from .passes.color import ColorSignals
from .passes.motion import MotionSignals
from .passes.object import ObjectSignals
from .passes.scene import SceneSignals


class BlueprintBuilder:
    """Maps raw CV/audio signals → typed Blueprint."""

    def build(
        self,
        *,
        blueprint_id: str,
        blueprint_name: str,
        video_id: str,
        stats: VideoStats,
        scene: SceneSignals,
        motion: MotionSignals,
        beat: BeatSignals,
        caption: CaptionSignals,
        color: ColorSignals,
        objects: ObjectSignals,
    ) -> Blueprint:
        # Compute overall pace from avg shot duration
        pace = self._pace_from_avg_shot(scene.avg_shot_duration)
        color_grade = self._color_grade(color, beat)
        transitions = self._transitions(scene, beat)

        # Build one Scene per detected shot
        scenes: list[Scene] = []
        boundaries = scene.boundaries or [0.0]
        # Build shot (start, end) pairs
        shots: list[tuple[float, float]] = []
        for i, start in enumerate(boundaries):
            end = boundaries[i + 1] if i + 1 < len(boundaries) else stats.duration_seconds
            shots.append((start, end))

        # Map motion frames onto each shot (use the frame closest to shot midpoint)
        for i, (start, end) in enumerate(shots):
            mid = (start + end) / 2.0
            motion_frame = self._motion_at(motion, mid)
            zoom_factor = 1.0 + max(-0.9, min(3.0, motion_frame.zoom * 5.0)) if motion_frame else 1.0
            cam_motion = motion_frame.motion if motion_frame else CameraMotion.STATIC

            shot_type = self._shot_type_for_scene(i, len(shots), objects)
            effects = self._effects_for_shot(i, shots, beat)
            captions = self._captions_for_shot(caption, start, end)

            # Beat sync for this scene
            beats_in_scene = [
                t for t in (beat.beat_times or []) if start <= t <= end
            ]
            bpm_sync = beat.bpm if beats_in_scene else None

            scenes.append(
                Scene(
                    index=i,
                    start=start,
                    end=end,
                    duration=end - start,
                    shot_type=shot_type,
                    camera_motion=cam_motion,
                    zoom_factor=zoom_factor,
                    effects=effects,
                    transition_in=transitions[min(i, len(transitions) - 1)] if transitions else Transition(),
                    captions=captions,
                    clip_suggestion=self._suggestion_for_shot(
                        i, len(shots), cam_motion, shot_type, end - start, objects
                    ),
                    dominant_colors_hex=color.dominant_hex[:3],
                    audio_peak_db=None,
                    bpm_sync=bpm_sync,
                )
            )

        # Music track from beat detection
        music = MusicTrack(
            title="",
            artist="",
            bpm=beat.bpm,
            key=None,
            energy=min(1.0, beat.energy * 2.0),
            beat_times=list(beat.beat_times or []),
            source_url=None,
            license=None,
        ) if beat.bpm is not None else None

        meta = BlueprintMeta(
            schema_version="1.0.0",
            generator="zorkvdo-analyzer",
            generated_at=datetime.now(timezone.utc),
            source_video_id=video_id,
            source_duration_seconds=stats.duration_seconds,
            fps=stats.fps,
            width=stats.width,
            height=stats.height,
        )

        tags = self._tags(scene, motion, beat, color, objects, pace)

        return Blueprint(
            id=blueprint_id,
            name=blueprint_name,
            meta=meta,
            pace=pace,
            overall_duration=stats.duration_seconds,
            scenes=scenes,
            music=music,
            color_grade=color_grade,
            tags=tags,
            notes="",
        )

    # ── helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _pace_from_avg_shot(avg: float) -> Pace:
        if avg <= 0:
            return Pace.MEDIUM
        if avg < 1.0:
            return Pace.HYPER
        if avg < 2.0:
            return Pace.FAST
        if avg < 4.0:
            return Pace.MEDIUM
        return Pace.SLOW

    @staticmethod
    def _motion_at(motion: MotionSignals, t: float):
        if not motion.frames:
            return None
        # Find the frame closest to t
        closest = min(motion.frames, key=lambda f: abs(f.time - t))
        return closest

    @staticmethod
    def _color_grade(color: ColorSignals, beat: BeatSignals) -> ColorGrade:
        if color.brightness < 0.25:
            return ColorGrade.NOIR
        if color.saturation > 0.65 and color.brightness > 0.55:
            return ColorGrade.NEON
        if color.saturation > 0.5:
            return ColorGrade.TEAL_ORANGE
        if color.brightness > 0.65:
            return ColorGrade.HIGH_CONTRAST
        return ColorGrade.NATURAL

    @staticmethod
    def _transitions(scene: SceneSignals, beat: BeatSignals) -> list[Transition]:
        """Default transition is CUT between scenes, with periodic flash on beats."""
        out: list[Transition] = []
        for i in range(max(1, len(scene.boundaries))):
            # Every 4th scene gets a flash on a beat boundary
            if i > 0 and i % 4 == 0 and beat.beat_times:
                out.append(Transition(type=TransitionType.FLASH, duration=0.15))
            else:
                out.append(Transition(type=TransitionType.CUT, duration=0.1))
        return out or [Transition()]

    @staticmethod
    def _shot_type_for_scene(index: int, total: int, objects: ObjectSignals) -> ShotType:
        # First scene = establishing/wide; last = CTA / close-up
        if total <= 1:
            return ShotType.MEDIUM
        if index == 0:
            return ShotType.WIDE
        if index == total - 1:
            return ShotType.CLOSE_UP
        # If many faces, talking-head style
        if objects.face_count >= 1:
            return ShotType.MEDIUM
        return ShotType.MEDIUM

    @staticmethod
    def _effects_for_shot(
        index: int,
        shots: list[tuple[float, float]],
        beat: BeatSignals,
    ) -> list[Effect]:
        effects: list[Effect] = []
        # Slow-motion on long shots (>3s)
        for start, end in [shots[index]]:
            if (end - start) > 3.0:
                effects.append(
                    Effect(type=EffectType.SLOW_MOTION, intensity=0.3, duration=0.0)
                )
        # Beat-synced zoom bump on first beat of scene
        if beat.beat_times:
            mid = (shots[index][0] + shots[index][1]) / 2.0
            closest_beat = min(beat.beat_times, key=lambda b: abs(b - mid))
            if abs(closest_beat - mid) < 0.3:
                effects.append(
                    Effect(type=EffectType.ZOOM_BUMP, intensity=0.6, duration=0.2)
                )
        return effects

    @staticmethod
    def _captions_for_shot(
        caption: CaptionSignals,
        shot_start: float,
        shot_end: float,
    ) -> list[CaptionStyle]:
        out: list[CaptionStyle] = []
        for b in caption.blocks:
            if b.end < shot_start or b.start > shot_end:
                continue
            cs = CaptionStyle(
                text=b.text,
                start=max(0.0, b.start - shot_start),
                end=min(shot_end - shot_start, b.end - shot_start),
                position=b.position,
                animation=CaptionAnimation.POP,
                font_family=caption.default_font,
                font_size=max(24.0, min(80.0, b.font_size_hint * 1.5)),
                color_hex=b.color_hex,
                stroke_color_hex="#000000",
                stroke_width=2.0,
                bold=True,
                uppercase=False,
            )
            out.append(cs)
        return out

    @staticmethod
    def _suggestion_for_shot(
        index: int,
        total: int,
        motion: CameraMotion,
        shot_type: ShotType,
        duration: float,
        objects: ObjectSignals,
    ) -> ClipSuggestion:
        # Role-based suggestion
        if total <= 1:
            role = "any"
        elif index == 0:
            role = "hook"
        elif index == total - 1:
            role = "cta"
        elif index == 1:
            role = "establishing"
        elif objects.face_count >= 1:
            role = "talking_head"
        else:
            role = "broll"

        keywords: list[str] = []
        if objects.face_count >= 1:
            keywords.append("person")
        for cls_name in list(objects.object_counts.keys())[:5]:
            keywords.append(cls_name)

        return ClipSuggestion(
            role=role,
            preferred_shot=shot_type,
            duration_range=(max(0.5, duration * 0.8), duration * 1.2),
            motion=motion,
            description=f"Fill this {duration:.1f}s slot with {role} footage.",
            keywords=keywords,
            min_face_count=1 if role in ("hook", "talking_head") else 0,
            allow_text_overlay=True,
        )

    @staticmethod
    def _tags(
        scene: SceneSignals,
        motion: MotionSignals,
        beat: BeatSignals,
        color: ColorSignals,
        objects: ObjectSignals,
        pace: Pace,
    ) -> list[str]:
        tags: list[str] = [f"pace:{pace.value}"]
        if motion.dominant_motion != CameraMotion.STATIC:
            tags.append(f"motion:{motion.dominant_motion.value}")
        if beat.bpm:
            if beat.bpm < 90:
                tags.append("mood:chill")
            elif beat.bpm < 130:
                tags.append("mood:energetic")
            else:
                tags.append("mood:hype")
        if color.dominant_hex:
            tags.append(f"color:{color.dominant_hex[0]}")
        if objects.face_count >= 1:
            tags.append("subject:person")
        # Add object keywords
        for cls_name in list(objects.object_counts.keys())[:3]:
            if cls_name != "face":
                tags.append(f"obj:{cls_name}")
        return tags
