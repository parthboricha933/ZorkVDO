"""Auth service — Firebase Auth + user profile sync.

The Flutter client owns the sign-in flow (email/password, Google, Apple,
etc.) via the Firebase Auth SDK. After sign-in, the client sends the
Firebase ID token to the backend in the Authorization header. The
backend verifies the token and uses the Firebase UID as the user
identifier.

This service handles:
  - `verify_token(token)` → returns the Firebase UID + claims
  - `sync_user(uid, profile)` → upserts the user doc in the `users`
    Firestore collection so we have a place to store app-specific
    fields (display_name, plan, bio, avatar_url, etc.)
  - `get_user_public(uid)` → returns the user profile
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.core.exceptions import AuthError, NotFoundError
from app.core.logging import get_logger
from app.core.security import FirebaseUser, verify_firebase_token
from app.db.base import RepositoryRegistry
from app.models.auth import UserPublic

log = get_logger(__name__)


class AuthService:
    def __init__(self, repos: RepositoryRegistry) -> None:
        self.repos = repos

    async def verify_token(self, token: str) -> FirebaseUser:
        """Verify a Firebase ID token. Raises AuthError on failure."""
        return verify_firebase_token(token)

    async def sync_user(self, user: FirebaseUser) -> UserPublic:
        """Upsert the user doc in Firestore after Firebase Auth sign-in.

        Called from `/auth/sync` on first launch after sign-in, or any
        time the client wants to refresh the backend's view of the user.
        """
        users = self.repos.get("users")
        existing = await users.get(user.uid)
        now = datetime.now(timezone.utc).isoformat()

        if existing:
            # Update mutable fields from Firebase claims
            updates = {}
            if user.email and user.email != existing.get("email"):
                updates["email"] = user.email
            if user.name and user.name != existing.get("display_name"):
                updates["display_name"] = user.name
            if user.picture and user.picture != existing.get("avatar_url"):
                updates["avatar_url"] = user.picture
            if user.email_verified != existing.get("email_verified"):
                updates["email_verified"] = user.email_verified
            if updates:
                updates["last_login_at"] = now
                await users.put(user.uid, updates)
                existing.update(updates)
            return self._to_public(existing)

        # First sign-in → create user doc
        doc = {
            "id": user.uid,
            "email": user.email or "",
            "display_name": user.name or (user.email.split("@")[0] if user.email else "Creator"),
            "avatar_url": user.picture,
            "bio": "",
            "plan": "free",
            "email_verified": user.email_verified,
            "auth_provider": user.provider or "password",
            "created_at": now,
            "updated_at": now,
            "last_login_at": now,
        }
        await users.put(user.uid, doc)
        log.info("user_synced", uid=user.uid, email=user.email, provider=user.provider)
        return self._to_public(doc)

    async def get_user_public(self, uid: str) -> UserPublic:
        users = self.repos.get("users")
        doc = await users.get(uid)
        if not doc:
            raise NotFoundError("user not found")
        return self._to_public(doc)

    @staticmethod
    def _to_public(doc: dict) -> UserPublic:
        return UserPublic(
            id=doc["id"],
            email=doc.get("email", ""),
            display_name=doc.get("display_name", ""),
            avatar_url=doc.get("avatar_url"),
            plan=doc.get("plan", "free"),
            created_at=doc.get("created_at", ""),
            updated_at=doc.get("updated_at", ""),
        )
