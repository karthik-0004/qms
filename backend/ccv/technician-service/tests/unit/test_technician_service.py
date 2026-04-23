import uuid
from datetime import datetime, timezone, timedelta
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.service import TechnicianDomainService


TENANT_ID = uuid.uuid4()
USER_ID = uuid.uuid4()
TECH_ID = uuid.uuid4()


def _mock_tech(status: str = "available") -> MagicMock:
    t = MagicMock()
    t.id = TECH_ID
    t.tenant_id = TENANT_ID
    t.employee_number = "EMP-001"
    t.first_name = "Alice"
    t.last_name = "Smith"
    t.email = "alice@example.com"
    t.status = status
    t.is_active = True
    t.deleted_at = None
    return t


def _mock_cert() -> MagicMock:
    c = MagicMock()
    c.id = uuid.uuid4()
    c.technician_id = TECH_ID
    c.certification_name = "CQE"
    c.is_active = True
    return c


def _mock_avail() -> MagicMock:
    a = MagicMock()
    a.id = uuid.uuid4()
    a.technician_id = TECH_ID
    a.availability_type = "available"
    return a


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def svc(session):
    return TechnicianDomainService(session)


# ─── Registration ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_technician_success(svc):
    svc._technicians.get_by_employee_number = AsyncMock(return_value=None)
    svc._technicians.get_by_email = AsyncMock(return_value=None)
    svc._technicians.create = AsyncMock(return_value=_mock_tech())

    tech = await svc.register_technician(
        TENANT_ID, USER_ID, "EMP-001", "Alice", "Smith", "alice@example.com"
    )
    assert tech.status == "available"
    assert tech.employee_number == "EMP-001"


@pytest.mark.asyncio
async def test_register_duplicate_employee_number(svc):
    svc._technicians.get_by_employee_number = AsyncMock(return_value=_mock_tech())

    with pytest.raises(ValueError, match="Employee number"):
        await svc.register_technician(
            TENANT_ID, USER_ID, "EMP-001", "Alice", "Smith", "other@example.com"
        )


@pytest.mark.asyncio
async def test_register_duplicate_email(svc):
    svc._technicians.get_by_employee_number = AsyncMock(return_value=None)
    svc._technicians.get_by_email = AsyncMock(return_value=_mock_tech())

    with pytest.raises(ValueError, match="Email"):
        await svc.register_technician(
            TENANT_ID, USER_ID, "EMP-002", "Alice", "Smith", "alice@example.com"
        )


# ─── Status transitions ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_transition_available_to_on_assignment(svc):
    tech = _mock_tech("available")
    svc._technicians.get_by_id = AsyncMock(return_value=tech)
    tech.status = "on_assignment"
    svc._technicians.update = AsyncMock(return_value=tech)

    result = await svc.transition_status(TECH_ID, TENANT_ID, "on_assignment", USER_ID)
    assert result.status == "on_assignment"


@pytest.mark.asyncio
async def test_invalid_transition_raises(svc):
    tech = _mock_tech("on_assignment")
    svc._technicians.get_by_id = AsyncMock(return_value=tech)

    with pytest.raises(ValueError, match="Cannot transition"):
        await svc.transition_status(TECH_ID, TENANT_ID, "inactive_unknown", USER_ID)


@pytest.mark.asyncio
async def test_available_to_on_leave(svc):
    tech = _mock_tech("available")
    svc._technicians.get_by_id = AsyncMock(return_value=tech)
    tech.status = "on_leave"
    svc._technicians.update = AsyncMock(return_value=tech)

    result = await svc.transition_status(TECH_ID, TENANT_ID, "on_leave", USER_ID)
    assert result.status == "on_leave"


# ─── Certifications ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_certification(svc):
    svc._technicians.get_by_id = AsyncMock(return_value=_mock_tech())
    svc._certifications.create = AsyncMock(return_value=_mock_cert())

    cert = await svc.add_certification(TECH_ID, TENANT_ID, USER_ID, "CQE")
    assert cert.certification_name == "CQE"
    assert cert.is_active is True


@pytest.mark.asyncio
async def test_revoke_certification(svc):
    cert = _mock_cert()
    cert.is_active = False
    svc._technicians.get_by_id = AsyncMock(return_value=_mock_tech())
    svc._certifications.get_by_id = AsyncMock(return_value=cert)

    result = await svc.revoke_certification(TECH_ID, TENANT_ID, cert.id)
    assert result.is_active is False


@pytest.mark.asyncio
async def test_revoke_cert_not_found(svc):
    svc._technicians.get_by_id = AsyncMock(return_value=_mock_tech())
    svc._certifications.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(LookupError):
        await svc.revoke_certification(TECH_ID, TENANT_ID, uuid.uuid4())


# ─── Availability ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_set_availability_success(svc):
    svc._technicians.get_by_id = AsyncMock(return_value=_mock_tech())
    svc._availability.create = AsyncMock(return_value=_mock_avail())

    now = datetime.now(timezone.utc)
    avail = await svc.set_availability(
        TECH_ID, TENANT_ID, "available", now, now + timedelta(hours=8)
    )
    assert avail.availability_type == "available"


@pytest.mark.asyncio
async def test_set_availability_invalid_type(svc):
    svc._technicians.get_by_id = AsyncMock(return_value=_mock_tech())

    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="Invalid availability_type"):
        await svc.set_availability(
            TECH_ID, TENANT_ID, "napping", now, now + timedelta(hours=8)
        )


@pytest.mark.asyncio
async def test_set_availability_end_before_start(svc):
    svc._technicians.get_by_id = AsyncMock(return_value=_mock_tech())

    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="end_dt must be after"):
        await svc.set_availability(
            TECH_ID, TENANT_ID, "available", now, now - timedelta(hours=1)
        )
