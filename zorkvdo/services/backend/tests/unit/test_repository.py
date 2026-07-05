"""Unit tests for the in-memory repository."""
from __future__ import annotations

import pytest

from app.db.memory import InMemoryRepository


@pytest.fixture
def repo():
    return InMemoryRepository("things")


async def test_put_and_get(repo):
    doc = await repo.put("1", {"name": "alpha"})
    assert doc["id"] == "1"
    assert doc["name"] == "alpha"
    assert "created_at" in doc
    assert "updated_at" in doc

    fetched = await repo.get("1")
    assert fetched["name"] == "alpha"


async def test_put_merges_existing(repo):
    await repo.put("1", {"name": "alpha", "score": 1})
    await repo.put("1", {"score": 2})
    fetched = await repo.get("1")
    assert fetched["name"] == "alpha"  # preserved
    assert fetched["score"] == 2  # updated


async def test_get_missing_returns_none(repo):
    assert await repo.get("nope") is None


async def test_delete(repo):
    await repo.put("1", {"x": 1})
    assert await repo.delete("1") is True
    assert await repo.get("1") is None
    assert await repo.delete("1") is False


async def test_query_with_where(repo):
    await repo.put("1", {"color": "red"})
    await repo.put("2", {"color": "blue"})
    await repo.put("3", {"color": "red"})
    rows = await repo.query(where={"color": "red"})
    assert len(rows) == 2


async def test_query_with_limit_offset(repo):
    for i in range(10):
        await repo.put(str(i), {"idx": i})
    rows = await repo.query(order_by="idx", limit=3, offset=2)
    assert [r["idx"] for r in rows] == [2, 3, 4]


async def test_count(repo):
    await repo.put("1", {"k": "a"})
    await repo.put("2", {"k": "a"})
    await repo.put("3", {"k": "b"})
    assert await repo.count(where={"k": "a"}) == 2
    assert await repo.count() == 3
