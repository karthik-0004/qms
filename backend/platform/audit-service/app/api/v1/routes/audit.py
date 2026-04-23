"""Audit Service — Audit log query API routes."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser
from rainer_common.responses import PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.database import get_db
from ....domain.services import AuditDomainService
from ....infra.db.repositories import AuditLogRepository
from ....schemas.responses import AuditLogResponse

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AuditDomainService:
    return AuditDomainService(AuditLogRepository(db))


@router.get("/logs", response_model=PaginatedResponse[AuditLogResponse],
            summary="Query audit logs (filtered, paginated)")
async def query_logs(
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    tenant_id: str | None = Query(default=None),
    user_id: str | None = Query(default=None),
    action: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    resource_id: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    from_date: datetime | None = Query(default=None),
    to_date: datetime | None = Query(default=None),
) -> PaginatedResponse[AuditLogResponse]:
    # If not super_admin, restrict to own tenant
    effective_tenant = tenant_id
    if current_user.role != "super_admin":
        effective_tenant = current_user.tenant_id

    logs, total = await service.query_logs(
        tenant_id=effective_tenant,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        severity=severity,
        from_date=from_date,
        to_date=to_date,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[AuditLogResponse.model_validate(l, from_attributes=True) for l in logs],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


@router.get("/logs/{log_id}", response_model=SuccessResponse[AuditLogResponse],
            summary="Get a single audit log entry")
async def get_log(
    log_id: str,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> SuccessResponse[AuditLogResponse]:
    log = await service.get_log(log_id)
    return SuccessResponse.of(AuditLogResponse.model_validate(log, from_attributes=True))


@router.post("/logs", response_model=SuccessResponse[AuditLogResponse],
             status_code=201, include_in_schema=False,
             summary="Internal: append audit log (service-to-service only)")
async def append_log(
    payload: dict,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> SuccessResponse[AuditLogResponse]:
    log = await service.append(**payload)
    return SuccessResponse.of(AuditLogResponse.model_validate(log, from_attributes=True))
