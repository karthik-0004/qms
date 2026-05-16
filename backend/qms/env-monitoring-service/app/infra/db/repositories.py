"""Env Monitoring Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import MonitoringPoint, MonitoringReading


class MonitoringPointRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, point_id: str) -> MonitoringPoint | None:
        result = await self._db.execute(
            select(MonitoringPoint).where(MonitoringPoint.id == point_id)
        )
        return result.scalar_one_or_none()

    async def list_points(
        self,
        tenant_id: str,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[MonitoringPoint], int]:
        query = select(MonitoringPoint).where(MonitoringPoint.tenant_id == tenant_id)
        count_q = select(func.count()).select_from(MonitoringPoint).where(
            MonitoringPoint.tenant_id == tenant_id
        )
        if status:
            query = query.where(MonitoringPoint.status == status)
            count_q = count_q.where(MonitoringPoint.status == status)

        query = query.offset(offset).limit(limit).order_by(MonitoringPoint.created_at.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(self, tenant_id: str, point_id: str, location: str,
                     parameter: str, frequency_type: str, created_by: str, **kwargs) -> MonitoringPoint:
        now = datetime.now(timezone.utc)
        point = MonitoringPoint(
            id=str(uuid4()), tenant_id=tenant_id, point_id=point_id,
            location=location, parameter=parameter, frequency_type=frequency_type,
            status="active", created_by=created_by, created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(point)
        await self._db.flush()
        return point

    async def update(self, point_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(MonitoringPoint).where(MonitoringPoint.id == point_id).values(**fields)
        )


class MonitoringReadingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, reading_id: str) -> MonitoringReading | None:
        result = await self._db.execute(
            select(MonitoringReading).where(MonitoringReading.id == reading_id)
        )
        return result.scalar_one_or_none()

    async def list_by_point(
        self,
        point_id: str,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[MonitoringReading]:
        query = select(MonitoringReading).where(MonitoringReading.point_id == point_id)
        if from_date:
            query = query.where(MonitoringReading.recorded_at >= from_date)
        if to_date:
            query = query.where(MonitoringReading.recorded_at <= to_date)
        query = query.order_by(MonitoringReading.recorded_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def list_excursions(self, point_id: str) -> list[MonitoringReading]:
        result = await self._db.execute(
            select(MonitoringReading).where(
                MonitoringReading.point_id == point_id,
                MonitoringReading.status != "within_limits",
            ).order_by(MonitoringReading.recorded_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, tenant_id: str, point_id: str, value: float,
                     recorded_at: datetime, status: str, **kwargs) -> MonitoringReading:
        now = datetime.now(timezone.utc)
        reading = MonitoringReading(
            id=str(uuid4()), tenant_id=tenant_id, point_id=point_id,
            value=value, recorded_at=recorded_at, status=status,
            created_at=now, **kwargs,
        )
        self._db.add(reading)
        await self._db.flush()
        return reading
