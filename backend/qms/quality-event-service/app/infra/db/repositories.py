"""Quality Event Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import QualityEvent


class QualityEventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, event_id: str) -> QualityEvent | None:
        result = await self._db.execute(
            select(QualityEvent).where(
                QualityEvent.id == event_id,
                QualityEvent.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_events(
        self,
        tenant_id: str,
        status: str | None = None,
        event_type: str | None = None,
        severity: str | None = None,
        assigned_to: str | None = None,
        department: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[QualityEvent], int]:
        query = select(QualityEvent).where(
            QualityEvent.tenant_id == tenant_id,
            QualityEvent.deleted_at.is_(None),
        )
        count_q = select(func.count()).select_from(QualityEvent).where(
            QualityEvent.tenant_id == tenant_id,
            QualityEvent.deleted_at.is_(None),
        )

        for col, val in [
            (QualityEvent.status, status),
            (QualityEvent.event_type, event_type),
            (QualityEvent.severity, severity),
            (QualityEvent.assigned_to, assigned_to),
            (QualityEvent.department, department),
        ]:
            if val:
                query = query.where(col == val)
                count_q = count_q.where(col == val)

        query = query.offset(offset).limit(limit).order_by(QualityEvent.detected_at.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(
        self,
        tenant_id: str,
        event_number: str,
        title: str,
        event_type: str,
        description: str,
        detected_at: datetime,
        created_by: str,
        **kwargs,
    ) -> QualityEvent:
        now = datetime.now(timezone.utc)
        event = QualityEvent(
            id=str(uuid4()),
            tenant_id=tenant_id,
            event_number=event_number,
            title=title,
            event_type=event_type,
            description=description,
            status="open",
            detected_at=detected_at,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            **kwargs,
        )
        self._db.add(event)
        await self._db.flush()
        return event

    async def update(self, event_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(QualityEvent).where(QualityEvent.id == event_id).values(**fields)
        )

    async def soft_delete(self, event_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(QualityEvent)
            .where(QualityEvent.id == event_id)
            .values(deleted_at=now, updated_at=now)
        )

    async def count_by_status(self, tenant_id: str) -> dict[str, int]:
        from sqlalchemy import case
        result = await self._db.execute(
            select(
                QualityEvent.status,
                func.count().label("count"),
            )
            .where(
                QualityEvent.tenant_id == tenant_id,
                QualityEvent.deleted_at.is_(None),
            )
            .group_by(QualityEvent.status)
        )
        return {row.status: row.count for row in result.fetchall()}
