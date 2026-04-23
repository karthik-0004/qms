import uuid
from datetime import date
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.service import BillingDomainService


TENANT_ID = uuid.uuid4()
USER_ID = uuid.uuid4()
INVOICE_ID = uuid.uuid4()
CUSTOMER_ID = uuid.uuid4()


def _mock_invoice(status: str = "draft", total: float = 5000.0, paid: float = 0) -> MagicMock:
    inv = MagicMock()
    inv.id = INVOICE_ID
    inv.tenant_id = TENANT_ID
    inv.customer_id = CUSTOMER_ID
    inv.invoice_number = "INV-2024-001"
    inv.status = status
    inv.total_amount = total
    inv.paid_amount = paid
    inv.balance_due = total - paid
    inv.subtotal = total
    inv.tax_rate = 0
    inv.discount_amount = 0
    inv.currency = "USD"
    inv.deleted_at = None
    return inv


def _mock_line_item() -> MagicMock:
    li = MagicMock()
    li.id = uuid.uuid4()
    li.invoice_id = INVOICE_ID
    li.description = "Calibration service"
    li.unit_price = 5000.0
    li.quantity = 1.0
    li.line_total = 5000.0
    return li


def _mock_payment(amount: float = 2500.0) -> MagicMock:
    p = MagicMock()
    p.id = uuid.uuid4()
    p.invoice_id = INVOICE_ID
    p.amount = amount
    p.payment_method = "bank_transfer"
    return p


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def svc(session):
    return BillingDomainService(session)


# ─── Create invoice ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_invoice_success(svc):
    svc._invoices.get_by_number = AsyncMock(return_value=None)
    svc._invoices.create = AsyncMock(return_value=_mock_invoice())

    inv = await svc.create_invoice(TENANT_ID, CUSTOMER_ID, USER_ID, "INV-2024-001")
    assert inv.status == "draft"
    assert inv.invoice_number == "INV-2024-001"


@pytest.mark.asyncio
async def test_create_invoice_duplicate_number(svc):
    svc._invoices.get_by_number = AsyncMock(return_value=_mock_invoice())

    with pytest.raises(ValueError, match="already exists"):
        await svc.create_invoice(TENANT_ID, CUSTOMER_ID, USER_ID, "INV-2024-001")


# ─── Line items ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_line_item_to_draft(svc):
    inv = _mock_invoice("draft", total=0)
    svc._invoices.get_by_id = AsyncMock(return_value=inv)
    svc._line_items.create = AsyncMock(return_value=_mock_line_item())
    svc._invoices.update = AsyncMock(return_value=inv)

    item = await svc.add_line_item(INVOICE_ID, TENANT_ID, "Calibration", 5000.0)
    assert item.unit_price == 5000.0
    svc._invoices.update.assert_called_once()


@pytest.mark.asyncio
async def test_add_line_item_to_sent_raises(svc):
    svc._invoices.get_by_id = AsyncMock(return_value=_mock_invoice("sent"))

    with pytest.raises(ValueError, match="draft"):
        await svc.add_line_item(INVOICE_ID, TENANT_ID, "Service", 1000.0)


# ─── Send invoice ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_invoice_success(svc):
    inv = _mock_invoice("draft", total=5000.0)
    svc._invoices.get_by_id = AsyncMock(return_value=inv)
    inv.status = "sent"
    svc._invoices.update = AsyncMock(return_value=inv)

    result = await svc.send_invoice(INVOICE_ID, TENANT_ID, USER_ID, due_date=date(2024, 3, 1))
    assert result.status == "sent"
    call_data = svc._invoices.update.call_args[0][1]
    assert call_data["status"] == "sent"
    assert "sent_at" in call_data


@pytest.mark.asyncio
async def test_send_non_draft_invoice_raises(svc):
    svc._invoices.get_by_id = AsyncMock(return_value=_mock_invoice("sent"))

    with pytest.raises(ValueError, match="draft"):
        await svc.send_invoice(INVOICE_ID, TENANT_ID, USER_ID)


@pytest.mark.asyncio
async def test_send_zero_total_invoice_raises(svc):
    svc._invoices.get_by_id = AsyncMock(return_value=_mock_invoice("draft", total=0))

    with pytest.raises(ValueError, match="zero total"):
        await svc.send_invoice(INVOICE_ID, TENANT_ID, USER_ID)


# ─── Payments ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_record_full_payment_sets_paid(svc):
    inv = _mock_invoice("sent", total=5000.0, paid=0)
    svc._invoices.get_by_id = AsyncMock(return_value=inv)
    svc._payments.create = AsyncMock(return_value=_mock_payment(5000.0))
    svc._payments.total_paid = AsyncMock(return_value=5000.0)
    inv.status = "paid"
    svc._invoices.update = AsyncMock(return_value=inv)

    payment = await svc.record_payment(
        INVOICE_ID, TENANT_ID, USER_ID, "bank_transfer", 5000.0, date.today()
    )
    assert payment.amount == 5000.0
    update_data = svc._invoices.update.call_args[0][1]
    assert update_data["status"] == "paid"


@pytest.mark.asyncio
async def test_record_partial_payment_sets_partially_paid(svc):
    inv = _mock_invoice("sent", total=5000.0, paid=0)
    svc._invoices.get_by_id = AsyncMock(return_value=inv)
    svc._payments.create = AsyncMock(return_value=_mock_payment(2500.0))
    svc._payments.total_paid = AsyncMock(return_value=2500.0)
    inv.status = "partially_paid"
    svc._invoices.update = AsyncMock(return_value=inv)

    payment = await svc.record_payment(
        INVOICE_ID, TENANT_ID, USER_ID, "bank_transfer", 2500.0, date.today()
    )
    assert payment.amount == 2500.0
    update_data = svc._invoices.update.call_args[0][1]
    assert update_data["status"] == "partially_paid"


@pytest.mark.asyncio
async def test_record_payment_invalid_method(svc):
    svc._invoices.get_by_id = AsyncMock(return_value=_mock_invoice("sent"))

    with pytest.raises(ValueError, match="Invalid payment_method"):
        await svc.record_payment(
            INVOICE_ID, TENANT_ID, USER_ID, "bitcoin", 100.0, date.today()
        )


@pytest.mark.asyncio
async def test_record_payment_zero_amount_raises(svc):
    svc._invoices.get_by_id = AsyncMock(return_value=_mock_invoice("sent"))

    with pytest.raises(ValueError, match="positive"):
        await svc.record_payment(
            INVOICE_ID, TENANT_ID, USER_ID, "bank_transfer", 0, date.today()
        )


@pytest.mark.asyncio
async def test_record_payment_cancelled_invoice_raises(svc):
    svc._invoices.get_by_id = AsyncMock(return_value=_mock_invoice("cancelled"))

    with pytest.raises(ValueError, match="cancelled"):
        await svc.record_payment(
            INVOICE_ID, TENANT_ID, USER_ID, "bank_transfer", 100.0, date.today()
        )
