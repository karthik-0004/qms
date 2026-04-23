"""Quality Event Service — Quality event API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.database import get_db
from ....domain.services import QualityEventDomainService
from ....infra.db.repositories import QualityEventRepository
from ....schemas.requests import CloseQualityEventRequest, CreateQualityEventRequest, UpdateQualityEventRequest
from ....schemas.responses import QualityEventResponse, QualityEventSummaryResponse

router = APIRouter(prefix="/quality-events", tags=["Quality Events"])
logger = structlog.get_logger(__name__)


def _get_service(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]) -> QualityEventDomainService:
    return QualityEventDomainService(repo=QualityEventRepository(db), tenant_id=current_user.tenant_id or "")


@router.get("", response_model=PaginatedResponse[QualityEventResponse], summary="List quality events")
async def list_events(
    current_user: CurrentUser,
    service: Annotated[QualityEventDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    assigned_to: str | None = Query(default=None),
    department: str | None = Query(default=None),
) -> PaginatedResponse[QualityEventResponse]:
    events, total = await service.list_events(
        status=status, event_type=event_type, severity=severity,
        assigned_to=assigned_to, department=department,
        page=pagination.page, page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[QualityEventResponse.model_validate(e, from_attributes=True) for e in events],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.post("", response_model=SuccessResponse[QualityEventResponse], status_code=201,
             summary="Create a quality event")
async def create_event(
    payload: CreateQualityEventRequest,
    current_user: CurrentUser,
    service: Annotated[QualityEventDomainService, Depends(_get_service)],
) -> SuccessResponse[QualityEventResponse]:
    event = await service.create_event(
        event_number=payload.event_number,
        title=payload.title,
        event_type=payload.event_type,
        description=payload.description,
        detected_at=payload.detected_at,
        created_by=current_user.sub,
        severity=payload.severity,
        priority=payload.priority,
        department=payload.department,
        location=payload.location,
        assigned_to=payload.assigned_to,
        immediate_action=payload.immediate_action,
        capa_required=payload.capa_required,
        due_date=payload.due_date,
        tags=payload.tags,
    )
    return SuccessResponse.of(QualityEventResponse.model_validate(event, from_attributes=True))


@router.get("/summary", response_model=SuccessResponse[QualityEventSummaryResponse],
            summary="Get quality events summary by status")
async def get_summary(
    current_user: CurrentUser,
    service: Annotated[QualityEventDomainService, Depends(_get_service)],
) -> SuccessResponse[QualityEventSummaryResponse]:
    summary = await service.get_summary()
    return SuccessResponse.of(QualityEventSummaryResponse(**summary))


@router.get("/{event_id}", response_model=SuccessResponse[QualityEventResponse],
            summary="Get quality event details")
async def get_event(
    event_id: str,
    current_user: CurrentUser,
    service: Annotated[QualityEventDomainService, Depends(_get_service)],
) -> SuccessResponse[QualityEventResponse]:
    event = await service.get_event(event_id)
    return SuccessResponse.of(QualityEventResponse.model_validate(event, from_attributes=True))


@router.patch("/{event_id}", response_model=SuccessResponse[QualityEventResponse],
              summary="Update a quality event")
async def update_event(
    event_id: str,
    payload: UpdateQualityEventRequest,
    current_user: CurrentUser,
    service: Annotated[QualityEventDomainService, Depends(_get_service)],
) -> SuccessResponse[QualityEventResponse]:
    fields = payload.model_dump(exclude_none=True)
    event = await service.update_event(event_id, updated_by=current_user.sub, **fields)
    return SuccessResponse.of(QualityEventResponse.model_validate(event, from_attributes=True))


@router.post("/{event_id}/close", response_model=SuccessResponse[QualityEventResponse],
             summary="Close a quality event")
async def close_event(
    event_id: str,
    payload: CloseQualityEventRequest,
    current_user: CurrentUser,
    service: Annotated[QualityEventDomainService, Depends(_get_service)],
) -> SuccessResponse[QualityEventResponse]:
    event = await service.close_event(event_id, closed_by=current_user.sub, resolution=payload.resolution)
    return SuccessResponse.of(QualityEventResponse.model_validate(event, from_attributes=True))


@router.delete("/{event_id}", response_model=MessageResponse, summary="Delete a quality event")
async def delete_event(
    event_id: str,
    current_user: CurrentUser,
    service: Annotated[QualityEventDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.delete_event(event_id, deleted_by=current_user.sub)
    return MessageResponse(message="Quality event deleted successfully")
