"""Billing Service — Pydantic response schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class InvoiceResponse(BaseModel):
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
    amount_paid: float
    amount_due: float
    currency: str
    tax_rate: float
    due_date: datetime | None
    paid_at: datetime | None
    notes: str | None
    payment_terms: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class InvoiceLineItemResponse(BaseModel):
    id: UUID
    invoice_id: UUID
    description: str
    unit_price: float
    quantity: float
    unit: str | None
    tax_rate: float | None
    line_total: float
    sort_order: int
    created_at: datetime


class PaymentResponse(BaseModel):
    id: UUID
    invoice_id: UUID
    tenant_id: UUID
    amount: float
    payment_method: str
    reference_number: str | None
    payment_date: datetime
    notes: str | None
    recorded_by: UUID
    created_at: datetime
