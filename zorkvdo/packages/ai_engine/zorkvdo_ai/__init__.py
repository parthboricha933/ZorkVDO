"""ZorkVDO AI engine — provider-agnostic AI + video analysis.

This package never hardcodes an AI provider. It exposes:

  - `AIClient` protocol  → chat + vision completions
  - `MockProvider`       → deterministic stub used in dev/tests
  - `OpenAIProvider`     → OpenAI-compatible chat + vision (lazy)
  - `AnthropicProvider`  → Anthropic Claude (lazy)
  - `GeminiProvider`     → Google Gemini (lazy)

Plus the video analysis pipeline:
  - `VideoAnalyzer`      → orchestrates scene/beat/caption/motion passes
  - `BlueprintBuilder`   → assembles a Blueprint from raw signals
  - `ClipMatcher`        → maps user clips into blueprint slots
"""
from .client import AIClient, build_ai_client
from .types import AiMessage, AiResponse, Role
from .providers.base import AIProvider
from .providers.mock import MockProvider
from .analysis import (
    BlueprintBuilder,
    ClipMatcher,
    VideoAnalyzer,
    AnalysisResult,
)

__all__ = [
    "AIClient",
    "AiMessage",
    "AiResponse",
    "AIProvider",
    "MockProvider",
    "build_ai_client",
    "BlueprintBuilder",
    "ClipMatcher",
    "VideoAnalyzer",
    "AnalysisResult",
]

__version__ = "0.1.0"
