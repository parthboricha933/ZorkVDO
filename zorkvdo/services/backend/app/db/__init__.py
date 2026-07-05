"""Repository pattern over a pluggable persistence backend.

Two backends are supported:

* `memory` — in-process dict-of-dicts. Zero setup, perfect for dev/tests.
* `firestore` — Google Cloud Firestore via the firebase-admin SDK.
  Activated when `DATABASE_BACKEND=firestore` AND a service-account
  JSON file is present. Until then, the memory backend is used.

Every collection (users, projects, ...) implements the same `Repository`
protocol, so business logic never knows which backend is live.
"""
from __future__ import annotations

from .base import Repository, get_repository_registry
from .memory import InMemoryRepository
from .factory import build_repositories, Repositories

__all__ = [
    "Repository",
    "Repositories",
    "InMemoryRepository",
    "build_repositories",
    "get_repository_registry",
]
