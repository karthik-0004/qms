"""Work Order Service — Pydantic response schemas."""

from __future__ import annotations

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

    @classmethod
    def from_model(cls, wo) -> "WorkOrderResponse":
        site = wo.site_address if isinstance(wo.site_address, dict) else {}
        meta = wo.metadata_ if isinstance(wo.metadata_, dict) else {}
        notes = meta.get("notes") if meta else None
        eh = wo.estimated_hours
        ah = wo.actual_hours
        return cls(
            id=wo.id,
            tenant_id=wo.tenant_id,
            customer_id=wo.customer_id,
            contract_id=wo.contract_id,
            wo_number=wo.work_order_number,
            title=wo.title,
            work_type=wo.work_order_type,
            description=wo.description,
            status=wo.status,
            priority=wo.priority,
            site_address=site.get("line1"),
            site_city=site.get("city"),
            site_state=site.get("state"),
            site_postal_code=site.get("postal_code"),
            assigned_technician_id=wo.assigned_technician_id,
            scheduled_start=wo.scheduled_start,
            scheduled_end=wo.scheduled_end,
            actual_start=wo.actual_start,
            actual_end=wo.actual_end,
            estimated_hours=float(eh) if eh is not None else None,
            actual_hours=float(ah) if ah is not None else None,
            notes=notes,
            created_by=wo.created_by,
            created_at=wo.created_at,
            updated_at=wo.updated_at,
        )


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

    @classmethod
    def from_model(cls, t) -> "WorkOrderTaskResponse":
        return cls(
            id=t.id,
            work_order_id=t.work_order_id,
            title=t.title,
            description=t.description,
            status="completed" if t.is_completed else "pending",
            sort_order=t.sort_order,
            completed_at=t.completed_at,
            completed_by=t.completed_by,
            created_at=t.created_at,
        )


class WorkOrderNoteResponse(BaseModel):
    id: UUID
    work_order_id: UUID
    author_id: UUID
    body: str
    is_internal: bool
    created_at: datetime

    @classmethod
    def from_model(cls, n) -> "WorkOrderNoteResponse":
        return cls(
            id=n.id,
            work_order_id=n.work_order_id,
            author_id=n.created_by,
            body=n.body,
            is_internal=n.is_internal,
            created_at=n.created_at,
        )
