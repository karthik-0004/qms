import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.infra.db.models import Invoice, InvoiceLineItem, Payment


class InvoiceRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> Invoice:
        invoice = Invoice(**data)
        self._session.add(invoice)
        await self._session.flush()
        await self._session.refresh(invoice)
        return invoice

    async def get_by_id(self, invoice_id: uuid.UUID, tenant_id: uuid.UUID) -> Invoice | None:
        result = await self._session.execute(
            select(Invoice).where(
                and_(
                    Invoice.id == invoice_id,
                    Invoice.tenant_id == tenant_id,
                    Invoice.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, invoice_number: str, tenant_id: uuid.UUID) -> Invoice | None:
        result = await self._session.execute(
            select(Invoice).where(
                and_(
                    Invoice.invoice_number == invoice_number,
                    Invoice.tenant_id == tenant_id,
                    Invoice.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Invoice]:
        stmt = select(Invoice).where(
            and_(Invoice.tenant_id == tenant_id, Invoice.deleted_at.is_(None))
        )
        if customer_id:
            stmt = stmt.where(Invoice.customer_id == customer_id)
        if status:
            stmt = stmt.where(Invoice.status == status)
        stmt = stmt.offset(skip).limit(limit).order_by(Invoice.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, invoice: Invoice, data: dict) -> Invoice:
        for key, value in data.items():
            setattr(invoice, key, value)
        await self._session.flush()
        await self._session.refresh(invoice)
        return invoice

    async def soft_delete(self, invoice: Invoice) -> None:
        invoice.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()


class InvoiceLineItemRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> InvoiceLineItem:
        item = InvoiceLineItem(**data)
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def list_for_invoice(self, invoice_id: uuid.UUID) -> list[InvoiceLineItem]:
        result = await self._session.execute(
            select(InvoiceLineItem)
            .where(InvoiceLineItem.invoice_id == invoice_id)
            .order_by(InvoiceLineItem.sort_order)
        )
        return list(result.scalars().all())


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> Payment:
        payment = Payment(**data)
        self._session.add(payment)
        await self._session.flush()
        await self._session.refresh(payment)
        return payment

    async def list_for_invoice(self, invoice_id: uuid.UUID) -> list[Payment]:
        result = await self._session.execute(
            select(Payment)
            .where(Payment.invoice_id == invoice_id)
            .order_by(Payment.payment_date.desc())
        )
        return list(result.scalars().all())

    async def total_paid(self, invoice_id: uuid.UUID) -> float:
        from sqlalchemy import func
        result = await self._session.execute(
            select(func.sum(Payment.amount)).where(Payment.invoice_id == invoice_id)
        )
        return float(result.scalar() or 0)
