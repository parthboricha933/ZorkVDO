"""Enumerations used throughout the Blueprint contract.

Kept as `str, Enum` so JSON serialisation round-trips losslessly.
"""
from __future__ import annotations

from enum import Enum


class CameraMotion(str, Enum):
    STATIC = "static"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    HANDHELD = "handheld"
    DOLLY = "dolly"
    ORBIT = "orbit"


class ShotType(str, Enum):
    EXTREME_WIDE = "extreme_wide"
    WIDE = "wide"
    MEDIUM = "medium"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE_UP = "extreme_close_up"
    OVER_SHOULDER = "over_shoulder"
    POV = "pov"
    AERIAL = "aerial"
    UNKNOWN = "unknown"


class TransitionType(str, Enum):
    CUT = "cut"
    CROSS_DISSOLVE = "cross_dissolve"
    FADE_TO_BLACK = "fade_to_black"
    FADE_TO_WHITE = "fade_to_white"
    WIPE = "wipe"
    FLASH = "flash"
    WHIP_PAN = "whip_pan"
    J_CUT = "j_cut"
    L_CUT = "l_cut"
    SMASH_CUT = "smash_cut"


class EffectType(str, Enum):
    NONE = "none"
    SLOW_MOTION = "slow_motion"
    FAST_MOTION = "fast_motion"
    REVERSE = "reverse"
    VHS = "vhs"
    GLITCH = "glitch"
    BLUR = "blur"
    SHAKE = "shake"
    ZOOM_BUMP = "zoom_bump"
    VIGNETTE = "vignette"
    GRAIN = "grain"
    LIGHT_LEAK = "light_leak"


class CaptionPosition(str, Enum):
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"
    BOTTOM_THIRD = "bottom_third"
    DYNAMIC = "dynamic"


class CaptionAnimation(str, Enum):
    NONE = "none"
    TYPEWRITER = "typewriter"
    POP = "pop"
    SLIDE_IN = "slide_in"
    KARAOKE = "karaoke"
    WORD_BY_WORD = "word_by_word"
    BOUNCE = "bounce"
    SHAKE = "shake"


class ColorGrade(str, Enum):
    NATURAL = "natural"
    WARM = "warm"
    COOL = "cool"
    TEAL_ORANGE = "teal_orange"
    NOIR = "noir"
    VINTAGE = "vintage"
    HIGH_CONTRAST = "high_contrast"
    PASTEL = "pastel"
    NEON = "neon"


class Pace(str, Enum):
    SLOW = "slow"
    MEDIUM = "medium"
    FAST = "fast"
    HYPER = "hyper"


class ClipRole(str, Enum):
    """What semantic role a clip should fill in a given scene."""

    HOOK = "hook"
    ESTABLISHING = "establishing"
    BROLL = "broll"
    TALKING_HEAD = "talking_head"
    PRODUCT = "product"
    ACTION = "action"
    TRANSITION = "transition"
    PUNCHLINE = "punchline"
    CTA = "cta"
    ANY = "any"


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
