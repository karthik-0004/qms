"""Plate Service — Domain service layer."""

from datetime import datetime, timezone
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from ..infra.db.repositories import PlateRepository, PlateStatusHistoryRepository
from ..infra.db.models import Plate

logger = structlog.get_logger(__name__)

VALID_TRANSITIONS: dict[str, list[str]] = {
    "registered": ["sampling_in_progress", "cancelled"],
    "sampling_in_progress": ["sampled", "cancelled"],
    "sampled": ["incubation_started", "cancelled"],
    "incubation_started": ["incubation_complete", "cancelled"],
    "incubation_complete": ["imaging_pending"],
    "imaging_pending": ["imaging_in_progress", "cancelled"],
    "imaging_in_progress": ["imaging_complete", "cancelled"],
    "imaging_complete": ["ai_analysis_pending"],
    "ai_analysis_pending": ["ai_analysis_running"],
    "ai_analysis_running": ["ai_analysis_complete", "ai_analysis_failed"],
    "ai_analysis_failed": ["ai_analysis_pending", "cancelled"],
    "ai_analysis_complete": ["qa_review_pending"],
    "qa_review_pending": ["qa_review_in_progress"],
    "qa_review_in_progress": ["approved", "rejected", "on_hold"],
    "on_hold": ["qa_review_in_progress", "cancelled"],
    "approved": [],
    "rejected": [],
    "cancelled": [],
}


class PlateServiceError(Exception):
    pass


class PlateNotFoundError(PlateServiceError):
    pass


class InvalidStatusTransitionError(PlateServiceError):
    pass


class DuplicateBarcodeError(PlateServiceError):
    pass


class PlateDomainService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = PlateRepository(db)
        self._history_repo = PlateStatusHistoryRepository(db)

    async def register_plate(
        self,
        tenant_id: str,
        barcode: str,
        sample_type: str,
        media_type: str,
        created_by: str,
        location_code: str | None = None,
        lot_number: str | None = None,
        notes: str | None = None,
        incubation_temp_celsius: float | None = None,
        incubation_hours: int | None = None,
        metadata: dict | None = None,
    ) -> Plate:
        existing = await self._repo.get_by_barcode(tenant_id, barcode)
        if existing:
            raise DuplicateBarcodeError(f"Barcode '{barcode}' already registered for this tenant.")

        plate = await self._repo.create(
            tenant_id=tenant_id,
            barcode=barcode,
            sample_type=sample_type,
            media_type=media_type,
            created_by=created_by,
            location_code=location_code,
            lot_number=lot_number,
            notes=notes,
            incubation_temp_celsius=incubation_temp_celsius,
            incubation_hours=incubation_hours,
            metadata_=metadata or {},
        )
        await self._history_repo.record(
            plate_id=plate.id,
            tenant_id=tenant_id,
            from_status=None,
            to_status="registered",
            changed_by=created_by,
        )
        logger.info("plate.registered", plate_id=plate.id, barcode=barcode, tenant_id=tenant_id)
        return plate

    async def get_plate(self, plate_id: str) -> Plate:
        plate = await self._repo.get_by_id(plate_id)
        if not plate:
            raise PlateNotFoundError(f"Plate '{plate_id}' not found.")
        return plate

    async def list_plates(
        self,
        tenant_id: str,
        status: str | None = None,
        sample_type: str | None = None,
        operator_id: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Plate], int]:
        return await self._repo.list_plates(
            tenant_id=tenant_id,
            status=status,
            sample_type=sample_type,
            operator_id=operator_id,
            offset=offset,
            limit=limit,
        )

    async def transition_status(
        self,
        plate_id: str,
        tenant_id: str,
        new_status: str,
        changed_by: str,
        reason: str | None = None,
        **extra_fields: Any,
    ) -> Plate:
        plate = await self.get_plate(plate_id)
        if plate.tenant_id != tenant_id:
            raise PlateNotFoundError(f"Plate '{plate_id}' not found.")

        allowed = VALID_TRANSITIONS.get(plate.status, [])
        if new_status not in allowed:
            raise InvalidStatusTransitionError(
                f"Cannot transition plate from '{plate.status}' to '{new_status}'."
            )

        update_fields: dict[str, Any] = {"status": new_status, **extra_fields}
        if new_status == "sampled":
            update_fields["sampled_at"] = datetime.now(timezone.utc)
        elif new_status == "incubation_started":
            update_fields["incubation_started_at"] = datetime.now(timezone.utc)
        elif new_status == "incubation_complete":
            update_fields["incubation_completed_at"] = datetime.now(timezone.utc)

        from_status = plate.status
        await self._repo.update(plate_id, **update_fields)
        await self._history_repo.record(
            plate_id=plate_id,
            tenant_id=tenant_id,
            from_status=from_status,
            to_status=new_status,
            changed_by=changed_by,
            reason=reason,
        )
        logger.info(
            "plate.status_changed",
            plate_id=plate_id,
            from_status=from_status,
            to_status=new_status,
        )
        return await self.get_plate(plate_id)

    async def update_plate(
        self,
        plate_id: str,
        tenant_id: str,
        updated_by: str,
        **fields: Any,
    ) -> Plate:
        plate = await self.get_plate(plate_id)
        if plate.tenant_id != tenant_id:
            raise PlateNotFoundError(f"Plate '{plate_id}' not found.")
        await self._repo.update(plate_id, **fields)
        return await self.get_plate(plate_id)

    async def get_history(self, plate_id: str) -> list:
        return await self._history_repo.list_by_plate(plate_id)
