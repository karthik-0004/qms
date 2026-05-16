"""Env Monitoring Service — Monitoring points API routes."""

from datetime import datetime
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_permission
from rainer_auth_lib.permissions import Permission
from rainer_common.responses import PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.database import get_db
from ....domain.services import EnvMonitoringDomainService
from ....infra.db.repositories import MonitoringPointRepository, MonitoringReadingRepository
from ....schemas.requests import AddReadingRequest, CreateMonitoringPointRequest, UpdateMonitoringPointRequest
from ....schemas.responses import MonitoringPointResponse, MonitoringReadingResponse

router = APIRouter(prefix="/monitoring-points", tags=["Monitoring Points"])
logger = structlog.get_logger(__name__)


def _get_service(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]) -> EnvMonitoringDomainService:
    return EnvMonitoringDomainService(
        point_repo=MonitoringPointRepository(db),
        reading_repo=MonitoringReadingRepository(db),
        tenant_id=current_user.tenant_id or "",
    )


@router.get("", response_model=PaginatedResponse[MonitoringPointResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="List monitoring points")
async def list_monitoring_points(
    current_user: CurrentUser,
    service: Annotated[EnvMonitoringDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(default=None),
) -> PaginatedResponse[MonitoringPointResponse]:
    points, total = await service.list_points(
        status=status,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[MonitoringPointResponse.model_validate(p, from_attributes=True) for p in points],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.post("", response_model=SuccessResponse[MonitoringPointResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Create a monitoring point")
async def create_monitoring_point(
    payload: CreateMonitoringPointRequest,
    current_user: CurrentUser,
    service: Annotated[EnvMonitoringDomainService, Depends(_get_service)],
) -> SuccessResponse[MonitoringPointResponse]:
    point = await service.create_point(
        point_id=payload.point_id,
        location=payload.location,
        parameter=payload.parameter,
        frequency_type=payload.frequency_type,
        created_by=current_user.sub,
        alert_limit=payload.alert_limit,
        action_limit=payload.action_limit,
        frequency_value=payload.frequency_value,
    )
    return SuccessResponse.of(MonitoringPointResponse.model_validate(point, from_attributes=True))


@router.get("/{point_id}", response_model=SuccessResponse[MonitoringPointResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="Get monitoring point")
async def get_monitoring_point(
    point_id: str,
    current_user: CurrentUser,
    service: Annotated[EnvMonitoringDomainService, Depends(_get_service)],
) -> SuccessResponse[MonitoringPointResponse]:
    point = await service.get_point(point_id)
    return SuccessResponse.of(MonitoringPointResponse.model_validate(point, from_attributes=True))


@router.patch("/{point_id}", response_model=SuccessResponse[MonitoringPointResponse],
              dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
              summary="Update a monitoring point")
async def update_monitoring_point(
    point_id: str,
    payload: UpdateMonitoringPointRequest,
    current_user: CurrentUser,
    service: Annotated[EnvMonitoringDomainService, Depends(_get_service)],
) -> SuccessResponse[MonitoringPointResponse]:
    fields = payload.model_dump(exclude_none=True)
    point = await service.update_point(point_id, **fields)
    return SuccessResponse.of(MonitoringPointResponse.model_validate(point, from_attributes=True))


@router.post("/{point_id}/readings", response_model=SuccessResponse[MonitoringReadingResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Add a reading to a monitoring point")
async def add_reading(
    point_id: str,
    payload: AddReadingRequest,
    current_user: CurrentUser,
    service: Annotated[EnvMonitoringDomainService, Depends(_get_service)],
) -> SuccessResponse[MonitoringReadingResponse]:
    reading = await service.add_reading(
        point_db_id=point_id,
        value=payload.value,
        recorded_at=payload.recorded_at,
        recorded_by_user_id=payload.recorded_by_user_id or current_user.sub,
        notes=payload.notes,
    )
    return SuccessResponse.of(MonitoringReadingResponse.model_validate(reading, from_attributes=True))


@router.get("/{point_id}/readings", response_model=SuccessResponse[list[MonitoringReadingResponse]],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="List readings for a monitoring point")
async def list_readings(
    point_id: str,
    current_user: CurrentUser,
    service: Annotated[EnvMonitoringDomainService, Depends(_get_service)],
    from_date: datetime | None = Query(default=None),
    to_date: datetime | None = Query(default=None),
) -> SuccessResponse[list[MonitoringReadingResponse]]:
    readings = await service.list_readings(point_id, from_date=from_date, to_date=to_date)
    return SuccessResponse.of([MonitoringReadingResponse.model_validate(r, from_attributes=True) for r in readings])


@router.get("/{point_id}/excursions", response_model=SuccessResponse[list[MonitoringReadingResponse]],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="List excursions for a monitoring point")
async def list_excursions(
    point_id: str,
    current_user: CurrentUser,
    service: Annotated[EnvMonitoringDomainService, Depends(_get_service)],
) -> SuccessResponse[list[MonitoringReadingResponse]]:
    excursions = await service.list_excursions(point_id)
    return SuccessResponse.of([MonitoringReadingResponse.model_validate(r, from_attributes=True) for r in excursions])
