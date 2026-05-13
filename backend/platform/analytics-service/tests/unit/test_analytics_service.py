"""Unit tests — AnalyticsDomainService business logic."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.services import AnalyticsDomainService

_EXPECTED_SUMMARY_KEYS = [
    "documents_draft",
    "documents_pending_review",
    "documents_approved",
    "documents_obsolete",
    "capas_0_30_days",
    "capas_31_60_days",
    "capas_61_90_days",
    "capas_over_90_days",
]


@pytest.fixture
def svc():
    return AnalyticsDomainService()


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


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
    async def test_returns_dashboard_structure_without_db(self, svc):
        result = await svc.get_dashboard("qms_overview", tenant_id="t1", date_range_days=30)
        assert result["dashboard_id"] == "qms_overview"
        assert result["tenant_id"] == "t1"
        assert "period" in result
        assert "charts" in result

    @pytest.mark.asyncio
    async def test_unknown_dashboard_returns_empty_summary_metrics(self, svc, mock_db):
        result = await svc.get_dashboard("unknown_dashboard", tenant_id="t1", db=mock_db)
        assert result["summary_metrics"] == {}
        assert result["charts"] == []

    @pytest.mark.asyncio
    async def test_qms_overview_returns_all_summary_metric_keys(self, svc, mock_db):
        mock_db.execute = AsyncMock(return_value=MagicMock(
            __iter__=lambda self: iter([]),
            scalar=lambda: 0,
        ))
        result = await svc.get_dashboard("qms_overview", tenant_id="t1", db=mock_db)
        metrics = result["summary_metrics"]
        for key in _EXPECTED_SUMMARY_KEYS:
            assert key in metrics, f"Missing key: {key}"
            assert isinstance(metrics[key], int), f"{key} must be int, got {type(metrics[key])}"

    @pytest.mark.asyncio
    async def test_qms_overview_aggregation_failure_returns_zeros_not_500(self, svc, mock_db):
        mock_db.execute = AsyncMock(side_effect=Exception("DB connection lost"))
        result = await svc.get_dashboard("qms_overview", tenant_id="t1", db=mock_db)
        assert result["dashboard_id"] == "qms_overview"
        metrics = result["summary_metrics"]
        for key in _EXPECTED_SUMMARY_KEYS:
            assert key in metrics, f"Missing key after failure: {key}"
            assert metrics[key] == 0, f"{key} should be 0 on failure, got {metrics[key]}"

    @pytest.mark.asyncio
    async def test_qms_overview_counts_documents_from_db(self, svc, mock_db):
        tenant_id = str(uuid4())
        doc_row = MagicMock(status="approved", cnt=42)
        capa_empty = MagicMock(scalar=lambda: 0)
        call_count = 0

        async def execute_side_effect(stmt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                result = MagicMock()
                result.__iter__ = lambda s: iter([doc_row])
                return result
            result = MagicMock()
            result.scalar = lambda: 0
            return result

        mock_db.execute = execute_side_effect
        result = await svc.get_dashboard("qms_overview", tenant_id=tenant_id, db=mock_db)
        assert result["summary_metrics"]["documents_approved"] == 42


class TestGetTimeSeries:
    @pytest.mark.asyncio
    async def test_returns_time_series_structure(self, svc):
        result = await svc.get_time_series("documents_created", tenant_id="t1")
        assert result["metric"] == "documents_created"
        assert "data_points" in result
        assert result["tenant_id"] == "t1"
