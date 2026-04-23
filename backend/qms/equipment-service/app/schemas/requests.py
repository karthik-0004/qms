"""Equipment Service — Pydantic request schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class CreateEquipmentRequest(BaseModel):
    asset_tag: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=255)
    equipment_type: str = Field(min_length=1, max_length=100)
    description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    location: str | None = None
    department: str | None = None
    requires_calibration: bool = False
    calibration_frequency_days: int | None = None
    requires_pm: bool = False
    pm_frequency_days: int | None = None
    purchase_date: datetime | None = None
    warranty_expiry: datetime | None = None
    assigned_to: str | None = None
    notes: str | None = None
    tags: list[str] = []


class UpdateEquipmentRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    location: str | None = None
    department: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    assigned_to: str | None = None
    notes: str | None = None
    tags: list[str] | None = None
    warranty_expiry: datetime | None = None


class RecordCalibrationRequest(BaseModel):
    calibration_date: datetime
    passed: bool
    certificate_file_id: str | None = None
    notes: str | None = None


class DecommissionRequest(BaseModel):
    reason: str = Field(min_length=1)
