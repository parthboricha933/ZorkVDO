"""Tests for the Celery task wrappers + app config."""
from __future__ import annotations

import pytest


def test_celery_app_loaded():
    """The Celery app should configure itself from settings."""
    from app.workers.celery_app import celery_app
    assert celery_app.main == "zorkvdo"
    assert "zorkvdo.ping" in celery_app.tasks
    assert "zorkvdo.run_analysis" in celery_app.tasks
    assert "zorkvdo.run_match_clips" in celery_app.tasks
    assert "zorkvdo.run_render" in celery_app.tasks


def test_celery_ping_task():
    """The ping task should return 'pong'."""
    from app.workers.celery_app import celery_app
    result = celery_app.tasks["zorkvdo.ping"].apply()
    assert result.result == "pong"


def test_celery_task_serializers_are_json():
    from app.workers.celery_app import celery_app
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.result_serializer == "json"


def test_celery_time_limits_set():
    from app.workers.celery_app import celery_app
    assert celery_app.conf.task_time_limit == 60 * 30
    assert celery_app.conf.task_soft_time_limit == 60 * 25


def test_celery_worker_recycles_after_10_tasks():
    """Memory hygiene: recycle worker after 10 tasks to release CV memory."""
    from app.workers.celery_app import celery_app
    assert celery_app.conf.worker_max_tasks_per_child == 10


def test_settings_loaded_from_env():
    """The Celery app should read broker URL from settings."""
    import os
    os.environ["CELERY_BROKER_URL"] = "redis://test-host:6379/9"
    os.environ["CELERY_RESULT_BACKEND"] = "redis://test-host:6379/8"
    from app.core.config import get_settings
    get_settings.cache_clear()
    s = get_settings()
    assert "test-host" in s.celery_broker_url
    # cleanup
    del os.environ["CELERY_BROKER_URL"]
    del os.environ["CELERY_RESULT_BACKEND"]
    get_settings.cache_clear()
