import uuid
from datetime import datetime, timezone
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.repository import (
    WorkOrderRepository,
    WorkOrderTaskRepository,
    WorkOrderNoteRepository,
)
from app.infra.db.models import WorkOrder, WorkOrderTask, WorkOrderNote

logger = structlog.get_logger()

VALID_WO_TRANSITIONS: dict[str, list[str]] = {
    "pending":      ["assigned", "cancelled"],
    "assigned":     ["in_progress", "pending", "cancelled"],
    "in_progress":  ["on_hold", "completed", "cancelled"],
    "on_hold":      ["in_progress", "cancelled"],
    "completed":    [],
    "cancelled":    [],
}

VALID_WO_TYPES = {
    "installation", "maintenance", "repair", "calibration",
    "inspection", "validation", "emergency", "other"
}

VALID_PRIORITIES = {"low", "normal", "high", "urgent"}


def _prepare_work_order_create_kwargs(extra: dict) -> dict:
    """Map API fields to SQLAlchemy WorkOrder columns (site JSON, metadata notes)."""
    row = dict(extra)
    line = row.pop("site_address", None)
    city = row.pop("site_city", None)
    state = row.pop("site_state", None)
    postal = row.pop("site_postal_code", None)
    if any(x is not None for x in (line, city, state, postal)):
        row["site_address"] = {
            "line1": line,
            "city": city,
            "state": state,
            "postal_code": postal,
        }
    notes = row.pop("notes", None)
    if notes is not None:
        meta = row.get("metadata_")
        if not isinstance(meta, dict):
            meta = {}
        else:
            meta = dict(meta)
        meta["notes"] = notes
        row["metadata_"] = meta
    return row


class WorkOrderDomainService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._work_orders = WorkOrderRepository(session)
        self._tasks = WorkOrderTaskRepository(session)
        self._notes = WorkOrderNoteRepository(session)

    async def create_work_order(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID,
        created_by: uuid.UUID,
        work_order_number: str,
        title: str,
        work_order_type: str,
        priority: str = "normal",
        **kwargs,
    ) -> WorkOrder:
        if work_order_type not in VALID_WO_TYPES:
            raise ValueError(f"Invalid work_order_type: {work_order_type}")
        if priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {priority}")

        existing = await self._work_orders.get_by_number(work_order_number, tenant_id)
        if existing:
            raise ValueError(f"Work order number '{work_order_number}' already exists")

        row = _prepare_work_order_create_kwargs(kwargs)
        wo = await self._work_orders.create({
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "created_by": created_by,
            "work_order_number": work_order_number,
            "title": title,
            "work_order_type": work_order_type,
            "priority": priority,
            "status": "pending",
            **row,
        })
        logger.info("workorder.created", wo_id=str(wo.id))
        return wo

    async def get_work_order(self, wo_id: uuid.UUID, tenant_id: uuid.UUID) -> WorkOrder:
        wo = await self._work_orders.get_by_id(wo_id, tenant_id)
        if not wo:
            raise LookupError(f"Work order {wo_id} not found")
        return wo

    async def list_work_orders(
        self,
        tenant_id: uuid.UUID,
        status: str | None = None,
        customer_id: uuid.UUID | None = None,
        technician_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[WorkOrder]:
        return await self._work_orders.list(
            tenant_id,
            status=status,
            customer_id=customer_id,
            technician_id=technician_id,
            skip=skip,
            limit=limit,
        )

    async def assign_technician(
        self,
        wo_id: uuid.UUID,
        tenant_id: uuid.UUID,
        technician_id: uuid.UUID,
        changed_by: uuid.UUID,
        scheduled_start: datetime | None = None,
        scheduled_end: datetime | None = None,
    ) -> WorkOrder:
        wo = await self.get_work_order(wo_id, tenant_id)
        if wo.status not in ("pending", "assigned"):
            raise ValueError(f"Cannot assign technician to work order in '{wo.status}' status")

        update_data: dict = {
            "assigned_technician_id": technician_id,
            "status": "assigned",
            "changed_by": changed_by,
        }
        if scheduled_start:
            update_data["scheduled_start"] = scheduled_start
        if scheduled_end:
            update_data["scheduled_end"] = scheduled_end

        wo = await self._work_orders.update(wo, update_data)
        logger.info("workorder.assigned", wo_id=str(wo_id), technician_id=str(technician_id))
        return wo

    async def transition_status(
        self,
        wo_id: uuid.UUID,
        tenant_id: uuid.UUID,
        new_status: str,
        changed_by: uuid.UUID,
        **kwargs,
    ) -> WorkOrder:
        wo = await self.get_work_order(wo_id, tenant_id)
        allowed = VALID_WO_TRANSITIONS.get(wo.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition work order from '{wo.status}' to '{new_status}'"
            )

        update_data: dict = {"status": new_status, "changed_by": changed_by}
        now = datetime.now(timezone.utc)

        if new_status == "in_progress" and not wo.actual_start:
            update_data["actual_start"] = now
        elif new_status == "completed":
            update_data["actual_end"] = now
            for k, v in kwargs.items():
                update_data[k] = v

        wo = await self._work_orders.update(wo, update_data)
        logger.info("workorder.status_changed", wo_id=str(wo_id), to_status=new_status)
        return wo

    # ─── Tasks ───────────────────────────────────────────────────────────────

    async def add_task(
        self,
        wo_id: uuid.UUID,
        tenant_id: uuid.UUID,
        title: str,
        description: str | None = None,
        sort_order: int = 0,
    ) -> WorkOrderTask:
        await self.get_work_order(wo_id, tenant_id)
        task = await self._tasks.create({
            "work_order_id": wo_id,
            "title": title,
            "description": description,
            "sort_order": sort_order,
        })
        return task

    async def complete_task(
        self,
        wo_id: uuid.UUID,
        tenant_id: uuid.UUID,
        task_id: uuid.UUID,
        completed_by: uuid.UUID,
    ) -> WorkOrderTask:
        await self.get_work_order(wo_id, tenant_id)
        task = await self._tasks.get_by_id(task_id, wo_id)
        if not task:
            raise LookupError(f"Task {task_id} not found")
        task = await self._tasks.update(task, {
            "is_completed": True,
            "completed_at": datetime.now(timezone.utc),
            "completed_by": completed_by,
        })
        return task

    async def list_tasks(self, wo_id: uuid.UUID, tenant_id: uuid.UUID) -> list[WorkOrderTask]:
        await self.get_work_order(wo_id, tenant_id)
        return await self._tasks.list_for_work_order(wo_id)

    # ─── Notes ───────────────────────────────────────────────────────────────

    async def add_note(
        self,
        wo_id: uuid.UUID,
        tenant_id: uuid.UUID,
        created_by: uuid.UUID,
        body: str,
        is_internal: bool = True,
    ) -> WorkOrderNote:
        await self.get_work_order(wo_id, tenant_id)
        note = await self._notes.create({
            "work_order_id": wo_id,
            "created_by": created_by,
            "body": body,
            "is_internal": is_internal,
        })
        return note

    async def list_notes(
        self, wo_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[WorkOrderNote]:
        await self.get_work_order(wo_id, tenant_id)
        return await self._notes.list_for_work_order(wo_id)
