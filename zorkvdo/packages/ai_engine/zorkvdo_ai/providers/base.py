"""Provider protocol."""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ..types import AiMessage, AiResponse


@runtime_checkable
class AIProvider(Protocol):
    name: str
    default_model: str

    async def chat(
        self,
        *,
        messages: list[AiMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AiResponse: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...
