"""Contract Service — Pydantic request schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class CreateContractRequest(BaseModel):
    customer_id: UUID
    contract_number: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    contract_type: str = Field(min_length=1)
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    total_value: float | None = None
    currency: str = "USD"
    payment_terms: str | None = None
    notes: str | None = None


class TransitionStatusRequest(BaseModel):
    new_status: str = Field(min_length=1)
    comment: str | None = None


class AddLineItemRequest(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    unit_price: float = Field(ge=0)
    quantity: float = Field(default=1.0, gt=0)
    unit: str | None = None
    sort_order: int = 0
