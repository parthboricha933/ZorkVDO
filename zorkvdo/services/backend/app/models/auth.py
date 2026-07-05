"""Auth-related request/response models.

Note: registration + login are NOT backend endpoints — they happen
client-side via the Firebase Auth SDK. The backend only verifies
Firebase ID tokens and syncs user profiles.
"""
from __future__ import annotations

from pydantic import BaseModel


class UserPublic(BaseModel):
    id: str
    email: str
    display_name: str
    avatar_url: str | None = None
    plan: str = "free"
    created_at: str
    updated_at: str


class SyncResponse(BaseModel):
    """Returned by POST /auth/sync after Firebase sign-in."""

    user: UserPublic
    is_new_user: bool


class LogoutResponse(BaseModel):
    """Firebase Auth logout happens client-side; this is a no-op confirmation."""

    message: str = "Logout happens client-side via Firebase Auth SDK."
