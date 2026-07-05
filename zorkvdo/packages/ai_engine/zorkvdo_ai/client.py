"""Provider-agnostic AI client.

The `AIClient` is the *only* surface business code uses. It dispatches
to the configured backend (`MockProvider` by default; real providers
are lazily imported when first used so the package stays light).
"""
from __future__ import annotations

from typing import Any

from .types import AiMessage, AiResponse, Role
from .providers.base import AIProvider

__all__ = ["AIClient", "AiMessage", "AiResponse", "Role", "build_ai_client"]


class AIClient:
    """High-level chat/vision client.

    Business code calls `chat()` or `vision()`; the client handles
    retries, provider routing, and telemetry. Swapping providers is a
    config change, not a code change.
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

    Real providers are imported lazily — `import ultralytics` etc. only
    happens when the provider is actually used.
    """
    name = (settings.ai_provider or "mock").lower()

    if name == "mock":
        from .providers.mock import MockProvider
        return AIClient(MockProvider(default_model="mock-1"))

    if name == "openai":
        from .providers.openai import OpenAIProvider
        return AIClient(
            OpenAIProvider(
                api_key=settings.openai_api_key.get_secret_value(),
                base_url=settings.openai_base_url,
                chat_model=settings.openai_chat_model,
                vision_model=settings.openai_vision_model,
            )
        )

    if name == "anthropic":
        from .providers.anthropic import AnthropicProvider
        return AIClient(
            AnthropicProvider(
                api_key=settings.anthropic_api_key.get_secret_value(),
                base_url=settings.anthropic_base_url,
                chat_model=settings.anthropic_chat_model,
            )
        )

    if name == "gemini":
        from .providers.gemini import GeminiProvider
        return AIClient(
            GeminiProvider(
                api_key=settings.gemini_api_key.get_secret_value(),
                model=settings.gemini_model,
            )
        )

    raise ValueError(f"unknown ai_provider: {name}")
