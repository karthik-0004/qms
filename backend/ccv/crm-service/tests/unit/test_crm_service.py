import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.domain.service import CRMDomainService


TENANT_ID = uuid.uuid4()
USER_ID = uuid.uuid4()
CUSTOMER_ID = uuid.uuid4()


def _mock_customer(status: str = "prospect") -> MagicMock:
    c = MagicMock()
    c.id = CUSTOMER_ID
    c.tenant_id = TENANT_ID
    c.company_name = "Acme Corp"
    c.status = status
    c.deleted_at = None
    return c


def _mock_contact() -> MagicMock:
    c = MagicMock()
    c.id = uuid.uuid4()
    c.customer_id = CUSTOMER_ID
    c.first_name = "Jane"
    c.last_name = "Doe"
    c.is_primary = True
    return c


def _mock_interaction() -> MagicMock:
    i = MagicMock()
    i.id = uuid.uuid4()
    i.customer_id = CUSTOMER_ID
    i.interaction_type = "call"
    i.subject = "Follow-up call"
    return i


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def svc(session):
    return CRMDomainService(session)


# ─── Customer creation ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_customer_success(svc):
    svc._customers.get_by_company_name = AsyncMock(return_value=None)
    svc._customers.create = AsyncMock(return_value=_mock_customer())

    customer = await svc.create_customer(TENANT_ID, USER_ID, "Acme Corp")

    assert customer.company_name == "Acme Corp"
    assert customer.status == "prospect"
    svc._customers.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_customer_duplicate_name_raises(svc):
    svc._customers.get_by_company_name = AsyncMock(return_value=_mock_customer())

    with pytest.raises(ValueError, match="already exists"):
        await svc.create_customer(TENANT_ID, USER_ID, "Acme Corp")


@pytest.mark.asyncio
async def test_get_customer_not_found_raises(svc):
    svc._customers.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(LookupError):
        await svc.get_customer(CUSTOMER_ID, TENANT_ID)


# ─── Status transitions ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_transition_prospect_to_qualified(svc):
    customer = _mock_customer("prospect")
    svc._customers.get_by_id = AsyncMock(return_value=customer)
    customer.status = "qualified"
    svc._customers.update = AsyncMock(return_value=customer)

    result = await svc.transition_status(CUSTOMER_ID, TENANT_ID, "qualified", USER_ID)
    assert result.status == "qualified"


@pytest.mark.asyncio
async def test_invalid_transition_raises(svc):
    customer = _mock_customer("prospect")
    svc._customers.get_by_id = AsyncMock(return_value=customer)

    with pytest.raises(ValueError, match="Cannot transition"):
        await svc.transition_status(CUSTOMER_ID, TENANT_ID, "approved", USER_ID)


@pytest.mark.asyncio
async def test_transition_to_customer(svc):
    customer = _mock_customer("qualified")
    svc._customers.get_by_id = AsyncMock(return_value=customer)
    customer.status = "customer"
    svc._customers.update = AsyncMock(return_value=customer)

    result = await svc.transition_status(CUSTOMER_ID, TENANT_ID, "customer", USER_ID)
    assert result.status == "customer"


@pytest.mark.asyncio
async def test_cancelled_is_terminal(svc):
    customer = _mock_customer("cancelled")
    svc._customers.get_by_id = AsyncMock(return_value=customer)

    with pytest.raises(ValueError, match="Cannot transition"):
        await svc.transition_status(CUSTOMER_ID, TENANT_ID, "prospect", USER_ID)


# ─── Contacts ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_contact_success(svc):
    svc._customers.get_by_id = AsyncMock(return_value=_mock_customer())
    svc._contacts.clear_primary_for_customer = AsyncMock()
    svc._contacts.create = AsyncMock(return_value=_mock_contact())

    contact = await svc.add_contact(
        CUSTOMER_ID, TENANT_ID, USER_ID, "Jane", "Doe", is_primary=True
    )
    assert contact.first_name == "Jane"
    svc._contacts.clear_primary_for_customer.assert_called_once_with(CUSTOMER_ID)


@pytest.mark.asyncio
async def test_add_contact_not_primary_no_clear(svc):
    svc._customers.get_by_id = AsyncMock(return_value=_mock_customer())
    svc._contacts.clear_primary_for_customer = AsyncMock()
    contact = _mock_contact()
    contact.is_primary = False
    svc._contacts.create = AsyncMock(return_value=contact)

    await svc.add_contact(CUSTOMER_ID, TENANT_ID, USER_ID, "Bob", "Smith", is_primary=False)
    svc._contacts.clear_primary_for_customer.assert_not_called()


@pytest.mark.asyncio
async def test_list_contacts(svc):
    svc._customers.get_by_id = AsyncMock(return_value=_mock_customer())
    svc._contacts.list_for_customer = AsyncMock(return_value=[_mock_contact()])

    contacts = await svc.list_contacts(CUSTOMER_ID, TENANT_ID)
    assert len(contacts) == 1


# ─── Interactions ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_log_interaction_success(svc):
    svc._customers.get_by_id = AsyncMock(return_value=_mock_customer())
    svc._interactions.create = AsyncMock(return_value=_mock_interaction())

    interaction = await svc.log_interaction(
        CUSTOMER_ID, TENANT_ID, USER_ID, "call", "Follow-up call"
    )
    assert interaction.interaction_type == "call"


@pytest.mark.asyncio
async def test_log_interaction_invalid_type(svc):
    svc._customers.get_by_id = AsyncMock(return_value=_mock_customer())

    with pytest.raises(ValueError, match="Invalid interaction_type"):
        await svc.log_interaction(CUSTOMER_ID, TENANT_ID, USER_ID, "unknown_type", "Subject")


@pytest.mark.asyncio
async def test_list_interactions(svc):
    svc._customers.get_by_id = AsyncMock(return_value=_mock_customer())
    svc._interactions.list_for_customer = AsyncMock(return_value=[_mock_interaction()])

    result = await svc.list_interactions(CUSTOMER_ID, TENANT_ID)
    assert len(result) == 1
