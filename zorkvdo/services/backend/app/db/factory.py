"""Build the RepositoryRegistry based on settings."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.core.config import Settings
from app.core.logging import get_logger
from app.db.base import Repository, RepositoryRegistry, get_repository_registry
from app.db.memory import InMemoryRepository

log = get_logger(__name__)


# Logical collections that the backend manages. Keeping this list
# explicit lets us iterate it both for bootstrapping repositories AND
# for documenting the data model.
COLLECTIONS: tuple[str, ...] = (
    "users",
    "projects",
    "templates",
    "videos",
    "blueprints",
    "history",
    "settings",
    "subscriptions",
    "notifications",
    "refresh_tokens",  # for token revocation
    "jobs",            # background analysis/render jobs
)


@dataclass
class Repositories:
    registry: RepositoryRegistry
    backend: str

    def get(self, collection: str) -> Repository:
        return self.registry.get(collection)

    def collections(self) -> Iterable[str]:
        return self.registry.collections()


def build_repositories(settings: Settings) -> Repositories:
    """Construct a fresh repository registry.

    Called once at app startup. The result is exposed to FastAPI via
    the `get_repositories` dependency.
    """
    registry = get_repository_registry()
    backend = settings.database_backend

    if backend == "firestore":
        try:
            from app.db.firestore import FirestoreRepository, _init_firestore

            client = _init_firestore(
                settings.firebase_project_id,
                settings.firebase_credentials_path,
            )
            for name in COLLECTIONS:
                registry.register(name, FirestoreRepository(name, client))
            log.info("repositories_ready", backend="firestore", collections=COLLECTIONS)
            return Repositories(registry=registry, backend="firestore")
        except Exception as e:
            log.warning(
                "firestore_unavailable_falling_back",
                error=str(e),
                fallback="memory",
            )
            backend = "memory"

    # default / fallback
    for name in COLLECTIONS:
        registry.register(name, InMemoryRepository(name))
    log.info("repositories_ready", backend="memory", collections=COLLECTIONS)
    return Repositories(registry=registry, backend="memory")
