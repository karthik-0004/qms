"""CAPA Service — Core CAPA lifecycle domain service."""

from datetime import datetime, timezone

import structlog

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError

from ..infra.db.models import CAPA, CAPAAction
from ..infra.db.repositories import CAPAActionRepository, CAPARepository

logger = structlog.get_logger(__name__)

VALID_CAPA_TRANSITIONS = {
    "open": {"start_investigation"},
    "under_investigation": {"identify_root_cause"},
    "root_cause_identified": {"implement_actions"},
    "implementation": {"verify_effectiveness", "close"},
    "effectiveness_check": {"close", "reopen"},
    "closed": {"reopen"},
}


class CAPADomainService:
    """CAPA lifecycle management: Open → Investigate → Actions → Verify → Close."""

    def __init__(
        self,
        capa_repo: CAPARepository,
        action_repo: CAPAActionRepository,
        tenant_id: str,
    ) -> None:
        self._capas = capa_repo
        self._actions = action_repo
        self._tenant_id = tenant_id

    async def create_capa(
        self,
        capa_number: str,
        title: str,
        description: str,
        created_by: str,
        capa_type: str = "corrective",
        severity: str = "major",
        source_type: str | None = None,
        source_id: str | None = None,
        owner_id: str | None = None,
        department: str | None = None,
        due_date: datetime | None = None,
        tags: list[str] | None = None,
    ) -> CAPA:
        capa = await self._capas.create(
            tenant_id=self._tenant_id,
            capa_number=capa_number,
            title=title,
            description=description,
            created_by=created_by,
            capa_type=capa_type,
            severity=severity,
            source_type=source_type,
            source_id=source_id,
            owner_id=owner_id or created_by,
            department=department,
            due_date=due_date,
            tags=tags or [],
        )
        logger.info("capa_created", capa_id=capa.id, tenant=self._tenant_id)
        return capa

    async def get_capa(self, capa_id: str) -> CAPA:
        capa = await self._capas.get_by_id(capa_id)
        if not capa:
            raise NotFoundError("CAPA", capa_id)
        if capa.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this CAPA")
        return capa

    async def list_capas(
        self,
        status: str | None = None,
        severity: str | None = None,
        owner_id: str | None = None,
        department: str | None = None,
        overdue_only: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[CAPA], int]:
        return await self._capas.list_capas(
            tenant_id=self._tenant_id,
            status=status, severity=severity, owner_id=owner_id,
            department=department, overdue_only=overdue_only,
            offset=(page - 1) * page_size, limit=page_size,
        )

    async def update_capa(self, capa_id: str, updated_by: str, **fields) -> CAPA:
        await self.get_capa(capa_id)
        allowed = {"title", "description", "severity", "owner_id", "department",
                   "root_cause", "root_cause_method", "due_date",
                   "target_close_date", "tags"}
        filtered = {k: v for k, v in fields.items() if k in allowed}
        if filtered:
            await self._capas.update(capa_id, **filtered)
        return await self.get_capa(capa_id)

    async def add_action(
        self,
        capa_id: str,
        action_type: str,
        description: str,
        created_by: str,
        assigned_to: str | None = None,
        due_date: datetime | None = None,
    ) -> CAPAAction:
        await self.get_capa(capa_id)
        action = await self._actions.create(
            capa_id=capa_id,
            action_type=action_type,
            description=description,
            assigned_to=assigned_to or created_by,
            due_date=due_date,
        )
        logger.info("capa_action_added", capa_id=capa_id, action_id=action.id)
        return action

    async def complete_action(
        self, capa_id: str, action_id: str, evidence: str | None = None
    ) -> CAPAAction:
        await self.get_capa(capa_id)
        action = await self._actions.get_by_id(action_id)
        if not action or action.capa_id != capa_id:
            raise NotFoundError("CAPAAction", action_id)
        await self._actions.update(
            action_id,
            status="completed",
            completed_at=datetime.now(timezone.utc),
            evidence=evidence,
        )
        return await self._actions.get_by_id(action_id)

    async def verify_effectiveness(
        self, capa_id: str, verified_by: str, verified: bool, notes: str | None = None
    ) -> CAPA:
        capa = await self.get_capa(capa_id)
        await self._capas.update(
            capa_id,
            effectiveness_verified=verified,
            effectiveness_check_date=datetime.now(timezone.utc),
        )
        if not verified:
            await self._capas.update(capa_id, status="implementation")
        logger.info("capa_effectiveness_verified", capa_id=capa_id, verified=verified)
        return await self.get_capa(capa_id)

    async def close_capa(self, capa_id: str, closed_by: str) -> CAPA:
        capa = await self.get_capa(capa_id)
        await self._capas.update(
            capa_id,
            status="closed",
            actual_close_date=datetime.now(timezone.utc),
        )
        logger.info("capa_closed", capa_id=capa_id, closed_by=closed_by)
        return await self.get_capa(capa_id)

    async def get_actions(self, capa_id: str) -> list[CAPAAction]:
        await self.get_capa(capa_id)
        return await self._actions.list_by_capa(capa_id)
