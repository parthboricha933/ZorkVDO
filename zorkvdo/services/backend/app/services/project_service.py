"""Project service."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.core.exceptions import NotFoundError, PermissionError
from app.db.base import RepositoryRegistry
from app.core.logging import get_logger
from app.models.projects import ProjectCreate, ProjectPublic, ProjectUpdate

log = get_logger(__name__)


class ProjectService:
    def __init__(self, repos: RepositoryRegistry) -> None:
        self.repos = repos

    async def create(self, owner_id: str, req: ProjectCreate) -> ProjectPublic:
        pid = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "id": pid,
            "owner_id": owner_id,
            "name": req.name,
            "description": req.description,
            "status": "active",
            "source_video_id": req.source_video_id,
            "blueprint_id": req.blueprint_id,
            "output_video_id": None,
            "created_at": now,
            "updated_at": now,
        }
        await self.repos.get("projects").put(pid, doc)
        await self._history(owner_id, "create", "project", pid, f"Created project '{req.name}'")
        return ProjectPublic(**doc)

    async def get(self, owner_id: str, project_id: str) -> ProjectPublic:
        doc = await self._get_owned(owner_id, project_id)
        return ProjectPublic(**doc)

    async def list(
        self, owner_id: str, *, limit: int = 50, offset: int = 0
    ) -> list[ProjectPublic]:
        rows = await self.repos.get("projects").query(
            where={"owner_id": owner_id}, order_by="created_at", limit=limit, offset=offset
        )
        return [ProjectPublic(**r) for r in rows]

    async def update(self, owner_id: str, project_id: str, req: ProjectUpdate) -> ProjectPublic:
        doc = await self._get_owned(owner_id, project_id)
        updates = req.model_dump(exclude_none=True)
        doc.update(updates)
        await self.repos.get("projects").put(project_id, doc)
        return ProjectPublic(**doc)

    async def delete(self, owner_id: str, project_id: str) -> bool:
        """Delete a project. Raises NotFoundError if not found or not owned."""
        await self._get_owned(owner_id, project_id)
        ok = await self.repos.get("projects").delete(project_id)
        if ok:
            await self._history(owner_id, "delete", "project", project_id, "Deleted project")
        return ok

    async def _get_owned(self, owner_id: str, project_id: str) -> dict:
        doc = await self.repos.get("projects").get(project_id)
        if not doc:
            raise NotFoundError("project not found")
        if doc["owner_id"] != owner_id:
            raise NotFoundError("project not found")
        return doc

    async def _history(
        self, owner_id: str, action: str, entity_type: str, entity_id: str, summary: str
    ) -> None:
        hid = uuid.uuid4().hex
        await self.repos.get("history").put(
            hid,
            {
                "id": hid,
                "owner_id": owner_id,
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "summary": summary,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
