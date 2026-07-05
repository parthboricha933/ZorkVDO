"""sys.path bootstrap — ensures the monorepo's `packages/` are importable.

We resolve paths relative to this file so the bootstrap works whether
the app is run via `uvicorn app.main:app`, `python -m app`, or pytest.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _ensure_local_packages() -> None:
    # backend root = .../services/backend
    backend_root = Path(__file__).resolve().parent.parent
    monorepo = backend_root.parent.parent
    for pkg in ("shared_schemas", "ai_engine"):
        path = monorepo / "packages" / pkg
        if path.exists():
            p = str(path)
            if p not in sys.path:
                sys.path.insert(0, p)


_ensure_local_packages()
