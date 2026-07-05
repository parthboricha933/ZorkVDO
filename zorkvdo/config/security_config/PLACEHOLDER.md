# Security Configuration Placeholder
#
# Secrets used for JWT signing, refresh-token signing, and field-level encryption.
#
# Environment variables (see .env):
#   JWT_SECRET                     (signs access tokens — generate with `openssl rand -hex 32`)
#   JWT_REFRESH_SECRET             (signs refresh tokens — generate separately)
#   JWT_ALGORITHM                  (default: HS256)
#   JWT_ACCESS_TTL_MINUTES         (default: 30)
#   JWT_REFRESH_TTL_DAYS           (default: 14)
#   ENCRYPTION_KEY                 (32-byte key for field-level AES — `openssl rand -hex 16`)
#   PASSWORD_MIN_LENGTH            (default: 8)
#
# Status: PLACEHOLDER — defaults to insecure placeholders that fail loud in prod.
