"""AI Service — Pydantic request schemas."""

from pydantic import BaseModel, Field


class CreateAnalysisRunRequest(BaseModel):
    plate_id: str
    image_id: str
    job_id: str | None = None
    model_name: str | None = None
    model_version: str | None = None


class CompleteRunRequest(BaseModel):
    colony_count: int = Field(ge=0)
    colony_positions: list = []
    confidence_score: float = Field(ge=0.0, le=1.0)
    contamination_detected: bool = False
    contamination_type: str | None = None
    anomaly_flags: list = []
    raw_output: dict = {}


class FailRunRequest(BaseModel):
    error_message: str = Field(min_length=1)
