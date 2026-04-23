"""Workflow Engine — Repository layer."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import WorkflowDefinition, WorkflowHistory, WorkflowInstance


class WorkflowDefinitionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, definition_id: str) -> WorkflowDefinition | None:
        result = await self._db.execute(
            select(WorkflowDefinition).where(WorkflowDefinition.id == definition_id)
        )
        return result.scalar_one_or_none()

    async def get_active_by_entity_type(self, entity_type: str) -> WorkflowDefinition | None:
        result = await self._db.execute(
            select(WorkflowDefinition).where(
                WorkflowDefinition.entity_type == entity_type,
                WorkflowDefinition.is_active.is_(True),
            ).order_by(WorkflowDefinition.version.desc())
        )
        return result.scalars().first()

    async def list_all(self) -> list[WorkflowDefinition]:
        result = await self._db.execute(select(WorkflowDefinition).order_by(WorkflowDefinition.entity_type))
        return list(result.scalars().all())

    async def create(
        self,
        name: str,
        entity_type: str,
        states: dict,
        transitions: dict,
        version: int = 1,
    ) -> WorkflowDefinition:
        now = datetime.now(timezone.utc)
        defn = WorkflowDefinition(
            id=str(uuid4()),
            name=name,
            entity_type=entity_type,
            states=states,
            transitions=transitions,
            version=version,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self._db.add(defn)
        await self._db.flush()
        return defn


class WorkflowInstanceRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, instance_id: str) -> WorkflowInstance | None:
        result = await self._db.execute(
            select(WorkflowInstance).where(WorkflowInstance.id == instance_id)
        )
        return result.scalar_one_or_none()

    async def get_by_entity(self, entity_type: str, entity_id: str) -> WorkflowInstance | None:
        result = await self._db.execute(
            select(WorkflowInstance).where(
                WorkflowInstance.entity_type == entity_type,
                WorkflowInstance.entity_id == entity_id,
                WorkflowInstance.completed_at.is_(None),
            )
        )
        return result.scalars().first()

    async def list_by_assignee(
        self, assignee_id: str, state: str | None = None
    ) -> list[WorkflowInstance]:
        query = select(WorkflowInstance).where(
            WorkflowInstance.assignee_id == assignee_id,
            WorkflowInstance.completed_at.is_(None),
        )
        if state:
            query = query.where(WorkflowInstance.current_state == state)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def list_all(
        self,
        entity_type: str | None = None,
        current_state: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[WorkflowInstance], int]:
        query = select(WorkflowInstance)
        count_q = select(func.count()).select_from(WorkflowInstance)
        if entity_type:
            query = query.where(WorkflowInstance.entity_type == entity_type)
            count_q = count_q.where(WorkflowInstance.entity_type == entity_type)
        if current_state:
            query = query.where(WorkflowInstance.current_state == current_state)
            count_q = count_q.where(WorkflowInstance.current_state == current_state)
        query = query.offset(offset).limit(limit).order_by(WorkflowInstance.created_at.desc())
        result = await self._db.execute(query)
        count = await self._db.execute(count_q)
        return list(result.scalars().all()), count.scalar_one()

    async def create(
        self,
        definition_id: str,
        entity_type: str,
        entity_id: str,
        initial_state: str,
        created_by: str,
        assignee_id: str | None = None,
        due_at: datetime | None = None,
        context: dict | None = None,
    ) -> WorkflowInstance:
        now = datetime.now(timezone.utc)
        instance = WorkflowInstance(
            id=str(uuid4()),
            definition_id=definition_id,
            entity_type=entity_type,
            entity_id=entity_id,
            current_state=initial_state,
            context=context or {},
            assignee_id=assignee_id,
            due_at=due_at,
            created_by=created_by,
            created_at=now,
            updated_at=now,
        )
        self._db.add(instance)
        await self._db.flush()
        return instance

    async def transition(
        self, instance_id: str, new_state: str, assignee_id: str | None = None
    ) -> None:
        values: dict = {
            "current_state": new_state,
            "updated_at": datetime.now(timezone.utc),
        }
        if assignee_id is not None:
            values["assignee_id"] = assignee_id
        await self._db.execute(
            update(WorkflowInstance).where(WorkflowInstance.id == instance_id).values(**values)
        )

    async def complete(self, instance_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(WorkflowInstance)
            .where(WorkflowInstance.id == instance_id)
            .values(completed_at=now, updated_at=now)
        )


class WorkflowHistoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_instance(self, instance_id: str) -> list[WorkflowHistory]:
        result = await self._db.execute(
            select(WorkflowHistory)
            .where(WorkflowHistory.instance_id == instance_id)
            .order_by(WorkflowHistory.occurred_at.asc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        instance_id: str,
        to_state: str,
        action: str,
        actor_id: str,
        from_state: str | None = None,
        comment: str | None = None,
        signature: str | None = None,
        metadata: dict | None = None,
    ) -> WorkflowHistory:
        entry = WorkflowHistory(
            id=str(uuid4()),
            instance_id=instance_id,
            from_state=from_state,
            to_state=to_state,
            action=action,
            actor_id=actor_id,
            comment=comment,
            signature=signature,
            metadata_=metadata or {},
            occurred_at=datetime.now(timezone.utc),
        )
        self._db.add(entry)
        await self._db.flush()
        return entry
