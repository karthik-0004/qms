"""Unit tests — ScheduleDomainService business logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from rainer_common.exceptions import ForbiddenError, NotFoundError

from app.domain.services import ScheduleDomainService, RECURRENCE_INTERVALS
from app.infra.db.models import Schedule, ScheduleEvent


def make_schedule(**kwargs) -> Schedule:
    defaults = dict(
        id=str(uuid4()), tenant_id="tenant-1", name="Monthly Review",
        description=None, entity_type="document", entity_id=str(uuid4()),
        recurrence_rule="monthly", is_active=True, advance_notice_days=7,
        owner_id=str(uuid4()), metadata_={}, next_occurrence=None, last_occurrence=None,
        created_by=str(uuid4()), deleted_at=None,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    s = MagicMock(spec=Schedule)
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


@pytest.fixture
def schedule_repo():
    return AsyncMock()


@pytest.fixture
def event_repo():
    return AsyncMock()


@pytest.fixture
def svc(schedule_repo, event_repo):
    return ScheduleDomainService(
        schedule_repo=schedule_repo,
        event_repo=event_repo,
        tenant_id="tenant-1",
    )


class TestCreateSchedule:
    @pytest.mark.asyncio
    async def test_creates_schedule_with_monthly_recurrence(self, svc, schedule_repo):
        mock_schedule = make_schedule()
        schedule_repo.create.return_value = mock_schedule
        result = await svc.create_schedule(
            name="Monthly Document Review",
            entity_type="document",
            recurrence_rule="monthly",
            created_by=str(uuid4()),
        )
        assert result is mock_schedule
        schedule_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_schedule_with_custom_recurrence(self, svc, schedule_repo):
        mock_schedule = make_schedule(recurrence_rule="custom:90_days")
        schedule_repo.create.return_value = mock_schedule
        result = await svc.create_schedule(
            name="90-Day Review",
            entity_type="equipment",
            recurrence_rule="custom:90_days",
            created_by=str(uuid4()),
        )
        assert result is mock_schedule

    @pytest.mark.asyncio
    async def test_raises_on_invalid_recurrence_rule(self, svc):
        with pytest.raises(ValueError, match="Invalid recurrence_rule"):
            await svc.create_schedule(
                name="Bad Schedule", entity_type="doc",
                recurrence_rule="invalid_rule", created_by=str(uuid4()),
            )

    def test_all_standard_recurrence_rules_valid(self):
        assert "daily" in RECURRENCE_INTERVALS
        assert "weekly" in RECURRENCE_INTERVALS
        assert "monthly" in RECURRENCE_INTERVALS
        assert "annual" in RECURRENCE_INTERVALS


class TestGetSchedule:
    @pytest.mark.asyncio
    async def test_returns_schedule(self, svc, schedule_repo):
        schedule = make_schedule()
        schedule_repo.get_by_id.return_value = schedule
        result = await svc.get_schedule(schedule.id)
        assert result is schedule

    @pytest.mark.asyncio
    async def test_raises_not_found(self, svc, schedule_repo):
        schedule_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await svc.get_schedule("nonexistent")

    @pytest.mark.asyncio
    async def test_raises_forbidden_for_wrong_tenant(self, svc, schedule_repo):
        schedule = make_schedule(tenant_id="other-tenant")
        schedule_repo.get_by_id.return_value = schedule
        with pytest.raises(ForbiddenError):
            await svc.get_schedule(schedule.id)


class TestCalculateNextOccurrence:
    def test_calculates_monthly_occurrence(self, svc):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        result = svc._calculate_next_occurrence("monthly", start)
        assert result > start

    def test_calculates_custom_occurrence(self, svc):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        result = svc._calculate_next_occurrence("custom:90_days", start)
        from datetime import timedelta
        expected = start + timedelta(days=90)
        assert result == expected

    def test_calculates_annual_occurrence(self, svc):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        result = svc._calculate_next_occurrence("annual", start)
        from datetime import timedelta
        expected = start + timedelta(days=365)
        assert result == expected


class TestDeactivateSchedule:
    @pytest.mark.asyncio
    async def test_deactivates_schedule(self, svc, schedule_repo):
        schedule = make_schedule(is_active=True)
        deactivated = make_schedule(is_active=False)
        schedule_repo.get_by_id.side_effect = [schedule, deactivated]
        schedule_repo.update.return_value = None

        result = await svc.deactivate_schedule(schedule.id)
        schedule_repo.update.assert_called_once_with(schedule.id, is_active=False)
