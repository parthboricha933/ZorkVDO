"""Individual CV/audio analysis passes.

Each pass is a small, focused class that takes a video path and returns
a typed signal dict. Passes are independent and can run in parallel.

Heavy dependencies (ultralytics, mediapipe) are imported lazily so the
backend boots without them installed — they raise a helpful error only
when the corresponding pass is actually invoked.
"""
from .prober import VideoProber
from .scene import SceneDetector
from .motion import MotionAnalyzer
from .beat import BeatDetector
from .caption import CaptionDetector
from .color import ColorAnalyzer
from .object import ObjectDetector

__all__ = [
    "VideoProber",
    "SceneDetector",
    "MotionAnalyzer",
    "BeatDetector",
    "CaptionDetector",
    "ColorAnalyzer",
    "ObjectDetector",
]
