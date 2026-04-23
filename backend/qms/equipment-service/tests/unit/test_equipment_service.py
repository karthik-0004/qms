"""Unit tests — EquipmentDomainService business logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError

from app.domain.services import EquipmentDomainService
from app.infra.db.models import Equipment


def make_equipment(**kwargs) -> Equipment:
    defaults = dict(
        id=str(uuid4()), tenant_id="tenant-1", asset_tag="EQ-001",
        name="pH Meter", description=None, equipment_type="analytical",
        manufacturer="Mettler Toledo", model="SevenCompact", serial_number="SN123",
        location="Lab A", department="QC", status="active",
        requires_calibration=True, calibration_frequency_days=365,
        last_calibration_date=None, next_calibration_date=None,
        requires_pm=False, pm_frequency_days=None,
        last_pm_date=None, next_pm_date=None,
        purchase_date=None, warranty_expiry=None, assigned_to=None,
        notes=None, tags=[], metadata_={},
        created_by=str(uuid4()), deleted_at=None,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    e = MagicMock(spec=Equipment)
    for k, v in defaults.items():
        setattr(e, k, v)
    return e


@pytest.fixture
def repo():
    return AsyncMock()


@pytest.fixture
def svc(repo):
    return EquipmentDomainService(repo=repo, tenant_id="tenant-1")


class TestCreateEquipment:
    @pytest.mark.asyncio
    async def test_creates_equipment(self, svc, repo):
        repo.get_by_asset_tag.return_value = None
        mock_eq = make_equipment()
        repo.create.return_value = mock_eq
        repo.get_by_id.return_value = mock_eq
        repo.update.return_value = None

        result = await svc.create_equipment(
            asset_tag="EQ-001", name="pH Meter",
            equipment_type="analytical", created_by=str(uuid4()),
        )
        assert result is mock_eq

    @pytest.mark.asyncio
    async def test_raises_conflict_if_asset_tag_exists(self, svc, repo):
        repo.get_by_asset_tag.return_value = make_equipment()
        with pytest.raises(ConflictError):
            await svc.create_equipment("EQ-001", "pH Meter", "analytical", str(uuid4()))


class TestGetEquipment:
    @pytest.mark.asyncio
    async def test_returns_equipment(self, svc, repo):
        eq = make_equipment()
        repo.get_by_id.return_value = eq
        result = await svc.get_equipment(eq.id)
        assert result is eq

    @pytest.mark.asyncio
    async def test_raises_not_found(self, svc, repo):
        repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await svc.get_equipment("nonexistent")

    @pytest.mark.asyncio
    async def test_raises_forbidden_for_wrong_tenant(self, svc, repo):
        eq = make_equipment(tenant_id="other-tenant")
        repo.get_by_id.return_value = eq
        with pytest.raises(ForbiddenError):
            await svc.get_equipment(eq.id)


class TestRecordCalibration:
    @pytest.mark.asyncio
    async def test_records_passed_calibration(self, svc, repo):
        eq = make_equipment(requires_calibration=True, calibration_frequency_days=365)
        repo.get_by_id.side_effect = [eq, make_equipment(status="active")]
        repo.update.return_value = None

        cal_date = datetime.now(timezone.utc)
        result = await svc.record_calibration(eq.id, str(uuid4()), cal_date, passed=True)
        repo.update.assert_called()

    @pytest.mark.asyncio
    async def test_records_failed_calibration_sets_out_of_calibration(self, svc, repo):
        eq = make_equipment(requires_calibration=True, calibration_frequency_days=365)
        out_of_cal = make_equipment(status="out_of_calibration")
        repo.get_by_id.side_effect = [eq, out_of_cal]
        repo.update.return_value = None

        cal_date = datetime.now(timezone.utc)
        result = await svc.record_calibration(eq.id, str(uuid4()), cal_date, passed=False)
        call_kwargs = repo.update.call_args.kwargs
        assert call_kwargs.get("status") == "out_of_calibration"

    @pytest.mark.asyncio
    async def test_raises_if_calibration_not_required(self, svc, repo):
        eq = make_equipment(requires_calibration=False)
        repo.get_by_id.return_value = eq
        with pytest.raises(ConflictError, match="not require calibration"):
            await svc.record_calibration(eq.id, str(uuid4()), datetime.now(timezone.utc), True)


class TestDecommission:
    @pytest.mark.asyncio
    async def test_decommissions_equipment(self, svc, repo):
        eq = make_equipment(status="active")
        repo.get_by_id.side_effect = [eq, make_equipment(status="decommissioned")]
        repo.update.return_value = None

        result = await svc.decommission(eq.id, str(uuid4()), "End of life")
        call_kwargs = repo.update.call_args.kwargs
        assert call_kwargs.get("status") == "decommissioned"


class TestDeleteEquipment:
    @pytest.mark.asyncio
    async def test_raises_if_still_active(self, svc, repo):
        eq = make_equipment(status="active")
        repo.get_by_id.return_value = eq
        with pytest.raises(ConflictError):
            await svc.delete_equipment(eq.id, str(uuid4()))

    @pytest.mark.asyncio
    async def test_deletes_decommissioned_equipment(self, svc, repo):
        eq = make_equipment(status="decommissioned")
        repo.get_by_id.return_value = eq
        repo.soft_delete.return_value = None
        await svc.delete_equipment(eq.id, str(uuid4()))
        repo.soft_delete.assert_called_with(eq.id)
