"""Tests for the AI client factory + provider routing."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from zorkvdo_ai import build_ai_client
from zorkvdo_ai.providers.mock import MockProvider


def _mock_settings(**kw):
    s = MagicMock()
    s.ai_provider = kw.get("ai_provider", "mock")
    s.openai_api_key = MagicMock(get_secret_value=lambda: kw.get("openai_api_key", ""))
    s.openai_base_url = "https://api.openai.com/v1"
    s.openai_chat_model = "gpt-4o"
    s.openai_vision_model = "gpt-4o"
    s.anthropic_api_key = MagicMock(get_secret_value=lambda: kw.get("anthropic_api_key", ""))
    s.anthropic_base_url = "https://api.anthropic.com"
    s.anthropic_chat_model = "claude-3-5-sonnet-20241022"
    s.gemini_api_key = MagicMock(get_secret_value=lambda: kw.get("gemini_api_key", ""))
    s.gemini_model = "gemini-1.5-pro"
    return s


def test_build_ai_client_mock_default():
    s = _mock_settings(ai_provider="mock")
    client = build_ai_client(s)
    assert client.provider_name == "mock"


def test_build_ai_client_openai_requires_key():
    s = _mock_settings(ai_provider="openai", openai_api_key="")
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        build_ai_client(s)


def test_build_ai_client_anthropic_requires_key():
    s = _mock_settings(ai_provider="anthropic", anthropic_api_key="")
    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        build_ai_client(s)


def test_build_ai_client_gemini_requires_key():
    s = _mock_settings(ai_provider="gemini", gemini_api_key="")
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        build_ai_client(s)


def test_build_ai_client_unknown_provider_raises():
    s = _mock_settings(ai_provider="nonexistent")
    with pytest.raises(ValueError, match="unknown ai_provider"):
        build_ai_client(s)


def test_build_ai_client_openai_constructs_with_key():
    s = _mock_settings(ai_provider="openai", openai_api_key="sk-test-key")
    client = build_ai_client(s)
    assert client.provider_name == "openai"


def test_build_ai_client_anthropic_constructs_with_key():
    s = _mock_settings(ai_provider="anthropic", anthropic_api_key="sk-ant-test")
    client = build_ai_client(s)
    assert client.provider_name == "anthropic"


def test_build_ai_client_gemini_constructs_with_key():
    s = _mock_settings(ai_provider="gemini", gemini_api_key="AIza-test")
    client = build_ai_client(s)
    assert client.provider_name == "gemini"
