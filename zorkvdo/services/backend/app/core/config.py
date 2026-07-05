"""Application configuration.

Single source of truth for runtime settings. Reads from environment
variables (or `.env` file in development). No hardcoded secrets.

Auth model: Firebase Authentication is primary. The Flutter client signs
in via the Firebase Auth SDK and sends a Firebase ID token in the
Authorization header. The backend verifies it via firebase-admin. There
is no separate JWT issuance, no bcrypt password hashing, no JWT_SECRET.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Backend = Literal["memory", "firestore"]
StorageBackend = Literal["local", "s3", "firebase"]
AppEnv = Literal["development", "staging", "production"]


class Settings(BaseSettings):
    """Strongly-typed settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ────────────────────────────────────────────────
    app_name: str = "ZorkVDO Backend"
    app_env: AppEnv = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_log_level: str = "INFO"
    app_cors_origins: str = "http://localhost:8080"

    # ── Backend URLs ───────────────────────────────────────
    base_api_url: str = "http://localhost:8000/api/v1"
    backend_url: str = "http://localhost:8000"

    # ── Gemini ─────────────────────────────────────────────
    ai_provider: str = "mock"  # mock | gemini
    gemini_api_key: SecretStr = SecretStr("")
    gemini_model: str = "gemini-1.5-pro"

    # ── Firebase (client SDK config from google-services.json) ──
    firebase_api_key: str = ""
    firebase_project_id: str = ""
    firebase_app_id: str = ""
    firebase_storage_bucket: str = ""
    firebase_messaging_sender_id: str = ""
    firebase_credentials_path: str = "./config/firebase_config/firebase-service-account.json"

    # ── Database ───────────────────────────────────────────
    database_backend: Backend = "memory"

    # ── Storage ────────────────────────────────────────────
    storage_provider: StorageBackend = "local"
    storage_local_root: Path = Path("./storage_local")
    storage_bucket: str = "zorkvdo-media"
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = ""
    s3_secret_key: SecretStr = SecretStr("")
    s3_region: str = "us-east-1"
    s3_use_path_style: bool = True

    # ── Notifications ──────────────────────────────────────
    fcm_server_key: SecretStr = SecretStr("")

    # ── Celery / Redis ─────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ── Video processing ───────────────────────────────────
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"
    yolo_model_path: str = "yolo11n.pt"
    mediapipe_model_path: str = ""
    ocr_model_path: str = ""
    analysis_scene_threshold: float = 27.0
    analysis_sample_fps: float = 2.0
    analysis_max_video_seconds: int = 600
    analysis_ocr_languages: str = "en"
    analysis_enable_face: bool = True
    analysis_enable_pose: bool = True

    # ── Upload limits ──────────────────────────────────────
    upload_max_bytes: int = 524_288_000
    upload_allowed_video_mimes: str = "video/mp4,video/quicktime,video/webm,video/x-matroska"
    upload_allowed_image_mimes: str = "image/jpeg,image/png,image/webp"

    # ── Derived helpers ────────────────────────────────────
    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.app_cors_origins.split(",") if o.strip()]

    @property
    def allowed_video_mimes(self) -> set[str]:
        return {m.strip() for m in self.upload_allowed_video_mimes.split(",") if m.strip()}

    @property
    def allowed_image_mimes(self) -> set[str]:
        return {m.strip() for m in self.upload_allowed_image_mimes.split(",") if m.strip()}

    @property
    def is_prod(self) -> bool:
        return self.app_env == "production"

    @field_validator("firebase_credentials_path")
    @classmethod
    def _check_credentials_path(cls, v: str) -> str:
        # Just record the path — existence is checked by the Firestore backend
        # at startup. Missing path → falls back to memory store.
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor — use as a FastAPI dependency."""
    return Settings()
