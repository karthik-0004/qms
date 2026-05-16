"""Audit Management Service — API routes."""

from datetime import datetime
from typing import Annotated, Optional

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_permission
from rainer_auth_lib.permissions import Permission
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.database import get_db
from ....domain.services import AuditDomainService
from ....infra.db.repositories import AuditRepository, ChecklistRepository
from ....schemas.requests import (
    ChecklistResponseRequest, CreateAuditRequest, CreateChecklistRequest,
    CreateFindingRequest, UpdateAuditRequest, UpdateFindingRequest,
)
from ....schemas.responses import (
    AuditChecklistResponse, AuditFindingResponse, AuditResponse, AuditSummaryResponse,
    ChecklistResponseRecord,
)

router = APIRouter(prefix="/audits", tags=["Audit Management"])
logger = structlog.get_logger(__name__)


def _get_service(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]) -> AuditDomainService:
    return AuditDomainService(
        repo=AuditRepository(db),
        checklist_repo=ChecklistRepository(db),
        tenant_id=current_user.tenant_id or "",
    )


def _audit_resp(audit) -> AuditResponse:
    d = AuditResponse.model_validate(audit, from_attributes=True)
    d.finding_count = len(audit.findings)
    d.major_nc_count = sum(1 for f in audit.findings if f.classification == "major_nc")
    d.minor_nc_count = sum(1 for f in audit.findings if f.classification == "minor_nc")
    return d


@router.get("", response_model=PaginatedResponse[AuditResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="List audits")
async def list_audits(
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    status: Optional[str] = Query(default=None),
    audit_type: Optional[str] = Query(default=None),
) -> PaginatedResponse[AuditResponse]:
    items, total = await service.list_audits(
        status=status, audit_type=audit_type,
        page=pagination.page, page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[_audit_resp(a) for a in items],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.get("/calendar", response_model=SuccessResponse[list[AuditResponse]],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="Get audit calendar data")
async def get_calendar(
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
    from_date: datetime = Query(...),
    to_date: datetime = Query(...),
) -> SuccessResponse[list[AuditResponse]]:
    items = await service.get_calendar(from_date, to_date)
    return SuccessResponse.of([_audit_resp(a) for a in items])


@router.post("", response_model=SuccessResponse[AuditResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Create audit")
async def create_audit(
    payload: CreateAuditRequest,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> SuccessResponse[AuditResponse]:
    fields = payload.model_dump()
    audit = await service.create_audit(created_by=current_user.sub, **fields)
    return SuccessResponse.of(_audit_resp(audit))


@router.get("/{audit_id}", response_model=SuccessResponse[AuditResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="Get audit")
async def get_audit(
    audit_id: str,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> SuccessResponse[AuditResponse]:
    audit = await service.get_audit(audit_id)
    return SuccessResponse.of(_audit_resp(audit))


@router.patch("/{audit_id}", response_model=SuccessResponse[AuditResponse],
              dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
              summary="Update audit")
async def update_audit(
    audit_id: str,
    payload: UpdateAuditRequest,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> SuccessResponse[AuditResponse]:
    fields = payload.model_dump(exclude_none=True)
    audit = await service.update_audit(audit_id, **fields)
    return SuccessResponse.of(_audit_resp(audit))


@router.post("/{audit_id}/start", response_model=SuccessResponse[AuditResponse],
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Start audit")
async def start_audit(
    audit_id: str,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> SuccessResponse[AuditResponse]:
    audit = await service.start_audit(audit_id)
    return SuccessResponse.of(_audit_resp(audit))


@router.post("/{audit_id}/complete", response_model=SuccessResponse[AuditResponse],
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Complete audit")
async def complete_audit(
    audit_id: str,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
    summary: Optional[str] = None,
) -> SuccessResponse[AuditResponse]:
    audit = await service.complete_audit(audit_id, summary=summary)
    return SuccessResponse.of(_audit_resp(audit))


@router.delete("/{audit_id}", response_model=MessageResponse,
               dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
               summary="Delete audit")
async def delete_audit(
    audit_id: str,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.delete_audit(audit_id)
    return MessageResponse.of("Audit deleted.")


@router.post("/{audit_id}/findings", response_model=SuccessResponse[AuditFindingResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Add finding to audit")
async def add_finding(
    audit_id: str,
    payload: CreateFindingRequest,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> SuccessResponse[AuditFindingResponse]:
    fields = payload.model_dump()
    finding = await service.add_finding(audit_id=audit_id, created_by=current_user.sub, **fields)
    return SuccessResponse.of(AuditFindingResponse.model_validate(finding, from_attributes=True))


@router.get("/{audit_id}/findings", response_model=SuccessResponse[list[AuditFindingResponse]],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="List findings for audit")
async def list_findings(
    audit_id: str,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> SuccessResponse[list[AuditFindingResponse]]:
    findings = await service.list_findings(audit_id)
    return SuccessResponse.of([AuditFindingResponse.model_validate(f, from_attributes=True) for f in findings])


@router.patch("/findings/{finding_id}", response_model=SuccessResponse[AuditFindingResponse],
              dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
              summary="Update finding")
async def update_finding(
    finding_id: str,
    payload: UpdateFindingRequest,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> SuccessResponse[AuditFindingResponse]:
    fields = payload.model_dump(exclude_none=True)
    finding = await service.update_finding(finding_id, **fields)
    return SuccessResponse.of(AuditFindingResponse.model_validate(finding, from_attributes=True))


# ── Checklists ──────────────────────────────────────────────────────────────

checklists_router = APIRouter(prefix="/checklists", tags=["Audit Checklists"])


@checklists_router.get("", response_model=SuccessResponse[list[AuditChecklistResponse]],
                       dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))])
async def list_checklists(
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> SuccessResponse[list[AuditChecklistResponse]]:
    items = await service.list_checklists()
    return SuccessResponse.of([AuditChecklistResponse.model_validate(c, from_attributes=True) for c in items])


@checklists_router.post("", response_model=SuccessResponse[AuditChecklistResponse], status_code=201,
                        dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))])
async def create_checklist(
    payload: CreateChecklistRequest,
    current_user: CurrentUser,
    service: Annotated[AuditDomainService, Depends(_get_service)],
) -> SuccessResponse[AuditChecklistResponse]:
    fields = payload.model_dump()
    checklist = await service.create_checklist(created_by=current_user.sub, **fields)
    return SuccessResponse.of(AuditChecklistResponse.model_validate(checklist, from_attributes=True))
