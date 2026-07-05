"""Auth service — register, login, refresh, logout.

JWTs are issued here. Refresh tokens are persisted to the
`refresh_tokens` collection so they can be revoked on logout.
"""
from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timezone

from app.core.config import Settings
from app.core.exceptions import AuthError, ConflictError, NotFoundError, ValidationError
from app.core.logging import bind_user, get_logger
from app.core.security import (
    create_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.base import RepositoryRegistry
from app.models.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserPublic,
)

log = get_logger(__name__)


class AuthService:
    def __init__(self, settings: Settings, repos: RepositoryRegistry) -> None:
        self.settings = settings
        self.repos = repos

    async def register(self, req: RegisterRequest) -> TokenResponse:
        users = self.repos.get("users")
        existing = await users.query(where={"email": req.email.lower()})
        if existing:
            raise ConflictError("email already registered", details={"email": req.email})

        if len(req.password) < self.settings.password_min_length:
            raise ValidationError(
                "password too short",
                details={"min_length": self.settings.password_min_length},
            )

        user_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        user_doc = {
            "id": user_id,
            "email": req.email.lower(),
            "password_hash": hash_password(req.password),
            "display_name": req.display_name,
            "avatar_url": None,
            "bio": "",
            "plan": "free",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        await users.put(user_id, user_doc)
        log.info("user_registered", user_id=user_id, email=req.email)
        return await self._issue_tokens(user_id, user_doc)

    async def login(self, req: LoginRequest) -> TokenResponse:
        users = self.repos.get("users")
        rows = await users.query(where={"email": req.email.lower()})
        if not rows:
            raise AuthError("invalid credentials")
        user = rows[0]
        if not verify_password(req.password, user.get("password_hash", "")):
            raise AuthError("invalid credentials")
        if not user.get("is_active", True):
            raise AuthError("account disabled")
        log.info("user_login", user_id=user["id"])
        return await self._issue_tokens(user["id"], user)

    async def refresh(self, req: RefreshRequest) -> TokenResponse:
        try:
            claims = decode_token(self.settings, req.refresh_token)
        except Exception as e:
            raise AuthError("invalid refresh token") from e
        if claims.get("type") != "refresh":
            raise AuthError("not a refresh token")

        # Ensure the token hasn't been revoked
        token_repo = self.repos.get("refresh_tokens")
        record = await token_repo.get(claims["jti"])
        if record is None:
            raise AuthError("refresh token revoked")

        users = self.repos.get("users")
        user = await users.get(claims["sub"])
        if not user or not user.get("is_active", True):
            raise AuthError("user not found or disabled")

        # Rotate: revoke old, issue new
        await token_repo.delete(claims["jti"])
        return await self._issue_tokens(user["id"], user)

    async def logout(self, access_token: str, refresh_token: str | None = None) -> bool:
        try:
            claims = decode_token(self.settings, access_token)
        except Exception:
            return False
        # Revoke the refresh token if supplied
        token_repo = self.repos.get("refresh_tokens")
        if refresh_token:
            try:
                rclaims = decode_token(self.settings, refresh_token)
                if rclaims.get("type") == "refresh":
                    await token_repo.delete(rclaims["jti"])
            except Exception:
                pass
        # Also revoke access (best-effort — short TTL anyway)
        if claims.get("type") == "access":
            # Mark the access jti as revoked
            await token_repo.put(
                f"revoked:{claims['jti']}",
                {"revoked_at": datetime.now(timezone.utc).isoformat(), "user_id": claims["sub"]},
            )
        bind_user(None)
        return True

    async def change_password(self, user_id: str, old_pw: str, new_pw: str) -> bool:
        users = self.repos.get("users")
        user = await users.get(user_id)
        if not user:
            raise NotFoundError("user not found")
        if not verify_password(old_pw, user.get("password_hash", "")):
            raise AuthError("incorrect current password")
        if len(new_pw) < self.settings.password_min_length:
            raise ValidationError(
                "password too short",
                details={"min_length": self.settings.password_min_length},
            )
        await users.put(user_id, {"password_hash": hash_password(new_pw)})
        # Revoke all refresh tokens for this user
        token_repo = self.repos.get("refresh_tokens")
        tokens = await token_repo.query(where={"user_id": user_id})
        for t in tokens:
            await token_repo.delete(t["id"])
        return True

    async def get_user_public(self, user_id: str) -> UserPublic:
        users = self.repos.get("users")
        user = await users.get(user_id)
        if not user:
            raise NotFoundError("user not found")
        return UserPublic(
            id=user["id"],
            email=user["email"],
            display_name=user["display_name"],
            avatar_url=user.get("avatar_url"),
            plan=user.get("plan", "free"),
            created_at=user["created_at"],
            updated_at=user["updated_at"],
        )

    # ── helpers ────────────────────────────────────────────────
    async def _issue_tokens(self, user_id: str, user: dict) -> TokenResponse:
        access, _ = create_token(
            settings=self.settings, user_id=user_id, token_type="access"
        )
        refresh, _ = create_token(
            settings=self.settings, user_id=user_id, token_type="refresh"
        )
        # Persist refresh jti for revocation
        rclaims = decode_token(self.settings, refresh)
        token_repo = self.repos.get("refresh_tokens")
        await token_repo.put(
            rclaims["jti"],
            {
                "user_id": user_id,
                "issued_at": rclaims["iat"],
                "expires_at": rclaims["exp"],
            },
        )
        bind_user(user_id)
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            token_type="bearer",
            expires_in=self.settings.jwt_access_ttl_minutes * 60,
            user=UserPublic(
                id=user["id"],
                email=user["email"],
                display_name=user["display_name"],
                avatar_url=user.get("avatar_url"),
                plan=user.get("plan", "free"),
                created_at=user["created_at"],
                updated_at=user["updated_at"],
            ),
        )


def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)
