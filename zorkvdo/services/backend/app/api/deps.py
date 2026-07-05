"""FastAPI dependencies.

All services are constructed once at startup and exposed via Depends().
Routes receive their dependencies through these functions, so swapping
an implementation (e.g. memory → firestore) is a one-line change.
"""
from __future__ import annotations

import threading
from typing import Annotated

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthError
from app.core.logging import get_logger
from app.core.security import decode_token
from app.db import Repositories, build_repositories
from app.services.analysis_service import AnalysisService
from app.services.auth_service import AuthService
from app.services.blueprint_service import BlueprintService
from app.services.project_service import ProjectService
from app.services.template_service import TemplateService
from app.services.user_service import UserService
from app.services.video_service import VideoService
from app.storage import Storage, build_storage
from zorkvdo_ai import build_ai_client

log = get_logger(__name__)

# ── App-state singletons (built lazily on first request) ──────────────
_lock = threading.Lock()
_repos_cache: Repositories | None = None
_storage_cache: Storage | None = None
_ai_client_cache = None


def get_repositories(request: Request) -> Repositories:
    """Return the singleton Repositories, building it if needed."""
    global _repos_cache
    if _repos_cache is None:
        with _lock:
            if _repos_cache is None:
                settings = get_settings()
                _repos_cache = build_repositories(settings)
                request.app.state.repositories = _repos_cache
    return _repos_cache


def get_storage(request: Request) -> Storage:
    global _storage_cache
    if _storage_cache is None:
        with _lock:
            if _storage_cache is None:
                settings = get_settings()
                _storage_cache = build_storage(settings)
                request.app.state.storage = _storage_cache
    return _storage_cache


def get_ai_client(request: Request):
    global _ai_client_cache
    if _ai_client_cache is None:
        with _lock:
            if _ai_client_cache is None:
                settings = get_settings()
                _ai_client_cache = build_ai_client(settings)
                request.app.state.ai_client = _ai_client_cache
    return _ai_client_cache


# ── Service factories ─────────────────────────────────────────────────
def get_auth_service(
    settings: Settings = Depends(get_settings),
    repos = Depends(get_repositories),
) -> AuthService:
    return AuthService(settings=settings, repos=repos.registry)


def get_project_service(repos = Depends(get_repositories)) -> ProjectService:
    return ProjectService(repos=repos.registry)


def get_video_service(
    repos = Depends(get_repositories),
    storage = Depends(get_storage),
    settings: Settings = Depends(get_settings),
) -> VideoService:
    return VideoService(repos=repos.registry, storage=storage, settings=settings)


def get_blueprint_service(repos = Depends(get_repositories)) -> BlueprintService:
    return BlueprintService(repos=repos.registry)


def get_template_service(repos = Depends(get_repositories)) -> TemplateService:
    return TemplateService(repos=repos.registry)


def get_user_service(repos = Depends(get_repositories)) -> UserService:
    return UserService(repos=repos.registry)


def get_analysis_service(
    repos = Depends(get_repositories),
    storage = Depends(get_storage),
    settings: Settings = Depends(get_settings),
) -> AnalysisService:
    return AnalysisService(repos=repos.registry, storage=storage, settings=settings)


# ── Authenticated user dependency ─────────────────────────────────────
_bearer = HTTPBearer(auto_error=False)


async def get_current_user_id(
    settings: Settings = Depends(get_settings),
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    authorization: str | None = Header(default=None),
) -> str:
    """Resolve the user_id from the Bearer token.

    Accepts either the standard `Authorization: Bearer ...` header or
    an `authorization` header (some clients lowercase it).
    """
    token: str | None = None
    if creds is not None:
        token = creds.credentials
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if not token:
        raise AuthError("missing bearer token")

    try:
        claims = decode_token(settings, token)
    except Exception as e:
        raise AuthError("invalid or expired token") from e
    if claims.get("type") != "access":
        raise AuthError("not an access token")

    # Check revocation list (best-effort; skip when collection missing)
    try:
        repos = get_repositories_sync()
        if repos:
            revoked = await repos.get("refresh_tokens").get(f"revoked:{claims['jti']}")
            if revoked:
                raise AuthError("token revoked")
    except AuthError:
        raise
    except Exception:
        pass

    user_id = claims.get("sub")
    if not user_id:
        raise AuthError("malformed token: no subject")
    return str(user_id)


def get_repositories_sync() -> Repositories | None:
    """Synchronous accessor for use outside FastAPI's DI."""
    return _repos_cache


# Type aliases for clean route signatures
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
