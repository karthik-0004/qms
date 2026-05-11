"""Work Order Service — Pydantic request schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class CreateWorkOrderRequest(BaseModel):
    customer_id: UUID
    contract_id: UUID | None = None
    work_order_number: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    work_type: str = Field(min_length=1)
    description: str | None = None
    priority: str = "normal"
    site_address: str | None = None
    site_city: str | None = None
    site_state: str | None = None
    site_postal_code: str | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    estimated_hours: float | None = None
    notes: str | None = None


class TransitionStatusRequest(BaseModel):
    new_status: str = Field(min_length=1)
    comment: str | None = None


class AssignTechnicianRequest(BaseModel):
    technician_id: UUID


class AddTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    sort_order: int = 0


class CompleteTaskRequest(BaseModel):
    notes: str | None = None


class AddNoteRequest(BaseModel):
    body: str = Field(min_length=1)
    is_internal: bool = False
