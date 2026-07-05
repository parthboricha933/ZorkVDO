"""User profile + settings + subscription + notification DTOs."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class UserProfileUpdate(BaseModel):
    display_name: str | None = Field(None, min_length=1, max_length=80)
    avatar_url: str | None = None
    bio: str | None = Field(None, max_length=280)


class UserSettings(BaseModel):
    theme: str = "system"  # light | dark | system
    language: str = "en"
    email_notifications: bool = True
    push_notifications: bool = True
    auto_save_projects: bool = True
    high_quality_render: bool = True
    default_aspect_ratio: str = "9:16"
    default_caption_font: str = "Inter"


class UserSettingsUpdate(BaseModel):
    theme: str | None = None
    language: str | None = None
    email_notifications: bool | None = None
    push_notifications: bool | None = None
    auto_save_projects: bool | None = None
    high_quality_render: bool | None = None
    default_aspect_ratio: str | None = None
    default_caption_font: str | None = None


class SubscriptionPlan(BaseModel):
    code: str
    name: str
    price_monthly_usd: float
    price_yearly_usd: float
    features: list[str]
    is_active: bool = True


class SubscriptionPublic(BaseModel):
    id: str
    user_id: str
    plan_code: str
    status: str  # active | cancelled | past_due | trialing
    started_at: str
    renews_at: str | None = None
    cancelled_at: str | None = None


class SubscribeRequest(BaseModel):
    plan_code: str
    period: str = "monthly"  # monthly | yearly
    payment_method_token: str | None = None


class NotificationPublic(BaseModel):
    id: str
    user_id: str
    kind: str  # info | success | warning | error
    title: str
    body: str = ""
    entity_type: str | None = None
    entity_id: str | None = None
    read: bool = False
    created_at: str


class FeedbackRequest(BaseModel):
    category: str = Field(..., pattern="^(bug|feature|general|account|other)$")
    subject: str = Field(..., min_length=1, max_length=120)
    message: str = Field(..., min_length=1, max_length=4000)
    contact_email: str | None = None


class AnalyticsSummary(BaseModel):
    projects_count: int
    videos_count: int
    blueprints_count: int
    renders_count: int
    total_render_seconds: float
    storage_used_bytes: int
    recent_activity: list[dict]
