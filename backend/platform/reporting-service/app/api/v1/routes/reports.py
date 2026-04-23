"""Reporting Service — Report generation API routes."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from rainer_auth_lib.dependencies import CurrentUser
from rainer_common.responses import SuccessResponse

from ....domain.services import ReportingDomainService

router = APIRouter(prefix="/reports", tags=["Reports"])


def _get_service() -> ReportingDomainService:
    return ReportingDomainService()


class GenerateReportRequest(BaseModel):
    template_key: str
    data: dict[str, Any] = {}
    format: str = "pdf"


@router.post("/generate", response_model=SuccessResponse[dict], status_code=202,
             summary="Trigger async report generation")
async def generate_report(
    payload: GenerateReportRequest,
    current_user: CurrentUser,
    service: Annotated[ReportingDomainService, Depends(_get_service)],
) -> SuccessResponse[dict]:
    job = await service.generate_report(
        template_key=payload.template_key,
        data=payload.data,
        format=payload.format,
        tenant_id=current_user.tenant_id,
        requested_by=current_user.sub,
    )
    return SuccessResponse.of(job)


@router.get("/jobs/{job_id}", response_model=SuccessResponse[dict],
            summary="Check report generation job status")
async def get_job_status(
    job_id: str,
    current_user: CurrentUser,
    service: Annotated[ReportingDomainService, Depends(_get_service)],
) -> SuccessResponse[dict]:
    status = await service.get_job_status(job_id)
    return SuccessResponse.of(status)


@router.get("/templates", response_model=SuccessResponse[list[dict]],
            summary="List available report templates")
async def list_templates(
    current_user: CurrentUser,
    service: Annotated[ReportingDomainService, Depends(_get_service)],
) -> SuccessResponse[list[dict]]:
    templates = await service.list_templates()
    return SuccessResponse.of(templates)
