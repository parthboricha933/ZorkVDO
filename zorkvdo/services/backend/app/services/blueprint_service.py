"""Blueprint service — persistence + retrieval of reusable blueprints."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.exceptions import NotFoundError, PermissionError
from app.db.base import RepositoryRegistry
from app.models.projects import BlueprintPublic, BlueprintSummary
from zorkvdo_schemas import Blueprint


class BlueprintService:
    def __init__(self, repos: RepositoryRegistry) -> None:
        self.repos = repos

    async def save(self, owner_id: str, blueprint: Blueprint) -> BlueprintPublic:
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "id": blueprint.id,
            "owner_id": owner_id,
            "name": blueprint.name,
            "source_video_id": blueprint.meta.source_video_id,
            "pace": blueprint.pace.value,
            "overall_duration": blueprint.overall_duration,
            "scenes": [s.model_dump(mode="json") for s in blueprint.scenes],
            "music": blueprint.music.model_dump(mode="json") if blueprint.music else None,
            "color_grade": blueprint.color_grade.value,
            "tags": blueprint.tags,
            "notes": blueprint.notes,
            "schema_version": blueprint.meta.schema_version,
            "created_at": now,
            "updated_at": now,
        }
        await self.repos.get("blueprints").put(blueprint.id, doc)
        return self._to_public(doc)

    async def get(self, owner_id: str, blueprint_id: str) -> BlueprintPublic:
        doc = await self._get_owned(owner_id, blueprint_id)
        return self._to_public(doc)

    async def get_raw(self, blueprint_id: str) -> Blueprint:
        doc = await self.repos.get("blueprints").get(blueprint_id)
        if not doc:
            raise NotFoundError("blueprint not found")
        return Blueprint.from_storage_dict({
            "id": doc["id"],
            "name": doc["name"],
            "meta": {
                "schema_version": doc["schema_version"],
                "generator": "zorkvdo-analyzer",
                "generated_at": doc["created_at"],
                "source_video_id": doc["source_video_id"],
                "source_duration_seconds": doc["overall_duration"],
                "fps": 30.0,
                "width": 1080,
                "height": 1920,
            },
            "pace": doc["pace"],
            "overall_duration": doc["overall_duration"],
            "scenes": doc["scenes"],
            "music": doc["music"],
            "color_grade": doc["color_grade"],
            "tags": doc["tags"],
            "notes": doc["notes"],
        })

    async def list(
        self, owner_id: str, *, limit: int = 50, offset: int = 0
    ) -> list[BlueprintSummary]:
        rows = await self.repos.get("blueprints").query(
            where={"owner_id": owner_id}, order_by="created_at", limit=limit, offset=offset
        )
        return [
            BlueprintSummary(
                id=r["id"],
                name=r["name"],
                source_video_id=r["source_video_id"],
                pace=r["pace"],
                scene_count=len(r.get("scenes", [])),
                overall_duration=r["overall_duration"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
            for r in rows
        ]

    async def delete(self, owner_id: str, blueprint_id: str) -> bool:
        """Delete a blueprint. Raises NotFoundError if not found or not owned.

        Cross-user delete returns 404 (rather than 403) to avoid leaking
        existence of resources the caller doesn't own.
        """
        await self._get_owned(owner_id, blueprint_id)
        return await self.repos.get("blueprints").delete(blueprint_id)

    async def _get_owned(self, owner_id: str, blueprint_id: str) -> dict:
        doc = await self.repos.get("blueprints").get(blueprint_id)
        if not doc:
            raise NotFoundError("blueprint not found")
        if doc["owner_id"] != owner_id:
            raise NotFoundError("blueprint not found")
        return doc

    @staticmethod
    def _to_public(doc: dict) -> BlueprintPublic:
        return BlueprintPublic(
            id=doc["id"],
            owner_id=doc["owner_id"],
            name=doc["name"],
            source_video_id=doc["source_video_id"],
            pace=doc["pace"],
            overall_duration=doc["overall_duration"],
            scenes=doc.get("scenes", []),
            music=doc.get("music"),
            color_grade=doc.get("color_grade", "natural"),
            tags=doc.get("tags", []),
            notes=doc.get("notes", ""),
            schema_version=doc.get("schema_version", "1.0.0"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )
