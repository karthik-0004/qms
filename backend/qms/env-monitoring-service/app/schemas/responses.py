"""Env Monitoring Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class MonitoringPointResponse(BaseModel):
    id: str
    tenant_id: str
    point_id: str
    location: str
    parameter: str
    alert_limit: float | None
    action_limit: float | None
    frequency_type: str
    frequency_value: int | None
    status: str
    last_reading_value: float | None
    last_reading_at: datetime | None
    created_by: str
    created_at: datetime
    updated_at: datetime


class MonitoringReadingResponse(BaseModel):
    id: str
    tenant_id: str
    point_id: str
    value: float
    recorded_at: datetime
    recorded_by_user_id: str | None
    status: str
    notes: str | None
    created_at: datetime
