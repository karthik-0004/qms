"""Analytics Service — Analytics and dashboard API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser
from rainer_common.responses import SuccessResponse

from ....core.database import get_db
from ....domain.services import AnalyticsDomainService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _get_service() -> AnalyticsDomainService:
    return AnalyticsDomainService()


@router.get("/dashboards", response_model=SuccessResponse[list[dict]],
            summary="List available dashboards")
async def list_dashboards(
    current_user: CurrentUser,
    service: Annotated[AnalyticsDomainService, Depends(_get_service)],
    product: str | None = Query(default=None),
) -> SuccessResponse[list[dict]]:
    dashboards = await service.list_dashboards(product=product)
    return SuccessResponse.of(dashboards)


@router.get("/dashboards/{dashboard_id}", response_model=SuccessResponse[dict],
            summary="Get dashboard data")
async def get_dashboard(
    dashboard_id: str,
    current_user: CurrentUser,
    service: Annotated[AnalyticsDomainService, Depends(_get_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
    date_range_days: int = Query(default=30, ge=1, le=365),
) -> SuccessResponse[dict]:
    dashboard = await service.get_dashboard(
        dashboard_id=dashboard_id,
        tenant_id=current_user.tenant_id or "",
        date_range_days=date_range_days,
        db=db,
    )
    return SuccessResponse.of(dashboard)


@router.get("/kpis", response_model=SuccessResponse[dict],
            summary="Get platform KPIs for current tenant")
async def get_kpis(
    current_user: CurrentUser,
    service: Annotated[AnalyticsDomainService, Depends(_get_service)],
) -> SuccessResponse[dict]:
    kpis = await service.get_platform_kpis(tenant_id=current_user.tenant_id or "")
    return SuccessResponse.of(kpis)


@router.get("/time-series", response_model=SuccessResponse[dict],
            summary="Get time-series data for a metric")
async def get_time_series(
    current_user: CurrentUser,
    service: Annotated[AnalyticsDomainService, Depends(_get_service)],
    metric: str = Query(..., description="Metric name to query"),
    interval: str = Query(default="day", description="Aggregation interval: hour, day, week, month"),
    days: int = Query(default=30, ge=1, le=365),
) -> SuccessResponse[dict]:
    data = await service.get_time_series(
        metric=metric,
        tenant_id=current_user.tenant_id or "",
        interval=interval,
        days=days,
    )
    return SuccessResponse.of(data)
