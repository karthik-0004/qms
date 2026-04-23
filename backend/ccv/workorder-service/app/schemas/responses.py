"""Work Order Service — Pydantic response schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class WorkOrderResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    contract_id: UUID | None
    wo_number: str
    title: str
    work_type: str
    description: str | None
    status: str
    priority: str
    site_address: str | None
    site_city: str | None
    site_state: str | None
    site_postal_code: str | None
    assigned_technician_id: UUID | None
    scheduled_start: datetime | None
    scheduled_end: datetime | None
    actual_start: datetime | None
    actual_end: datetime | None
    estimated_hours: float | None
    actual_hours: float | None
    notes: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class WorkOrderTaskResponse(BaseModel):
    id: UUID
    work_order_id: UUID
    title: str
    description: str | None
    status: str
    sort_order: int
    completed_at: datetime | None
    completed_by: UUID | None
    created_at: datetime


class WorkOrderNoteResponse(BaseModel):
    id: UUID
    work_order_id: UUID
    author_id: UUID
    body: str
    is_internal: bool
    created_at: datetime
