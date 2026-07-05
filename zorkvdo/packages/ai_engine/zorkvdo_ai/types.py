"""Shared types used by both the AIClient and the providers.

Keeping these in a separate module avoids a circular import between
`client.py` and `providers/base.py`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant"]


@dataclass
class AiMessage:
    role: Role
    content: str
    # For vision inputs (multimodal models)
    image_urls: list[str] = field(default_factory=list)


@dataclass
class AiResponse:
    text: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    raw: dict[str, Any] | None = None
