"""Complaints Service — Complaint management API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_permission
from rainer_auth_lib.permissions import Permission
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.database import get_db
from ....domain.services import ComplaintDomainService
from ....infra.db.repositories import ComplaintRepository
from ....schemas.requests import (
    CreateComplaintRequest,
    EscalateToCapaRequest,
    RespondToComplaintRequest,
    UpdateComplaintRequest,
)
from ....schemas.responses import ComplaintResponse

router = APIRouter(prefix="/complaints", tags=["Complaints"])
logger = structlog.get_logger(__name__)


def _get_service(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]) -> ComplaintDomainService:
    return ComplaintDomainService(
        complaint_repo=ComplaintRepository(db),
        tenant_id=current_user.tenant_id or "",
    )


@router.get("", response_model=PaginatedResponse[ComplaintResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="List complaints")
async def list_complaints(
    current_user: CurrentUser,
    service: Annotated[ComplaintDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    category: str | None = Query(default=None),
) -> PaginatedResponse[ComplaintResponse]:
    complaints, total = await service.list_complaints(
        status=status, severity=severity, category=category,
        page=pagination.page, page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[ComplaintResponse.model_validate(c, from_attributes=True) for c in complaints],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.post("", response_model=SuccessResponse[ComplaintResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Create a complaint")
async def create_complaint(
    payload: CreateComplaintRequest,
    current_user: CurrentUser,
    service: Annotated[ComplaintDomainService, Depends(_get_service)],
) -> SuccessResponse[ComplaintResponse]:
    complaint = await service.create_complaint(
        complaint_number=payload.complaint_number,
        description=payload.description,
        received_at=payload.received_at,
        created_by=current_user.sub,
        customer_name=payload.customer_name,
        received_via=payload.received_via,
        severity=payload.severity,
        category=payload.category,
        investigator_id=payload.investigator_id,
    )
    return SuccessResponse.of(ComplaintResponse.model_validate(complaint, from_attributes=True))


@router.get("/{complaint_id}", response_model=SuccessResponse[ComplaintResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="Get complaint details")
async def get_complaint(
    complaint_id: str,
    current_user: CurrentUser,
    service: Annotated[ComplaintDomainService, Depends(_get_service)],
) -> SuccessResponse[ComplaintResponse]:
    complaint = await service.get_complaint(complaint_id)
    return SuccessResponse.of(ComplaintResponse.model_validate(complaint, from_attributes=True))


@router.patch("/{complaint_id}", response_model=SuccessResponse[ComplaintResponse],
              dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
              summary="Update a complaint")
async def update_complaint(
    complaint_id: str,
    payload: UpdateComplaintRequest,
    current_user: CurrentUser,
    service: Annotated[ComplaintDomainService, Depends(_get_service)],
) -> SuccessResponse[ComplaintResponse]:
    fields = payload.model_dump(exclude_none=True)
    complaint = await service.update_complaint(complaint_id, **fields)
    return SuccessResponse.of(ComplaintResponse.model_validate(complaint, from_attributes=True))


@router.delete("/{complaint_id}", response_model=MessageResponse,
               dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
               summary="Soft delete a complaint")
async def delete_complaint(
    complaint_id: str,
    current_user: CurrentUser,
    service: Annotated[ComplaintDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.soft_delete_complaint(complaint_id)
    return MessageResponse(message="Complaint deleted successfully")


@router.post("/{complaint_id}/respond", response_model=SuccessResponse[ComplaintResponse],
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Respond to a complaint")
async def respond_to_complaint(
    complaint_id: str,
    payload: RespondToComplaintRequest,
    current_user: CurrentUser,
    service: Annotated[ComplaintDomainService, Depends(_get_service)],
) -> SuccessResponse[ComplaintResponse]:
    complaint = await service.respond_to_complaint(complaint_id, response_text=payload.response_text)
    return SuccessResponse.of(ComplaintResponse.model_validate(complaint, from_attributes=True))


@router.post("/{complaint_id}/escalate-to-capa", response_model=SuccessResponse[ComplaintResponse],
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Escalate complaint to CAPA")
async def escalate_to_capa(
    complaint_id: str,
    payload: EscalateToCapaRequest,
    current_user: CurrentUser,
    service: Annotated[ComplaintDomainService, Depends(_get_service)],
) -> SuccessResponse[ComplaintResponse]:
    complaint = await service.escalate_to_capa(complaint_id, capa_id=payload.capa_id)
    return SuccessResponse.of(ComplaintResponse.model_validate(complaint, from_attributes=True))
