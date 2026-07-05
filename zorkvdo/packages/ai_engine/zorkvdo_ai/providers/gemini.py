"""Google Gemini provider."""
from __future__ import annotations

from typing import Any

from ..types import AiMessage, AiResponse


class GeminiProvider:
    name = "gemini"
    default_model = "gemini-1.5-pro"

    def __init__(self, *, api_key: str, model: str = "gemini-1.5-pro") -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required when AI_PROVIDER=gemini")
        self._api_key = api_key
        self._model = model
        self.default_model = model

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

        # Convert to Gemini's "contents" format
        contents: list[dict[str, Any]] = []
        system_text = "\n\n".join(m.content for m in messages if m.role == "system")
        for m in messages:
            if m.role == "system":
                continue
            role = "user" if m.role == "user" else "model"
            if m.image_urls:
                parts: list[dict[str, Any]] = []
                if m.content:
                    parts.append({"text": m.content})
                for url in m.image_urls:
                    parts.append({"file_data": {"file_uri": url}})
                contents.append({"role": role, "parts": parts})
            else:
                contents.append({"role": role, "parts": [{"text": m.content}]})

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens or 2048,
            },
        }
        if system_text:
            payload["systemInstruction"] = {"parts": [{"text": system_text}]}

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            f"?key={self._api_key}"
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = ""
        for cand in data.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                if "text" in part:
                    text += part["text"]

        return AiResponse(
            text=text,
            model=model,
            usage={
                "prompt_tokens": data.get("usageMetadata", {}).get("promptTokenCount", 0),
                "completion_tokens": data.get("usageMetadata", {}).get("candidatesTokenCount", 0),
            },
            raw=data,
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        import hashlib

        out: list[list[float]] = []
        for t in texts:
            h = hashlib.sha256(t.encode()).digest()
            out.append([(b - 128) / 128.0 for b in h[:8]])
        return out
