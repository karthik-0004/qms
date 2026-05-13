"""Analytics Service — Cross-module KPI and dashboard domain service."""

from datetime import datetime, timedelta, timezone
from typing import Any

import structlog
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..infra.db.models import CAPAMirror, DocumentMirror

logger = structlog.get_logger(__name__)

_OPEN_CAPA_STATUSES = (
    "open",
    "under_investigation",
    "root_cause_identified",
    "implementation",
    "effectiveness_check",
)

_ZERO_DOC_COUNTS: dict[str, int] = {
    "draft": 0,
    "under_review": 0,
    "approved": 0,
    "obsolete": 0,
}

_ZERO_CAPA_AGING: dict[str, int] = {
    "capas_0_30_days": 0,
    "capas_31_60_days": 0,
    "capas_61_90_days": 0,
    "capas_over_90_days": 0,
}


class AnalyticsDomainService:
    """Cross-module analytics, KPIs, and dashboard data aggregation."""

    async def get_platform_kpis(self, tenant_id: str) -> dict[str, Any]:
        """Get high-level platform KPIs for a tenant dashboard."""
        return {
            "tenant_id": tenant_id,
            "as_of": datetime.now(timezone.utc).isoformat(),
            "kpis": {
                "total_users": 0,
                "active_users_30d": 0,
                "documents_total": 0,
                "documents_pending_review": 0,
                "open_capas": 0,
                "overdue_capas": 0,
                "upcoming_trainings": 0,
                "equipment_due_calibration": 0,
                "open_quality_events": 0,
                "workorders_this_month": 0,
                "certificates_issued_ytd": 0,
            },
        }

    async def get_dashboard(
        self,
        dashboard_id: str,
        tenant_id: str,
        date_range_days: int = 30,
        db: AsyncSession | None = None,
    ) -> dict[str, Any]:
        """Get dashboard data (charts, metrics) for a specific dashboard."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=date_range_days)

        base = {
            "dashboard_id": dashboard_id,
            "tenant_id": tenant_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "charts": [],
            "summary_metrics": {},
        }

        if dashboard_id != "qms_overview" or db is None:
            return base

        try:
            doc_counts = await self._get_document_counts(db, tenant_id)
            capa_aging = await self._get_capa_aging_counts(db, tenant_id)
        except Exception:
            logger.exception("analytics_aggregation_failed", dashboard_id=dashboard_id, tenant_id=tenant_id)
            doc_counts = dict(_ZERO_DOC_COUNTS)
            capa_aging = dict(_ZERO_CAPA_AGING)

        base["summary_metrics"] = {
            "documents_draft": doc_counts.get("draft", 0),
            "documents_pending_review": doc_counts.get("under_review", 0),
            "documents_approved": doc_counts.get("approved", 0),
            "documents_obsolete": doc_counts.get("obsolete", 0),
            **capa_aging,
        }
        return base

    async def _get_document_counts(
        self, db: AsyncSession, tenant_id: str
    ) -> dict[str, int]:
        """Count documents per status for a tenant (excludes soft-deleted rows)."""
        result = await db.execute(
            select(DocumentMirror.status, func.count().label("cnt"))
            .where(
                and_(
                    DocumentMirror.tenant_id == tenant_id,
                    DocumentMirror.deleted_at.is_(None),
                    DocumentMirror.status.in_(("draft", "under_review", "approved", "obsolete")),
                )
            )
            .group_by(DocumentMirror.status)
        )
        return {row.status: row.cnt for row in result}

    async def _get_capa_aging_counts(
        self, db: AsyncSession, tenant_id: str
    ) -> dict[str, int]:
        """Count open CAPAs by age bucket for a tenant (excludes soft-deleted rows)."""
        now = datetime.now(timezone.utc)

        async def _count(min_days: int, max_days: int | None = None) -> int:
            clauses = [
                CAPAMirror.tenant_id == tenant_id,
                CAPAMirror.status.in_(_OPEN_CAPA_STATUSES),
                CAPAMirror.deleted_at.is_(None),
                CAPAMirror.created_at < (now - timedelta(days=min_days)),
            ]
            if max_days is not None:
                clauses.append(CAPAMirror.created_at >= (now - timedelta(days=max_days)))
            row = await db.execute(
                select(func.count()).select_from(CAPAMirror).where(and_(*clauses))
            )
            return row.scalar() or 0

        b0 = await _count(0, 30)
        b30 = await _count(30, 60)
        b60 = await _count(60, 90)
        b90 = await _count(90)
        return {
            "capas_0_30_days": b0,
            "capas_31_60_days": b30,
            "capas_61_90_days": b60,
            "capas_over_90_days": b90,
        }

    async def list_dashboards(self, product: str | None = None) -> list[dict[str, Any]]:
        """List available dashboards, optionally filtered by product."""
        dashboards = [
            {"id": "platform_overview", "name": "Platform Overview", "product": None},
            {"id": "qms_overview", "name": "QMS Overview", "product": "qms"},
            {"id": "document_status", "name": "Document Status", "product": "qms"},
            {"id": "capa_metrics", "name": "CAPA Metrics", "product": "qms"},
            {"id": "training_compliance", "name": "Training Compliance", "product": "qms"},
            {"id": "em_overview", "name": "EM Overview", "product": "em"},
            {"id": "plate_analysis", "name": "Plate Analysis Trends", "product": "em"},
            {"id": "ccv_overview", "name": "CCV Overview", "product": "ccv"},
            {"id": "workorder_metrics", "name": "Work Order Metrics", "product": "ccv"},
            {"id": "certificate_tracking", "name": "Certificate Tracking", "product": "ccv"},
        ]
        if product:
            dashboards = [d for d in dashboards if d["product"] in (None, product)]
        return dashboards

    async def get_time_series(
        self,
        metric: str,
        tenant_id: str,
        interval: str = "day",
        days: int = 30,
    ) -> dict[str, Any]:
        """Get time-series data for a specific metric."""
        return {
            "metric": metric,
            "interval": interval,
            "data_points": [],
            "tenant_id": tenant_id,
        }
