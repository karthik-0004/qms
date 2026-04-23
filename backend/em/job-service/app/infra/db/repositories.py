"""Job Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Job


class JobRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, job_id: str) -> Job | None:
        result = await self._db.execute(
            select(Job).where(Job.id == job_id)
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        status: str | None = None,
        job_type: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Job], int]:
        query = select(Job).where(Job.tenant_id == tenant_id)
        count_q = select(func.count()).select_from(Job).where(Job.tenant_id == tenant_id)
        if status:
            query = query.where(Job.status == status)
            count_q = count_q.where(Job.status == status)
        if job_type:
            query = query.where(Job.job_type == job_type)
            count_q = count_q.where(Job.job_type == job_type)

        query = query.offset(offset).limit(limit).order_by(Job.queued_at.desc())
        items = list((await self._db.execute(query)).scalars().all())
        total = (await self._db.execute(count_q)).scalar_one()
        return items, total

    async def get_next_pending(
        self, tenant_id: str, job_type: str | None = None
    ) -> Job | None:
        """Claim next available pending job (priority-ordered)."""
        query = select(Job).where(
            Job.tenant_id == tenant_id,
            Job.status == "pending",
        )
        if job_type:
            query = query.where(Job.job_type == job_type)
        query = query.order_by(Job.priority.asc(), Job.queued_at.asc()).limit(1)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_retryable(self, now: datetime) -> list[Job]:
        """Get jobs that are due for retry."""
        result = await self._db.execute(
            select(Job).where(
                Job.status == "retrying",
                Job.next_retry_at <= now,
            ).order_by(Job.next_retry_at.asc()).limit(50)
        )
        return list(result.scalars().all())

    async def create(
        self,
        tenant_id: str,
        job_type: str,
        payload: dict,
        created_by: str,
        priority: int = 5,
        max_retries: int = 3,
    ) -> Job:
        now = datetime.now(timezone.utc)
        job = Job(
            id=str(uuid4()),
            tenant_id=tenant_id,
            job_type=job_type,
            payload=payload,
            created_by=created_by,
            priority=priority,
            max_retries=max_retries,
            status="pending",
            retry_count=0,
            queued_at=now,
            created_at=now,
            updated_at=now,
        )
        self._db.add(job)
        await self._db.flush()
        return job

    async def update(self, job_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(Job).where(Job.id == job_id).values(**fields)
        )
