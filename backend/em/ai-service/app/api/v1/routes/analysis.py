"""AI Service — Analysis run API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....domain.services import AIDomainService
from ....schemas.requests import CompleteRunRequest, CreateAnalysisRunRequest, FailRunRequest
from ....schemas.responses import AnalysisResultResponse, AnalysisRunResponse

router = APIRouter(prefix="/analysis", tags=["AI Analysis"])
logger = structlog.get_logger(__name__)

TenantId = Annotated[str, Header(alias="x-tenant-id")]
UserId = Annotated[str, Header(alias="x-user-id")]


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> AIDomainService:
    return AIDomainService(db)


@router.get("/runs", response_model=dict, summary="List analysis runs")
async def list_runs(
    tenant_id: TenantId,
    service: Annotated[AIDomainService, Depends(_get_service)],
    status: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    runs, total = await service.list_runs(tenant_id=tenant_id, status=status, offset=offset, limit=limit)
    return {
        "data": [AnalysisRunResponse.model_validate(r, from_attributes=True) for r in runs],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("/runs", response_model=AnalysisRunResponse, status_code=201, summary="Create analysis run")
async def create_run(
    payload: CreateAnalysisRunRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[AIDomainService, Depends(_get_service)],
) -> AnalysisRunResponse:
    run = await service.create_analysis_run(
        tenant_id=tenant_id,
        plate_id=payload.plate_id,
        image_id=payload.image_id,
        triggered_by=user_id,
        job_id=payload.job_id,
        model_name=payload.model_name,
        model_version=payload.model_version,
    )
    return AnalysisRunResponse.model_validate(run, from_attributes=True)


@router.get("/runs/{run_id}", response_model=AnalysisRunResponse, summary="Get analysis run")
async def get_run(
    run_id: str,
    service: Annotated[AIDomainService, Depends(_get_service)],
) -> AnalysisRunResponse:
    run = await service.get_run(run_id)
    return AnalysisRunResponse.model_validate(run, from_attributes=True)


@router.post("/runs/{run_id}/start", response_model=AnalysisRunResponse, summary="Start analysis run")
async def start_run(
    run_id: str,
    service: Annotated[AIDomainService, Depends(_get_service)],
) -> AnalysisRunResponse:
    run = await service.start_run(run_id)
    return AnalysisRunResponse.model_validate(run, from_attributes=True)


@router.post("/runs/{run_id}/complete", response_model=AnalysisRunResponse, summary="Complete analysis run")
async def complete_run(
    run_id: str,
    payload: CompleteRunRequest,
    service: Annotated[AIDomainService, Depends(_get_service)],
) -> AnalysisRunResponse:
    run, _result = await service.complete_run(
        run_id=run_id,
        colony_count=payload.colony_count,
        colony_positions=payload.colony_positions,
        confidence_score=payload.confidence_score,
        contamination_detected=payload.contamination_detected,
        raw_output=payload.raw_output,
        contamination_type=payload.contamination_type,
        anomaly_flags=payload.anomaly_flags,
    )
    return AnalysisRunResponse.model_validate(run, from_attributes=True)


@router.post("/runs/{run_id}/fail", response_model=AnalysisRunResponse, summary="Mark analysis run as failed")
async def fail_run(
    run_id: str,
    payload: FailRunRequest,
    service: Annotated[AIDomainService, Depends(_get_service)],
) -> AnalysisRunResponse:
    run = await service.fail_run(run_id, error_message=payload.error_message)
    return AnalysisRunResponse.model_validate(run, from_attributes=True)


@router.get("/runs/{run_id}/result", response_model=AnalysisResultResponse | None,
            summary="Get analysis result for run")
async def get_result(
    run_id: str,
    service: Annotated[AIDomainService, Depends(_get_service)],
) -> AnalysisResultResponse | None:
    result = await service.get_result_for_run(run_id)
    if not result:
        return None
    return AnalysisResultResponse.model_validate(result, from_attributes=True)
