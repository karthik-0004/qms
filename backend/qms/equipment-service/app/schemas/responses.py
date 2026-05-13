"""Equipment Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EquipmentResponse(BaseModel):
    id: str
    tenant_id: str
    asset_tag: str
    name: str
    description: str | None
    equipment_type: str
    manufacturer: str | None
    model: str | None
    serial_number: str | None
    location: str | None
    department: str | None
    status: str
    requires_calibration: bool
    calibration_frequency_days: int | None
    last_calibration_date: datetime | None
    next_calibration_date: datetime | None
    requires_pm: bool
    pm_frequency_days: int | None
    last_pm_date: datetime | None
    next_pm_date: datetime | None
    purchase_date: datetime | None
    warranty_expiry: datetime | None
    assigned_to: str | None
    notes: str | None
    tags: list
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CalibrationRecordResponse(BaseModel):
    id: str
    equipment_id: str
    tenant_id: str
    calibration_date: datetime
    performed_by: str
    passed: bool
    result: str
    standards_used: str | None
    as_found_readings: str | None
    as_left_readings: str | None
    measurement_uncertainty: str | None
    notes: str | None
    next_due_date: datetime | None
    certificate_file_id: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
