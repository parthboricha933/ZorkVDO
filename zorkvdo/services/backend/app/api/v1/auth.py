"""Auth routes: /api/v1/auth/*."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.api.deps import CurrentUserId, get_auth_service
from app.models.auth import (
    LoginRequest,
    LogoutResponse,
    PasswordChangeRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    req: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.register(req)


@router.post("/login", response_model=TokenResponse)
async def login(
    req: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.login(req)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    req: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth_service.refresh(req)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    user_id: CurrentUserId,
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    """Revoke the current access token (and any refresh token in the body)."""
    import json

    # Extract refresh token from body if present
    body: dict = {}
    try:
        raw = await request.body()
        if raw:
            body = json.loads(raw)
    except Exception:
        body = {}
    refresh_token = body.get("refresh_token")

    # Get the access token from the Authorization header
    auth_header = request.headers.get("authorization", "")
    access_token = ""
    if auth_header.lower().startswith("bearer "):
        access_token = auth_header[7:].strip()

    revoked = await auth_service.logout(access_token, refresh_token)
    return LogoutResponse(revoked=revoked)


@router.post("/logout-all", response_model=LogoutResponse)
async def logout_all(
    user_id: CurrentUserId,
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    """Revoke every refresh token for the current user."""
    token_repo = auth_service.repos.get("refresh_tokens")
    tokens = await token_repo.query(where={"user_id": user_id})
    for t in tokens:
        await token_repo.delete(t["id"])
    return LogoutResponse(revoked=len(tokens) > 0)


@router.get("/me", response_model=UserPublic)
async def me(
    user_id: CurrentUserId,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserPublic:
    return await auth_service.get_user_public(user_id)


@router.post("/change-password")
async def change_password(
    req: PasswordChangeRequest,
    user_id: CurrentUserId,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    ok = await auth_service.change_password(user_id, req.old_password, req.new_password)
    return {"changed": ok}
