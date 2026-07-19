"""Domain exceptions + FastAPI exception handlers.

All business-logic errors inherit from `AppError`. Each carries an
`error_code` that the frontend can branch on, and an HTTP status code.
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error."""

    status_code: int = 400
    error_code: str = "app_error"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthError(AppError):
    status_code = 401
    error_code = "auth_error"


class NotFoundError(AppError):
    status_code = 404
    error_code = "not_found"


class ConflictError(AppError):
    status_code = 409
    error_code = "conflict"


class ValidationError(AppError):
    status_code = 422
    error_code = "validation_error"


class PermissionError(AppError):
    status_code = 403
    error_code = "forbidden"


class RateLimitError(AppError):
    status_code = 429
    error_code = "rate_limit_exceeded"


class StorageError(AppError):
    status_code = 502
    error_code = "storage_error"


class QuotaExceededError(AppError):
    status_code = 402
    error_code = "quota_exceeded"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        from app.core.logging import get_logger
        get_logger(__name__).exception("unhandled_error", error=str(exc))
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": str(exc),
                    "details": {
                        "type": type(exc).__name__,
                        "traceback": traceback.format_exc().split("\n")[-15:],
                    },
                }
            },
        )
