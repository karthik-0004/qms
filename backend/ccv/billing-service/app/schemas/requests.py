"""Billing Service — Pydantic request schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class CreateInvoiceRequest(BaseModel):
    customer_id: UUID
    contract_id: UUID | None = None
    work_order_id: UUID | None = None
    invoice_number: str = Field(min_length=1, max_length=100)
    due_date: datetime | None = None
    currency: str = "USD"
    tax_rate: float = 0.0
    notes: str | None = None
    payment_terms: str | None = None


class AddLineItemRequest(BaseModel):
    description: str = Field(min_length=1, max_length=500)
    unit_price: float = Field(ge=0)
    quantity: float = Field(default=1.0, gt=0)
    unit: str | None = None
    tax_rate: float | None = None
    sort_order: int = 0


class TransitionStatusRequest(BaseModel):
    new_status: str = Field(min_length=1)
    comment: str | None = None


class RecordPaymentRequest(BaseModel):
    amount: float = Field(gt=0)
    payment_method: str = Field(min_length=1)
    reference_number: str | None = None
    payment_date: datetime | None = None
    notes: str | None = None
