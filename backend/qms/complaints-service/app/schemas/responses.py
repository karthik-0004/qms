"""Complaints Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class ComplaintResponse(BaseModel):
    id: str
    tenant_id: str
    complaint_number: str
    customer_name: str | None
    received_via: str
    severity: str
    category: str | None
    description: str
    status: str
    investigator_id: str | None
    root_cause: str | None
    response_text: str | None
    response_sent_at: datetime | None
    capa_id: str | None
    received_at: datetime
    created_by: str
    created_at: datetime
    updated_at: datetime
