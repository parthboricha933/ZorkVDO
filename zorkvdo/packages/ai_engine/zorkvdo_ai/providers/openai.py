"""OpenAI-compatible provider (works with OpenAI, Azure-OpenAI, OpenRouter, vLLM, ...)."""
from __future__ import annotations

from typing import Any

from ..types import AiMessage, AiResponse


class OpenAIProvider:
    name = "openai"
    default_model = "gpt-4o"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        chat_model: str = "gpt-4o",
        vision_model: str = "gpt-4o",
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._chat_model = chat_model
        self._vision_model = vision_model
        self.default_model = chat_model

    def _build_payload(
        self,
        messages: list[AiMessage],
        model: str,
        temperature: float,
        max_tokens: int | None,
        tools: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        openai_msgs: list[dict[str, Any]] = []
        for m in messages:
            if m.image_urls:
                # Multimodal content
                content: list[dict[str, Any]] = [{"type": "text", "text": m.content}]
                for url in m.image_urls:
                    content.append({"type": "image_url", "image_url": {"url": url}})
                openai_msgs.append({"role": m.role, "content": content})
            else:
                openai_msgs.append({"role": m.role, "content": m.content})
        payload: dict[str, Any] = {
            "model": model,
            "messages": openai_msgs,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if tools:
            payload["tools"] = tools
        return payload

    async def chat(
        self,
        *,
        messages: list[AiMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AiResponse:
        import asyncio
        import httpx

        payload = self._build_payload(messages, model, temperature, max_tokens, tools)
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self._base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        return AiResponse(
            text=data["choices"][0]["message"]["content"],
            model=data.get("model", model),
            usage=data.get("usage", {}),
            raw=data,
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        import httpx

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self._base_url}/embeddings",
                json={"model": "text-embedding-3-small", "input": texts},
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()
        return [item["embedding"] for item in data["data"]]
