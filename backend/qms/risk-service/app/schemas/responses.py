"""Risk Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class RiskResponse(BaseModel):
    id: str
    tenant_id: str
    risk_id: str
    category: str
    description: str
    severity: int
    likelihood: int
    risk_score: int
    mitigation_plan: str | None
    owner_id: str | None
    status: str
    review_date: datetime | None
    created_by: str
    created_at: datetime
    updated_at: datetime


class RiskMatrixCell(BaseModel):
    severity: int
    likelihood: int
    count: int
    risk_ids: list[str]
