"""JWT + password utilities.

The auth flow is provider-agnostic: JWTs are issued by this service.
Firebase Auth can later be wired in as an *alternative* identity provider
via `verify_external_token` in the auth service — but the access/refresh
tokens used by the API are always ours.

We use `bcrypt` directly (not passlib) to avoid the well-known
passlib/bcrypt 4.x incompatibility. Passwords >72 bytes are
SHA-256-hashed first (a standard workaround that preserves bcrypt's
salt + work-factor protection while removing the byte limit).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import bcrypt
import jwt

from app.core.config import Settings
from app.core.logging import get_logger

log = get_logger(__name__)

TokenType = Literal["access", "refresh"]


class TokenError(Exception):
    """Raised when a token is invalid, expired, or malformed."""


def _pre_hash(password: str) -> bytes:
    """Pre-hash long passwords so bcrypt's 72-byte limit isn't an issue.

    This is the same scheme Django uses: SHA-256 → base64 → bcrypt.
    """
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(plain: str) -> str:
    """Return a bcrypt hash suitable for storage."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(_pre_hash(plain), salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time password verification."""
    try:
        return hmac.compare_digest(
            bcrypt.hashpw(_pre_hash(plain), hashed.encode("utf-8")),
            hashed.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_token(
    *,
    settings: Settings,
    user_id: str,
    token_type: TokenType,
    extra_claims: dict[str, Any] | None = None,
) -> tuple[str, datetime]:
    """Return (token, expires_at_utc)."""
    if token_type == "access":
        ttl = timedelta(minutes=settings.jwt_access_ttl_minutes)
    else:
        ttl = timedelta(days=settings.jwt_refresh_ttl_days)
    expires_at = datetime.now(timezone.utc) + ttl
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": user_id,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": uuid.uuid4().hex,
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(
        payload,
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    log.debug("jwt_issued", user_id=user_id, token_type=token_type, exp=expires_at.isoformat())
    return token, expires_at


def decode_token(settings: Settings, token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as e:
        raise TokenError("token expired") from e
    except jwt.InvalidTokenError as e:
        raise TokenError(f"invalid token: {e}") from e
