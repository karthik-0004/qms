"""Unit tests — AnalyticsDomainService business logic."""

import pytest

from app.domain.services import AnalyticsDomainService


@pytest.fixture
def svc():
    return AnalyticsDomainService()


class TestGetPlatformKPIs:
    @pytest.mark.asyncio
    async def test_returns_kpi_structure(self, svc):
        result = await svc.get_platform_kpis(tenant_id="t1")
        assert "tenant_id" in result
        assert "kpis" in result
        assert "as_of" in result
        kpis = result["kpis"]
        assert "total_users" in kpis
        assert "open_capas" in kpis
        assert "documents_total" in kpis


class TestListDashboards:
    @pytest.mark.asyncio
    async def test_returns_all_dashboards_without_filter(self, svc):
        dashboards = await svc.list_dashboards()
        assert len(dashboards) > 0

    @pytest.mark.asyncio
    async def test_filters_by_product(self, svc):
        qms = await svc.list_dashboards(product="qms")
        for d in qms:
            assert d["product"] in ("qms", None)

    @pytest.mark.asyncio
    async def test_platform_overview_always_included(self, svc):
        dashboards = await svc.list_dashboards(product="qms")
        ids = {d["id"] for d in dashboards}
        assert "platform_overview" in ids or any(d["product"] is None for d in dashboards)


class TestGetDashboard:
    @pytest.mark.asyncio
    async def test_returns_dashboard_structure(self, svc):
        result = await svc.get_dashboard("qms_overview", tenant_id="t1", date_range_days=30)
        assert result["dashboard_id"] == "qms_overview"
        assert result["tenant_id"] == "t1"
        assert "period" in result
        assert "charts" in result


class TestGetTimeSeries:
    @pytest.mark.asyncio
    async def test_returns_time_series_structure(self, svc):
        result = await svc.get_time_series("documents_created", tenant_id="t1")
        assert result["metric"] == "documents_created"
        assert "data_points" in result
        assert result["tenant_id"] == "t1"
