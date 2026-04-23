"""Unit tests — PlateDomainService."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domain.services import (
    DuplicateBarcodeError,
    InvalidStatusTransitionError,
    PlateDomainService,
    PlateNotFoundError,
)
from app.infra.db.models import Plate, PlateStatusHistory


def _make_plate(**kwargs) -> Plate:
    defaults = dict(
        id=str(uuid4()),
        tenant_id=str(uuid4()),
        barcode="PLATE-001",
        sample_type="settle_plate",
        media_type="TSA",
        operator_id=str(uuid4()),
        status="registered",
        metadata_={},
        created_by=str(uuid4()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted_at=None,
    )
    defaults.update(kwargs)
    return MagicMock(spec=Plate, **defaults)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def service(mock_db):
    svc = PlateDomainService(mock_db)
    svc._repo = AsyncMock()
    svc._history_repo = AsyncMock()
    return svc


# ─── register_plate ──────────────────────────────────────────────────────────

class TestRegisterPlate:
    async def test_registers_successfully(self, service):
        service._repo.get_by_barcode.return_value = None
        plate = _make_plate(barcode="PLATE-001")
        service._repo.create.return_value = plate

        result = await service.register_plate(
            tenant_id=plate.tenant_id,
            barcode="PLATE-001",
            sample_type="settle_plate",
            media_type="TSA",
            created_by=plate.created_by,
        )

        assert result.barcode == "PLATE-001"
        service._history_repo.record.assert_awaited_once()

    async def test_raises_on_duplicate_barcode(self, service):
        existing = _make_plate()
        service._repo.get_by_barcode.return_value = existing

        with pytest.raises(DuplicateBarcodeError):
            await service.register_plate(
                tenant_id=existing.tenant_id,
                barcode="PLATE-001",
                sample_type="settle_plate",
                media_type="TSA",
                created_by=str(uuid4()),
            )


# ─── get_plate ────────────────────────────────────────────────────────────────

class TestGetPlate:
    async def test_returns_existing_plate(self, service):
        plate = _make_plate()
        service._repo.get_by_id.return_value = plate

        result = await service.get_plate(plate.id)
        assert result.id == plate.id

    async def test_raises_if_not_found(self, service):
        service._repo.get_by_id.return_value = None

        with pytest.raises(PlateNotFoundError):
            await service.get_plate(str(uuid4()))


# ─── list_plates ──────────────────────────────────────────────────────────────

class TestListPlates:
    async def test_returns_paginated_list(self, service):
        plates = [_make_plate() for _ in range(3)]
        service._repo.list_plates.return_value = (plates, 3)
        tenant_id = str(uuid4())

        items, total = await service.list_plates(tenant_id=tenant_id)

        assert len(items) == 3
        assert total == 3


# ─── transition_status ────────────────────────────────────────────────────────

class TestTransitionStatus:
    async def test_valid_transition_registered_to_sampling(self, service):
        tenant_id = str(uuid4())
        plate = _make_plate(tenant_id=tenant_id, status="registered")
        updated = _make_plate(tenant_id=tenant_id, status="sampling_in_progress")
        service._repo.get_by_id.side_effect = [plate, updated]

        result = await service.transition_status(
            plate_id=plate.id,
            tenant_id=tenant_id,
            new_status="sampling_in_progress",
            changed_by=str(uuid4()),
        )

        assert result.status == "sampling_in_progress"
        service._repo.update.assert_awaited_once()
        service._history_repo.record.assert_awaited_once()

    async def test_invalid_transition_raises(self, service):
        tenant_id = str(uuid4())
        plate = _make_plate(tenant_id=tenant_id, status="approved")
        service._repo.get_by_id.return_value = plate

        with pytest.raises(InvalidStatusTransitionError):
            await service.transition_status(
                plate_id=plate.id,
                tenant_id=tenant_id,
                new_status="registered",
                changed_by=str(uuid4()),
            )

    async def test_cross_tenant_raises_not_found(self, service):
        plate = _make_plate(tenant_id=str(uuid4()), status="registered")
        service._repo.get_by_id.return_value = plate

        with pytest.raises(PlateNotFoundError):
            await service.transition_status(
                plate_id=plate.id,
                tenant_id=str(uuid4()),  # different tenant
                new_status="sampling_in_progress",
                changed_by=str(uuid4()),
            )

    async def test_sampled_sets_sampled_at(self, service):
        tenant_id = str(uuid4())
        plate = _make_plate(tenant_id=tenant_id, status="sampling_in_progress")
        updated = _make_plate(tenant_id=tenant_id, status="sampled")
        service._repo.get_by_id.side_effect = [plate, updated]

        await service.transition_status(
            plate_id=plate.id,
            tenant_id=tenant_id,
            new_status="sampled",
            changed_by=str(uuid4()),
        )

        call_kwargs = service._repo.update.call_args.kwargs
        assert "sampled_at" in call_kwargs


# ─── get_history ──────────────────────────────────────────────────────────────

class TestGetHistory:
    async def test_returns_history(self, service):
        entries = [MagicMock(spec=PlateStatusHistory) for _ in range(3)]
        service._history_repo.list_by_plate.return_value = entries

        result = await service.get_history(str(uuid4()))

        assert len(result) == 3
