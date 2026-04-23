"""Unit tests — CAPADomainService business logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from rainer_common.exceptions import ForbiddenError, NotFoundError

from app.domain.services import CAPADomainService
from app.infra.db.models import CAPA, CAPAAction


def make_capa(**kwargs) -> CAPA:
    defaults = dict(
        id=str(uuid4()), tenant_id="tenant-1", capa_number="CAPA-001",
        title="Test CAPA", capa_type="corrective",
        description="Root cause found", status="open", severity="major",
        source_type="quality_event", source_id=str(uuid4()),
        owner_id=str(uuid4()), department="QA", due_date=None,
        actual_close_date=None, effectiveness_verified=False,
        tags=[], attachments=[], deleted_at=None,
        created_by=str(uuid4()),
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    c = MagicMock(spec=CAPA)
    for k, v in defaults.items():
        setattr(c, k, v)
    return c


@pytest.fixture
def capa_repo():
    return AsyncMock()


@pytest.fixture
def action_repo():
    return AsyncMock()


@pytest.fixture
def svc(capa_repo, action_repo):
    return CAPADomainService(capa_repo=capa_repo, action_repo=action_repo, tenant_id="tenant-1")


class TestCreateCAPA:
    @pytest.mark.asyncio
    async def test_creates_capa(self, svc, capa_repo):
        mock_capa = make_capa()
        capa_repo.create.return_value = mock_capa
        result = await svc.create_capa(
            capa_number="CAPA-001", title="Test CAPA",
            description="Something needs fixing", created_by=str(uuid4()),
        )
        assert result is mock_capa
        capa_repo.create.assert_called_once()


class TestGetCAPA:
    @pytest.mark.asyncio
    async def test_returns_capa(self, svc, capa_repo):
        capa = make_capa()
        capa_repo.get_by_id.return_value = capa
        result = await svc.get_capa(capa.id)
        assert result is capa

    @pytest.mark.asyncio
    async def test_raises_not_found(self, svc, capa_repo):
        capa_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await svc.get_capa("nonexistent")

    @pytest.mark.asyncio
    async def test_raises_forbidden_for_wrong_tenant(self, svc, capa_repo):
        capa = make_capa(tenant_id="other-tenant")
        capa_repo.get_by_id.return_value = capa
        with pytest.raises(ForbiddenError):
            await svc.get_capa(capa.id)


class TestAddAction:
    @pytest.mark.asyncio
    async def test_adds_action_to_capa(self, svc, capa_repo, action_repo):
        capa = make_capa()
        capa_repo.get_by_id.return_value = capa
        mock_action = MagicMock(spec=CAPAAction)
        action_repo.create.return_value = mock_action

        result = await svc.add_action(
            capa_id=capa.id,
            action_type="corrective",
            description="Fix the process",
            created_by=str(uuid4()),
        )
        assert result is mock_action
        action_repo.create.assert_called_once()


class TestCloseCAPA:
    @pytest.mark.asyncio
    async def test_closes_capa(self, svc, capa_repo):
        capa = make_capa(status="implementation")
        capa_repo.get_by_id.side_effect = [capa, make_capa(status="closed")]
        capa_repo.update.return_value = None

        result = await svc.close_capa(capa.id, closed_by=str(uuid4()))
        capa_repo.update.assert_called_once()
