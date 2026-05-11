"""Billing Service — Pydantic response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class InvoiceResponse(BaseModel):
    """Maps SQLAlchemy `Invoice` (paid_amount, balance_due, paid_date) to API field names."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    tenant_id: UUID
    customer_id: UUID
    contract_id: UUID | None
    work_order_id: UUID | None
    invoice_number: str
    status: str
    subtotal: float
    tax_amount: float
    total_amount: float
    amount_paid: float = Field(alias="paid_amount")
    amount_due: float = Field(alias="balance_due")
    currency: str
    tax_rate: float
    due_date: datetime | None
    paid_at: datetime | None = Field(alias="paid_date")
    notes: str | None
    payment_terms: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, inv) -> "InvoiceResponse":
        return cls.model_validate(inv, from_attributes=True)


class InvoiceLineItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    invoice_id: UUID
    description: str
    unit_price: float
    quantity: float
    unit: str | None
    tax_rate: float | None = None  # not persisted in DB schema
    line_total: float
    sort_order: int
    created_at: datetime

    @classmethod
    def from_model(cls, item) -> "InvoiceLineItemResponse":
        return cls.model_validate(item, from_attributes=True)


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    invoice_id: UUID
    tenant_id: UUID
    amount: float
    payment_method: str
    reference_number: str | None
    payment_date: datetime
    notes: str | None
    recorded_by: UUID = Field(alias="created_by")
    created_at: datetime

    @classmethod
    def from_model(cls, p) -> "PaymentResponse":
        return cls.model_validate(p, from_attributes=True)
