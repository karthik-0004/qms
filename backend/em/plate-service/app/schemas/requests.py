"""Plate Service — Pydantic request schemas."""

from pydantic import BaseModel, Field


class RegisterPlateRequest(BaseModel):
    barcode: str = Field(min_length=1, max_length=100)
    sample_type: str = Field(min_length=1, max_length=100)
    media_type: str = Field(min_length=1, max_length=100)
    location_code: str | None = None
    lot_number: str | None = None
    notes: str | None = None
    incubation_temp_celsius: float | None = None
    incubation_hours: int | None = None
    metadata: dict = {}


class TransitionStatusRequest(BaseModel):
    new_status: str = Field(min_length=1)
    reason: str | None = None
