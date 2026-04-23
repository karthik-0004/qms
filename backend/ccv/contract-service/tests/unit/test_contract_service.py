import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.service import ContractDomainService


TENANT_ID = uuid.uuid4()
USER_ID = uuid.uuid4()
CONTRACT_ID = uuid.uuid4()
CUSTOMER_ID = uuid.uuid4()


def _mock_contract(status: str = "draft") -> MagicMock:
    c = MagicMock()
    c.id = CONTRACT_ID
    c.tenant_id = TENANT_ID
    c.customer_id = CUSTOMER_ID
    c.contract_number = "CCV-2024-001"
    c.status = status
    c.total_value = 50000.0
    c.deleted_at = None
    return c


def _mock_line_item() -> MagicMock:
    li = MagicMock()
    li.id = uuid.uuid4()
    li.contract_id = CONTRACT_ID
    li.description = "Calibration service — annual"
    li.unit_price = 5000.0
    li.quantity = 1.0
    li.total_price = 5000.0
    return li


def _mock_history(from_s: str | None, to_s: str) -> MagicMock:
    h = MagicMock()
    h.id = uuid.uuid4()
    h.contract_id = CONTRACT_ID
    h.from_status = from_s
    h.to_status = to_s
    return h


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def svc(session):
    return ContractDomainService(session)


# ─── Create contract ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_contract_success(svc):
    svc._contracts.get_by_number = AsyncMock(return_value=None)
    svc._contracts.create = AsyncMock(return_value=_mock_contract())
    svc._history.create = AsyncMock(return_value=_mock_history(None, "draft"))

    contract = await svc.create_contract(
        TENANT_ID, CUSTOMER_ID, USER_ID,
        "CCV-2024-001", "Annual Calibration", "calibration_contract"
    )
    assert contract.status == "draft"
    svc._history.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_contract_duplicate_number(svc):
    svc._contracts.get_by_number = AsyncMock(return_value=_mock_contract())

    with pytest.raises(ValueError, match="already exists"):
        await svc.create_contract(
            TENANT_ID, CUSTOMER_ID, USER_ID,
            "CCV-2024-001", "title", "calibration_contract"
        )


@pytest.mark.asyncio
async def test_create_contract_invalid_type(svc):
    svc._contracts.get_by_number = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="Invalid contract_type"):
        await svc.create_contract(
            TENANT_ID, CUSTOMER_ID, USER_ID,
            "CCV-2024-002", "title", "invalid_type"
        )


# ─── Status transitions ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_transition_draft_to_under_review(svc):
    contract = _mock_contract("draft")
    svc._contracts.get_by_id = AsyncMock(return_value=contract)
    contract.status = "under_review"
    svc._contracts.update = AsyncMock(return_value=contract)
    svc._history.create = AsyncMock()

    result = await svc.transition_status(CONTRACT_ID, TENANT_ID, "under_review", USER_ID)
    assert result.status == "under_review"
    svc._history.create.assert_called_once()


@pytest.mark.asyncio
async def test_transition_approved_to_active_sets_signed_at(svc):
    contract = _mock_contract("approved")
    svc._contracts.get_by_id = AsyncMock(return_value=contract)
    contract.status = "active"
    updated = MagicMock()
    updated.status = "active"
    updated.signed_at = "2024-01-01T00:00:00Z"
    svc._contracts.update = AsyncMock(return_value=updated)
    svc._history.create = AsyncMock()

    result = await svc.transition_status(CONTRACT_ID, TENANT_ID, "active", USER_ID)
    assert result.status == "active"
    call_kwargs = svc._contracts.update.call_args[0][1]
    assert "signed_at" in call_kwargs


@pytest.mark.asyncio
async def test_invalid_transition_raises(svc):
    contract = _mock_contract("draft")
    svc._contracts.get_by_id = AsyncMock(return_value=contract)

    with pytest.raises(ValueError, match="Cannot transition"):
        await svc.transition_status(CONTRACT_ID, TENANT_ID, "expired", USER_ID)


@pytest.mark.asyncio
async def test_expired_is_terminal(svc):
    contract = _mock_contract("expired")
    svc._contracts.get_by_id = AsyncMock(return_value=contract)

    with pytest.raises(ValueError, match="Cannot transition"):
        await svc.transition_status(CONTRACT_ID, TENANT_ID, "draft", USER_ID)


# ─── Line items ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_line_item_to_draft(svc):
    svc._contracts.get_by_id = AsyncMock(return_value=_mock_contract("draft"))
    svc._line_items.create = AsyncMock(return_value=_mock_line_item())

    item = await svc.add_line_item(
        CONTRACT_ID, TENANT_ID, "Calibration service", 5000.0, quantity=1.0
    )
    assert item.unit_price == 5000.0


@pytest.mark.asyncio
async def test_add_line_item_to_active_raises(svc):
    svc._contracts.get_by_id = AsyncMock(return_value=_mock_contract("active"))

    with pytest.raises(ValueError, match="draft"):
        await svc.add_line_item(CONTRACT_ID, TENANT_ID, "Extra service", 1000.0)


@pytest.mark.asyncio
async def test_list_line_items(svc):
    svc._contracts.get_by_id = AsyncMock(return_value=_mock_contract())
    svc._line_items.list_for_contract = AsyncMock(return_value=[_mock_line_item()])

    items = await svc.list_line_items(CONTRACT_ID, TENANT_ID)
    assert len(items) == 1


# ─── History ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_history(svc):
    svc._contracts.get_by_id = AsyncMock(return_value=_mock_contract())
    svc._history.list_for_contract = AsyncMock(
        return_value=[_mock_history(None, "draft"), _mock_history("draft", "under_review")]
    )

    history = await svc.get_history(CONTRACT_ID, TENANT_ID)
    assert len(history) == 2
