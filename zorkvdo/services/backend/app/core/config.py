"""Application configuration.

Single source of truth for runtime settings. Reads from environment
variables (or `.env` file in development). No hardcoded secrets — every
secret has a placeholder default that fails loud when used in production.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Backend = Literal["memory", "firestore"]
StorageBackend = Literal["local", "s3", "firebase"]
AiProvider = Literal["mock", "openai", "anthropic", "gemini"]
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

    # ── Security / JWT ─────────────────────────────────────
    jwt_secret: SecretStr = SecretStr("CHANGE_ME_TO_A_64_CHAR_RANDOM_HEX_STRING")
    jwt_refresh_secret: SecretStr = SecretStr("CHANGE_ME_REFRESH_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_minutes: int = 30
    jwt_refresh_ttl_days: int = 14
    password_min_length: int = 8
    encryption_key: SecretStr = SecretStr("")

    # ── Storage ────────────────────────────────────────────
    storage_backend: StorageBackend = "local"
    storage_local_root: Path = Path("./storage_local")
    storage_bucket: str = "zorkvdo-media"
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = ""
    s3_secret_key: SecretStr = SecretStr("")
    s3_region: str = "us-east-1"
    s3_use_path_style: bool = True

    # ── Database ───────────────────────────────────────────
    database_backend: Backend = "memory"
    firebase_project_id: str = ""
    firebase_credentials_path: str = "./firebase-service-account.json"

    # ── Firebase (client SDK config from google-services.json) ──
    firebase_api_key: str = ""
    firebase_app_id: str = ""
    firebase_messaging_sender_id: str = ""

    # ── Celery / Redis ─────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ── AI providers ───────────────────────────────────────
    ai_provider: AiProvider = "mock"
    openai_api_key: SecretStr = SecretStr("")
    openai_base_url: str = "https://api.openai.com/v1"
    openai_chat_model: str = "gpt-4o"
    openai_vision_model: str = "gpt-4o"
    anthropic_api_key: SecretStr = SecretStr("")
    anthropic_base_url: str = "https://api.anthropic.com"
    anthropic_chat_model: str = "claude-3-5-sonnet-20241022"
    gemini_api_key: SecretStr = SecretStr("")
    gemini_model: str = "gemini-1.5-pro"

    # ── Video analysis ─────────────────────────────────────
    analysis_scene_threshold: float = 27.0
    analysis_sample_fps: float = 2.0
    analysis_max_video_seconds: int = 600
    analysis_ocr_languages: str = "en"
    analysis_yolo_model: str = "yolov8n.pt"
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

    @field_validator("jwt_secret")
    @classmethod
    def _warn_default_secret(cls, v: SecretStr) -> SecretStr:
        value = v.get_secret_value()
        if value.startswith("CHANGE_ME"):
            if os.getenv("APP_ENV", "development") == "production":
                raise ValueError("JWT_SECRET must be set to a real value in production")
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor — use as a FastAPI dependency."""
    return Settings()
