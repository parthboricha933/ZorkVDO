"""Repository protocol + shared helpers."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def now_iso() -> str:
    return utc_now().isoformat()


@runtime_checkable
class Repository(Protocol):
    """Minimal document-store protocol used by every collection."""

    collection: str

    async def get(self, doc_id: str) -> dict[str, Any] | None: ...

    async def put(self, doc_id: str, data: dict[str, Any]) -> dict[str, Any]: ...

    async def delete(self, doc_id: str) -> bool: ...

    async def query(
        self,
        *,
        where: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]: ...

    async def count(self, *, where: dict[str, Any] | None = None) -> int: ...


class RepositoryRegistry:
    """Holds one Repository per logical collection.

    Business services receive this registry and pick the collection
    they need. Swapping backends is a factory change, not a service change.
    """

    def __init__(self) -> None:
        self._repos: dict[str, Repository] = {}

    def register(self, collection: str, repo: Repository) -> None:
        self._repos[collection] = repo

    def get(self, collection: str) -> Repository:
        if collection not in self._repos:
            raise KeyError(f"unknown collection '{collection}'")
        return self._repos[collection]

    def collections(self) -> Iterable[str]:
        return self._repos.keys()


# Module-level singleton used by the FastAPI dependency.
_REGISTRY = RepositoryRegistry()


def get_repository_registry() -> RepositoryRegistry:
    return _REGISTRY


def touch(data: dict[str, Any]) -> dict[str, Any]:
    """Update the `updated_at` timestamp."""
    data["updated_at"] = now_iso()
    return data
