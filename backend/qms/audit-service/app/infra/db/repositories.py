"""Audit Management Service — SQLAlchemy repositories."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Audit, AuditChecklist, AuditChecklistItem, AuditChecklistResponse, AuditFinding


class AuditRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, **kwargs) -> Audit:
        obj = Audit(**kwargs)
        self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def get(self, audit_id: str, tenant_id: str) -> Optional[Audit]:
        q = (
            select(Audit)
            .where(Audit.id == audit_id, Audit.tenant_id == tenant_id, Audit.deleted_at.is_(None))
            .options(selectinload(Audit.findings), selectinload(Audit.checklist_responses))
        )
        result = await self._db.execute(q)
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        audit_type: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Audit], int]:
        q = select(Audit).where(Audit.tenant_id == tenant_id, Audit.deleted_at.is_(None))
        if status:
            q = q.where(Audit.status == status)
        if audit_type:
            q = q.where(Audit.audit_type == audit_type)
        if from_date:
            q = q.where(Audit.scheduled_start >= from_date)
        if to_date:
            q = q.where(Audit.scheduled_start <= to_date)

        count_q = select(func.count()).select_from(q.subquery())
        total = (await self._db.execute(count_q)).scalar_one()

        q = q.order_by(Audit.scheduled_start.desc().nullslast()).offset((page - 1) * page_size).limit(page_size)
        result = await self._db.execute(q)
        return list(result.scalars()), total

    async def update(self, audit_id: str, tenant_id: str, **kwargs) -> Optional[Audit]:
        kwargs["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(Audit).where(Audit.id == audit_id, Audit.tenant_id == tenant_id).values(**kwargs)
        )
        await self._db.flush()
        return await self.get(audit_id, tenant_id)

    async def delete(self, audit_id: str, tenant_id: str) -> bool:
        await self._db.execute(
            update(Audit).where(Audit.id == audit_id, Audit.tenant_id == tenant_id)
            .values(deleted_at=datetime.now(timezone.utc))
        )
        await self._db.flush()
        return True

    async def add_finding(self, **kwargs) -> AuditFinding:
        obj = AuditFinding(**kwargs)
        self._db.add(obj)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def get_finding(self, finding_id: str, tenant_id: str) -> Optional[AuditFinding]:
        q = select(AuditFinding).where(AuditFinding.id == finding_id, AuditFinding.tenant_id == tenant_id)
        result = await self._db.execute(q)
        return result.scalar_one_or_none()

    async def update_finding(self, finding_id: str, tenant_id: str, **kwargs) -> Optional[AuditFinding]:
        kwargs["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(AuditFinding).where(AuditFinding.id == finding_id, AuditFinding.tenant_id == tenant_id).values(**kwargs)
        )
        await self._db.flush()
        return await self.get_finding(finding_id, tenant_id)

    async def list_findings(self, audit_id: str) -> list[AuditFinding]:
        q = select(AuditFinding).where(AuditFinding.audit_id == audit_id).order_by(AuditFinding.created_at)
        result = await self._db.execute(q)
        return list(result.scalars())


class ChecklistRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, **kwargs) -> AuditChecklist:
        items_data = kwargs.pop("items", [])
        obj = AuditChecklist(**kwargs)
        self._db.add(obj)
        await self._db.flush()

        for i, item in enumerate(items_data):
            checklist_item = AuditChecklistItem(
                id=item.get("id", __import__("uuid").uuid4().hex),
                checklist_id=obj.id,
                question=item["question"],
                iso_clause=item.get("iso_clause"),
                expected_evidence=item.get("expected_evidence"),
                sort_order=i,
            )
            self._db.add(checklist_item)
        await self._db.flush()
        await self._db.refresh(obj)
        return obj

    async def get(self, checklist_id: str, tenant_id: str) -> Optional[AuditChecklist]:
        q = (
            select(AuditChecklist)
            .where(AuditChecklist.id == checklist_id, AuditChecklist.tenant_id == tenant_id)
            .options(selectinload(AuditChecklist.items))
        )
        result = await self._db.execute(q)
        return result.scalar_one_or_none()

    async def list(self, tenant_id: str) -> list[AuditChecklist]:
        q = (
            select(AuditChecklist)
            .where(AuditChecklist.tenant_id == tenant_id, AuditChecklist.is_active.is_(True))
            .options(selectinload(AuditChecklist.items))
            .order_by(AuditChecklist.name)
        )
        result = await self._db.execute(q)
        return list(result.scalars())
