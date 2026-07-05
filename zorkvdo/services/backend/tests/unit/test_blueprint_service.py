"""Tests for the BlueprintService — persistence + retrieval."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.core.exceptions import NotFoundError
from app.services.blueprint_service import BlueprintService
from zorkvdo_schemas import (
    Blueprint,
    BlueprintMeta,
    ColorGrade,
    Pace,
    Scene,
    ShotType,
)


def _make_blueprint(name="Test BP") -> Blueprint:
    meta = BlueprintMeta(
        schema_version="1.0.0",
        generator="test",
        generated_at=datetime.now(timezone.utc),
        source_video_id="v1",
        source_duration_seconds=10.0,
        fps=30.0,
        width=1080,
        height=1920,
    )
    return Blueprint(
        id="bp_test_1",
        name=name,
        meta=meta,
        pace=Pace.MEDIUM,
        overall_duration=10.0,
        scenes=[
            Scene(index=0, start=0.0, end=5.0, duration=5.0, shot_type=ShotType.WIDE),
            Scene(index=1, start=5.0, end=10.0, duration=5.0, shot_type=ShotType.CLOSE_UP),
        ],
        music=None,
        color_grade=ColorGrade.NATURAL,
        tags=["test", "demo"],
    )


@pytest.fixture
async def bp_service(repos):
    return BlueprintService(repos.registry)


async def test_save_and_get_blueprint(bp_service):
    bp = _make_blueprint("My BP")
    pub = await bp_service.save("user1", bp)
    assert pub.id == "bp_test_1"
    assert pub.name == "My BP"
    assert pub.owner_id == "user1"
    assert len(pub.scenes) == 2
    assert "test" in pub.tags

    fetched = await bp_service.get("user1", "bp_test_1")
    assert fetched.id == "bp_test_1"
    assert fetched.name == "My BP"


async def test_get_blueprint_other_user_returns_404(bp_service):
    bp = _make_blueprint()
    await bp_service.save("user1", bp)
    with pytest.raises(NotFoundError):
        await bp_service.get("user2", "bp_test_1")


async def test_list_blueprints(bp_service):
    bp1 = _make_blueprint("BP1")
    bp1.id = "bp_1"
    bp2 = _make_blueprint("BP2")
    bp2.id = "bp_2"
    await bp_service.save("user1", bp1)
    await bp_service.save("user1", bp2)
    # Other user
    bp3 = _make_blueprint("BP3")
    bp3.id = "bp_3"
    await bp_service.save("user2", bp3)

    summaries = await bp_service.list("user1")
    assert len(summaries) == 2
    names = {s.name for s in summaries}
    assert names == {"BP1", "BP2"}


async def test_delete_blueprint(bp_service):
    bp = _make_blueprint()
    await bp_service.save("user1", bp)
    assert await bp_service.delete("user1", "bp_test_1") is True
    # Delete again → NotFoundError (it's gone)
    with pytest.raises(NotFoundError):
        await bp_service.delete("user1", "bp_test_1")


async def test_get_raw_blueprint_round_trips(bp_service):
    """The raw Blueprint (typed) should round-trip through storage."""
    bp = _make_blueprint()
    await bp_service.save("user1", bp)
    raw = await bp_service.get_raw("bp_test_1")
    assert isinstance(raw, Blueprint)
    assert raw.id == "bp_test_1"
    assert raw.pace == Pace.MEDIUM
    assert len(raw.scenes) == 2
    assert raw.scenes[0].shot_type == ShotType.WIDE


async def test_get_raw_unknown_raises(bp_service):
    with pytest.raises(NotFoundError):
        await bp_service.get_raw("nonexistent")
