"""CAPA Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class CAPAResponse(BaseModel):
    id: str
    tenant_id: str
    capa_number: str
    title: str
    capa_type: str
    description: str
    status: str
    severity: str
    root_cause: str | None
    root_cause_method: str | None
    source_type: str | None
    source_id: str | None
    owner_id: str | None
    department: str | None
    due_date: datetime | None
    target_close_date: datetime | None
    actual_close_date: datetime | None
    effectiveness_verified: bool
    effectiveness_check_date: datetime | None
    tags: list
    created_by: str
    created_at: datetime
    updated_at: datetime


class CAPAActionResponse(BaseModel):
    id: str
    capa_id: str
    action_type: str
    description: str
    assigned_to: str | None
    due_date: datetime | None
    status: str
    completed_at: datetime | None
    evidence: str | None
    created_at: datetime
