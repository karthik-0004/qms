"""Complaints Service — Pydantic request schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class CreateComplaintRequest(BaseModel):
    complaint_number: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    received_at: datetime
    customer_name: str | None = None
    received_via: str = "email"
    severity: str = "minor"
    category: str | None = None
    investigator_id: str | None = None


class UpdateComplaintRequest(BaseModel):
    customer_name: str | None = None
    received_via: str | None = None
    severity: str | None = None
    category: str | None = None
    description: str | None = None
    status: str | None = None
    investigator_id: str | None = None
    root_cause: str | None = None
    capa_id: str | None = None


class RespondToComplaintRequest(BaseModel):
    response_text: str = Field(min_length=1)


class EscalateToCapaRequest(BaseModel):
    capa_id: str = Field(min_length=1)
