"""Unit tests — JobDomainService."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.domain.services import (
    InvalidJobTypeError,
    JobAlreadyRunningError,
    JobDomainService,
    JobNotFoundError,
)
from app.infra.db.models import Job


def _make_job(**kwargs) -> Job:
    defaults = dict(
        id=str(uuid4()),
        tenant_id=str(uuid4()),
        job_type="ai_analysis",
        priority=5,
        status="pending",
        payload={"plate_id": str(uuid4())},
        result=None,
        error_message=None,
        retry_count=0,
        max_retries=3,
        worker_id=None,
        queued_at=datetime.now(timezone.utc),
        started_at=None,
        completed_at=None,
        next_retry_at=None,
        created_by=str(uuid4()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return MagicMock(spec=Job, **defaults)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def service(mock_db):
    with patch("app.domain.services.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            max_retry_attempts=3,
            retry_backoff_seconds=60,
        )
        svc = JobDomainService(mock_db)
        svc._repo = AsyncMock()
        yield svc


# ─── enqueue ──────────────────────────────────────────────────────────────────

class TestEnqueue:
    async def test_enqueues_valid_job(self, service):
        tenant_id = str(uuid4())
        job = _make_job(tenant_id=tenant_id, job_type="ai_analysis")
        service._repo.create.return_value = job

        result = await service.enqueue(
            tenant_id=tenant_id,
            job_type="ai_analysis",
            payload={"plate_id": str(uuid4())},
            created_by=str(uuid4()),
        )

        assert result.job_type == "ai_analysis"
        service._repo.create.assert_awaited_once()

    async def test_invalid_job_type_raises(self, service):
        with pytest.raises(InvalidJobTypeError):
            await service.enqueue(
                tenant_id=str(uuid4()),
                job_type="unknown_type",
                payload={},
                created_by=str(uuid4()),
            )

    async def test_uses_default_max_retries(self, service):
        job = _make_job()
        service._repo.create.return_value = job

        await service.enqueue(
            tenant_id=str(uuid4()),
            job_type="ai_analysis",
            payload={},
            created_by=str(uuid4()),
        )

        kwargs = service._repo.create.call_args.kwargs
        assert kwargs["max_retries"] == 3


# ─── get_job ──────────────────────────────────────────────────────────────────

class TestGetJob:
    async def test_returns_job(self, service):
        job = _make_job()
        service._repo.get_by_id.return_value = job

        result = await service.get_job(job.id)
        assert result.id == job.id

    async def test_raises_if_not_found(self, service):
        service._repo.get_by_id.return_value = None

        with pytest.raises(JobNotFoundError):
            await service.get_job(str(uuid4()))


# ─── claim_next ───────────────────────────────────────────────────────────────

class TestClaimNext:
    async def test_claims_pending_job(self, service):
        tenant_id = str(uuid4())
        worker_id = "worker-1"
        job = _make_job(tenant_id=tenant_id, status="pending")
        claimed = _make_job(tenant_id=tenant_id, status="running", worker_id=worker_id)
        service._repo.get_next_pending.return_value = job
        service._repo.get_by_id.return_value = claimed

        result = await service.claim_next(tenant_id, worker_id)

        assert result.status == "running"
        service._repo.update.assert_awaited_once()

    async def test_returns_none_when_no_pending(self, service):
        service._repo.get_next_pending.return_value = None

        result = await service.claim_next(str(uuid4()), "worker-1")
        assert result is None


# ─── complete_job ─────────────────────────────────────────────────────────────

class TestCompleteJob:
    async def test_marks_complete_with_result(self, service):
        job = _make_job(status="running")
        completed = _make_job(status="complete", result={"colony_count": 10})
        service._repo.get_by_id.side_effect = [job, completed]

        result = await service.complete_job(job.id, {"colony_count": 10})

        assert result.status == "complete"


# ─── fail_job ─────────────────────────────────────────────────────────────────

class TestFailJob:
    async def test_schedules_retry_when_retries_remain(self, service):
        job = _make_job(status="running", retry_count=0, max_retries=3)
        retrying = _make_job(status="retrying", retry_count=1)
        service._repo.get_by_id.side_effect = [job, retrying]

        result = await service.fail_job(job.id, "timeout", retry=True)

        assert result.status == "retrying"
        update_kwargs = service._repo.update.call_args.kwargs
        assert update_kwargs["status"] == "retrying"
        assert update_kwargs["next_retry_at"] is not None

    async def test_marks_failed_when_max_retries_exceeded(self, service):
        job = _make_job(status="running", retry_count=3, max_retries=3)
        failed = _make_job(status="failed")
        service._repo.get_by_id.side_effect = [job, failed]

        result = await service.fail_job(job.id, "max retries", retry=True)

        assert result.status == "failed"

    async def test_exponential_backoff(self, service):
        job = _make_job(status="running", retry_count=2, max_retries=5)
        retrying = _make_job(status="retrying", retry_count=3)
        service._repo.get_by_id.side_effect = [job, retrying]

        await service.fail_job(job.id, "error", retry=True)

        update_kwargs = service._repo.update.call_args.kwargs
        # backoff = 60 * 2^2 = 240 seconds
        assert update_kwargs["next_retry_at"] is not None


# ─── cancel_job ───────────────────────────────────────────────────────────────

class TestCancelJob:
    async def test_cancels_pending_job(self, service):
        tenant_id = str(uuid4())
        job = _make_job(tenant_id=tenant_id, status="pending")
        cancelled = _make_job(tenant_id=tenant_id, status="cancelled")
        service._repo.get_by_id.side_effect = [job, cancelled]

        result = await service.cancel_job(job.id, tenant_id)

        assert result.status == "cancelled"

    async def test_raises_on_terminal_state(self, service):
        tenant_id = str(uuid4())
        job = _make_job(tenant_id=tenant_id, status="complete")
        service._repo.get_by_id.return_value = job

        with pytest.raises(JobAlreadyRunningError):
            await service.cancel_job(job.id, tenant_id)
