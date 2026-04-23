import uuid
from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.service import WorkOrderDomainService


TENANT_ID = uuid.uuid4()
USER_ID = uuid.uuid4()
WO_ID = uuid.uuid4()
CUSTOMER_ID = uuid.uuid4()
TECH_ID = uuid.uuid4()


def _mock_wo(status: str = "pending") -> MagicMock:
    wo = MagicMock()
    wo.id = WO_ID
    wo.tenant_id = TENANT_ID
    wo.customer_id = CUSTOMER_ID
    wo.work_order_number = "WO-2024-001"
    wo.status = status
    wo.assigned_technician_id = None
    wo.actual_start = None
    wo.deleted_at = None
    return wo


def _mock_task() -> MagicMock:
    t = MagicMock()
    t.id = uuid.uuid4()
    t.work_order_id = WO_ID
    t.title = "Check calibration"
    t.is_completed = False
    return t


def _mock_note() -> MagicMock:
    n = MagicMock()
    n.id = uuid.uuid4()
    n.work_order_id = WO_ID
    n.body = "Site access confirmed"
    n.is_internal = True
    return n


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def svc(session):
    return WorkOrderDomainService(session)


# ─── Creation ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_work_order_success(svc):
    svc._work_orders.get_by_number = AsyncMock(return_value=None)
    svc._work_orders.create = AsyncMock(return_value=_mock_wo())

    wo = await svc.create_work_order(
        TENANT_ID, CUSTOMER_ID, USER_ID,
        "WO-2024-001", "Annual maintenance", "maintenance"
    )
    assert wo.status == "pending"
    assert wo.work_order_number == "WO-2024-001"


@pytest.mark.asyncio
async def test_create_work_order_duplicate_number(svc):
    svc._work_orders.get_by_number = AsyncMock(return_value=_mock_wo())

    with pytest.raises(ValueError, match="already exists"):
        await svc.create_work_order(
            TENANT_ID, CUSTOMER_ID, USER_ID,
            "WO-2024-001", "title", "maintenance"
        )


@pytest.mark.asyncio
async def test_create_work_order_invalid_type(svc):
    svc._work_orders.get_by_number = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="Invalid work_order_type"):
        await svc.create_work_order(
            TENANT_ID, CUSTOMER_ID, USER_ID,
            "WO-2024-002", "title", "invalid"
        )


@pytest.mark.asyncio
async def test_create_work_order_invalid_priority(svc):
    svc._work_orders.get_by_number = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="Invalid priority"):
        await svc.create_work_order(
            TENANT_ID, CUSTOMER_ID, USER_ID,
            "WO-2024-003", "title", "maintenance", priority="critical"
        )


# ─── Assign technician ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_assign_technician_pending_to_assigned(svc):
    wo = _mock_wo("pending")
    svc._work_orders.get_by_id = AsyncMock(return_value=wo)
    wo.status = "assigned"
    wo.assigned_technician_id = TECH_ID
    svc._work_orders.update = AsyncMock(return_value=wo)

    result = await svc.assign_technician(WO_ID, TENANT_ID, TECH_ID, USER_ID)
    assert result.status == "assigned"
    assert result.assigned_technician_id == TECH_ID


@pytest.mark.asyncio
async def test_assign_technician_to_completed_raises(svc):
    wo = _mock_wo("completed")
    svc._work_orders.get_by_id = AsyncMock(return_value=wo)

    with pytest.raises(ValueError, match="Cannot assign"):
        await svc.assign_technician(WO_ID, TENANT_ID, TECH_ID, USER_ID)


# ─── Status transitions ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_transition_assigned_to_in_progress(svc):
    wo = _mock_wo("assigned")
    svc._work_orders.get_by_id = AsyncMock(return_value=wo)
    wo.status = "in_progress"
    svc._work_orders.update = AsyncMock(return_value=wo)

    result = await svc.transition_status(WO_ID, TENANT_ID, "in_progress", USER_ID)
    assert result.status == "in_progress"
    call_data = svc._work_orders.update.call_args[0][1]
    assert "actual_start" in call_data


@pytest.mark.asyncio
async def test_transition_in_progress_to_completed_sets_actual_end(svc):
    wo = _mock_wo("in_progress")
    wo.actual_start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    svc._work_orders.get_by_id = AsyncMock(return_value=wo)
    wo.status = "completed"
    svc._work_orders.update = AsyncMock(return_value=wo)

    result = await svc.transition_status(WO_ID, TENANT_ID, "completed", USER_ID)
    assert result.status == "completed"
    call_data = svc._work_orders.update.call_args[0][1]
    assert "actual_end" in call_data


@pytest.mark.asyncio
async def test_invalid_transition_raises(svc):
    wo = _mock_wo("pending")
    svc._work_orders.get_by_id = AsyncMock(return_value=wo)

    with pytest.raises(ValueError, match="Cannot transition"):
        await svc.transition_status(WO_ID, TENANT_ID, "completed", USER_ID)


# ─── Tasks ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_task(svc):
    svc._work_orders.get_by_id = AsyncMock(return_value=_mock_wo())
    svc._tasks.create = AsyncMock(return_value=_mock_task())

    task = await svc.add_task(WO_ID, TENANT_ID, "Check calibration")
    assert task.title == "Check calibration"


@pytest.mark.asyncio
async def test_complete_task(svc):
    task = _mock_task()
    task.is_completed = True
    svc._work_orders.get_by_id = AsyncMock(return_value=_mock_wo())
    svc._tasks.get_by_id = AsyncMock(return_value=task)
    svc._tasks.update = AsyncMock(return_value=task)

    result = await svc.complete_task(WO_ID, TENANT_ID, task.id, USER_ID)
    assert result.is_completed is True


@pytest.mark.asyncio
async def test_complete_task_not_found(svc):
    svc._work_orders.get_by_id = AsyncMock(return_value=_mock_wo())
    svc._tasks.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(LookupError):
        await svc.complete_task(WO_ID, TENANT_ID, uuid.uuid4(), USER_ID)


# ─── Notes ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_note(svc):
    svc._work_orders.get_by_id = AsyncMock(return_value=_mock_wo())
    svc._notes.create = AsyncMock(return_value=_mock_note())

    note = await svc.add_note(WO_ID, TENANT_ID, USER_ID, "Site access confirmed")
    assert note.body == "Site access confirmed"
