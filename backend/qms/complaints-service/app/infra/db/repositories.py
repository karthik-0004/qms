"""Complaints Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Complaint


class ComplaintRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, complaint_id: str) -> Complaint | None:
        result = await self._db.execute(
            select(Complaint).where(Complaint.id == complaint_id, Complaint.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_complaints(
        self,
        tenant_id: str,
        status: str | None = None,
        severity: str | None = None,
        category: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Complaint], int]:
        query = select(Complaint).where(Complaint.tenant_id == tenant_id, Complaint.deleted_at.is_(None))
        count_q = select(func.count()).select_from(Complaint).where(
            Complaint.tenant_id == tenant_id, Complaint.deleted_at.is_(None)
        )
        for col, val in [(Complaint.status, status), (Complaint.severity, severity),
                         (Complaint.category, category)]:
            if val:
                query = query.where(col == val)
                count_q = count_q.where(col == val)

        query = query.offset(offset).limit(limit).order_by(Complaint.received_at.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(self, tenant_id: str, complaint_number: str, description: str,
                     received_at: datetime, created_by: str, **kwargs) -> Complaint:
        now = datetime.now(timezone.utc)
        complaint = Complaint(
            id=str(uuid4()), tenant_id=tenant_id, complaint_number=complaint_number,
            description=description, received_at=received_at, status="open",
            created_by=created_by, created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(complaint)
        await self._db.flush()
        return complaint

    async def update(self, complaint_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(Complaint).where(Complaint.id == complaint_id).values(**fields)
        )

    async def soft_delete(self, complaint_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(Complaint).where(Complaint.id == complaint_id).values(
                deleted_at=now, updated_at=now, status="withdrawn"
            )
        )
