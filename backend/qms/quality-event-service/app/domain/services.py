"""Quality Event Service — Core quality event domain service."""

from datetime import datetime, timezone

import structlog

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError

from ..infra.db.models import QualityEvent
from ..infra.db.repositories import QualityEventRepository

logger = structlog.get_logger(__name__)

VALID_TRANSITIONS = {
    "open": {"investigate", "close"},
    "under_investigation": {"resolve", "close"},
    "resolved": {"close", "reopen"},
    "closed": {"reopen"},
}


class QualityEventDomainService:
    def __init__(self, repo: QualityEventRepository, tenant_id: str) -> None:
        self._repo = repo
        self._tenant_id = tenant_id

    async def create_event(
        self,
        event_number: str,
        title: str,
        event_type: str,
        description: str,
        detected_at: datetime,
        created_by: str,
        severity: str = "minor",
        priority: str = "medium",
        department: str | None = None,
        location: str | None = None,
        assigned_to: str | None = None,
        immediate_action: str | None = None,
        capa_required: bool = False,
        due_date: datetime | None = None,
        tags: list[str] | None = None,
    ) -> QualityEvent:
        existing = await self._repo.get_by_id(event_number) if False else None
        result = await self._repo.create(
            tenant_id=self._tenant_id,
            event_number=event_number,
            title=title,
            event_type=event_type,
            description=description,
            detected_at=detected_at,
            created_by=created_by,
            severity=severity,
            priority=priority,
            department=department,
            location=location,
            assigned_to=assigned_to or created_by,
            immediate_action=immediate_action,
            capa_required=capa_required,
            due_date=due_date,
            tags=tags or [],
        )
        logger.info("quality_event_created", event_id=result.id, tenant=self._tenant_id)
        return result

    async def get_event(self, event_id: str) -> QualityEvent:
        event = await self._repo.get_by_id(event_id)
        if not event:
            raise NotFoundError("QualityEvent", event_id)
        if event.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this quality event")
        return event

    async def list_events(
        self,
        status: str | None = None,
        event_type: str | None = None,
        severity: str | None = None,
        assigned_to: str | None = None,
        department: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[QualityEvent], int]:
        return await self._repo.list_events(
            tenant_id=self._tenant_id,
            status=status, event_type=event_type, severity=severity,
            assigned_to=assigned_to, department=department,
            offset=(page - 1) * page_size, limit=page_size,
        )

    async def update_event(self, event_id: str, updated_by: str, **fields) -> QualityEvent:
        await self.get_event(event_id)
        allowed = {"title", "description", "severity", "priority", "department", "location",
                   "assigned_to", "root_cause", "immediate_action", "capa_required",
                   "due_date", "tags", "attachments"}
        filtered = {k: v for k, v in fields.items() if k in allowed}
        if filtered:
            await self._repo.update(event_id, **filtered)
        return await self.get_event(event_id)

    async def close_event(self, event_id: str, closed_by: str, resolution: str | None = None) -> QualityEvent:
        await self.get_event(event_id)
        await self._repo.update(
            event_id,
            status="closed",
            closed_at=datetime.now(timezone.utc),
            root_cause=resolution,
        )
        logger.info("quality_event_closed", event_id=event_id, closed_by=closed_by)
        return await self.get_event(event_id)

    async def delete_event(self, event_id: str, deleted_by: str) -> None:
        event = await self.get_event(event_id)
        if event.status == "closed":
            raise ForbiddenError("Cannot delete closed quality events")
        await self._repo.soft_delete(event_id)

    async def get_summary(self) -> dict:
        counts = await self._repo.count_by_status(self._tenant_id)
        return {"by_status": counts, "tenant_id": self._tenant_id}
