"""Unit tests — QualityEventDomainService business logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from rainer_common.exceptions import ForbiddenError, NotFoundError

from app.domain.services import QualityEventDomainService
from app.infra.db.models import QualityEvent


def make_event(**kwargs) -> QualityEvent:
    defaults = dict(
        id=str(uuid4()), tenant_id="tenant-1", event_number="QE-001",
        title="Test Quality Event", event_type="deviation",
        description="Something went wrong", status="open", severity="minor",
        priority="medium", department="QA", location=None,
        detected_at=datetime.now(timezone.utc),
        detected_by=str(uuid4()), assigned_to=str(uuid4()),
        root_cause=None, immediate_action=None,
        capa_required=False, capa_id=None, due_date=None, closed_at=None,
        tags=[], attachments=[], metadata_={},
        created_by=str(uuid4()), deleted_at=None,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    e = MagicMock(spec=QualityEvent)
    for k, v in defaults.items():
        setattr(e, k, v)
    return e


@pytest.fixture
def repo():
    return AsyncMock()


@pytest.fixture
def svc(repo):
    return QualityEventDomainService(repo=repo, tenant_id="tenant-1")


class TestCreateEvent:
    @pytest.mark.asyncio
    async def test_creates_event(self, svc, repo):
        mock_event = make_event()
        repo.create.return_value = mock_event
        result = await svc.create_event(
            event_number="QE-001",
            title="Test Event",
            event_type="deviation",
            description="Something happened",
            detected_at=datetime.now(timezone.utc),
            created_by=str(uuid4()),
        )
        assert result is mock_event
        repo.create.assert_called_once()


class TestGetEvent:
    @pytest.mark.asyncio
    async def test_returns_event(self, svc, repo):
        event = make_event()
        repo.get_by_id.return_value = event
        result = await svc.get_event(event.id)
        assert result is event

    @pytest.mark.asyncio
    async def test_raises_not_found(self, svc, repo):
        repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await svc.get_event("nonexistent")

    @pytest.mark.asyncio
    async def test_raises_forbidden_for_wrong_tenant(self, svc, repo):
        event = make_event(tenant_id="other-tenant")
        repo.get_by_id.return_value = event
        with pytest.raises(ForbiddenError):
            await svc.get_event(event.id)


class TestCloseEvent:
    @pytest.mark.asyncio
    async def test_closes_event(self, svc, repo):
        event = make_event(status="open")
        repo.get_by_id.side_effect = [event, make_event(status="closed")]
        repo.update.return_value = None

        result = await svc.close_event(event.id, closed_by=str(uuid4()))
        repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_cannot_delete_closed_event(self, svc, repo):
        event = make_event(status="closed")
        repo.get_by_id.return_value = event
        with pytest.raises(ForbiddenError):
            await svc.delete_event(event.id, deleted_by=str(uuid4()))


class TestGetSummary:
    @pytest.mark.asyncio
    async def test_returns_summary(self, svc, repo):
        repo.count_by_status.return_value = {"open": 5, "closed": 3}
        result = await svc.get_summary()
        assert "by_status" in result
        assert result["by_status"]["open"] == 5
