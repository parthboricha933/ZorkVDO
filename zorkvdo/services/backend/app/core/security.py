"""Firebase Authentication utilities.

The Flutter client signs in via the Firebase Auth SDK and sends a
Firebase ID token in the `Authorization: Bearer <token>` header. The
backend verifies the token via `firebase-admin.auth.verify_id_token()`
and uses the resulting `uid` as the user identifier.

There is no bcrypt password hashing, no JWT issuance, no JWT_SECRET —
Firebase Auth owns the entire identity layer.

If `firebase-admin` is not installed or no service account is
configured, `verify_token` raises `AuthError` so the request is
rejected with 401. The rest of the app continues to function — only
authenticated endpoints are unreachable.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.exceptions import AuthError
from app.core.logging import get_logger

log = get_logger(__name__)


@dataclass
class FirebaseUser:
    """Decoded Firebase ID token claims + uid."""

    uid: str
    email: str | None
    email_verified: bool
    name: str | None
    picture: str | None
    provider: str | None
    raw_claims: dict[str, Any]


# Module-level cache of the initialised firebase-admin app.
# `verify_id_token` is synchronous in firebase-admin — we call it via
# `asyncio.to_thread` from the dependency to avoid blocking the event loop.
_firebase_app: Any | None = None
_firebase_init_attempted: bool = False


def _get_firebase_app() -> Any:
    """Lazily initialise firebase-admin. Returns the app object."""
    global _firebase_app, _firebase_init_attempted
    if _firebase_app is not None:
        return _firebase_app
    if _firebase_init_attempted:
        # Already tried and failed — don't retry on every request.
        raise AuthError(
            "Firebase Auth not configured. Drop a service-account JSON at "
            "FIREBASE_CREDENTIALS_PATH and restart the backend."
        )

    _firebase_init_attempted = True
    try:
        import firebase_admin
        from firebase_admin import credentials
    except ImportError as e:
        raise AuthError(
            "firebase-admin is not installed. Install with: pip install firebase-admin"
        ) from e

    import os
    from pathlib import Path

    if firebase_admin._apps.get("[DEFAULT]"):  # type: ignore[attr-defined]
        _firebase_app = firebase_admin.get_app()
        return _firebase_app

    cred = None

    # ── Priority 1: FIREBASE_CREDENTIALS_BASE64 env var ────────────────
    # Base64-encoded service account JSON — works without a volume mount.
    # Generate with:  base64 -w0 firebase-service-account.json
    creds_b64 = os.environ.get("FIREBASE_CREDENTIALS_BASE64", "")
    if creds_b64:
        import base64
        import tempfile
        try:
            creds_json = base64.b64decode(creds_b64)
            # Write to a temp file so firebase-admin can read it
            tmp = tempfile.NamedTemporaryFile(
                mode="wb", suffix=".json", delete=False
            )
            tmp.write(creds_json)
            tmp.close()
            cred = credentials.Certificate(tmp.name)
            log.info("firebase_credentials_loaded_from_base64")
        except Exception as e:
            log.warning("firebase_credentials_base64_decode_failed", error=str(e))

    # ── Priority 2: FIREBASE_CREDENTIALS_PATH file on disk ─────────────
    if cred is None:
        creds_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "")
        if creds_path and Path(creds_path).exists():
            cred = credentials.Certificate(creds_path)
            log.info("firebase_credentials_loaded_from_path", path=creds_path)

    # ── Priority 3: GOOGLE_APPLICATION_CREDENTIALS ─────────────────────
    if cred is None and os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        cred = credentials.ApplicationDefault()

    # ── No credentials available ───────────────────────────────────────
    if cred is None:
        log.warning(
            "firebase_auth_not_configured",
            hint="Set FIREBASE_CREDENTIALS_BASE64 env var (base64-encoded service account JSON)",
        )
        raise AuthError(
            "Firebase Auth not configured. Set FIREBASE_CREDENTIALS_BASE64 env var "
            "with the base64-encoded service account JSON."
        )

    project_id = os.environ.get("FIREBASE_PROJECT_ID", "")
    firebase_admin.initialize_app(cred, {"projectId": project_id} or None)
    _firebase_app = firebase_admin.get_app()
    log.info("firebase_auth_initialised", project_id=project_id)
    return _firebase_app


def verify_firebase_token(token: str) -> FirebaseUser:
    """Verify a Firebase ID token and return the user info.

    Raises `AuthError` if:
      - firebase-admin isn't installed
      - no service-account JSON is configured
      - the token is malformed, expired, or revoked
    """
    try:
        app = _get_firebase_app()
        from firebase_admin import auth as fb_auth

        claims = fb_auth.verify_id_token(token, check_revoked=True)
    except AuthError:
        raise
    except Exception as e:
        # firebase-admin raises `firebase_admin.auth.InvalidIdTokenError`,
        # `ExpiredIdTokenError`, `RevokedIdTokenError`, etc. — collapse them
        # all into a single AuthError for the API surface.
        log.warning("firebase_token_invalid", error=str(e)[:200])
        raise AuthError("invalid or expired Firebase ID token") from e

    return FirebaseUser(
        uid=claims["uid"],
        email=claims.get("email"),
        email_verified=claims.get("email_verified", False),
        name=claims.get("name"),
        picture=claims.get("picture"),
        provider=claims.get("firebase", {}).get("sign_in_provider"),
        raw_claims=claims,
    )


def is_firebase_configured() -> bool:
    """True if firebase-admin can be initialised (used by status probes)."""
    try:
        _get_firebase_app()
        return True
    except AuthError:
        return False
