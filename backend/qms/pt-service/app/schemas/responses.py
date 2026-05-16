"""PT Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class PTProgramResponse(BaseModel):
    id: str
    tenant_id: str
    provider: str
    scheme_name: str
    parameter: str
    frequency_months: int
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


class PTRoundResponse(BaseModel):
    id: str
    tenant_id: str
    program_id: str
    round_id: str
    sample_received_date: datetime | None
    result_due_date: datetime | None
    reported_result: float | None
    reference_value: float | None
    z_score: float | None
    en_number: float | None
    status: str
    capa_id: str | None
    notes: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime


class PTScoreResponse(BaseModel):
    round_id: str
    reported_result: float
    reference_value: float
    z_score: float
    en_number: float
    z_score_pass: bool
    en_number_pass: bool
