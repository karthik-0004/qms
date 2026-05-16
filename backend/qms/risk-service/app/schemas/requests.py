"""Risk Service — Pydantic request schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class CreateRiskRequest(BaseModel):
    risk_id: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1)
    severity: int = Field(ge=1, le=5)
    likelihood: int = Field(ge=1, le=5)
    mitigation_plan: str | None = None
    owner_id: str | None = None
    review_date: datetime | None = None


class UpdateRiskRequest(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    severity: int | None = Field(default=None, ge=1, le=5)
    likelihood: int | None = Field(default=None, ge=1, le=5)
    mitigation_plan: str | None = None
    owner_id: str | None = None
    status: str | None = None
    review_date: datetime | None = None
