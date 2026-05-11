"""Technician Service — Technician management API routes."""

from datetime import datetime, timedelta, timezone
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
    return [TechnicianResponse.from_model(t) for t in technicians]


@router.post("", response_model=TechnicianResponse, status_code=201, summary="Register technician")
async def register_technician(
    payload: RegisterTechnicianRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> TechnicianResponse:
    fields = payload.model_dump(
        exclude={
            "user_id",
            "employee_number",
            "first_name",
            "last_name",
            "email",
            "service_area",
            "notes",
        }
    )
    service_regions = [payload.service_area] if payload.service_area else None
    tech = await service.register_technician(
        tenant_id=tenant_id,
        created_by=user_id,
        employee_number=payload.employee_number,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        user_id=payload.user_id,
        service_regions=service_regions,
        **fields,
    )
    return TechnicianResponse.from_model(tech)


@router.get("/{tech_id}", response_model=TechnicianResponse, summary="Get technician")
async def get_technician(
    tech_id: UUID,
    tenant_id: TenantId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> TechnicianResponse:
    tech = await service.get_technician(tech_id, tenant_id)
    return TechnicianResponse.from_model(tech)


@router.patch("/{tech_id}", response_model=TechnicianResponse, summary="Update technician")
async def update_technician(
    tech_id: UUID,
    payload: UpdateTechnicianRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> TechnicianResponse:
    fields = payload.model_dump(exclude_none=True)
    if "service_area" in fields:
        service_area = fields.pop("service_area")
        fields["service_regions"] = [service_area] if service_area else None
    fields.pop("notes", None)
    tech = await service.update_technician(tech_id, tenant_id, changed_by=user_id, **fields)
    return TechnicianResponse.from_model(tech)


@router.post("/{tech_id}/status", response_model=TechnicianResponse, summary="Transition technician status")
async def transition_status(
    tech_id: UUID,
    payload: TransitionStatusRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> TechnicianResponse:
    tech = await service.transition_status(tech_id, tenant_id, payload.new_status, user_id)
    return TechnicianResponse.from_model(tech)


@router.post("/{tech_id}/availability", response_model=TechnicianResponse, summary="Set availability")
async def set_availability(
    tech_id: UUID,
    payload: SetAvailabilityRequest,
    tenant_id: TenantId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> TechnicianResponse:
    start = payload.available_from or datetime.now(timezone.utc)
    end = start + timedelta(hours=8)
    avail_type = "available" if payload.is_available else "unavailable"
    await service.set_availability(
        tech_id,
        tenant_id,
        availability_type=avail_type,
        start_dt=start,
        end_dt=end,
        notes=payload.unavailable_reason,
    )
    tech = await service.get_technician(tech_id, tenant_id)
    return TechnicianResponse.from_model(tech)


# ─── Certifications ──────────────────────────────────────────────────────

@router.get("/{tech_id}/certifications", response_model=list[CertificationResponse],
            summary="List certifications")
async def list_certifications(
    tech_id: UUID,
    tenant_id: TenantId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
) -> list[CertificationResponse]:
    certs = await service.list_certifications(tech_id, tenant_id)
    return [CertificationResponse.from_model(c) for c in certs]


@router.post("/{tech_id}/certifications", response_model=CertificationResponse, status_code=201,
             summary="Add certification")
async def add_certification(
    tech_id: UUID,
    payload: AddCertificationRequest,
    tenant_id: TenantId,
    service: Annotated[TechnicianDomainService, Depends(_get_service)],
    x_user_id: UUID | None = Header(default=None, alias="x-user-id"),
) -> CertificationResponse:
    tech = await service.get_technician(tech_id, tenant_id)
    created_by = x_user_id or tech.user_id or tech.created_by
    issued = payload.issued_date.date() if payload.issued_date else None
    expires = payload.expiry_date.date() if payload.expiry_date else None
    cert = await service.add_certification(
        tech_id,
        tenant_id,
        created_by=created_by,
        certification_name=payload.name,
        issuing_body=payload.issuing_body,
        certificate_number=payload.certificate_number,
        issued_date=issued,
        expiry_date=expires,
    )
    return CertificationResponse.from_model(cert)
