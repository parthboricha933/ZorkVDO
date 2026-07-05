"""Auth routes: /api/v1/auth/*.

Endpoints:
  - GET  /auth/me        → current user profile (verifies Firebase token)
  - POST /auth/sync      → upsert user doc after Firebase sign-in
  - POST /auth/logout    → no-op (Firebase logout is client-side)

Registration and login are NOT here — they happen via the Firebase Auth
SDK in the Flutter client.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUserId, get_auth_service
from app.models.auth import LogoutResponse, SyncResponse, UserPublic
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserPublic)
async def me(
    uid: CurrentUserId,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserPublic:
    """Return the current user's profile. Verifies the Firebase token via the dependency."""
    return await auth_service.get_user_public(uid)


@router.post("/sync", response_model=SyncResponse)
async def sync_user(
    uid: CurrentUserId,
    auth_service: AuthService = Depends(get_auth_service),
) -> SyncResponse:
    """Upsert the user doc in Firestore after Firebase sign-in.

    The Flutter client calls this once after successful Firebase sign-in
    to ensure the backend has a user record (needed for plan, settings,
    notifications, etc.).
    """
    from app.api.deps import _last_firebase_user
    user = _last_firebase_user(uid)
    if user is None:
        # If the dependency didn't stash the user, re-verify is not possible
        # without the raw token. Fall back to a profile-only sync.
        from app.core.exceptions import AuthError
        raise AuthError("Firebase user context not available — re-send token")
    existing = await auth_service.repos.get("users").get(uid)
    profile = await auth_service.sync_user(user)
    return SyncResponse(user=profile, is_new_user=existing is None)


@router.post("/logout", response_model=LogoutResponse)
async def logout(uid: CurrentUserId) -> LogoutResponse:
    """Firebase Auth logout happens client-side. This endpoint exists for
    symmetry + to allow the client to call it as part of its logout flow."""
    return LogoutResponse()
