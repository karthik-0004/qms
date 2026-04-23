"""AI Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class AnalysisRunResponse(BaseModel):
    id: str
    tenant_id: str
    plate_id: str
    image_id: str
    model_name: str
    model_version: str
    status: str
    triggered_by: str
    job_id: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: float | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class AnalysisResultResponse(BaseModel):
    id: str
    analysis_run_id: str
    tenant_id: str
    plate_id: str
    colony_count: int
    colony_positions: list
    confidence_score: float
    contamination_detected: bool
    contamination_type: str | None
    anomaly_flags: list
    raw_output: dict
    created_at: datetime
