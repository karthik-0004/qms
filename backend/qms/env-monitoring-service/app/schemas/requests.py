"""Env Monitoring Service — Pydantic request schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class CreateMonitoringPointRequest(BaseModel):
    point_id: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=255)
    parameter: str = Field(min_length=1, max_length=100)
    alert_limit: float | None = None
    action_limit: float | None = None
    frequency_type: str = Field(min_length=1, max_length=50)
    frequency_value: int | None = None


class UpdateMonitoringPointRequest(BaseModel):
    location: str | None = Field(default=None, min_length=1, max_length=255)
    parameter: str | None = Field(default=None, min_length=1, max_length=100)
    alert_limit: float | None = None
    action_limit: float | None = None
    frequency_type: str | None = None
    frequency_value: int | None = None
    status: str | None = None


class AddReadingRequest(BaseModel):
    value: float
    recorded_at: datetime
    recorded_by_user_id: str | None = None
    notes: str | None = None
