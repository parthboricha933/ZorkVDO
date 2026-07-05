"""Anthropic Claude provider."""
from __future__ import annotations

from typing import Any

from ..types import AiMessage, AiResponse


class AnthropicProvider:
    name = "anthropic"
    default_model = "claude-3-5-sonnet-20241022"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.anthropic.com",
        chat_model: str = "claude-3-5-sonnet-20241022",
    ) -> None:
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when AI_PROVIDER=anthropic")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._chat_model = chat_model
        self.default_model = chat_model

    async def chat(
        self,
        *,
        messages: list[AiMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AiResponse:
        import httpx

        system_text = "\n\n".join(m.content for m in messages if m.role == "system")
        user_msgs: list[dict[str, Any]] = []
        for m in messages:
            if m.role == "system":
                continue
            if m.image_urls:
                content: list[dict[str, Any]] = []
                if m.content:
                    content.append({"type": "text", "text": m.content})
                for url in m.image_urls:
                    content.append(
                        {
                            "type": "image",
                            "source": {"type": "url", "url": url},
                        }
                    )
                user_msgs.append({"role": m.role, "content": content})
            else:
                user_msgs.append({"role": m.role, "content": m.content})

        payload: dict[str, Any] = {
            "model": model,
            "messages": user_msgs,
            "max_tokens": max_tokens or 2048,
            "temperature": temperature,
        }
        if system_text:
            payload["system"] = system_text

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self._base_url}/v1/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        text = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                text += block.get("text", "")

        return AiResponse(
            text=text,
            model=data.get("model", model),
            usage=data.get("usage", {}),
            raw=data,
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        # Anthropic doesn't expose embeddings as of this version; use the mock
        # implementation locally to keep the interface consistent.
        import hashlib

        out: list[list[float]] = []
        for t in texts:
            h = hashlib.sha256(t.encode()).digest()
            out.append([(b - 128) / 128.0 for b in h[:8]])
        return out
