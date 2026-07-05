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

Integrations tracked (per project spec):
  AI:            Gemini
  Firebase:      Auth, Firestore, Storage, FCM, Analytics (client), Crashlytics (client)
  Backend:       FastAPI
  Video:         FFmpeg, OpenCV, MoviePy
  CV:            YOLOv11, MediaPipe, EasyOCR
  Audio:         librosa
  Workers:       Redis
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


# ──────────────────────────────────────────────────────────────────────
# Probes
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
        message="API key present. Provider=gemini.",
        required_env_vars=required,
        last_checked=_now_iso(),
        extra={"model": s.gemini_model, "provider": "gemini"},
    )


async def _probe_firebase_auth(s: Settings) -> IntegrationReport:
    """Firebase Auth — backend verifies ID tokens via firebase-admin."""
    required = ["FIREBASE_CREDENTIALS_PATH", "FIREBASE_PROJECT_ID"]
    cred_path = s.firebase_credentials_path
    cred_exists = bool(cred_path) and os.path.exists(cred_path)
    has_project = bool(s.firebase_project_id)

    if not cred_exists or not has_project:
        missing = []
        if not cred_exists:
            missing.append("firebase-service-account.json (file)")
        if not has_project:
            missing.append("FIREBASE_PROJECT_ID")
        return IntegrationReport(
            name="Firebase Authentication",
            category="firebase",
            status=Status.MISSING_KEY,
            message=(
                "Firebase service account not configured. Backend cannot verify ID tokens — "
                "all authenticated endpoints will return 401. Drop firebase-service-account.json "
                f"at {cred_path}."
            ),
            required_env_vars=required,
            missing_env_vars=missing,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Firebase Authentication",
        category="firebase",
        status=Status.CONFIGURED,
        message="Service account present. Backend can verify Firebase ID tokens.",
        required_env_vars=required,
        last_checked=_now_iso(),
        extra={"project_id": s.firebase_project_id, "credentials_path": cred_path},
    )


async def _probe_firestore(s: Settings) -> IntegrationReport:
    if s.database_backend != "firestore":
        return IntegrationReport(
            name="Firestore",
            category="firebase",
            status=Status.DISABLED,
            message=f"Not active (DATABASE_BACKEND={s.database_backend}). Using in-memory store.",
            required_env_vars=["DATABASE_BACKEND", "FIREBASE_CREDENTIALS_PATH"],
            last_checked=_now_iso(),
        )
    required = ["FIREBASE_PROJECT_ID", "FIREBASE_CREDENTIALS_PATH"]
    cred_path = s.firebase_credentials_path
    cred_exists = os.path.exists(cred_path) if cred_path else False
    if not s.firebase_project_id or not cred_exists:
        missing = []
        if not s.firebase_project_id:
            missing.append("FIREBASE_PROJECT_ID")
        if not cred_exists:
            missing.append("firebase-service-account.json (file)")
        return IntegrationReport(
            name="Firestore",
            category="firebase",
            status=Status.MISSING_KEY,
            message=f"Service-account JSON not found at {cred_path}.",
            required_env_vars=required,
            missing_env_vars=missing,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Firestore",
        category="firebase",
        status=Status.CONFIGURED,
        message="Service account present. Firestore backend active.",
        required_env_vars=required,
        last_checked=_now_iso(),
        extra={"project_id": s.firebase_project_id, "credentials_path": cred_path},
    )


async def _probe_firebase_storage(s: Settings) -> IntegrationReport:
    required = ["FIREBASE_STORAGE_BUCKET", "FIREBASE_PROJECT_ID"]
    has_bucket = bool(s.firebase_storage_bucket)
    has_project = bool(s.firebase_project_id)
    if not has_bucket or not has_project:
        missing = []
        if not has_bucket:
            missing.append("FIREBASE_STORAGE_BUCKET")
        if not has_project:
            missing.append("FIREBASE_PROJECT_ID")
        return IntegrationReport(
            name="Firebase Storage",
            category="firebase",
            status=Status.MISSING_KEY,
            message="Firebase Storage config incomplete.",
            required_env_vars=required,
            missing_env_vars=missing,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Firebase Storage",
        category="firebase",
        status=Status.CONFIGURED,
        message=f"Storage bucket configured: {s.firebase_storage_bucket}",
        required_env_vars=required,
        last_checked=_now_iso(),
        extra={"bucket": s.firebase_storage_bucket},
    )


async def _probe_fcm(s: Settings) -> IntegrationReport:
    required = ["FCM_SERVER_KEY"]
    has_key = bool(s.fcm_server_key.get_secret_value())
    if not has_key:
        return IntegrationReport(
            name="Firebase Cloud Messaging",
            category="firebase",
            status=Status.MISSING_KEY,
            message="FCM_SERVER_KEY not set. Push notifications disabled (in-app notifications still work).",
            required_env_vars=required,
            missing_env_vars=required,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Firebase Cloud Messaging",
        category="firebase",
        status=Status.CONFIGURED,
        message="FCM server key present.",
        required_env_vars=required,
        last_checked=_now_iso(),
    )


async def _probe_firebase_analytics(s: Settings) -> IntegrationReport:
    """Firebase Analytics is client-side (Flutter app). The backend just
    confirms the google-services.json values are present so the Flutter
    app can initialise it."""
    required = ["FIREBASE_API_KEY", "FIREBASE_APP_ID"]
    has_api_key = bool(s.firebase_api_key)
    has_app_id = bool(s.firebase_app_id)
    if not has_api_key or not has_app_id:
        missing = []
        if not has_api_key:
            missing.append("FIREBASE_API_KEY")
        if not has_app_id:
            missing.append("FIREBASE_APP_ID")
        return IntegrationReport(
            name="Firebase Analytics (client)",
            category="firebase",
            status=Status.MISSING_KEY,
            message="Client SDK config incomplete. Flutter app cannot initialise Firebase Analytics.",
            required_env_vars=required,
            missing_env_vars=missing,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Firebase Analytics (client)",
        category="firebase",
        status=Status.CONFIGURED,
        message="Client SDK config present. Flutter app can initialise Firebase Analytics.",
        required_env_vars=required,
        last_checked=_now_iso(),
    )


async def _probe_firebase_crashlytics(s: Settings) -> IntegrationReport:
    """Firebase Crashlytics is client-side (Flutter app)."""
    required = ["FIREBASE_API_KEY", "FIREBASE_APP_ID"]
    has_api_key = bool(s.firebase_api_key)
    has_app_id = bool(s.firebase_app_id)
    if not has_api_key or not has_app_id:
        missing = []
        if not has_api_key:
            missing.append("FIREBASE_API_KEY")
        if not has_app_id:
            missing.append("FIREBASE_APP_ID")
        return IntegrationReport(
            name="Firebase Crashlytics (client)",
            category="firebase",
            status=Status.MISSING_KEY,
            message="Client SDK config incomplete. Flutter app cannot initialise Crashlytics.",
            required_env_vars=required,
            missing_env_vars=missing,
            last_checked=_now_iso(),
        )
    return IntegrationReport(
        name="Firebase Crashlytics (client)",
        category="firebase",
        status=Status.CONFIGURED,
        message="Client SDK config present. Flutter app can initialise Crashlytics.",
        required_env_vars=required,
        last_checked=_now_iso(),
    )


async def _probe_storage(s: Settings) -> IntegrationReport:
    if s.storage_provider == "local":
        return IntegrationReport(
            name="Storage (local)",
            category="storage",
            status=Status.CONNECTED,
            message=f"Using local filesystem at {s.storage_local_root}.",
            required_env_vars=[],
            last_checked=_now_iso(),
            extra={"backend": "local", "root": str(s.storage_local_root)},
        )
    if s.storage_provider == "s3":
        required = ["S3_ACCESS_KEY", "S3_SECRET_KEY"]
        if not s.s3_access_key or not s.s3_secret_key.get_secret_value():
            missing = []
            if not s.s3_access_key:
                missing.append("S3_ACCESS_KEY")
            if not s.s3_secret_key.get_secret_value():
                missing.append("S3_SECRET_KEY")
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
            extra={"endpoint": s.s3_endpoint, "bucket": s.storage_bucket, "region": s.s3_region},
        )
    if s.storage_provider == "firebase":
        return await _probe_firebase_storage(s)
    return IntegrationReport(
        name="Storage",
        category="storage",
        status=Status.DISABLED,
        message=f"Unknown storage backend: {s.storage_provider}",
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


async def _probe_ffmpeg(s: Settings) -> IntegrationReport:
    import shutil
    from subprocess import run

    ffmpeg = shutil.which("ffmpeg") or s.ffmpeg_path
    ffprobe = shutil.which("ffprobe") or s.ffprobe_path
    if not ffmpeg or not ffprobe:
        return IntegrationReport(
            name="FFmpeg",
            category="video",
            status=Status.MISSING_KEY,
            message="ffmpeg/ffprobe binary not found. Video analysis and rendering will fail.",
            required_env_vars=["FFMPEG_PATH", "FFPROBE_PATH"],
            missing_env_vars=[n for n, v in [("FFMPEG_PATH", ffmpeg), ("FFPROBE_PATH", ffprobe)] if not v],
            last_checked=_now_iso(),
        )
    try:
        proc = run([ffmpeg, "-version"], capture_output=True, timeout=3)
        version_line = proc.stdout.decode(errors="ignore").split("\n")[0]
    except Exception:
        version_line = ""
    return IntegrationReport(
        name="FFmpeg",
        category="video",
        status=Status.CONNECTED,
        message=f"ffmpeg + ffprobe available. {version_line}",
        required_env_vars=["FFMPEG_PATH"],
        last_checked=_now_iso(),
        extra={"ffmpeg": ffmpeg, "ffprobe": ffprobe},
    )


async def _probe_opencv(_: Settings) -> IntegrationReport:
    try:
        import cv2  # noqa: F401
        return IntegrationReport(
            name="OpenCV",
            category="video",
            status=Status.CONNECTED,
            message="opencv-python is installed.",
            required_env_vars=[],
            last_checked=_now_iso(),
            extra={"version": cv2.__version__},
        )
    except ImportError:
        return IntegrationReport(
            name="OpenCV",
            category="video",
            status=Status.DISABLED,
            message="opencv-python not installed. Video analysis cannot run.",
            required_env_vars=[],
            last_checked=_now_iso(),
        )


async def _probe_moviepy(_: Settings) -> IntegrationReport:
    try:
        import moviepy  # noqa: F401
        return IntegrationReport(
            name="MoviePy",
            category="video",
            status=Status.CONNECTED,
            message="moviepy is installed. Complex editing ops available.",
            required_env_vars=[],
            last_checked=_now_iso(),
            extra={"version": getattr(moviepy, "__version__", "unknown")},
        )
    except ImportError:
        return IntegrationReport(
            name="MoviePy",
            category="video",
            status=Status.DISABLED,
            message="moviepy not installed. Complex editing ops (text anims, PiP, transitions, audio mixing) disabled. FFmpeg still handles trim/scale/concat.",
            required_env_vars=[],
            last_checked=_now_iso(),
        )


async def _probe_yolo(s: Settings) -> IntegrationReport:
    try:
        import ultralytics  # noqa: F401
        return IntegrationReport(
            name="YOLOv11 (object detection)",
            category="cv",
            status=Status.CONNECTED,
            message="ultralytics is installed. Object detection active.",
            required_env_vars=[],
            last_checked=_now_iso(),
            extra={"model": s.yolo_model_path},
        )
    except ImportError:
        return IntegrationReport(
            name="YOLOv11 (object detection)",
            category="cv",
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
            category="cv",
            status=Status.CONNECTED,
            message="mediapipe is installed. Pose detection active.",
            required_env_vars=[],
            last_checked=_now_iso(),
        )
    except ImportError:
        return IntegrationReport(
            name="MediaPipe (pose)",
            category="cv",
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
            category="cv",
            status=Status.CONNECTED,
            message="easyocr is installed. Caption OCR active.",
            required_env_vars=[],
            last_checked=_now_iso(),
            extra={"languages": os.environ.get("ANALYSIS_OCR_LANGUAGES", "en")},
        )
    except ImportError:
        return IntegrationReport(
            name="EasyOCR (captions)",
            category="cv",
            status=Status.DISABLED,
            message="easyocr not installed. Caption OCR skipped (rest of analysis unaffected).",
            required_env_vars=[],
            last_checked=_now_iso(),
        )


async def _probe_librosa(_: Settings) -> IntegrationReport:
    try:
        import librosa  # noqa: F401
        return IntegrationReport(
            name="librosa (audio)",
            category="audio",
            status=Status.CONNECTED,
            message="librosa is installed. Beat detection + audio analysis active.",
            required_env_vars=[],
            last_checked=_now_iso(),
            extra={"version": librosa.__version__},
        )
    except ImportError:
        return IntegrationReport(
            name="librosa (audio)",
            category="audio",
            status=Status.DISABLED,
            message="librosa not installed. Beat detection disabled.",
            required_env_vars=[],
            last_checked=_now_iso(),
        )


async def _probe_fastapi(_: Settings) -> IntegrationReport:
    try:
        import fastapi
        return IntegrationReport(
            name="FastAPI",
            category="backend",
            status=Status.CONNECTED,
            message="FastAPI is running.",
            required_env_vars=[],
            last_checked=_now_iso(),
            extra={"version": fastapi.__version__},
        )
    except ImportError:
        return IntegrationReport(
            name="FastAPI",
            category="backend",
            status=Status.DISABLED,
            message="FastAPI not installed (impossible — backend wouldn't be running).",
            required_env_vars=[],
            last_checked=_now_iso(),
        )


# ──────────────────────────────────────────────────────────────────────
# Registry
# ──────────────────────────────────────────────────────────────────────
_PROBES: list[tuple[str, Callable[[Settings], Awaitable[IntegrationReport]]]] = [
    ("gemini", _probe_gemini),
    ("firebase_auth", _probe_firebase_auth),
    ("firestore", _probe_firestore),
    ("firebase_storage", _probe_firebase_storage),
    ("fcm", _probe_fcm),
    ("firebase_analytics", _probe_firebase_analytics),
    ("firebase_crashlytics", _probe_firebase_crashlytics),
    ("storage", _probe_storage),
    ("redis", _probe_redis),
    ("ffmpeg", _probe_ffmpeg),
    ("opencv", _probe_opencv),
    ("moviepy", _probe_moviepy),
    ("yolo", _probe_yolo),
    ("mediapipe", _probe_mediapipe),
    ("easyocr", _probe_easyocr),
    ("librosa", _probe_librosa),
    ("fastapi", _probe_fastapi),
]


class IntegrationStatus:
    def __init__(self) -> None:
        self._cache: dict[str, IntegrationReport] = {}
        self._last_refresh: str = ""

    async def refresh(self, settings: Settings) -> dict[str, IntegrationReport]:
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


_registry = IntegrationStatus()


def get_integration_status() -> IntegrationStatus:
    return _registry
