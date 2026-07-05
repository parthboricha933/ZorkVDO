"""Template service — pre-built editing templates browseable in-app."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.exceptions import NotFoundError
from app.db.base import RepositoryRegistry
from app.models.projects import TemplatePublic


# A small built-in catalog seeded on first request. In production this
# would live in Firestore and be managed via an admin UI.
SEED_TEMPLATES: list[dict] = [
    {
        "id": "tpl_hook_punchline",
        "name": "Hook → Punchline",
        "description": "Open with a 0.8s hook, build with three 1.5s b-roll beats, finish on a punchline close-up. Great for product reveals.",
        "category": "product",
        "is_premium": False,
        "tags": ["pace:fast", "product", "hook"],
    },
    {
        "id": "tpl_talking_head",
        "name": "Talking Head + B-roll",
        "description": "3s talking-head intro, alternating b-roll cuts every 1.2s synced to a beat. Best for explainer content.",
        "category": "education",
        "is_premium": False,
        "tags": ["pace:medium", "education", "talking_head"],
    },
    {
        "id": "tpl_hype_reel",
        "name": "Hype Reel",
        "description": "Sub-second cuts on every beat with flash transitions. For sports, fashion, action.",
        "category": "action",
        "is_premium": True,
        "tags": ["pace:hyper", "action", "flash"],
    },
    {
        "id": "tpl_chill_vlog",
        "name": "Chill Vlog",
        "description": "Long 4s shots with slow dissolves and ambient color grade. Calm, narrative pacing.",
        "category": "lifestyle",
        "is_premium": False,
        "tags": ["pace:slow", "lifestyle", "dissolve"],
    },
]


class TemplateService:
    def __init__(self, repos: RepositoryRegistry) -> None:
        self.repos = repos
        self._seeded = False

    async def _seed(self) -> None:
        if self._seeded:
            return
        existing = await self.repos.get("templates").query()
        if existing:
            self._seeded = True
            return
        now = datetime.now(timezone.utc).isoformat()
        for tpl in SEED_TEMPLATES:
            doc = {**tpl, "preview_url": None, "blueprint_id": None, "created_at": now, "updated_at": now}
            await self.repos.get("templates").put(tpl["id"], doc)
        self._seeded = True

    async def list(
        self, *, category: str | None = None, is_premium: bool | None = None
    ) -> list[TemplatePublic]:
        await self._seed()
        rows = await self.repos.get("templates").query(order_by="name")
        out: list[TemplatePublic] = []
        for r in rows:
            if category and r.get("category") != category:
                continue
            if is_premium is not None and r.get("is_premium") != is_premium:
                continue
            out.append(TemplatePublic(**r))
        return out

    async def get(self, template_id: str) -> TemplatePublic:
        await self._seed()
        doc = await self.repos.get("templates").get(template_id)
        if not doc:
            raise NotFoundError("template not found")
        return TemplatePublic(**doc)
