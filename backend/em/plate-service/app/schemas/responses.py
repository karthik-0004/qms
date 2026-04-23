"""Plate Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class PlateResponse(BaseModel):
    id: str
    tenant_id: str
    barcode: str
    sample_type: str
    media_type: str
    incubation_temp_celsius: float | None
    incubation_hours: int | None
    location_code: str | None
    lot_number: str | None
    operator_id: str
    status: str
    notes: str | None
    sampled_at: datetime | None
    incubation_started_at: datetime | None
    incubation_completed_at: datetime | None
    created_by: str
    created_at: datetime
    updated_at: datetime


class PlateStatusHistoryResponse(BaseModel):
    id: str
    plate_id: str
    from_status: str | None
    to_status: str
    changed_by: str
    reason: str | None
    changed_at: datetime
