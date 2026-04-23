"""Quality Event Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class QualityEventResponse(BaseModel):
    id: str
    tenant_id: str
    event_number: str
    title: str
    event_type: str
    description: str
    status: str
    severity: str
    priority: str
    department: str | None
    location: str | None
    detected_at: datetime
    detected_by: str | None
    assigned_to: str | None
    root_cause: str | None
    immediate_action: str | None
    capa_required: bool
    capa_id: str | None
    due_date: datetime | None
    closed_at: datetime | None
    tags: list
    created_by: str
    created_at: datetime
    updated_at: datetime


class QualityEventSummaryResponse(BaseModel):
    by_status: dict
    tenant_id: str
