"""Tests for the database factory + Firestore fallback."""
from __future__ import annotations

import pytest

from app.core.config import Settings
from app.db import build_repositories
from app.db.memory import InMemoryRepository


def test_build_repositories_memory_default():
    s = Settings(database_backend="memory")
    repos = build_repositories(s)
    assert repos.backend == "memory"
    # All collections should be registered
    expected = {
        "users", "projects", "templates", "videos", "blueprints",
        "history", "settings", "subscriptions", "notifications",
        "refresh_tokens", "jobs",
    }
    assert expected <= set(repos.collections())


def test_build_repositories_firestore_falls_back_when_no_creds():
    """When firestore is requested but no credentials are present, fall back."""
    s = Settings(
        database_backend="firestore",
        firebase_project_id="",
        firebase_credentials_path="/nonexistent/path.json",
    )
    repos = build_repositories(s)
    assert repos.backend == "memory"


def test_repository_get_unknown_raises():
    """Asking for an unregistered collection should KeyError."""
    s = Settings(database_backend="memory")
    repos = build_repositories(s)
    with pytest.raises(KeyError):
        repos.get("nonexistent_collection")
