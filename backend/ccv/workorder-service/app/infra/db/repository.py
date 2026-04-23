import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.infra.db.models import WorkOrder, WorkOrderTask, WorkOrderNote


class WorkOrderRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> WorkOrder:
        wo = WorkOrder(**data)
        self._session.add(wo)
        await self._session.flush()
        await self._session.refresh(wo)
        return wo

    async def get_by_id(self, wo_id: uuid.UUID, tenant_id: uuid.UUID) -> WorkOrder | None:
        result = await self._session.execute(
            select(WorkOrder).where(
                and_(
                    WorkOrder.id == wo_id,
                    WorkOrder.tenant_id == tenant_id,
                    WorkOrder.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, wo_number: str, tenant_id: uuid.UUID) -> WorkOrder | None:
        result = await self._session.execute(
            select(WorkOrder).where(
                and_(
                    WorkOrder.work_order_number == wo_number,
                    WorkOrder.tenant_id == tenant_id,
                    WorkOrder.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: uuid.UUID,
        status: str | None = None,
        technician_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[WorkOrder]:
        stmt = select(WorkOrder).where(
            and_(WorkOrder.tenant_id == tenant_id, WorkOrder.deleted_at.is_(None))
        )
        if status:
            stmt = stmt.where(WorkOrder.status == status)
        if technician_id:
            stmt = stmt.where(WorkOrder.assigned_technician_id == technician_id)
        stmt = stmt.offset(skip).limit(limit).order_by(WorkOrder.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, wo: WorkOrder, data: dict) -> WorkOrder:
        for key, value in data.items():
            setattr(wo, key, value)
        await self._session.flush()
        await self._session.refresh(wo)
        return wo

    async def soft_delete(self, wo: WorkOrder) -> None:
        wo.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()


class WorkOrderTaskRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> WorkOrderTask:
        task = WorkOrderTask(**data)
        self._session.add(task)
        await self._session.flush()
        await self._session.refresh(task)
        return task

    async def get_by_id(self, task_id: uuid.UUID, wo_id: uuid.UUID) -> WorkOrderTask | None:
        result = await self._session.execute(
            select(WorkOrderTask).where(
                and_(WorkOrderTask.id == task_id, WorkOrderTask.work_order_id == wo_id)
            )
        )
        return result.scalar_one_or_none()

    async def list_for_work_order(self, wo_id: uuid.UUID) -> list[WorkOrderTask]:
        result = await self._session.execute(
            select(WorkOrderTask)
            .where(WorkOrderTask.work_order_id == wo_id)
            .order_by(WorkOrderTask.sort_order)
        )
        return list(result.scalars().all())

    async def update(self, task: WorkOrderTask, data: dict) -> WorkOrderTask:
        for key, value in data.items():
            setattr(task, key, value)
        await self._session.flush()
        await self._session.refresh(task)
        return task


class WorkOrderNoteRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> WorkOrderNote:
        note = WorkOrderNote(**data)
        self._session.add(note)
        await self._session.flush()
        await self._session.refresh(note)
        return note

    async def list_for_work_order(self, wo_id: uuid.UUID) -> list[WorkOrderNote]:
        result = await self._session.execute(
            select(WorkOrderNote)
            .where(WorkOrderNote.work_order_id == wo_id)
            .order_by(WorkOrderNote.created_at.desc())
        )
        return list(result.scalars().all())
