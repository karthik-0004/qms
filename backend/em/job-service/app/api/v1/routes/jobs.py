"""Job Service — Async job queue API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....domain.services import JobDomainService
from ....schemas.requests import ClaimJobRequest, CompleteJobRequest, EnqueueJobRequest, FailJobRequest
from ....schemas.responses import JobResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])
logger = structlog.get_logger(__name__)

TenantId = Annotated[str, Header(alias="x-tenant-id")]
UserId = Annotated[str, Header(alias="x-user-id")]


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> JobDomainService:
    return JobDomainService(db)


@router.get("", response_model=dict, summary="List jobs (paginated)")
async def list_jobs(
    tenant_id: TenantId,
    service: Annotated[JobDomainService, Depends(_get_service)],
    status: str | None = Query(default=None),
    job_type: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    jobs, total = await service.list_jobs(
        tenant_id=tenant_id, status=status, job_type=job_type, offset=offset, limit=limit
    )
    return {
        "data": [JobResponse.model_validate(j, from_attributes=True) for j in jobs],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("", response_model=JobResponse, status_code=201, summary="Enqueue a new job")
async def enqueue_job(
    payload: EnqueueJobRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[JobDomainService, Depends(_get_service)],
) -> JobResponse:
    job = await service.enqueue(
        tenant_id=tenant_id,
        job_type=payload.job_type,
        payload=payload.payload,
        created_by=user_id,
        priority=payload.priority,
        max_retries=payload.max_retries,
    )
    return JobResponse.model_validate(job, from_attributes=True)


@router.get("/{job_id}", response_model=JobResponse, summary="Get job details")
async def get_job(
    job_id: str,
    service: Annotated[JobDomainService, Depends(_get_service)],
) -> JobResponse:
    job = await service.get_job(job_id)
    return JobResponse.model_validate(job, from_attributes=True)


@router.post("/claim", response_model=JobResponse | None, summary="Claim next pending job")
async def claim_job(
    payload: ClaimJobRequest,
    tenant_id: TenantId,
    service: Annotated[JobDomainService, Depends(_get_service)],
) -> JobResponse | None:
    job = await service.claim_next(
        tenant_id=tenant_id, worker_id=payload.worker_id, job_type=payload.job_type
    )
    if not job:
        return None
    return JobResponse.model_validate(job, from_attributes=True)


@router.post("/{job_id}/complete", response_model=JobResponse, summary="Complete a job")
async def complete_job(
    job_id: str,
    payload: CompleteJobRequest,
    service: Annotated[JobDomainService, Depends(_get_service)],
) -> JobResponse:
    job = await service.complete_job(job_id, result=payload.result)
    return JobResponse.model_validate(job, from_attributes=True)


@router.post("/{job_id}/fail", response_model=JobResponse, summary="Fail a job")
async def fail_job(
    job_id: str,
    payload: FailJobRequest,
    service: Annotated[JobDomainService, Depends(_get_service)],
) -> JobResponse:
    job = await service.fail_job(job_id, error_message=payload.error_message, retry=payload.retry)
    return JobResponse.model_validate(job, from_attributes=True)


@router.post("/{job_id}/cancel", response_model=JobResponse, summary="Cancel a job")
async def cancel_job(
    job_id: str,
    tenant_id: TenantId,
    service: Annotated[JobDomainService, Depends(_get_service)],
) -> JobResponse:
    job = await service.cancel_job(job_id, tenant_id=tenant_id)
    return JobResponse.model_validate(job, from_attributes=True)
