"""Equipment Service — Core equipment management domain service."""

from datetime import datetime, timedelta, timezone

import structlog

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError

from ..infra.db.models import CalibrationRecord, Equipment
from ..infra.db.repositories import EquipmentRepository

logger = structlog.get_logger(__name__)


class EquipmentDomainService:
    """Equipment asset management: tracking, calibration, and maintenance scheduling."""

    def __init__(self, repo: EquipmentRepository, tenant_id: str) -> None:
        self._repo = repo
        self._tenant_id = tenant_id

    async def create_equipment(
        self,
        asset_tag: str,
        name: str,
        equipment_type: str,
        created_by: str,
        **kwargs,
    ) -> Equipment:
        existing = await self._repo.get_by_asset_tag(self._tenant_id, asset_tag)
        if existing:
            raise ConflictError(f"Equipment with asset tag '{asset_tag}' already exists")

        equipment = await self._repo.create(
            tenant_id=self._tenant_id,
            asset_tag=asset_tag,
            name=name,
            equipment_type=equipment_type,
            created_by=created_by,
            **kwargs,
        )

        # Auto-calculate next calibration/PM dates
        if equipment.calibration_frequency_days:
            next_cal = datetime.now(timezone.utc) + timedelta(days=equipment.calibration_frequency_days)
            await self._repo.update(equipment.id, next_calibration_date=next_cal)

        logger.info("equipment_created", equipment_id=equipment.id, asset_tag=asset_tag)
        return await self._repo.get_by_id(equipment.id)

    async def get_equipment(self, equipment_id: str) -> Equipment:
        equipment = await self._repo.get_by_id(equipment_id)
        if not equipment:
            raise NotFoundError("Equipment", equipment_id)
        if equipment.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this equipment record")
        return equipment

    async def list_equipment(
        self,
        status: str | None = None,
        equipment_type: str | None = None,
        department: str | None = None,
        requires_calibration: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Equipment], int]:
        return await self._repo.list_equipment(
            tenant_id=self._tenant_id,
            status=status,
            equipment_type=equipment_type,
            department=department,
            requires_calibration=requires_calibration,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def update_equipment(self, equipment_id: str, updated_by: str, **fields) -> Equipment:
        await self.get_equipment(equipment_id)
        allowed = {"name", "description", "location", "department", "status",
                   "manufacturer", "model", "serial_number", "assigned_to",
                   "notes", "tags", "warranty_expiry"}
        filtered = {k: v for k, v in fields.items() if k in allowed}
        if filtered:
            await self._repo.update(equipment_id, **filtered)
        return await self.get_equipment(equipment_id)

    async def record_calibration(
        self,
        equipment_id: str,
        calibrated_by: str,
        calibration_date: datetime,
        passed: bool,
        certificate_file_id: str | None = None,
        notes: str | None = None,
    ) -> Equipment:
        equipment = await self.get_equipment(equipment_id)
        if not equipment.requires_calibration:
            raise ConflictError("Equipment does not require calibration")

        next_cal = None
        if passed and equipment.calibration_frequency_days:
            next_cal = calibration_date + timedelta(days=equipment.calibration_frequency_days)

        new_status = "active" if passed else "out_of_calibration"
        await self._repo.update(
            equipment_id,
            last_calibration_date=calibration_date,
            next_calibration_date=next_cal,
            status=new_status,
        )

        await self._repo.create_calibration_record(
            equipment_id=equipment_id,
            tenant_id=self._tenant_id,
            calibration_date=calibration_date,
            performed_by=calibrated_by,
            passed=passed,
            result="pass" if passed else "fail",
            notes=notes,
            next_due_date=next_cal,
            certificate_file_id=certificate_file_id,
        )

        logger.info("equipment_calibrated", equipment_id=equipment_id, passed=passed)
        return await self.get_equipment(equipment_id)

    async def list_calibration_records(self, equipment_id: str) -> list[CalibrationRecord]:
        await self.get_equipment(equipment_id)
        return await self._repo.list_calibration_records(
            equipment_id=equipment_id, tenant_id=self._tenant_id
        )

    async def get_due_for_calibration(self, days_ahead: int = 30) -> list[Equipment]:
        return await self._repo.get_due_for_calibration(self._tenant_id, days_ahead)

    async def decommission(self, equipment_id: str, decommissioned_by: str, reason: str) -> Equipment:
        await self.get_equipment(equipment_id)
        await self._repo.update(equipment_id, status="decommissioned")
        logger.info("equipment_decommissioned", equipment_id=equipment_id, by=decommissioned_by)
        return await self.get_equipment(equipment_id)

    async def delete_equipment(self, equipment_id: str, deleted_by: str) -> None:
        equipment = await self.get_equipment(equipment_id)
        if equipment.status == "active":
            raise ConflictError("Cannot delete active equipment. Decommission it first.")
        await self._repo.soft_delete(equipment_id)
