"""In-memory repository implementation.

Thread-safe enough for FastAPI's async event loop (single-threaded by
default per worker). For multi-process deployments use the Firestore
backend — `memory` is intentionally dev/test-only.
"""
from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.db.base import Repository, now_iso

log = get_logger(__name__)


class InMemoryRepository(Repository):
    """Dict-of-dicts store with simple equality filters."""

    def __init__(self, collection: str) -> None:
        self.collection = collection
        self._store: dict[str, dict[str, Any]] = {}

    async def get(self, doc_id: str) -> dict[str, Any] | None:
        doc = self._store.get(doc_id)
        return dict(doc) if doc else None

    async def put(self, doc_id: str, data: dict[str, Any]) -> dict[str, Any]:
        existing = self._store.get(doc_id, {})
        merged = {**existing, **data}
        if "id" not in merged:
            merged["id"] = doc_id
        if "created_at" not in merged:
            merged["created_at"] = now_iso()
        merged["updated_at"] = now_iso()
        self._store[doc_id] = merged
        return dict(merged)

    async def delete(self, doc_id: str) -> bool:
        if doc_id in self._store:
            del self._store[doc_id]
            return True
        return False

    async def query(
        self,
        *,
        where: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for doc in self._store.values():
            if where and not all(doc.get(k) == v for k, v in where.items()):
                continue
            rows.append(dict(doc))
        if order_by:
            rows.sort(
                key=lambda d: (d.get(order_by) is None, d.get(order_by)),
            )
        if offset:
            rows = rows[offset:]
        if limit is not None:
            rows = rows[:limit]
        return rows

    async def count(self, *, where: dict[str, Any] | None = None) -> int:
        return len(await self.query(where=where))

    # ── test-only helpers ────────────────────────────────
    def _clear(self) -> None:
        self._store.clear()
