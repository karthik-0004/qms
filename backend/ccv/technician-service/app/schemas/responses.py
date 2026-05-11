"""Technician Service — Pydantic response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class TechnicianResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID | None
    first_name: str
    last_name: str
    email: str
    phone: str | None
    status: str
    specializations: list[str]
    service_area: str | None
    hourly_rate: float | None
    is_available: bool
    unavailable_reason: str | None
    notes: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, tech) -> "TechnicianResponse":
        service_regions = tech.service_regions if isinstance(tech.service_regions, list) else []
        service_area = service_regions[0] if service_regions else None
        specializations = tech.specializations if isinstance(tech.specializations, list) else []
        return cls(
            id=tech.id,
            tenant_id=tech.tenant_id,
            user_id=tech.user_id,
            first_name=tech.first_name,
            last_name=tech.last_name,
            email=tech.email,
            phone=tech.phone,
            status=tech.status,
            specializations=specializations,
            service_area=service_area,
            hourly_rate=float(tech.hourly_rate) if tech.hourly_rate is not None else None,
            is_available=tech.status == "available",
            unavailable_reason=None,
            notes=None,
            created_by=tech.created_by,
            created_at=tech.created_at,
            updated_at=tech.updated_at,
        )


class CertificationResponse(BaseModel):
    id: UUID
    technician_id: UUID
    name: str
    issuing_body: str | None
    certificate_number: str | None
    issued_date: datetime | None
    expiry_date: datetime | None
    created_at: datetime
