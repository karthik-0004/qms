"""Job Service — Domain service layer."""

from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from ..infra.db.repositories import JobRepository
from ..infra.db.models import Job
from ..core.config import get_settings

logger = structlog.get_logger(__name__)

VALID_JOB_TYPES = {
    "ai_analysis",
    "report_generation",
    "data_export",
    "plate_summary",
    "notification_dispatch",
}


class JobServiceError(Exception):
    pass


class JobNotFoundError(JobServiceError):
    pass


class InvalidJobTypeError(JobServiceError):
    pass


class JobAlreadyRunningError(JobServiceError):
    pass


class JobDomainService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = JobRepository(db)
        self._settings = get_settings()

    async def enqueue(
        self,
        tenant_id: str,
        job_type: str,
        payload: dict,
        created_by: str,
        priority: int = 5,
        max_retries: int | None = None,
    ) -> Job:
        if job_type not in VALID_JOB_TYPES:
            raise InvalidJobTypeError(
                f"Unknown job type '{job_type}'. Valid: {sorted(VALID_JOB_TYPES)}"
            )
        job = await self._repo.create(
            tenant_id=tenant_id,
            job_type=job_type,
            payload=payload,
            created_by=created_by,
            priority=priority,
            max_retries=max_retries if max_retries is not None else self._settings.max_retry_attempts,
        )
        logger.info(
            "job.enqueued",
            job_id=job.id,
            job_type=job_type,
            priority=priority,
            tenant_id=tenant_id,
        )
        return job

    async def get_job(self, job_id: str) -> Job:
        job = await self._repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundError(f"Job '{job_id}' not found.")
        return job

    async def list_jobs(
        self,
        tenant_id: str,
        status: str | None = None,
        job_type: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Job], int]:
        return await self._repo.list_by_tenant(
            tenant_id=tenant_id,
            status=status,
            job_type=job_type,
            offset=offset,
            limit=limit,
        )

    async def claim_next(
        self,
        tenant_id: str,
        worker_id: str,
        job_type: str | None = None,
    ) -> Job | None:
        job = await self._repo.get_next_pending(tenant_id, job_type)
        if not job:
            return None
        await self._repo.update(
            job.id,
            status="running",
            worker_id=worker_id,
            started_at=datetime.now(timezone.utc),
        )
        logger.info("job.claimed", job_id=job.id, worker_id=worker_id)
        return await self.get_job(job.id)

    async def complete_job(self, job_id: str, result: dict) -> Job:
        job = await self.get_job(job_id)
        await self._repo.update(
            job_id,
            status="complete",
            result=result,
            completed_at=datetime.now(timezone.utc),
        )
        logger.info("job.completed", job_id=job_id)
        return await self.get_job(job_id)

    async def fail_job(
        self,
        job_id: str,
        error_message: str,
        retry: bool = True,
    ) -> Job:
        job = await self.get_job(job_id)
        if retry and job.retry_count < job.max_retries:
            backoff = self._settings.retry_backoff_seconds * (2 ** job.retry_count)
            next_retry = datetime.now(timezone.utc) + timedelta(seconds=backoff)
            await self._repo.update(
                job_id,
                status="retrying",
                error_message=error_message,
                retry_count=job.retry_count + 1,
                next_retry_at=next_retry,
            )
            logger.warning(
                "job.scheduled_retry",
                job_id=job_id,
                retry_count=job.retry_count + 1,
                next_retry=next_retry.isoformat(),
            )
        else:
            await self._repo.update(
                job_id,
                status="failed",
                error_message=error_message,
                completed_at=datetime.now(timezone.utc),
            )
            logger.error("job.failed", job_id=job_id, error=error_message)
        return await self.get_job(job_id)

    async def cancel_job(self, job_id: str, tenant_id: str) -> Job:
        job = await self.get_job(job_id)
        if job.tenant_id != tenant_id:
            raise JobNotFoundError(f"Job '{job_id}' not found.")
        if job.status in ("complete", "failed", "cancelled"):
            raise JobAlreadyRunningError(f"Job '{job_id}' is already in terminal state '{job.status}'.")
        await self._repo.update(job_id, status="cancelled")
        logger.info("job.cancelled", job_id=job_id)
        return await self.get_job(job_id)
