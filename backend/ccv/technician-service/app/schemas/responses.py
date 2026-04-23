"""Technician Service — Pydantic response schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class TechnicianResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    status: str
    specializations: list
    service_area: str | None
    hourly_rate: float | None
    is_available: bool
    unavailable_reason: str | None
    notes: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class CertificationResponse(BaseModel):
    id: UUID
    technician_id: UUID
    name: str
    issuing_body: str | None
    certificate_number: str | None
    issued_date: datetime | None
    expiry_date: datetime | None
    created_at: datetime
