"""Tests for the TemplateService — seeding + filtering."""
from __future__ import annotations

import pytest

from app.core.exceptions import NotFoundError
from app.services.template_service import TemplateService, SEED_TEMPLATES


@pytest.fixture
async def tpl_service(repos):
    return TemplateService(repos.registry)


async def test_seed_creates_templates(tpl_service):
    """First call to list() seeds the catalog."""
    items = await tpl_service.list()
    assert len(items) == len(SEED_TEMPLATES)
    # IDs match
    ids = {t.id for t in items}
    assert ids == {t["id"] for t in SEED_TEMPLATES}


async def test_seed_idempotent(tpl_service):
    """Calling list twice doesn't re-seed."""
    items1 = await tpl_service.list()
    items2 = await tpl_service.list()
    assert len(items1) == len(items2)


async def test_filter_by_category(tpl_service):
    items = await tpl_service.list(category="action")
    assert all(t.category == "action" for t in items)
    assert any(t.id == "tpl_hype_reel" for t in items)


async def test_filter_by_premium(tpl_service):
    items = await tpl_service.list(is_premium=True)
    assert all(t.is_premium for t in items)
    items = await tpl_service.list(is_premium=False)
    assert all(not t.is_premium for t in items)


async def test_get_by_id(tpl_service):
    await tpl_service.list()  # seed
    tpl = await tpl_service.get("tpl_hook_punchline")
    assert tpl.id == "tpl_hook_punchline"
    assert tpl.name == "Hook → Punchline"


async def test_get_unknown_returns_404(tpl_service):
    with pytest.raises(NotFoundError):
        await tpl_service.get("does_not_exist")
