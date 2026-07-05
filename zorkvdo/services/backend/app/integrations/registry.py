"""Integration status registry.

Single source of truth for "is service X configured?". Every external
dependency reports one of:

  - `connected`     — credentials present AND a live check passed
  - `configured`    — credentials present but no live check run yet
  - `missing_key`   — required env var is empty
  - `invalid`       — credentials present but rejected by the service
  - `offline`       — service unreachable
  - `disabled`      — intentionally turned off (e.g. AI_PROVIDER=mock)

Business code calls `IntegrationStatus.get("gemini")` before using a
service. If the status is not `connected` or `configured`, the calling
feature is skipped with a friendly warning — never a crash.
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Awaitable, Callable

from app.core.config import Settings
from app.core.logging import get_logger

log = get_logger(__name__)


class Status(str, Enum):
    CONNECTED = "connected"
    CONFIGURED = "configured"
    MISSING_KEY = "missing_api_key"
    INVALID = "invalid_credentials"
    OFFLINE = "service_offline"
    DISABLED = "disabled"


@dataclass
class IntegrationReport:
    """One row in the API Status Page."""

    name: str
    category: str
    status: Status
    message: str
    required_env_vars: list[str] = field(default_factory=list)
    missing_env_vars: list[str] = field(default_factory=list)
    last_checked: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "status": self.status.value,
            "message": self.message,
            "required_env_vars": self.required_env_vars,
            "missing_env_vars": self.missing_env_vars,
            "last_checked": self.last_checked,
            "extra": self.extra,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


def _has(*names: str) -> tuple[bool, list[str]]:
    """Return (all_present, missing)."""
    missing = [n for n in names if not _env(n)]
    return (not missing, missing)


# ──────────────────────────────────────────────────────────────────────
# Per-integration probes
# ──────────────────────────────────────────────────────────────────────
async def _probe_gemini(s: Settings) -> IntegrationReport:
    required = ["GEMINI_API_KEY"]
    has_key = bool(s.gemini_api_key.get_secret_value())
    if s.ai_provider != "gemini":
        return IntegrationReport(
            name="Gemini AI",
            category="ai",
            status=Status.DISABLED,
            message=f"Not active (AI_PROVIDER={s.ai_provider}). Set AI_PROVIDER=gemini to enable.",
            required_env_vars=required,
            last_checked=_now_iso(),
        )
    if not has_key:
        return IntegrationReport(
            name="Gemini AI",
            category="ai",
            status=Status.MISSING_KEY,
            message="GEMINI_API_KEY is not set. AI generation features will fall back to the mock provider.",
            required_env_vars=required,
            missing_env_vars=required,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Gemini AI",
        category="ai",
        status=Status.CONFIGURED,
        message="API key present. Live call not yet attempted.",
        required_env_vars=required,
        last_checked=_now_iso(),
        extra={"model": s.gemini_model, "provider": "gemini"},
    )


async def _probe_openai(s: Settings) -> IntegrationReport:
    required = ["OPENAI_API_KEY"]
    has_key = bool(s.openai_api_key.get_secret_value())
    if s.ai_provider != "openai":
        return IntegrationReport(
            name="OpenAI",
            category="ai",
            status=Status.DISABLED,
            message=f"Not active (AI_PROVIDER={s.ai_provider}).",
            required_env_vars=required,
            last_checked=_now_iso(),
        )
    if not has_key:
        return IntegrationReport(
            name="OpenAI",
            category="ai",
            status=Status.MISSING_KEY,
            message="OPENAI_API_KEY is not set.",
            required_env_vars=required,
            missing_env_vars=required,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="OpenAI",
        category="ai",
        status=Status.CONFIGURED,
        message="API key present.",
        required_env_vars=required,
        last_checked=_now_iso(),
    )


async def _probe_anthropic(s: Settings) -> IntegrationReport:
    required = ["ANTHROPIC_API_KEY"]
    has_key = bool(s.anthropic_api_key.get_secret_value())
    if s.ai_provider != "anthropic":
        return IntegrationReport(
            name="Anthropic",
            category="ai",
            status=Status.DISABLED,
            message=f"Not active (AI_PROVIDER={s.ai_provider}).",
            required_env_vars=required,
            last_checked=_now_iso(),
        )
    if not has_key:
        return IntegrationReport(
            name="Anthropic",
            category="ai",
            status=Status.MISSING_KEY,
            message="ANTHROPIC_API_KEY is not set.",
            required_env_vars=required,
            missing_env_vars=required,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Anthropic",
        category="ai",
        status=Status.CONFIGURED,
        message="API key present.",
        required_env_vars=required,
        last_checked=_now_iso(),
    )


async def _probe_firebase(s: Settings) -> IntegrationReport:
    required = ["FIREBASE_PROJECT_ID", "FIREBASE_API_KEY"]
    has_project = bool(s.firebase_project_id)
    has_api_key = bool(s.firebase_api_key)
    if not has_project or not has_api_key:
        missing = []
        if not has_project:
            missing.append("FIREBASE_PROJECT_ID")
        if not has_api_key:
            missing.append("FIREBASE_API_KEY")
        return IntegrationReport(
            name="Firebase (client SDK)",
            category="firebase",
            status=Status.MISSING_KEY,
            message="Firebase client config incomplete. Auth + Firestore + Storage will fall back to local backends.",
            required_env_vars=required,
            missing_env_vars=missing,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Firebase (client SDK)",
        category="firebase",
        status=Status.CONFIGURED,
        message="Client SDK config present (google-services.json values).",
        required_env_vars=required,
        last_checked=_now_iso(),
        extra={
            "project_id": s.firebase_project_id,
            "app_id": s.firebase_app_id,
            "messaging_sender_id": s.firebase_messaging_sender_id,
        },
    )


async def _probe_firestore(s: Settings) -> IntegrationReport:
    if s.database_backend != "firestore":
        return IntegrationReport(
            name="Firestore",
            category="database",
            status=Status.DISABLED,
            message=f"Not active (DATABASE_BACKEND={s.database_backend}). Using in-memory store.",
            required_env_vars=["DATABASE_BACKEND", "FIREBASE_CREDENTIALS_PATH"],
            last_checked=_now_iso(),
        )
    required = ["FIREBASE_PROJECT_ID"]
    present, missing = _has(*required)
    cred_path = s.firebase_credentials_path
    cred_exists = os.path.exists(cred_path) if cred_path else False
    if not present or not cred_exists:
        miss = list(missing)
        if not cred_exists:
            miss.append("firebase-service-account.json (file)")
        return IntegrationReport(
            name="Firestore",
            category="database",
            status=Status.MISSING_KEY,
            message=f"Service-account JSON not found at {cred_path}. Place it there to enable Firestore.",
            required_env_vars=required + ["FIREBASE_CREDENTIALS_PATH"],
            missing_env_vars=miss,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Firestore",
        category="database",
        status=Status.CONFIGURED,
        message="Service account present. Live ping not yet attempted.",
        required_env_vars=required,
        last_checked=_now_iso(),
        extra={"project_id": s.firebase_project_id, "credentials_path": cred_path},
    )


async def _probe_storage(s: Settings) -> IntegrationReport:
    if s.storage_backend == "local":
        return IntegrationReport(
            name="Storage (local)",
            category="storage",
            status=Status.CONNECTED,
            message=f"Using local filesystem at {s.storage_local_root}.",
            required_env_vars=[],
            last_checked=_now_iso(),
            extra={"backend": "local", "root": str(s.storage_local_root)},
        )
    if s.storage_backend == "s3":
        required = ["S3_ACCESS_KEY", "S3_SECRET_KEY"]
        present, missing = _has(*required)
        if not present:
            return IntegrationReport(
                name="Storage (S3)",
                category="storage",
                status=Status.MISSING_KEY,
                message="S3 credentials missing. Falling back to local storage.",
                required_env_vars=required,
                missing_env_vars=missing,
                last_checked=_now_iso(),
            )
        return IntegrationReport(
            name="Storage (S3)",
            category="storage",
            status=Status.CONFIGURED,
            message=f"S3 credentials present. Endpoint: {s.s3_endpoint}, bucket: {s.storage_bucket}.",
            required_env_vars=required,
            last_checked=_now_iso(),
            extra={
                "endpoint": s.s3_endpoint,
                "bucket": s.storage_bucket,
                "region": s.s3_region,
            },
        )
    if s.storage_backend == "firebase":
        required = ["FIREBASE_PROJECT_ID", "FIREBASE_STORAGE_BUCKET"]
        present, missing = _has(*required)
        if not present:
            return IntegrationReport(
                name="Storage (Firebase)",
                category="storage",
                status=Status.MISSING_KEY,
                message="Firebase storage config incomplete. Falling back to local.",
                required_env_vars=required,
                missing_env_vars=missing,
                last_checked=_now_iso(),
            )
        return IntegrationReport(
            name="Storage (Firebase)",
            category="storage",
            status=Status.CONFIGURED,
            message="Firebase storage config present.",
            required_env_vars=required,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Storage",
        category="storage",
        status=Status.DISABLED,
        message=f"Unknown storage backend: {s.storage_backend}",
        last_checked=_now_iso(),
    )


async def _probe_redis(s: Settings) -> IntegrationReport:
    """Best-effort Redis ping. Failure → reports offline but doesn't crash."""
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(s.redis_url, socket_connect_timeout=2)
        try:
            await client.ping()
            return IntegrationReport(
                name="Redis",
                category="workers",
                status=Status.CONNECTED,
                message="Redis is reachable. Background workers will dispatch normally.",
                required_env_vars=["REDIS_URL"],
                last_checked=_now_iso(),
                extra={"url": s.redis_url},
            )
        finally:
            await client.aclose()
    except Exception as e:
        return IntegrationReport(
            name="Redis",
            category="workers",
            status=Status.OFFLINE,
            message=f"Redis unreachable ({type(e).__name__}). Background jobs will run inline (slower).",
            required_env_vars=["REDIS_URL"],
            last_checked=_now_iso(),
            extra={"error": str(e)[:200]},
        )


async def _probe_ffmpeg(_: Settings) -> IntegrationReport:
    """Probe ffmpeg + ffprobe binaries."""
    import shutil
    from subprocess import run

    ffmpeg = shutil.which("ffmpeg") or os.environ.get("FFMPEG_PATH", "")
    ffprobe = shutil.which("ffprobe") or os.environ.get("FFPROBE_PATH", "")
    if not ffmpeg or not ffprobe:
        return IntegrationReport(
            name="FFmpeg",
            category="video_engine",
            status=Status.MISSING_KEY,
            message="ffmpeg/ffprobe binary not found on PATH. Video analysis and rendering will fail.",
            required_env_vars=["FFMPEG_PATH", "FFPROBE_PATH"],
            missing_env_vars=[n for n, v in [("FFMPEG_PATH", ffmpeg), ("FFPROBE_PATH", ffprobe)] if not v],
            last_checked=_now_iso(),
        )
    # Quick version check
    try:
        proc = run([ffmpeg, "-version"], capture_output=True, timeout=3)
        version_line = proc.stdout.decode(errors="ignore").split("\n")[0]
    except Exception:
        version_line = ""
    return IntegrationReport(
        name="FFmpeg",
        category="video_engine",
        status=Status.CONNECTED,
        message=f"ffmpeg + ffprobe available. {version_line}",
        required_env_vars=["FFMPEG_PATH"],
        last_checked=_now_iso(),
        extra={"ffmpeg": ffmpeg, "ffprobe": ffprobe},
    )


async def _probe_yolo(_: Settings) -> IntegrationReport:
    try:
        import ultralytics  # noqa: F401
        return IntegrationReport(
            name="YOLO (object detection)",
            category="video_engine",
            status=Status.CONNECTED,
            message="ultralytics is installed. Object detection active.",
            required_env_vars=[],
            last_checked=_now_iso(),
            extra={"model": os.environ.get("YOLO_MODEL_PATH", "yolov8n.pt")},
        )
    except ImportError:
        return IntegrationReport(
            name="YOLO (object detection)",
            category="video_engine",
            status=Status.DISABLED,
            message="ultralytics not installed. Falling back to OpenCV Haar cascades for face detection. Object detection disabled.",
            required_env_vars=[],
            last_checked=_now_iso(),
        )


async def _probe_mediapipe(_: Settings) -> IntegrationReport:
    try:
        import mediapipe  # noqa: F401
        return IntegrationReport(
            name="MediaPipe (pose)",
            category="video_engine",
            status=Status.CONNECTED,
            message="mediapipe is installed. Pose detection active.",
            required_env_vars=[],
            last_checked=_now_iso(),
        )
    except ImportError:
        return IntegrationReport(
            name="MediaPipe (pose)",
            category="video_engine",
            status=Status.DISABLED,
            message="mediapipe not installed. Pose detection skipped (rest of analysis unaffected).",
            required_env_vars=[],
            last_checked=_now_iso(),
        )


async def _probe_easyocr(_: Settings) -> IntegrationReport:
    try:
        import easyocr  # noqa: F401
        return IntegrationReport(
            name="EasyOCR (captions)",
            category="video_engine",
            status=Status.CONNECTED,
            message="easyocr is installed. Caption OCR active.",
            required_env_vars=[],
            last_checked=_now_iso(),
            extra={"languages": os.environ.get("ANALYSIS_OCR_LANGUAGES", "en")},
        )
    except ImportError:
        return IntegrationReport(
            name="EasyOCR (captions)",
            category="video_engine",
            status=Status.DISABLED,
            message="easyocr not installed. Caption OCR skipped (rest of analysis unaffected).",
            required_env_vars=[],
            last_checked=_now_iso(),
        )


async def _probe_fcm(_: Settings) -> IntegrationReport:
    required = ["FCM_SERVER_KEY"]
    present, missing = _has(*required)
    if not present:
        return IntegrationReport(
            name="Firebase Cloud Messaging",
            category="notifications",
            status=Status.MISSING_KEY,
            message="FCM_SERVER_KEY not set. Push notifications disabled (in-app notifications still work).",
            required_env_vars=required,
            missing_env_vars=missing,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Firebase Cloud Messaging",
        category="notifications",
        status=Status.CONFIGURED,
        message="FCM server key present.",
        required_env_vars=required,
        last_checked=_now_iso(),
    )


async def _probe_email(_: Settings) -> IntegrationReport:
    resend = _env("RESEND_API_KEY")
    smtp = _env("SMTP_HOST")
    if resend:
        return IntegrationReport(
            name="Email (Resend)",
            category="notifications",
            status=Status.CONFIGURED,
            message="RESEND_API_KEY present. Transactional email enabled.",
            required_env_vars=["RESEND_API_KEY"],
            last_checked=_now_iso(),
        )
    if smtp:
        return IntegrationReport(
            name="Email (SMTP)",
            category="notifications",
            status=Status.CONFIGURED,
            message="SMTP_HOST present. Transactional email enabled.",
            required_env_vars=["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD"],
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Email",
        category="notifications",
        status=Status.MISSING_KEY,
        message="No email provider configured. Set RESEND_API_KEY or SMTP_HOST to enable transactional email.",
        required_env_vars=["RESEND_API_KEY"],
        last_checked=_now_iso(),
    )


async def _probe_analytics(_: Settings) -> IntegrationReport:
    provider = _env("ANALYTICS_PROVIDER") or "none"
    if provider == "none":
        return IntegrationReport(
            name="Analytics",
            category="analytics",
            status=Status.DISABLED,
            message="ANALYTICS_PROVIDER=none. Product analytics disabled.",
            required_env_vars=[],
            last_checked=_now_iso(),
        )
    key = _env("ANALYTICS_KEY") or _env("POSTHOG_API_KEY")
    if not key:
        return IntegrationReport(
            name=f"Analytics ({provider})",
            category="analytics",
            status=Status.MISSING_KEY,
            message=f"ANALYTICS_PROVIDER={provider} but no API key set.",
            required_env_vars=["ANALYTICS_KEY"],
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name=f"Analytics ({provider})",
        category="analytics",
        status=Status.CONFIGURED,
        message=f"Provider={provider}, key present.",
        required_env_vars=["ANALYTICS_KEY"],
        last_checked=_now_iso(),
    )


async def _probe_sentry(_: Settings) -> IntegrationReport:
    dsn = _env("SENTRY_DSN")
    if not dsn:
        return IntegrationReport(
            name="Sentry (errors)",
            category="analytics",
            status=Status.DISABLED,
            message="SENTRY_DSN not set. Error tracking disabled (recommended before launch).",
            required_env_vars=["SENTRY_DSN"],
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Sentry (errors)",
        category="analytics",
        status=Status.CONFIGURED,
        message="Sentry DSN present.",
        required_env_vars=["SENTRY_DSN"],
        last_checked=_now_iso(),
    )


async def _probe_stripe(_: Settings) -> IntegrationReport:
    required = ["STRIPE_SECRET_KEY"]
    present, missing = _has(*required)
    if not present:
        return IntegrationReport(
            name="Stripe (payments)",
            category="payments",
            status=Status.MISSING_KEY,
            message="STRIPE_SECRET_KEY not set. Subscription endpoints return mock responses.",
            required_env_vars=required,
            missing_env_vars=missing,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Stripe (payments)",
        category="payments",
        status=Status.CONFIGURED,
        message="Stripe secret key present.",
        required_env_vars=required,
        last_checked=_now_iso(),
    )


# ──────────────────────────────────────────────────────────────────────
# Registry
# ──────────────────────────────────────────────────────────────────────
_PROBES: list[tuple[str, Callable[[Settings], Awaitable[IntegrationReport]]]] = [
    ("gemini", _probe_gemini),
    ("openai", _probe_openai),
    ("anthropic", _probe_anthropic),
    ("firebase", _probe_firebase),
    ("firestore", _probe_firestore),
    ("storage", _probe_storage),
    ("redis", _probe_redis),
    ("ffmpeg", _probe_ffmpeg),
    ("yolo", _probe_yolo),
    ("mediapipe", _probe_mediapipe),
    ("easyocr", _probe_easyocr),
    ("fcm", _probe_fcm),
    ("email", _probe_email),
    ("analytics", _probe_analytics),
    ("sentry", _probe_sentry),
    ("stripe", _probe_stripe),
]


class IntegrationStatus:
    """Cached registry of integration statuses.

    Probes run on first access and again on `refresh()`. Business code
    can check `is_available("gemini")` before calling a service.
    """

    def __init__(self) -> None:
        self._cache: dict[str, IntegrationReport] = {}
        self._last_refresh: str = ""

    async def refresh(self, settings: Settings) -> dict[str, IntegrationReport]:
        """Re-run every probe."""
        reports = await asyncio.gather(*[probe(settings) for _, probe in _PROBES])
        self._cache = {name: report for (name, _), report in zip(_PROBES, reports)}
        self._last_refresh = _now_iso()
        log.info(
            "integration_status_refreshed",
            total=len(self._cache),
            connected=sum(1 for r in self._cache.values() if r.status == Status.CONNECTED),
            missing=sum(1 for r in self._cache.values() if r.status == Status.MISSING_KEY),
            disabled=sum(1 for r in self._cache.values() if r.status == Status.DISABLED),
        )
        return self._cache

    def get(self, name: str) -> IntegrationReport | None:
        return self._cache.get(name)

    def is_available(self, name: str) -> bool:
        """True if the integration is configured OR connected."""
        report = self._cache.get(name)
        return report is not None and report.status in (Status.CONNECTED, Status.CONFIGURED)

    def all_reports(self) -> list[IntegrationReport]:
        return list(self._cache.values())

    def summary(self) -> dict[str, Any]:
        return {
            "last_refreshed": self._last_refresh,
            "total": len(self._cache),
            "by_status": {
                status.value: sum(1 for r in self._cache.values() if r.status == status)
                for status in Status
            },
            "by_category": _group_by_category(self._cache),
        }


def _group_by_category(cache: dict[str, IntegrationReport]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for report in cache.values():
        out.setdefault(report.category, []).append(report.to_dict())
    return out


# Module-level singleton
_registry = IntegrationStatus()


def get_integration_status() -> IntegrationStatus:
    return _registry
