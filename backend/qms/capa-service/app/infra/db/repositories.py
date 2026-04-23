"""CAPA Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import CAPA, CAPAAction


class CAPARepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, capa_id: str) -> CAPA | None:
        result = await self._db.execute(
            select(CAPA).where(CAPA.id == capa_id, CAPA.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_capas(
        self,
        tenant_id: str,
        status: str | None = None,
        severity: str | None = None,
        owner_id: str | None = None,
        department: str | None = None,
        overdue_only: bool = False,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[CAPA], int]:
        query = select(CAPA).where(CAPA.tenant_id == tenant_id, CAPA.deleted_at.is_(None))
        count_q = select(func.count()).select_from(CAPA).where(CAPA.tenant_id == tenant_id, CAPA.deleted_at.is_(None))

        for col, val in [(CAPA.status, status), (CAPA.severity, severity),
                         (CAPA.owner_id, owner_id), (CAPA.department, department)]:
            if val:
                query = query.where(col == val)
                count_q = count_q.where(col == val)

        if overdue_only:
            now = datetime.now(timezone.utc)
            query = query.where(CAPA.due_date < now, CAPA.status != "closed")
            count_q = count_q.where(CAPA.due_date < now, CAPA.status != "closed")

        query = query.offset(offset).limit(limit).order_by(CAPA.created_at.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(self, tenant_id: str, capa_number: str, title: str,
                     description: str, created_by: str, **kwargs) -> CAPA:
        now = datetime.now(timezone.utc)
        capa = CAPA(
            id=str(uuid4()), tenant_id=tenant_id, capa_number=capa_number,
            title=title, description=description, status="open",
            created_by=created_by, created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(capa)
        await self._db.flush()
        return capa

    async def update(self, capa_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(update(CAPA).where(CAPA.id == capa_id).values(**fields))

    async def soft_delete(self, capa_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(CAPA).where(CAPA.id == capa_id).values(deleted_at=now, updated_at=now)
        )


class CAPAActionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, action_id: str) -> CAPAAction | None:
        result = await self._db.execute(select(CAPAAction).where(CAPAAction.id == action_id))
        return result.scalar_one_or_none()

    async def list_by_capa(self, capa_id: str) -> list[CAPAAction]:
        result = await self._db.execute(
            select(CAPAAction).where(CAPAAction.capa_id == capa_id).order_by(CAPAAction.created_at.asc())
        )
        return list(result.scalars().all())

    async def create(self, capa_id: str, action_type: str, description: str, **kwargs) -> CAPAAction:
        now = datetime.now(timezone.utc)
        action = CAPAAction(
            id=str(uuid4()), capa_id=capa_id, action_type=action_type,
            description=description, status="pending", created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(action)
        await self._db.flush()
        return action

    async def update(self, action_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(update(CAPAAction).where(CAPAAction.id == action_id).values(**fields))
