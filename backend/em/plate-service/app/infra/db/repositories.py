"""Plate Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Plate, PlateStatusHistory


class PlateRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, plate_id: str) -> Plate | None:
        result = await self._db.execute(
            select(Plate).where(Plate.id == plate_id, Plate.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_barcode(self, tenant_id: str, barcode: str) -> Plate | None:
        result = await self._db.execute(
            select(Plate).where(
                Plate.tenant_id == tenant_id,
                Plate.barcode == barcode,
                Plate.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_plates(
        self,
        tenant_id: str,
        status: str | None = None,
        sample_type: str | None = None,
        operator_id: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Plate], int]:
        query = select(Plate).where(Plate.tenant_id == tenant_id, Plate.deleted_at.is_(None))
        count_q = select(func.count()).select_from(Plate).where(
            Plate.tenant_id == tenant_id, Plate.deleted_at.is_(None)
        )
        if status:
            query = query.where(Plate.status == status)
            count_q = count_q.where(Plate.status == status)
        if sample_type:
            query = query.where(Plate.sample_type == sample_type)
            count_q = count_q.where(Plate.sample_type == sample_type)
        if operator_id:
            query = query.where(Plate.operator_id == operator_id)
            count_q = count_q.where(Plate.operator_id == operator_id)

        query = query.offset(offset).limit(limit).order_by(Plate.created_at.desc())
        items = list((await self._db.execute(query)).scalars().all())
        total = (await self._db.execute(count_q)).scalar_one()
        return items, total

    async def create(self, tenant_id: str, barcode: str, sample_type: str,
                     media_type: str, created_by: str, **kwargs) -> Plate:
        now = datetime.now(timezone.utc)
        plate = Plate(
            id=str(uuid4()), tenant_id=tenant_id, barcode=barcode,
            sample_type=sample_type, media_type=media_type,
            created_by=created_by, operator_id=created_by,
            status="registered", created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(plate)
        await self._db.flush()
        return plate

    async def update(self, plate_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(update(Plate).where(Plate.id == plate_id).values(**fields))

    async def soft_delete(self, plate_id: str) -> None:
        await self.update(plate_id, deleted_at=datetime.now(timezone.utc))


class PlateStatusHistoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def record(self, plate_id: str, tenant_id: str, to_status: str,
                     changed_by: str, from_status: str | None = None,
                     reason: str | None = None) -> PlateStatusHistory:
        entry = PlateStatusHistory(
            id=str(uuid4()), plate_id=plate_id, tenant_id=tenant_id,
            from_status=from_status, to_status=to_status,
            changed_by=changed_by, reason=reason,
            changed_at=datetime.now(timezone.utc),
        )
        self._db.add(entry)
        await self._db.flush()
        return entry

    async def list_by_plate(self, plate_id: str) -> list[PlateStatusHistory]:
        result = await self._db.execute(
            select(PlateStatusHistory)
            .where(PlateStatusHistory.plate_id == plate_id)
            .order_by(PlateStatusHistory.changed_at.asc())
        )
        return list(result.scalars().all())
