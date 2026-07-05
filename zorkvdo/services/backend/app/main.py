"""FastAPI application factory + middleware + lifespan."""
from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure local packages are importable
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BACKEND_ROOT))
sys.path.insert(0, str(_BACKEND_ROOT.parent.parent / "packages" / "shared_schemas"))
sys.path.insert(0, str(_BACKEND_ROOT.parent.parent / "packages" / "ai_engine"))

# Apply the path bootstrap first
from app._paths import _ensure_local_packages  # noqa: E402
_ensure_local_packages()

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.middleware.gzip import GZipMiddleware  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402

from app._paths import _ensure_local_packages  # noqa: F401, E402
from app.api.deps import (  # noqa: E402
    get_ai_client,
    get_repositories,
    get_storage,
)
from app.api.v1 import (  # noqa: E402
    auth,
    blueprints,
    feedback,
    health,
    jobs,
    projects,
    status,
    templates,
    users,
    videos,
)
from app.core.config import get_settings  # noqa: E402
from app.core.exceptions import register_exception_handlers  # noqa: E402
from app.core.logging import (  # noqa: E402
    bind_user,
    configure_logging,
    get_logger,
    new_request_id,
)
from app.core.logging import request_id_ctx  # noqa: E402

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup + shutdown."""
    settings = get_settings()
    configure_logging(level=settings.app_log_level, json_logs=settings.is_prod)
    log.info("app_starting", env=settings.app_env, host=settings.app_host, port=settings.app_port)

    # Eagerly initialise singletons so /ready reports correctly
    try:
        repos = get_repositories.__wrapped__ if hasattr(get_repositories, "__wrapped__") else None
        # Build directly via the factories (they cache)
        from app.db import build_repositories
        from app.storage import build_storage
        from zorkvdo_ai import build_ai_client

        rs = build_repositories(settings)
        st = build_storage(settings)
        ai = build_ai_client(settings)
        app.state.repositories = rs
        app.state.storage = st
        app.state.ai_client = ai

        # Warm the API deps caches so subsequent requests reuse them
        from app.api import deps as _deps
        _deps._repos_cache = rs
        _deps._storage_cache = st
        _deps._ai_client_cache = ai

        log.info(
            "app_started",
            db=rs.backend,
            storage=st.backend,
            ai_provider=ai.provider_name,
        )
    except Exception as e:
        log.exception("app_startup_failed", error=str(e))
        raise

    yield

    log.info("app_stopping")
    # Cleanup if needed
    log.info("app_stopped")


def create_app() -> FastAPI:
    """Build the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="ZorkVDO API",
        version="0.1.0",
        description="AI-powered viral video blueprint generator",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ─────────────────────────────────────────
    app.add_middleware(GZipMiddleware, minimum_size=1024)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or new_request_id()
        request.state.request_id = rid
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        # Clear context after request
        bind_user(None)
        return response

    # ── Exception handlers ─────────────────────────────────
    register_exception_handlers(app)

    # ── Static file serving for local storage backend ──────
    @app.get("/storage/{bucket}/{path:path}")
    async def serve_storage(bucket: str, path: str):
        """Serve files from local storage backend (dev/test convenience)."""
        from app.core.exceptions import NotFoundError
        from app.core.config import get_settings
        s = get_settings()
        if s.storage_backend != "local":
            raise NotFoundError("local storage not enabled")
        full = Path(s.storage_local_root) / bucket / path
        if not full.exists() or not full.is_file():
            raise NotFoundError("file not found")
        return JSONResponse(
            status_code=200,
            content={"url": str(full), "size": full.stat().st_size},
        )

    # ── Routes ─────────────────────────────────────────────
    api_prefix = "/api/v1"
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(projects.router, prefix=api_prefix)
    app.include_router(videos.router, prefix=api_prefix)
    app.include_router(blueprints.router, prefix=api_prefix)
    app.include_router(templates.router, prefix=api_prefix)
    app.include_router(users.router, prefix=api_prefix)
    app.include_router(jobs.router, prefix=api_prefix)
    app.include_router(feedback.router, prefix=api_prefix)
    app.include_router(status.router, prefix=api_prefix)

    @app.get("/")
    async def root() -> dict:
        return {
            "name": "ZorkVDO API",
            "version": "0.1.0",
            "docs": "/docs",
            "health": f"{api_prefix}/health",
        }

    return app


app = create_app()


def run() -> None:  # pragma: no cover - CLI entry
    """CLI entry point: `python -m app.main` or `zorkvdo-api`."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
        log_level=settings.app_log_level.lower(),
    )


if __name__ == "__main__":  # pragma: no cover
    run()
