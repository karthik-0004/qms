"""Technician Service — Technician management API routes."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.service import TechnicianDomainService
from app.schemas.requests import (
    AddCertificationRequest,
    RegisterTechnicianRequest,
    SetAvailabilityRequest,
    TransitionStatusRequest,
    UpdateTechnicianRequest,
)
from app.schemas.responses import CertificationResponse, TechnicianResponse

router = APIRouter(prefix="/technicians", tags=["Technicians"])
logger = structlog.get_logger(__name__)

TenantId = Annotated[UUID, Header(alias="x-tenant-id")]
UserId = Annotated[UUID, Header(alias="x-user-id")]


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> TechnicianDomainService:
    return TechnicianDomainService(db)


@router.get("", response_model=list[TechnicianResponse], summary="List technicians")
async def list_technicians(
    tenant_id: TenantId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
    status: str | None = Query(default=None),
    is_available: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[TechnicianResponse]:
    technicians = await service.list_technicians(
        tenant_id=tenant_id, status=status, is_available=is_available, skip=skip, limit=limit,
    )
    return [TechnicianResponse.model_validate(t, from_attributes=True) for t in technicians]


@router.post("", response_model=TechnicianResponse, status_code=201, summary="Register technician")
async def register_technician(
    payload: RegisterTechnicianRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> TechnicianResponse:
    fields = payload.model_dump(exclude={"user_id", "first_name", "last_name"})
    tech = await service.register_technician(
        tenant_id=tenant_id, created_by=user_id, user_id=payload.user_id,
        first_name=payload.first_name, last_name=payload.last_name, **fields,
    )
    return TechnicianResponse.model_validate(tech, from_attributes=True)


@router.get("/{tech_id}", response_model=TechnicianResponse, summary="Get technician")
async def get_technician(
    tech_id: UUID,
    tenant_id: TenantId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> TechnicianResponse:
    tech = await service.get_technician(tech_id, tenant_id)
    return TechnicianResponse.model_validate(tech, from_attributes=True)


@router.patch("/{tech_id}", response_model=TechnicianResponse, summary="Update technician")
async def update_technician(
    tech_id: UUID,
    payload: UpdateTechnicianRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> TechnicianResponse:
    fields = payload.model_dump(exclude_none=True)
    tech = await service.update_technician(tech_id, tenant_id, changed_by=user_id, **fields)
    return TechnicianResponse.model_validate(tech, from_attributes=True)


@router.post("/{tech_id}/status", response_model=TechnicianResponse, summary="Transition technician status")
async def transition_status(
    tech_id: UUID,
    payload: TransitionStatusRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> TechnicianResponse:
    tech = await service.transition_status(tech_id, tenant_id, payload.new_status, user_id)
    return TechnicianResponse.model_validate(tech, from_attributes=True)


@router.post("/{tech_id}/availability", response_model=TechnicianResponse, summary="Set availability")
async def set_availability(
    tech_id: UUID,
    payload: SetAvailabilityRequest,
    tenant_id: TenantId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> TechnicianResponse:
    tech = await service.set_availability(
        tech_id, tenant_id, is_available=payload.is_available,
        unavailable_reason=payload.unavailable_reason, available_from=payload.available_from,
    )
    return TechnicianResponse.model_validate(tech, from_attributes=True)


# ─── Certifications ──────────────────────────────────────────────────────

@router.get("/{tech_id}/certifications", response_model=list[CertificationResponse],
            summary="List certifications")
async def list_certifications(
    tech_id: UUID,
    tenant_id: TenantId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> list[CertificationResponse]:
    certs = await service.list_certifications(tech_id, tenant_id)
    return [CertificationResponse.model_validate(c, from_attributes=True) for c in certs]


@router.post("/{tech_id}/certifications", response_model=CertificationResponse, status_code=201,
             summary="Add certification")
async def add_certification(
    tech_id: UUID,
    payload: AddCertificationRequest,
    tenant_id: TenantId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> CertificationResponse:
    cert = await service.add_certification(
        tech_id, tenant_id, name=payload.name, issuing_body=payload.issuing_body,
        certificate_number=payload.certificate_number,
        issued_date=payload.issued_date, expiry_date=payload.expiry_date,
    )
    return CertificationResponse.model_validate(cert, from_attributes=True)
