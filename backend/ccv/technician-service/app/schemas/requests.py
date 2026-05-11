"""Technician Service — Pydantic request schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class RegisterTechnicianRequest(BaseModel):
    user_id: UUID
    employee_number: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    phone: str | None = None
    specializations: list[str] = []
    service_area: str | None = None
    hourly_rate: float | None = None
    notes: str | None = None


class UpdateTechnicianRequest(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = None
    phone: str | None = None
    specializations: list[str] | None = None
    service_area: str | None = None
    hourly_rate: float | None = None
    notes: str | None = None


class TransitionStatusRequest(BaseModel):
    new_status: str = Field(min_length=1)


class AddCertificationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    issuing_body: str | None = None
    certificate_number: str | None = None
    issued_date: datetime | None = None
    expiry_date: datetime | None = None


class SetAvailabilityRequest(BaseModel):
    is_available: bool
    unavailable_reason: str | None = None
    available_from: datetime | None = None
