"""Risk Service — Risk management API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_permission
from rainer_auth_lib.permissions import Permission
from rainer_common.responses import PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.database import get_db
from ....domain.services import RiskDomainService
from ....infra.db.repositories import RiskRepository
from ....schemas.requests import CreateRiskRequest, UpdateRiskRequest
from ....schemas.responses import RiskMatrixCell, RiskResponse

router = APIRouter(prefix="/risks", tags=["Risks"])
logger = structlog.get_logger(__name__)


def _get_service(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]) -> RiskDomainService:
    return RiskDomainService(
        risk_repo=RiskRepository(db),
        tenant_id=current_user.tenant_id or "",
    )


@router.get("/matrix", response_model=SuccessResponse[list[RiskMatrixCell]],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="Get 5x5 risk matrix")
async def get_risk_matrix(
    current_user: CurrentUser,
    service: Annotated[RiskDomainService, Depends(_get_service)],
) -> SuccessResponse[list[RiskMatrixCell]]:
    matrix = await service.get_risk_matrix()
    return SuccessResponse.of([RiskMatrixCell(**cell) for cell in matrix])


@router.get("", response_model=PaginatedResponse[RiskResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="List risks")
async def list_risks(
    current_user: CurrentUser,
    service: Annotated[RiskDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    category: str | None = Query(default=None),
    status: str | None = Query(default=None),
    owner_id: str | None = Query(default=None),
) -> PaginatedResponse[RiskResponse]:
    risks, total = await service.list_risks(
        category=category, status=status, owner_id=owner_id,
        page=pagination.page, page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[RiskResponse.model_validate(r, from_attributes=True) for r in risks],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.post("", response_model=SuccessResponse[RiskResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Create a risk")
async def create_risk(
    payload: CreateRiskRequest,
    current_user: CurrentUser,
    service: Annotated[RiskDomainService, Depends(_get_service)],
) -> SuccessResponse[RiskResponse]:
    risk = await service.create_risk(
        risk_id=payload.risk_id,
        category=payload.category,
        description=payload.description,
        severity=payload.severity,
        likelihood=payload.likelihood,
        created_by=current_user.sub,
        mitigation_plan=payload.mitigation_plan,
        owner_id=payload.owner_id,
        review_date=payload.review_date,
    )
    return SuccessResponse.of(RiskResponse.model_validate(risk, from_attributes=True))


@router.get("/{risk_id}", response_model=SuccessResponse[RiskResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="Get risk details")
async def get_risk(
    risk_id: str,
    current_user: CurrentUser,
    service: Annotated[RiskDomainService, Depends(_get_service)],
) -> SuccessResponse[RiskResponse]:
    risk = await service.get_risk(risk_id)
    return SuccessResponse.of(RiskResponse.model_validate(risk, from_attributes=True))


@router.patch("/{risk_id}", response_model=SuccessResponse[RiskResponse],
              dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
              summary="Update a risk")
async def update_risk(
    risk_id: str,
    payload: UpdateRiskRequest,
    current_user: CurrentUser,
    service: Annotated[RiskDomainService, Depends(_get_service)],
) -> SuccessResponse[RiskResponse]:
    fields = payload.model_dump(exclude_none=True)
    risk = await service.update_risk(risk_id, **fields)
    return SuccessResponse.of(RiskResponse.model_validate(risk, from_attributes=True))
