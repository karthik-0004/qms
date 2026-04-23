"""Unit tests — ConfigDomainService business logic."""

import pytest

from rainer_common.exceptions import NotFoundError

from app.domain.services import ConfigDomainService


@pytest.fixture
def svc():
    return ConfigDomainService()


class TestFeatureFlags:
    @pytest.mark.asyncio
    async def test_returns_all_flags(self, svc):
        flags = await svc.get_feature_flags()
        assert isinstance(flags, dict)
        assert "qms.documents" in flags
        assert "em.plates" in flags
        assert "ccv.crm" in flags

    @pytest.mark.asyncio
    async def test_tenant_override_overrides_default(self, svc):
        overrides = {"qms.risk": True}
        flags = await svc.get_feature_flags(tenant_overrides=overrides)
        assert flags["qms.risk"] is True

    @pytest.mark.asyncio
    async def test_get_single_flag(self, svc):
        value = await svc.get_feature_flag("platform.mfa")
        assert isinstance(value, bool)

    @pytest.mark.asyncio
    async def test_raises_not_found_for_unknown_flag(self, svc):
        with pytest.raises(NotFoundError):
            await svc.get_feature_flag("nonexistent.flag")


class TestEnums:
    @pytest.mark.asyncio
    async def test_returns_enum_values(self, svc):
        enums = await svc.get_enums("document_status")
        assert len(enums) > 0
        assert all("value" in e and "label" in e for e in enums)

    @pytest.mark.asyncio
    async def test_raises_not_found_for_unknown_type(self, svc):
        with pytest.raises(NotFoundError):
            await svc.get_enums("nonexistent_type")

    @pytest.mark.asyncio
    async def test_list_enum_types(self, svc):
        types = await svc.list_enum_types()
        assert "document_status" in types
        assert "severity" in types
        assert "workorder_status" in types

    @pytest.mark.asyncio
    async def test_all_enum_types_are_queryable(self, svc):
        types = await svc.list_enum_types()
        for t in types:
            values = await svc.get_enums(t)
            assert len(values) > 0


class TestPlatformConfig:
    @pytest.mark.asyncio
    async def test_returns_complete_config(self, svc):
        config = await svc.get_platform_config()
        assert "feature_flags" in config
        assert "supported_products" in config
        assert "supported_tiers" in config
        assert set(config["supported_products"]) == {"qms", "em", "ccv"}
