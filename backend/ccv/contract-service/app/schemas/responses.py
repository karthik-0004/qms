"""Contract Service — Pydantic response schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ContractResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    contract_number: str
    title: str
    contract_type: str
    description: str | None
    status: str
    start_date: datetime | None
    end_date: datetime | None
    total_value: float | None
    currency: str
    payment_terms: str | None
    notes: str | None
    approved_at: datetime | None
    approved_by: UUID | None
    signed_at: datetime | None
    signed_by: UUID | None
    terminated_at: datetime | None
    termination_reason: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class ContractLineItemResponse(BaseModel):
    id: UUID
    contract_id: UUID
    description: str
    unit_price: float
    quantity: float
    unit: str | None
    total_price: float
    sort_order: int
    created_at: datetime


class ContractHistoryResponse(BaseModel):
    id: UUID
    contract_id: UUID
    from_status: str | None
    to_status: str
    changed_by: UUID
    comment: str | None
    created_at: datetime
