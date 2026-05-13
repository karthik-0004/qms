"""CAPA Service — CAPA lifecycle API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_permission
from rainer_auth_lib.permissions import Permission
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.database import get_db
from ....domain.services import CAPADomainService
from ....infra.db.repositories import CAPAActionRepository, CAPARepository
from ....schemas.requests import (
    AddCAPAActionRequest,
    CompleteActionRequest,
    CreateCAPARequest,
    UpdateCAPARequest,
    VerifyEffectivenessRequest,
)
from ....schemas.responses import CAPAActionResponse, CAPAResponse

router = APIRouter(prefix="/capas", tags=["CAPAs"])
logger = structlog.get_logger(__name__)


def _get_service(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]) -> CAPADomainService:
    return CAPADomainService(
        capa_repo=CAPARepository(db),
        action_repo=CAPAActionRepository(db),
        tenant_id=current_user.tenant_id or "",
    )


@router.get("", response_model=PaginatedResponse[CAPAResponse],
            dependencies=[Depends(require_permission(Permission.CAPA_READ))],
            summary="List CAPAs")
async def list_capas(
    current_user: CurrentUser,
    service: Annotated[CAPADomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    owner_id: str | None = Query(default=None),
    department: str | None = Query(default=None),
    overdue_only: bool = Query(default=False),
) -> PaginatedResponse[CAPAResponse]:
    capas, total = await service.list_capas(
        status=status, severity=severity, owner_id=owner_id,
        department=department, overdue_only=overdue_only,
        page=pagination.page, page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[CAPAResponse.model_validate(c, from_attributes=True) for c in capas],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.post("", response_model=SuccessResponse[CAPAResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.CAPA_WRITE))],
             summary="Create a CAPA")
async def create_capa(
    payload: CreateCAPARequest,
    current_user: CurrentUser,
    service: Annotated[CAPADomainService, Depends(_get_service)],
) -> SuccessResponse[CAPAResponse]:
    capa = await service.create_capa(
        capa_number=payload.capa_number,
        title=payload.title,
        description=payload.description,
        created_by=current_user.sub,
        capa_type=payload.capa_type,
        severity=payload.severity,
        source_type=payload.source_type,
        source_id=payload.source_id,
        owner_id=payload.owner_id,
        department=payload.department,
        due_date=payload.due_date,
        tags=payload.tags,
    )
    return SuccessResponse.of(CAPAResponse.model_validate(capa, from_attributes=True))


@router.get("/{capa_id}", response_model=SuccessResponse[CAPAResponse],
            dependencies=[Depends(require_permission(Permission.CAPA_READ))],
            summary="Get CAPA details")
async def get_capa(
    capa_id: str,
    current_user: CurrentUser,
    service: Annotated[CAPADomainService, Depends(_get_service)],
) -> SuccessResponse[CAPAResponse]:
    capa = await service.get_capa(capa_id)
    return SuccessResponse.of(CAPAResponse.model_validate(capa, from_attributes=True))


@router.patch("/{capa_id}", response_model=SuccessResponse[CAPAResponse],
              dependencies=[Depends(require_permission(Permission.CAPA_WRITE))],
              summary="Update a CAPA")
async def update_capa(
    capa_id: str,
    payload: UpdateCAPARequest,
    current_user: CurrentUser,
    service: Annotated[CAPADomainService, Depends(_get_service)],
) -> SuccessResponse[CAPAResponse]:
    fields = payload.model_dump(exclude_none=True)
    capa = await service.update_capa(capa_id, updated_by=current_user.sub, **fields)
    return SuccessResponse.of(CAPAResponse.model_validate(capa, from_attributes=True))


@router.post("/{capa_id}/close", response_model=SuccessResponse[CAPAResponse],
             dependencies=[Depends(require_permission(Permission.CAPA_APPROVE))],
             summary="Close a CAPA")
async def close_capa(
    capa_id: str,
    current_user: CurrentUser,
    service: Annotated[CAPADomainService, Depends(_get_service)],
) -> SuccessResponse[CAPAResponse]:
    capa = await service.close_capa(capa_id, closed_by=current_user.sub)
    return SuccessResponse.of(CAPAResponse.model_validate(capa, from_attributes=True))


@router.post("/{capa_id}/verify-effectiveness", response_model=SuccessResponse[CAPAResponse],
             dependencies=[Depends(require_permission(Permission.CAPA_APPROVE))],
             summary="Verify CAPA effectiveness")
async def verify_effectiveness(
    capa_id: str,
    payload: VerifyEffectivenessRequest,
    current_user: CurrentUser,
    service: Annotated[CAPADomainService, Depends(_get_service)],
) -> SuccessResponse[CAPAResponse]:
    capa = await service.verify_effectiveness(
        capa_id=capa_id, verified_by=current_user.sub,
        verified=payload.verified, notes=payload.notes,
    )
    return SuccessResponse.of(CAPAResponse.model_validate(capa, from_attributes=True))


@router.get("/{capa_id}/actions", response_model=SuccessResponse[list[CAPAActionResponse]],
            dependencies=[Depends(require_permission(Permission.CAPA_READ))],
            summary="List CAPA actions")
async def list_actions(
    capa_id: str,
    current_user: CurrentUser,
    service: Annotated[CAPADomainService, Depends(_get_service)],
) -> SuccessResponse[list[CAPAActionResponse]]:
    actions = await service.get_actions(capa_id)
    return SuccessResponse.of([CAPAActionResponse.model_validate(a, from_attributes=True) for a in actions])


@router.post("/{capa_id}/actions", response_model=SuccessResponse[CAPAActionResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.CAPA_WRITE))],
             summary="Add action to CAPA")
async def add_action(
    capa_id: str,
    payload: AddCAPAActionRequest,
    current_user: CurrentUser,
    service: Annotated[CAPADomainService, Depends(_get_service)],
) -> SuccessResponse[CAPAActionResponse]:
    action = await service.add_action(
        capa_id=capa_id,
        action_type=payload.action_type,
        description=payload.description,
        created_by=current_user.sub,
        assigned_to=payload.assigned_to,
        due_date=payload.due_date,
    )
    return SuccessResponse.of(CAPAActionResponse.model_validate(action, from_attributes=True))


@router.post("/{capa_id}/actions/{action_id}/complete", response_model=SuccessResponse[CAPAActionResponse],
             dependencies=[Depends(require_permission(Permission.CAPA_WRITE))],
             summary="Complete a CAPA action")
async def complete_action(
    capa_id: str,
    action_id: str,
    payload: CompleteActionRequest,
    current_user: CurrentUser,
    service: Annotated[CAPADomainService, Depends(_get_service)],
) -> SuccessResponse[CAPAActionResponse]:
    action = await service.complete_action(capa_id=capa_id, action_id=action_id, evidence=payload.evidence)
    return SuccessResponse.of(CAPAActionResponse.model_validate(action, from_attributes=True))
