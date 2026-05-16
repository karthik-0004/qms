"""Risk Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Risk


class RiskRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, risk_id: str) -> Risk | None:
        result = await self._db.execute(select(Risk).where(Risk.id == risk_id))
        return result.scalar_one_or_none()

    async def list_risks(
        self,
        tenant_id: str,
        category: str | None = None,
        status: str | None = None,
        owner_id: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Risk], int]:
        query = select(Risk).where(Risk.tenant_id == tenant_id)
        count_q = select(func.count()).select_from(Risk).where(Risk.tenant_id == tenant_id)

        for col, val in [(Risk.category, category), (Risk.status, status), (Risk.owner_id, owner_id)]:
            if val:
                query = query.where(col == val)
                count_q = count_q.where(col == val)

        query = query.offset(offset).limit(limit).order_by(Risk.created_at.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def list_all_for_matrix(self, tenant_id: str) -> list[Risk]:
        result = await self._db.execute(
            select(Risk).where(Risk.tenant_id == tenant_id, Risk.status != "closed")
        )
        return list(result.scalars().all())

    async def create(self, tenant_id: str, risk_id: str, category: str,
                     description: str, severity: int, likelihood: int,
                     created_by: str, **kwargs) -> Risk:
        now = datetime.now(timezone.utc)
        risk = Risk(
            id=str(uuid4()), tenant_id=tenant_id, risk_id=risk_id,
            category=category, description=description,
            severity=severity, likelihood=likelihood,
            risk_score=severity * likelihood,
            status="open", created_by=created_by, created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(risk)
        await self._db.flush()
        return risk

    async def update(self, risk_id: str, **fields) -> None:
        # Recompute risk_score if severity or likelihood changed
        if "severity" in fields or "likelihood" in fields:
            current = await self.get_by_id(risk_id)
            if current:
                severity = fields.get("severity", current.severity)
                likelihood = fields.get("likelihood", current.likelihood)
                fields["risk_score"] = severity * likelihood
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(update(Risk).where(Risk.id == risk_id).values(**fields))
