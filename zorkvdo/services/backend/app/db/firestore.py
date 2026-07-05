"""Firestore repository implementation.

Activated only when:
  - `DATABASE_BACKEND=firestore`
  - A service-account JSON exists at `FIREBASE_CREDENTIALS_PATH`
    OR `GOOGLE_APPLICATION_CREDENTIALS` is set in the environment.

Until then, the factory falls back to `InMemoryRepository` so the
backend is always runnable.
"""
from __future__ import annotations

from typing import Any

from app.core.exceptions import AppError
from app.core.logging import get_logger
from app.db.base import Repository, now_iso

log = get_logger(__name__)


class FirestoreRepository(Repository):
    """Thin async wrapper around the (sync) firebase-admin Firestore client.

    firebase-admin is currently blocking; we wrap calls in `asyncio.to_thread`
    so the FastAPI event loop is never stalled.
    """

    def __init__(self, collection: str, client: Any) -> None:
        self.collection = collection
        self._client = client

    async def get(self, doc_id: str) -> dict[str, Any] | None:
        import asyncio

        snap = await asyncio.to_thread(
            self._client.collection(self.collection).document(doc_id).get
        )
        if not snap.exists:
            return None
        return dict(snap.to_dict())

    async def put(self, doc_id: str, data: dict[str, Any]) -> dict[str, Any]:
        import asyncio

        payload = {**data}
        payload.setdefault("id", doc_id)
        if "created_at" not in payload:
            payload["created_at"] = now_iso()
        payload["updated_at"] = now_iso()
        await asyncio.to_thread(
            self._client.collection(self.collection).document(doc_id).set, payload
        )
        return payload

    async def delete(self, doc_id: str) -> bool:
        import asyncio

        ref = self._client.collection(self.collection).document(doc_id)
        snap = await asyncio.to_thread(ref.get)
        if not snap.exists:
            return False
        await asyncio.to_thread(ref.delete)
        return True

    async def query(
        self,
        *,
        where: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        import asyncio

        q = self._client.collection(self.collection)
        if where:
            for k, v in where.items():
                q = q.where(k, "==", v)
        if order_by:
            q = q.order_by(order_by)
        if limit is not None:
            q = q.limit(limit)
        snaps = await asyncio.to_thread(q.get)
        rows = [dict(s.to_dict()) for s in snaps]
        if offset:
            rows = rows[offset:]
        return rows

    async def count(self, *, where: dict[str, Any] | None = None) -> int:
        rows = await self.query(where=where)
        return len(rows)


def _init_firestore(project_id: str, credentials_path: str) -> Any:
    """Initialise the firebase-admin SDK and return the Firestore client."""
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
    except ImportError as e:  # pragma: no cover - import guard
        raise AppError(
            "firebase-admin not installed",
            details={"hint": "pip install firebase-admin"},
        ) from e

    import os
    from pathlib import Path

    if firebase_admin._apps.get("[DEFAULT]"):  # type: ignore[attr-defined]
        return firestore.client()

    cred = None
    if credentials_path and Path(credentials_path).exists():
        cred = credentials.Certificate(credentials_path)
    elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        cred = credentials.ApplicationDefault()
    else:
        raise AppError(
            "firebase credentials missing",
            details={
                "expected_path": credentials_path,
                "hint": "set FIREBASE_CREDENTIALS_PATH or GOOGLE_APPLICATION_CREDENTIALS",
            },
        )

    firebase_admin.initialize_app(cred, {"projectId": project_id})
    log.info("firebase_initialized", project_id=project_id)
    return firestore.client()
