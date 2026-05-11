import uuid
from datetime import datetime, timezone, date
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.repository import InvoiceRepository, InvoiceLineItemRepository, PaymentRepository
from app.infra.db.models import Invoice, InvoiceLineItem, Payment

logger = structlog.get_logger()

VALID_INVOICE_TRANSITIONS: dict[str, list[str]] = {
    "draft":           ["sent", "cancelled"],
    "sent":            ["partially_paid", "paid", "overdue", "cancelled"],
    "partially_paid":  ["paid", "overdue", "cancelled"],
    "paid":            [],
    "overdue":         ["paid", "partially_paid", "cancelled"],
    "cancelled":       [],
}

VALID_PAYMENT_METHODS = {
    "bank_transfer", "credit_card", "cheque", "cash", "ach", "wire", "other"
}


class BillingDomainService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._invoices = InvoiceRepository(session)
        self._line_items = InvoiceLineItemRepository(session)
        self._payments = PaymentRepository(session)

    # ─── Invoices ────────────────────────────────────────────────────────────

    async def create_invoice(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID,
        created_by: uuid.UUID,
        invoice_number: str,
        currency: str = "USD",
        **kwargs,
    ) -> Invoice:
        existing = await self._invoices.get_by_number(invoice_number, tenant_id)
        if existing:
            raise ValueError(f"Invoice number '{invoice_number}' already exists")

        invoice = await self._invoices.create({
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "created_by": created_by,
            "invoice_number": invoice_number,
            "currency": currency,
            "status": "draft",
            "subtotal": 0,
            "tax_amount": 0,
            "total_amount": 0,
            "paid_amount": 0,
            "balance_due": 0,
            **kwargs,
        })
        logger.info("invoice.created", invoice_id=str(invoice.id))
        return invoice

    async def get_invoice(self, invoice_id: uuid.UUID, tenant_id: uuid.UUID) -> Invoice:
        invoice = await self._invoices.get_by_id(invoice_id, tenant_id)
        if not invoice:
            raise LookupError(f"Invoice {invoice_id} not found")
        return invoice

    async def list_invoices(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Invoice]:
        return await self._invoices.list(
            tenant_id, customer_id=customer_id, status=status, skip=skip, limit=limit
        )

    async def list_line_items(
        self, invoice_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[InvoiceLineItem]:
        await self.get_invoice(invoice_id, tenant_id)
        return await self._line_items.list_for_invoice(invoice_id)

    async def add_line_item(
        self,
        invoice_id: uuid.UUID,
        tenant_id: uuid.UUID,
        description: str,
        unit_price: float,
        quantity: float = 1.0,
        unit: str | None = None,
        sort_order: int = 0,
    ) -> InvoiceLineItem:
        invoice = await self.get_invoice(invoice_id, tenant_id)
        if invoice.status != "draft":
            raise ValueError("Line items can only be added to draft invoices")

        line_total = round(unit_price * quantity, 2)
        item = await self._line_items.create({
            "invoice_id": invoice_id,
            "description": description,
            "unit_price": unit_price,
            "quantity": quantity,
            "unit": unit,
            "line_total": line_total,
            "sort_order": sort_order,
        })

        new_subtotal = float(invoice.subtotal or 0) + line_total
        tax_amount = round(new_subtotal * float(invoice.tax_rate or 0), 2)
        total = round(new_subtotal + tax_amount - float(invoice.discount_amount or 0), 2)
        await self._invoices.update(invoice, {
            "subtotal": new_subtotal,
            "tax_amount": tax_amount,
            "total_amount": total,
            "balance_due": round(total - float(invoice.paid_amount or 0), 2),
        })
        return item

    async def send_invoice(
        self,
        invoice_id: uuid.UUID,
        tenant_id: uuid.UUID,
        changed_by: uuid.UUID,
        due_date: date | None = None,
    ) -> Invoice:
        invoice = await self.get_invoice(invoice_id, tenant_id)
        if invoice.status != "draft":
            raise ValueError("Only draft invoices can be sent")
        if float(invoice.total_amount or 0) <= 0:
            logger.warning(
                "invoice.send_zero_total",
                invoice_id=str(invoice_id),
                total_amount=float(invoice.total_amount or 0),
            )

        update_data: dict = {
            "status": "sent",
            "sent_at": datetime.now(timezone.utc),
            "issue_date": date.today(),
            "changed_by": changed_by,
        }
        if due_date:
            update_data["due_date"] = due_date

        invoice = await self._invoices.update(invoice, update_data)
        logger.info("invoice.sent", invoice_id=str(invoice_id))
        return invoice

    async def transition_status(
        self,
        invoice_id: uuid.UUID,
        tenant_id: uuid.UUID,
        new_status: str,
        changed_by: uuid.UUID,
        comment: str | None = None,
    ) -> Invoice:
        invoice = await self.get_invoice(invoice_id, tenant_id)
        allowed = VALID_INVOICE_TRANSITIONS.get(invoice.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition invoice from '{invoice.status}' to '{new_status}'"
            )
        update_data: dict = {"status": new_status, "changed_by": changed_by}
        # Match send_invoice behaviour when marking draft → sent (issue date, timestamps).
        if invoice.status == "draft" and new_status == "sent":
            if float(invoice.total_amount or 0) <= 0:
                logger.warning(
                    "invoice.transition_sent_zero_total",
                    invoice_id=str(invoice_id),
                    total_amount=float(invoice.total_amount or 0),
                )
            update_data["sent_at"] = datetime.now(timezone.utc)
            update_data["issue_date"] = date.today()
        if comment:
            logger.info(
                "invoice.status_transition",
                invoice_id=str(invoice_id),
                new_status=new_status,
                comment=comment,
            )
        invoice = await self._invoices.update(invoice, update_data)
        return invoice

    # ─── Payments ────────────────────────────────────────────────────────────

    async def record_payment(
        self,
        invoice_id: uuid.UUID,
        tenant_id: uuid.UUID,
        created_by: uuid.UUID,
        payment_method: str,
        amount: float,
        payment_date: date,
        reference_number: str | None = None,
        notes: str | None = None,
    ) -> Payment:
        if payment_method not in VALID_PAYMENT_METHODS:
            raise ValueError(f"Invalid payment_method: {payment_method}")
        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        invoice = await self.get_invoice(invoice_id, tenant_id)
        if invoice.status in ("cancelled",):
            raise ValueError("Cannot record payment for a cancelled invoice")

        payment = await self._payments.create({
            "tenant_id": tenant_id,
            "invoice_id": invoice_id,
            "created_by": created_by,
            "payment_method": payment_method,
            "amount": amount,
            "payment_date": payment_date,
            "reference_number": reference_number,
            "notes": notes,
            "currency": invoice.currency,
        })

        total_paid = await self._payments.total_paid(invoice_id)
        balance_due = round(float(invoice.total_amount or 0) - total_paid, 2)

        new_status = invoice.status
        if balance_due <= 0:
            new_status = "paid"
        elif total_paid > 0:
            new_status = "partially_paid"

        await self._invoices.update(invoice, {
            "paid_amount": total_paid,
            "balance_due": max(balance_due, 0),
            "status": new_status,
            "paid_date": payment_date if new_status == "paid" else None,
            "changed_by": created_by,
        })
        logger.info(
            "payment.recorded",
            invoice_id=str(invoice_id),
            amount=amount,
            new_status=new_status,
        )
        return payment

    async def list_payments(
        self, invoice_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[Payment]:
        await self.get_invoice(invoice_id, tenant_id)
        return await self._payments.list_for_invoice(invoice_id)
