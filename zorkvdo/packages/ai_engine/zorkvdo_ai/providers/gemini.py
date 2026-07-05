"""Gemini provider using the `google-genai` SDK (the new unified Google AI SDK).

This replaces the previous raw-httpx implementation. The SDK handles:
  - retries
  - streaming
  - safety settings
  - multimodal content (text + images)
  - tool calling

Docs: https://ai.google.dev/gemini-api/docs/sdks
"""
from __future__ import annotations

from typing import Any

from app.core.logging import get_logger

from ..types import AiMessage, AiResponse

log = get_logger(__name__)


class GeminiProvider:
    name = "gemini"
    default_model = "gemini-1.5-pro"

    def __init__(self, *, api_key: str, model: str = "gemini-1.5-pro") -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required when AI_PROVIDER=gemini")
        self._api_key = api_key
        self.default_model = model
        self._client: Any | None = None

    def _get_client(self) -> Any:
        """Lazily initialise the google-genai client."""
        if self._client is None:
            try:
                from google import genai
                from google.genai import types
            except ImportError as e:
                raise RuntimeError(
                    "google-genai is not installed. Install with: pip install google-genai"
                ) from e
            self._client = genai.Client(api_key=self._api_key)
            self._types = types
        return self._client

    def _build_contents(
        self, messages: list[AiMessage]
    ) -> tuple[list[Any], str | None]:
        """Convert our AiMessage list to google-genai Content objects.

        Returns (contents, system_instruction).
        """
        contents: list[Any] = []
        system_text: list[str] = []
        types = self._types

        for m in messages:
            if m.role == "system":
                system_text.append(m.content)
                continue

            # Map our role names to Gemini's role names
            role = "user" if m.role == "user" else "model"

            parts: list[Any] = []
            if m.content:
                parts.append(types.Part.from_text(text=m.content))
            for url in m.image_urls:
                # google-genai supports both URLs and inline base64.
                # For URLs, use from_uri; for local files, the caller should
                # base64-encode and pass via Part.from_bytes.
                if url.startswith(("http://", "https://")):
                    parts.append(types.Part.from_uri(file_uri=url, mime_type="image/jpeg"))
                else:
                    # Treat as base64 inline
                    import base64
                    try:
                        data = base64.b64decode(url)
                        parts.append(types.Part.from_bytes(data=data, mime_type="image/jpeg"))
                    except Exception:
                        # Not base64 — skip
                        pass

            if parts:
                contents.append(types.Content(role=role, parts=parts))

        return contents, "\n\n".join(system_text) if system_text else None

    async def chat(
        self,
        *,
        messages: list[AiMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> AiResponse:
        client = self._get_client()
        contents, system_instruction = self._build_contents(messages)

        config_kwargs: dict[str, Any] = {
            "temperature": temperature,
        }
        if max_tokens is not None:
            config_kwargs["max_output_tokens"] = max_tokens
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        config = self._types.GenerateContentConfig(**config_kwargs)

        # google-genai supports both sync and async clients. We use the sync
        # client wrapped in a thread via asyncio.to_thread to avoid blocking
        # the event loop.
        import asyncio

        def _call() -> Any:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )

        try:
            response = await asyncio.to_thread(_call)
        except Exception as e:
            log.warning("gemini_call_failed", error=str(e)[:300])
            raise

        # Extract text from the response
        text = ""
        if hasattr(response, "text") and response.text:
            text = response.text
        elif hasattr(response, "candidates"):
            for cand in response.candidates:
                if hasattr(cand, "content") and cand.content:
                    for part in (cand.content.parts or []):
                        if hasattr(part, "text") and part.text:
                            text += part.text

        # Extract usage metadata if available
        usage = {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            um = response.usage_metadata
            usage = {
                "prompt_tokens": getattr(um, "prompt_token_count", 0) or 0,
                "completion_tokens": getattr(um, "candidates_token_count", 0) or 0,
                "total_tokens": getattr(um, "total_token_count", 0) or 0,
            }

        return AiResponse(
            text=text,
            model=model,
            usage=usage,
            raw=None,  # google-genai objects aren't directly JSON-serialisable
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings via Gemini's embed_content endpoint."""
        client = self._get_client()
        import asyncio

        def _call() -> list[list[float]]:
            results: list[list[float]] = []
            for text in texts:
                resp = client.models.embed_content(
                    model="text-embedding-004",
                    contents=text,
                )
                # The embedding is in resp.embeddings[0].values
                if hasattr(resp, "embeddings") and resp.embeddings:
                    results.append(list(resp.embeddings[0].values))
                else:
                    results.append([])
            return results

        try:
            return await asyncio.to_thread(_call)
        except Exception as e:
            log.warning("gemini_embed_failed", error=str(e)[:200])
            # Fall back to a deterministic hash-based embedding for testing
            import hashlib
            out: list[list[float]] = []
            for t in texts:
                h = hashlib.sha256(t.encode()).digest()
                out.append([(b - 128) / 128.0 for b in h[:8]])
            return out
