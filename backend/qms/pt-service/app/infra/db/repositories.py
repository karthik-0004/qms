"""PT Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import PTProgram, PTRound


class PTProgramRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, program_id: str) -> PTProgram | None:
        result = await self._db.execute(select(PTProgram).where(PTProgram.id == program_id))
        return result.scalar_one_or_none()

    async def list_programs(
        self,
        tenant_id: str,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[PTProgram], int]:
        query = select(PTProgram).where(PTProgram.tenant_id == tenant_id)
        count_q = select(func.count()).select_from(PTProgram).where(PTProgram.tenant_id == tenant_id)
        query = query.offset(offset).limit(limit).order_by(PTProgram.created_at.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(self, tenant_id: str, provider: str, scheme_name: str,
                     parameter: str, frequency_months: int, created_by: str, **kwargs) -> PTProgram:
        now = datetime.now(timezone.utc)
        program = PTProgram(
            id=str(uuid4()), tenant_id=tenant_id, provider=provider,
            scheme_name=scheme_name, parameter=parameter,
            frequency_months=frequency_months, is_active=True,
            created_by=created_by, created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(program)
        await self._db.flush()
        return program


class PTRoundRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, round_id: str) -> PTRound | None:
        result = await self._db.execute(select(PTRound).where(PTRound.id == round_id))
        return result.scalar_one_or_none()

    async def list_by_program(self, program_id: str) -> list[PTRound]:
        result = await self._db.execute(
            select(PTRound).where(PTRound.program_id == program_id).order_by(PTRound.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, tenant_id: str, program_id: str, round_id: str,
                     created_by: str, **kwargs) -> PTRound:
        now = datetime.now(timezone.utc)
        pt_round = PTRound(
            id=str(uuid4()), tenant_id=tenant_id, program_id=program_id,
            round_id=round_id, status="pending",
            created_by=created_by, created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(pt_round)
        await self._db.flush()
        return pt_round

    async def update(self, round_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(update(PTRound).where(PTRound.id == round_id).values(**fields))
