"""Schedule Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Schedule, ScheduleEvent


class ScheduleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, schedule_id: str) -> Schedule | None:
        result = await self._db.execute(
            select(Schedule).where(
                Schedule.id == schedule_id,
                Schedule.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_schedules(
        self,
        tenant_id: str,
        entity_type: str | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Schedule], int]:
        query = select(Schedule).where(
            Schedule.tenant_id == tenant_id,
            Schedule.deleted_at.is_(None),
        )
        count_q = select(func.count()).select_from(Schedule).where(
            Schedule.tenant_id == tenant_id,
            Schedule.deleted_at.is_(None),
        )
        if entity_type:
            query = query.where(Schedule.entity_type == entity_type)
            count_q = count_q.where(Schedule.entity_type == entity_type)
        if is_active is not None:
            query = query.where(Schedule.is_active == is_active)
            count_q = count_q.where(Schedule.is_active == is_active)

        query = query.offset(offset).limit(limit).order_by(Schedule.next_occurrence.asc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def get_upcoming(self, tenant_id: str, threshold: datetime) -> list[Schedule]:
        result = await self._db.execute(
            select(Schedule).where(
                Schedule.tenant_id == tenant_id,
                Schedule.is_active.is_(True),
                Schedule.next_occurrence.is_not(None),
                Schedule.next_occurrence <= threshold,
                Schedule.deleted_at.is_(None),
            ).order_by(Schedule.next_occurrence.asc())
        )
        return list(result.scalars().all())

    async def create(
        self, tenant_id: str, name: str, entity_type: str, recurrence_rule: str,
        created_by: str, **kwargs
    ) -> Schedule:
        now = datetime.now(timezone.utc)
        schedule = Schedule(
            id=str(uuid4()), tenant_id=tenant_id, name=name, entity_type=entity_type,
            recurrence_rule=recurrence_rule, created_by=created_by, is_active=True,
            created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(schedule)
        await self._db.flush()
        return schedule

    async def update(self, schedule_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(Schedule).where(Schedule.id == schedule_id).values(**fields)
        )


class ScheduleEventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, event_id: str) -> ScheduleEvent | None:
        result = await self._db.execute(
            select(ScheduleEvent).where(ScheduleEvent.id == event_id)
        )
        return result.scalar_one_or_none()

    async def list_by_schedule(
        self, schedule_id: str, status: str | None = None
    ) -> list[ScheduleEvent]:
        query = select(ScheduleEvent).where(ScheduleEvent.schedule_id == schedule_id)
        if status:
            query = query.where(ScheduleEvent.status == status)
        result = await self._db.execute(
            query.order_by(ScheduleEvent.scheduled_at.asc())
        )
        return list(result.scalars().all())

    async def create(
        self, schedule_id: str, tenant_id: str, scheduled_at: datetime
    ) -> ScheduleEvent:
        event = ScheduleEvent(
            id=str(uuid4()), schedule_id=schedule_id, tenant_id=tenant_id,
            scheduled_at=scheduled_at, status="pending",
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(event)
        await self._db.flush()
        return event

    async def acknowledge(
        self, event_id: str, acknowledged_by: str, notes: str | None = None
    ) -> None:
        await self._db.execute(
            update(ScheduleEvent)
            .where(ScheduleEvent.id == event_id)
            .values(
                status="acknowledged",
                acknowledged_at=datetime.now(timezone.utc),
                acknowledged_by=acknowledged_by,
                notes=notes,
            )
        )
