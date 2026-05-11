"""Unit tests — TenantDomainService business logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from rainer_common.exceptions import ConflictError, NotFoundError

from app.core.config import Settings
from app.domain.services import TenantDomainService
from app.infra.db.models import Tenant, TenantSettings


def make_tenant(**kwargs) -> Tenant:
    defaults = dict(
        id=str(uuid4()),
        tenant_name="Test Corp",
        slug="test-corp",
        db_name="tenant_test_corp_db",
        db_user="tenant_test_corp_user",
        db_host="postgres",
        db_port=5432,
        status="active",
        tier="starter",
        products=["qms"],
        region="us-east-1",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted_at=None,
    )
    defaults.update(kwargs)
    tenant = MagicMock(spec=Tenant)
    for k, v in defaults.items():
        setattr(tenant, k, v)
    return tenant


def make_settings_obj() -> Settings:
    return Settings(
        rainer_env="testing",
        database_url="sqlite+aiosqlite:///:memory:",
        postgres_admin_url="postgresql://rainer:pass@localhost/postgres",
        rainer_master_secret="test-master",
    )


@pytest.fixture
def tenant_repo():
    return AsyncMock()


@pytest.fixture
def settings_repo():
    return AsyncMock()


@pytest.fixture
def svc(tenant_repo, settings_repo):
    return TenantDomainService(
        tenant_repo=tenant_repo,
        settings_repo=settings_repo,
        settings=make_settings_obj(),
    )


class TestCreateTenant:
    @pytest.mark.asyncio
    async def test_raises_conflict_if_name_exists(self, svc, tenant_repo):
        tenant_repo.get_by_name.return_value = make_tenant()
        with pytest.raises(ConflictError):
            await svc.create_tenant("Test Corp", ["qms"])

    @pytest.mark.asyncio
    async def test_creates_and_provisions_tenant(self, svc, tenant_repo, settings_repo):
        tenant_repo.get_by_name.return_value = None
        mock_tenant = make_tenant(status="provisioning")
        tenant_repo.create.return_value = mock_tenant
        tenant_repo.update_status.return_value = None
        settings_repo.create.return_value = MagicMock()

        with patch.object(svc, "_provision_db", new=AsyncMock()):
            result = await svc.create_tenant("New Corp", ["qms", "ccv"])

        tenant_repo.create.assert_called_once()
        settings_repo.create.assert_called_once_with(tenant_id=mock_tenant.id)


class TestGetTenant:
    @pytest.mark.asyncio
    async def test_returns_tenant(self, svc, tenant_repo):
        tenant = make_tenant()
        tenant_repo.get_by_id.return_value = tenant
        result = await svc.get_tenant(tenant.id)
        assert result.id == tenant.id

    @pytest.mark.asyncio
    async def test_raises_not_found(self, svc, tenant_repo):
        tenant_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await svc.get_tenant("nonexistent-id")


class TestSuspendTenant:
    @pytest.mark.asyncio
    async def test_suspends_active_tenant(self, svc, tenant_repo):
        tenant = make_tenant(status="active")
        tenant_repo.get_by_id.return_value = tenant
        tenant_repo.update_status.return_value = None
        await svc.suspend_tenant(tenant.id)
        tenant_repo.update_status.assert_called_with(tenant.id, "suspended")

    @pytest.mark.asyncio
    async def test_raises_conflict_if_already_suspended(self, svc, tenant_repo):
        tenant = make_tenant(status="suspended")
        tenant_repo.get_by_id.return_value = tenant
        with pytest.raises(ConflictError):
            await svc.suspend_tenant(tenant.id)


class TestDeleteTenant:
    @pytest.mark.asyncio
    async def test_soft_deletes_tenant(self, svc, tenant_repo):
        tenant = make_tenant()
        tenant_repo.get_by_id.return_value = tenant
        tenant_repo.soft_delete.return_value = None
        await svc.delete_tenant(tenant.id)
        tenant_repo.soft_delete.assert_called_with(tenant.id)


class TestUpdateTenant:
    @pytest.mark.asyncio
    async def test_raises_conflict_if_name_exists_for_other_tenant(self, svc, tenant_repo):
        other_tenant = make_tenant(id=str(uuid4()), tenant_name="Existing Corp")
        tenant_repo.get_by_name.return_value = other_tenant

        with pytest.raises(ConflictError):
            await svc.update_tenant("some-tenant-id", tenant_name="Existing Corp")

    @pytest.mark.asyncio
    async def test_updates_when_name_is_same_tenant(self, svc, tenant_repo):
        same_tenant = make_tenant(id="same-id", tenant_name="Same Corp")
        tenant_repo.get_by_name.return_value = same_tenant

        await svc.update_tenant("same-id", tenant_name="Same Corp")
        tenant_repo.update.assert_called_once()
