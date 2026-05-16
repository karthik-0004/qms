"""PT Service — Proficiency testing API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_permission
from rainer_auth_lib.permissions import Permission
from rainer_common.responses import PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.database import get_db
from ....domain.services import PTDomainService
from ....infra.db.repositories import PTProgramRepository, PTRoundRepository
from ....schemas.requests import CreatePTProgramRequest, CreatePTRoundRequest, UpdatePTRoundRequest
from ....schemas.responses import PTProgramResponse, PTRoundResponse, PTScoreResponse

router = APIRouter(prefix="/pt", tags=["Proficiency Testing"])
logger = structlog.get_logger(__name__)


def _get_service(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]) -> PTDomainService:
    return PTDomainService(
        program_repo=PTProgramRepository(db),
        round_repo=PTRoundRepository(db),
        tenant_id=current_user.tenant_id or "",
    )


@router.get("/programs", response_model=PaginatedResponse[PTProgramResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="List PT programs")
async def list_programs(
    current_user: CurrentUser,
    service: Annotated[PTDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
) -> PaginatedResponse[PTProgramResponse]:
    programs, total = await service.list_programs(page=pagination.page, page_size=pagination.page_size)
    return PaginatedResponse.of(
        data=[PTProgramResponse.model_validate(p, from_attributes=True) for p in programs],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.post("/programs", response_model=SuccessResponse[PTProgramResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Create a PT program")
async def create_program(
    payload: CreatePTProgramRequest,
    current_user: CurrentUser,
    service: Annotated[PTDomainService, Depends(_get_service)],
) -> SuccessResponse[PTProgramResponse]:
    program = await service.create_program(
        provider=payload.provider,
        scheme_name=payload.scheme_name,
        parameter=payload.parameter,
        frequency_months=payload.frequency_months,
        created_by=current_user.sub,
    )
    return SuccessResponse.of(PTProgramResponse.model_validate(program, from_attributes=True))


@router.get("/programs/{program_id}", response_model=SuccessResponse[PTProgramResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="Get PT program")
async def get_program(
    program_id: str,
    current_user: CurrentUser,
    service: Annotated[PTDomainService, Depends(_get_service)],
) -> SuccessResponse[PTProgramResponse]:
    program = await service.get_program(program_id)
    return SuccessResponse.of(PTProgramResponse.model_validate(program, from_attributes=True))


@router.get("/programs/{program_id}/rounds", response_model=SuccessResponse[list[PTRoundResponse]],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="List rounds for a PT program")
async def list_rounds_for_program(
    program_id: str,
    current_user: CurrentUser,
    service: Annotated[PTDomainService, Depends(_get_service)],
) -> SuccessResponse[list[PTRoundResponse]]:
    rounds = await service.list_rounds_for_program(program_id)
    return SuccessResponse.of([PTRoundResponse.model_validate(r, from_attributes=True) for r in rounds])


@router.post("/rounds", response_model=SuccessResponse[PTRoundResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Create a PT round")
async def create_round(
    payload: CreatePTRoundRequest,
    current_user: CurrentUser,
    service: Annotated[PTDomainService, Depends(_get_service)],
) -> SuccessResponse[PTRoundResponse]:
    pt_round = await service.create_round(
        program_id=payload.program_id,
        round_id=payload.round_id,
        created_by=current_user.sub,
        sample_received_date=payload.sample_received_date,
        result_due_date=payload.result_due_date,
        notes=payload.notes,
    )
    return SuccessResponse.of(PTRoundResponse.model_validate(pt_round, from_attributes=True))


@router.get("/rounds/{round_id}", response_model=SuccessResponse[PTRoundResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="Get PT round")
async def get_round(
    round_id: str,
    current_user: CurrentUser,
    service: Annotated[PTDomainService, Depends(_get_service)],
) -> SuccessResponse[PTRoundResponse]:
    pt_round = await service.get_round(round_id)
    return SuccessResponse.of(PTRoundResponse.model_validate(pt_round, from_attributes=True))


@router.patch("/rounds/{round_id}", response_model=SuccessResponse[PTRoundResponse],
              dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
              summary="Update a PT round")
async def update_round(
    round_id: str,
    payload: UpdatePTRoundRequest,
    current_user: CurrentUser,
    service: Annotated[PTDomainService, Depends(_get_service)],
) -> SuccessResponse[PTRoundResponse]:
    fields = payload.model_dump(exclude_none=True)
    pt_round = await service.update_round(round_id, **fields)
    return SuccessResponse.of(PTRoundResponse.model_validate(pt_round, from_attributes=True))


@router.get("/rounds/{round_id}/calculate-scores", response_model=SuccessResponse[PTScoreResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
            summary="Calculate z-score and En number for a PT round")
async def calculate_scores(
    round_id: str,
    current_user: CurrentUser,
    service: Annotated[PTDomainService, Depends(_get_service)],
) -> SuccessResponse[PTScoreResponse]:
    scores = await service.calculate_scores(round_id)
    return SuccessResponse.of(PTScoreResponse(**scores))
