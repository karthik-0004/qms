"""Audit Management Service — Domain service."""

from datetime import datetime, timezone
from typing import Optional
import uuid

from rainer_common.exceptions import RainerException

from ..infra.db.models import Audit, AuditFinding
from ..infra.db.repositories import AuditRepository, ChecklistRepository

AUDIT_STATUSES = ["scheduled", "in_progress", "completed", "cancelled"]
FINDING_CLASSIFICATIONS = ["major_nc", "minor_nc", "observation", "ofi"]


class AuditDomainService:
    def __init__(self, repo: AuditRepository, checklist_repo: ChecklistRepository, tenant_id: str) -> None:
        self._repo = repo
        self._checklist_repo = checklist_repo
        self._tenant_id = tenant_id

    async def create_audit(self, created_by: str, **kwargs) -> Audit:
        now = datetime.now(timezone.utc)
        audit_id = str(uuid.uuid4())
        return await self._repo.create(
            id=audit_id,
            tenant_id=self._tenant_id,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            **kwargs,
        )

    async def get_audit(self, audit_id: str) -> Audit:
        audit = await self._repo.get(audit_id, self._tenant_id)
        if not audit:
            raise RainerException("AUDIT_NOT_FOUND", f"Audit {audit_id} not found", status_code=404)
        return audit

    async def list_audits(
        self,
        status: Optional[str] = None,
        audit_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Audit], int]:
        return await self._repo.list(
            self._tenant_id,
            status=status,
            audit_type=audit_type,
            from_date=from_date,
            to_date=to_date,
            page=page,
            page_size=page_size,
        )

    async def update_audit(self, audit_id: str, **kwargs) -> Audit:
        audit = await self.get_audit(audit_id)
        updated = await self._repo.update(audit_id, self._tenant_id, **kwargs)
        if not updated:
            raise RainerException("AUDIT_NOT_FOUND", "Audit not found", status_code=404)
        return updated

    async def start_audit(self, audit_id: str) -> Audit:
        return await self.update_audit(
            audit_id,
            status="in_progress",
            performed_start=datetime.now(timezone.utc),
        )

    async def complete_audit(self, audit_id: str, summary: Optional[str] = None) -> Audit:
        kwargs: dict = {"status": "completed", "performed_end": datetime.now(timezone.utc)}
        if summary:
            kwargs["summary"] = summary
        return await self.update_audit(audit_id, **kwargs)

    async def delete_audit(self, audit_id: str) -> bool:
        await self.get_audit(audit_id)
        return await self._repo.delete(audit_id, self._tenant_id)

    async def add_finding(self, audit_id: str, created_by: str, **kwargs) -> AuditFinding:
        await self.get_audit(audit_id)
        now = datetime.now(timezone.utc)

        existing = await self._repo.list_findings(audit_id)
        finding_number = f"F-{len(existing) + 1:03d}"

        return await self._repo.add_finding(
            id=str(uuid.uuid4()),
            tenant_id=self._tenant_id,
            audit_id=audit_id,
            finding_number=finding_number,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            **kwargs,
        )

    async def update_finding(self, finding_id: str, **kwargs) -> AuditFinding:
        finding = await self._repo.get_finding(finding_id, self._tenant_id)
        if not finding:
            raise RainerException("FINDING_NOT_FOUND", "Finding not found", status_code=404)
        updated = await self._repo.update_finding(finding_id, self._tenant_id, **kwargs)
        if not updated:
            raise RainerException("FINDING_NOT_FOUND", "Finding not found", status_code=404)
        return updated

    async def list_findings(self, audit_id: str) -> list[AuditFinding]:
        return await self._repo.list_findings(audit_id)

    async def get_calendar(
        self, from_date: datetime, to_date: datetime
    ) -> list[Audit]:
        items, _ = await self._repo.list(
            self._tenant_id,
            from_date=from_date,
            to_date=to_date,
            page=1,
            page_size=500,
        )
        return items

    async def list_checklists(self):
        return await self._checklist_repo.list(self._tenant_id)

    async def create_checklist(self, created_by: str, **kwargs):
        now = datetime.now(timezone.utc)
        return await self._checklist_repo.create(
            id=str(uuid.uuid4()),
            tenant_id=self._tenant_id,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            **kwargs,
        )
