"""PT Service — Pydantic request schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class CreatePTProgramRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=255)
    scheme_name: str = Field(min_length=1, max_length=255)
    parameter: str = Field(min_length=1, max_length=100)
    frequency_months: int = Field(ge=1)


class CreatePTRoundRequest(BaseModel):
    program_id: str
    round_id: str = Field(min_length=1, max_length=100)
    sample_received_date: datetime | None = None
    result_due_date: datetime | None = None
    notes: str | None = None


class UpdatePTRoundRequest(BaseModel):
    sample_received_date: datetime | None = None
    result_due_date: datetime | None = None
    reported_result: float | None = None
    reference_value: float | None = None
    z_score: float | None = None
    en_number: float | None = None
    status: str | None = None
    capa_id: str | None = None
    notes: str | None = None
