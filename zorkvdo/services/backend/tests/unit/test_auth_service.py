"""Unit tests for the AuthService — pure service, no HTTP."""
from __future__ import annotations

import pytest

from app.core.config import Settings
from app.core.exceptions import AuthError, ConflictError, ValidationError
from app.db import build_repositories
from app.models.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


@pytest.fixture
def settings():
    return Settings(
        jwt_secret="x" * 64,
        jwt_access_ttl_minutes=15,
        jwt_refresh_ttl_days=7,
        password_min_length=8,
    )


@pytest.fixture
async def auth_service(settings):
    repos = build_repositories(settings)
    return AuthService(settings=settings, repos=repos.registry)


async def test_register_creates_user_and_returns_tokens(auth_service):
    resp = await auth_service.register(
        RegisterRequest(
            email="alice@example.com",
            password="supersecret123",
            display_name="Alice",
        )
    )
    assert resp.access_token
    assert resp.refresh_token
    assert resp.user.email == "alice@example.com"
    assert resp.user.display_name == "Alice"


async def test_register_rejects_duplicate_email(auth_service):
    await auth_service.register(
        RegisterRequest(
            email="bob@example.com",
            password="supersecret123",
            display_name="Bob",
        )
    )
    with pytest.raises(ConflictError):
        await auth_service.register(
            RegisterRequest(
                email="bob@example.com",
                password="anotherpass123",
                display_name="Bob2",
            )
        )


async def test_register_rejects_short_password(auth_service):
    """Short passwords are rejected — either by Pydantic at construction time
    or by the service's own min_length check."""
    from pydantic import ValidationError as PydanticValidationError
    with pytest.raises((ValidationError, PydanticValidationError)):
        await auth_service.register(
            RegisterRequest(
                email="carol@example.com",
                password="short",
                display_name="Carol",
            )
        )


async def test_register_rejects_password_below_service_min(settings):
    """A password that passes Pydantic (>=8) but is below the service's
    configured min_length should be rejected by the service."""
    from app.db import build_repositories
    from app.services.auth_service import AuthService
    # Service requires 12 chars
    settings.password_min_length = 12
    svc = AuthService(settings=settings, repos=build_repositories(settings).registry)
    # 8 chars passes Pydantic but should fail service validation
    with pytest.raises(ValidationError):
        await svc.register(
            RegisterRequest(
                email="dave@example.com",
                password="onlyeight",  # 9 chars — passes Pydantic, fails service min(12)
                display_name="Dave",
            )
        )


async def test_login_succeeds_with_correct_password(auth_service):
    await auth_service.register(
        RegisterRequest(
            email="dave@example.com",
            password="supersecret123",
            display_name="Dave",
        )
    )
    resp = await auth_service.login(
        LoginRequest(email="dave@example.com", password="supersecret123")
    )
    assert resp.access_token
    assert resp.user.email == "dave@example.com"


async def test_login_fails_with_wrong_password(auth_service):
    await auth_service.register(
        RegisterRequest(
            email="eve@example.com",
            password="supersecret123",
            display_name="Eve",
        )
    )
    with pytest.raises(AuthError):
        await auth_service.login(
            LoginRequest(email="eve@example.com", password="wrong")
        )


async def test_login_fails_with_unknown_email(auth_service):
    with pytest.raises(AuthError):
        await auth_service.login(
            LoginRequest(email="nobody@example.com", password="x" * 20)
        )


async def test_refresh_rotates_token(auth_service):
    resp = await auth_service.register(
        RegisterRequest(
            email="frank@example.com",
            password="supersecret123",
            display_name="Frank",
        )
    )
    from app.models.auth import RefreshRequest
    resp2 = await auth_service.refresh(RefreshRequest(refresh_token=resp.refresh_token))
    assert resp2.access_token != resp.access_token
    # Old refresh should now be revoked
    with pytest.raises(AuthError):
        await auth_service.refresh(RefreshRequest(refresh_token=resp.refresh_token))


async def test_refresh_rejects_access_token(auth_service):
    resp = await auth_service.register(
        RegisterRequest(
            email="grace@example.com",
            password="supersecret123",
            display_name="Grace",
        )
    )
    from app.models.auth import RefreshRequest
    with pytest.raises(AuthError):
        await auth_service.refresh(RefreshRequest(refresh_token=resp.access_token))


async def test_change_password_revokes_refresh_tokens(auth_service):
    resp = await auth_service.register(
        RegisterRequest(
            email="heidi@example.com",
            password="supersecret123",
            display_name="Heidi",
        )
    )
    ok = await auth_service.change_password("heidi@example.com".encode().hex() if False else resp.user.id, "supersecret123", "newpassword123")
    assert ok
    from app.models.auth import RefreshRequest
    with pytest.raises(AuthError):
        await auth_service.refresh(RefreshRequest(refresh_token=resp.refresh_token))


async def test_get_user_public(auth_service):
    resp = await auth_service.register(
        RegisterRequest(
            email="ivan@example.com",
            password="supersecret123",
            display_name="Ivan",
        )
    )
    pub = await auth_service.get_user_public(resp.user.id)
    assert pub.email == "ivan@example.com"
