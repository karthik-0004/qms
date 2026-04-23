"""Quality Event Service — Pydantic request schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class CreateQualityEventRequest(BaseModel):
    event_number: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    event_type: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    detected_at: datetime
    severity: str = "minor"
    priority: str = "medium"
    department: str | None = None
    location: str | None = None
    assigned_to: str | None = None
    immediate_action: str | None = None
    capa_required: bool = False
    due_date: datetime | None = None
    tags: list[str] = []


class UpdateQualityEventRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    severity: str | None = None
    priority: str | None = None
    department: str | None = None
    location: str | None = None
    assigned_to: str | None = None
    root_cause: str | None = None
    immediate_action: str | None = None
    capa_required: bool | None = None
    due_date: datetime | None = None
    tags: list[str] | None = None


class CloseQualityEventRequest(BaseModel):
    resolution: str | None = None
