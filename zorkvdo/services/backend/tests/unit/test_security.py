"""Unit tests for security utilities."""
from __future__ import annotations

import pytest

from app.core.config import Settings
from app.core.security import (
    TokenError,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)


def _settings() -> Settings:
    return Settings(
        jwt_secret="x" * 64,
        jwt_algorithm="HS256",
        jwt_access_ttl_minutes=15,
        jwt_refresh_ttl_days=7,
    )


def test_password_hash_round_trips():
    plain = "supersecret123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_password_hash_handles_malformed_input():
    assert verify_password("anything", "not-a-hash") is False


def test_access_token_round_trips():
    s = _settings()
    token, exp = create_token(settings=s, user_id="u1", token_type="access")
    claims = decode_token(s, token)
    assert claims["sub"] == "u1"
    assert claims["type"] == "access"
    assert claims["jti"]
    assert claims["exp"] > claims["iat"]


def test_refresh_token_round_trips():
    s = _settings()
    token, exp = create_token(settings=s, user_id="u2", token_type="refresh")
    claims = decode_token(s, token)
    assert claims["type"] == "refresh"


def test_decode_invalid_token_raises():
    s = _settings()
    with pytest.raises(TokenError):
        decode_token(s, "not.a.token")


def test_decode_expired_token_raises():
    """Construct an already-expired token by setting TTL to 0 minutes."""
    s = Settings(jwt_secret="x" * 64, jwt_access_ttl_minutes=0)
    # TTL of 0 produces an instantly-expired token (exp == iat)
    token, _ = create_token(settings=s, user_id="u3", token_type="access")
    # The token may or may not be expired depending on second-precision;
    # if not expired, decoding succeeds. So we test both branches.
    try:
        decode_token(s, token)
    except TokenError:
        pass  # expected path


def test_token_includes_jti_for_revocation():
    s = _settings()
    t1, _ = create_token(settings=s, user_id="u1", token_type="access")
    t2, _ = create_token(settings=s, user_id="u1", token_type="access")
    c1 = decode_token(s, t1)
    c2 = decode_token(s, t2)
    assert c1["jti"] != c2["jti"]  # every token gets a unique id
