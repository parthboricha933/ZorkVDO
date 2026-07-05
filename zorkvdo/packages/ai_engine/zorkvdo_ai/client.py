"""Provider-agnostic AI client.

The `AIClient` is the *only* surface business code uses. It dispatches
to the configured backend. Supported providers:
  - `mock`  — deterministic stub (dev/test, no key needed)
  - `gemini` — Google Gemini via `google-genai` SDK

Adding a new provider = implement the `AIProvider` protocol in
`packages/ai_engine/zorkvdo_ai/providers/` and add a branch to
`build_ai_client` below.
"""
from __future__ import annotations

from typing import Any

from .types import AiMessage, AiResponse, Role
from .providers.base import AIProvider

__all__ = ["AIClient", "AiMessage", "AiResponse", "Role", "build_ai_client"]


class AIClient:
    """High-level chat/vision client.

    Business code calls `chat()` or `vision()`; the client handles
    provider routing. Swapping providers is a config change, not a
    code change.
    """

    def __init__(self, provider: AIProvider, *, default_model: str | None = None) -> None:
        self._provider = provider
        self._default_model = default_model or provider.default_model

    @property
    def provider_name(self) -> str:
        return self._provider.name

    async def chat(
        self,
        messages: list[AiMessage],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AiResponse:
        return await self._provider.chat(
            messages=messages,
            model=model or self._default_model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
        )

    async def vision(
        self,
        prompt: str,
        image_urls: list[str],
        *,
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> AiResponse:
        msg = AiMessage(role="user", content=prompt, image_urls=image_urls)
        return await self._provider.chat(
            messages=[msg],
            model=model or self._default_model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=None,
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return await self._provider.embed(texts)


def build_ai_client(settings: Any) -> AIClient:
    """Factory that picks a provider based on settings.ai_provider.

    Real providers are imported lazily so the backend can boot without
    `google-genai` installed — Gemini is only loaded if `AI_PROVIDER=gemini`.
    """
    name = getattr(settings, "ai_provider", "mock") or "mock"

    if name == "mock":
        from .providers.mock import MockProvider
        return AIClient(MockProvider(default_model="mock-1"))

    if name == "gemini":
        from .providers.gemini import GeminiProvider
        return AIClient(
            GeminiProvider(
                api_key=settings.gemini_api_key.get_secret_value(),
                model=settings.gemini_model,
            )
        )

    raise ValueError(
        f"unknown AI_PROVIDER: {name!r}. Supported: 'mock' | 'gemini'."
    )
