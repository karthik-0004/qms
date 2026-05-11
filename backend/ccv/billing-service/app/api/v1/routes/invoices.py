"""Billing Service — Invoice lifecycle API routes."""

from datetime import date, datetime, timezone
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.service import BillingDomainService
from app.schemas.requests import (
    AddLineItemRequest,
    CreateInvoiceRequest,
    RecordPaymentRequest,
    TransitionStatusRequest,
)
from app.schemas.responses import InvoiceLineItemResponse, InvoiceResponse, PaymentResponse

router = APIRouter(prefix="/invoices", tags=["Invoices"])
logger = structlog.get_logger(__name__)

TenantId = Annotated[UUID, Header(alias="x-tenant-id")]
UserId = Annotated[UUID, Header(alias="x-user-id")]


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> BillingDomainService:
    return BillingDomainService(db)


@router.get("", response_model=list[InvoiceResponse], summary="List invoices")
async def list_invoices(
    tenant_id: TenantId,
    service: Annotated[BillingDomainService, Depends(_get_service)],
    status: str | None = Query(default=None),
    customer_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[InvoiceResponse]:
    invoices = await service.list_invoices(
        tenant_id=tenant_id, status=status, customer_id=customer_id, skip=skip, limit=limit,
    )
    return [InvoiceResponse.from_model(i) for i in invoices]


@router.post("", response_model=InvoiceResponse, status_code=201, summary="Create invoice")
async def create_invoice(
    payload: CreateInvoiceRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[BillingDomainService, Depends(_get_service)],
) -> InvoiceResponse:
    fields = payload.model_dump(exclude={"customer_id", "invoice_number"})
    invoice = await service.create_invoice(
        tenant_id=tenant_id, customer_id=payload.customer_id, created_by=user_id,
        invoice_number=payload.invoice_number, **fields,
    )
    return InvoiceResponse.from_model(invoice)


@router.get("/{invoice_id}", response_model=InvoiceResponse, summary="Get invoice")
async def get_invoice(
    invoice_id: UUID,
    tenant_id: TenantId,
    service: Annotated[BillingDomainService, Depends(_get_service)],
) -> InvoiceResponse:
    invoice = await service.get_invoice(invoice_id, tenant_id)
    return InvoiceResponse.from_model(invoice)


@router.post("/{invoice_id}/status", response_model=InvoiceResponse, summary="Transition invoice status")
async def transition_status(
    invoice_id: UUID,
    payload: TransitionStatusRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[BillingDomainService, Depends(_get_service)],
) -> InvoiceResponse:
    invoice = await service.transition_status(
        invoice_id, tenant_id, payload.new_status, user_id, comment=payload.comment,
    )
    return InvoiceResponse.from_model(invoice)


# ─── Line Items ──────────────────────────────────────────────────────────

@router.get("/{invoice_id}/line-items", response_model=list[InvoiceLineItemResponse],
            summary="List invoice line items")
async def list_line_items(
    invoice_id: UUID,
    tenant_id: TenantId,
    service: Annotated[BillingDomainService, Depends(_get_service)],
) -> list[InvoiceLineItemResponse]:
    items = await service.list_line_items(invoice_id, tenant_id)
    return [InvoiceLineItemResponse.from_model(i) for i in items]


@router.post("/{invoice_id}/line-items", response_model=InvoiceLineItemResponse, status_code=201,
             summary="Add line item")
async def add_line_item(
    invoice_id: UUID,
    payload: AddLineItemRequest,
    tenant_id: TenantId,
    service: Annotated[BillingDomainService, Depends(_get_service)],
) -> InvoiceLineItemResponse:
    item = await service.add_line_item(
        invoice_id=invoice_id,
        tenant_id=tenant_id,
        description=payload.description,
        unit_price=payload.unit_price,
        quantity=payload.quantity,
        unit=payload.unit,
        sort_order=payload.sort_order,
    )
    return InvoiceLineItemResponse.from_model(item)


# ─── Payments ─────────────────────────────────────────────────────────────

@router.get("/{invoice_id}/payments", response_model=list[PaymentResponse], summary="List payments")
async def list_payments(
    invoice_id: UUID,
    tenant_id: TenantId,
    service: Annotated[BillingDomainService, Depends(_get_service)],
) -> list[PaymentResponse]:
    payments = await service.list_payments(invoice_id, tenant_id)
    return [PaymentResponse.from_model(p) for p in payments]


@router.post("/{invoice_id}/payments", response_model=PaymentResponse, status_code=201,
             summary="Record payment")
async def record_payment(
    invoice_id: UUID,
    payload: RecordPaymentRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[BillingDomainService, Depends(_get_service)],
) -> PaymentResponse:
    pay_date: date
    if payload.payment_date is not None:
        pay_date = (
            payload.payment_date.date()
            if isinstance(payload.payment_date, datetime)
            else payload.payment_date
        )
    else:
        pay_date = datetime.now(timezone.utc).date()
    payment = await service.record_payment(
        invoice_id=invoice_id,
        tenant_id=tenant_id,
        created_by=user_id,
        payment_method=payload.payment_method,
        amount=payload.amount,
        payment_date=pay_date,
        reference_number=payload.reference_number,
        notes=payload.notes,
    )
    return PaymentResponse.from_model(payment)
