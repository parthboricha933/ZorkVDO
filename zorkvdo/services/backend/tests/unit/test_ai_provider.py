"""Unit tests for the MockProvider."""
from __future__ import annotations

import json

import pytest

from zorkvdo_ai import AIClient, AiMessage
from zorkvdo_ai.providers.mock import MockProvider


@pytest.fixture
def client():
    return AIClient(MockProvider())


async def test_mock_chat_returns_text(client):
    resp = await client.chat(
        messages=[AiMessage(role="user", content="hello")],
        model="mock-1",
    )
    assert resp.text
    assert resp.model == "mock-1"
    assert "usage" in resp.raw or "usage" in resp.__dict__


async def test_mock_returns_json_when_prompted(client):
    resp = await client.chat(
        messages=[AiMessage(role="user", content="Generate a blueprint JSON")],
        model="mock-1",
    )
    data = json.loads(resp.text)
    assert data["mock"] is True
    assert "digest" in data


async def test_mock_embed_returns_deterministic_vectors(client):
    v1 = await client.embed(["hello", "world"])
    v2 = await client.embed(["hello", "world"])
    assert v1 == v2
    assert len(v1) == 2
    assert len(v1[0]) == 8


async def test_mock_vision_message(client):
    resp = await client.vision(
        prompt="describe this",
        image_urls=["https://example.com/x.png"],
    )
    assert resp.text


async def test_mock_default_model_set():
    p = MockProvider(default_model="mock-7")
    c = AIClient(p)
    assert p.default_model == "mock-7"
