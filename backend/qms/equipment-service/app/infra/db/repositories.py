"""Equipment Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import CalibrationRecord, Equipment


class EquipmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, equipment_id: str) -> Equipment | None:
        result = await self._db.execute(
            select(Equipment).where(
                Equipment.id == equipment_id,
                Equipment.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_asset_tag(self, tenant_id: str, asset_tag: str) -> Equipment | None:
        result = await self._db.execute(
            select(Equipment).where(
                Equipment.tenant_id == tenant_id,
                Equipment.asset_tag == asset_tag,
                Equipment.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_equipment(
        self,
        tenant_id: str,
        status: str | None = None,
        equipment_type: str | None = None,
        department: str | None = None,
        requires_calibration: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Equipment], int]:
        query = select(Equipment).where(
            Equipment.tenant_id == tenant_id,
            Equipment.deleted_at.is_(None),
        )
        count_q = select(func.count()).select_from(Equipment).where(
            Equipment.tenant_id == tenant_id,
            Equipment.deleted_at.is_(None),
        )

        for col, val in [
            (Equipment.status, status),
            (Equipment.equipment_type, equipment_type),
            (Equipment.department, department),
        ]:
            if val:
                query = query.where(col == val)
                count_q = count_q.where(col == val)

        if requires_calibration is not None:
            query = query.where(Equipment.requires_calibration == requires_calibration)
            count_q = count_q.where(Equipment.requires_calibration == requires_calibration)

        query = query.offset(offset).limit(limit).order_by(Equipment.name.asc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(
        self, tenant_id: str, asset_tag: str, name: str, equipment_type: str,
        created_by: str, **kwargs
    ) -> Equipment:
        now = datetime.now(timezone.utc)
        equipment = Equipment(
            id=str(uuid4()), tenant_id=tenant_id, asset_tag=asset_tag,
            name=name, equipment_type=equipment_type, status="active",
            created_by=created_by, created_at=now, updated_at=now,
            **kwargs,
        )
        self._db.add(equipment)
        await self._db.flush()
        return equipment

    async def update(self, equipment_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(Equipment).where(Equipment.id == equipment_id).values(**fields)
        )

    async def soft_delete(self, equipment_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(Equipment)
            .where(Equipment.id == equipment_id)
            .values(deleted_at=now, updated_at=now)
        )

    async def get_due_for_calibration(
        self, tenant_id: str, days_ahead: int = 30
    ) -> list[Equipment]:
        threshold = datetime.now(timezone.utc) + timedelta(days=days_ahead)
        result = await self._db.execute(
            select(Equipment).where(
                Equipment.tenant_id == tenant_id,
                Equipment.requires_calibration.is_(True),
                Equipment.next_calibration_date.is_not(None),
                Equipment.next_calibration_date <= threshold,
                Equipment.status == "active",
                Equipment.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def create_calibration_record(
        self,
        equipment_id: str,
        tenant_id: str,
        calibration_date: datetime,
        performed_by: str,
        passed: bool,
        result: str,
        standards_used: str | None = None,
        as_found_readings: str | None = None,
        as_left_readings: str | None = None,
        measurement_uncertainty: str | None = None,
        notes: str | None = None,
        next_due_date: datetime | None = None,
        certificate_file_id: str | None = None,
    ) -> CalibrationRecord:
        now = datetime.now(timezone.utc)
        record = CalibrationRecord(
            id=str(uuid4()),
            equipment_id=equipment_id,
            tenant_id=tenant_id,
            calibration_date=calibration_date,
            performed_by=performed_by,
            passed=passed,
            result=result,
            standards_used=standards_used,
            as_found_readings=as_found_readings,
            as_left_readings=as_left_readings,
            measurement_uncertainty=measurement_uncertainty,
            notes=notes,
            next_due_date=next_due_date,
            certificate_file_id=certificate_file_id,
            created_at=now,
        )
        self._db.add(record)
        await self._db.flush()
        return record

    async def list_calibration_records(
        self, equipment_id: str, tenant_id: str
    ) -> list[CalibrationRecord]:
        result = await self._db.execute(
            select(CalibrationRecord).where(
                CalibrationRecord.equipment_id == equipment_id,
                CalibrationRecord.tenant_id == tenant_id,
            ).order_by(CalibrationRecord.calibration_date.desc())
        )
        return list(result.scalars().all())
