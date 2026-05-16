"""Management Review Service — Management review API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_permission
from rainer_auth_lib.permissions import Permission
from rainer_common.responses import PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.database import get_db
from ....domain.services import ManagementReviewDomainService
from ....infra.db.repositories import ManagementReviewRepository
from ....schemas.requests import CreateManagementReviewRequest, UpdateManagementReviewRequest
from ....schemas.responses import ManagementReviewResponse

router = APIRouter(prefix="/management-reviews", tags=["Management Reviews"])
logger = structlog.get_logger(__name__)


def _get_service(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]) -> ManagementReviewDomainService:
    return ManagementReviewDomainService(
        review_repo=ManagementReviewRepository(db),
        tenant_id=current_user.tenant_id or "",
    )


@router.get("", response_model=PaginatedResponse[ManagementReviewResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="List management reviews")
async def list_management_reviews(
    current_user: CurrentUser,
    service: Annotated[ManagementReviewDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(default=None),
) -> PaginatedResponse[ManagementReviewResponse]:
    reviews, total = await service.list_reviews(
        status=status,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[ManagementReviewResponse.model_validate(r, from_attributes=True) for r in reviews],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.post("", response_model=SuccessResponse[ManagementReviewResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Create a management review")
async def create_management_review(
    payload: CreateManagementReviewRequest,
    current_user: CurrentUser,
    service: Annotated[ManagementReviewDomainService, Depends(_get_service)],
) -> SuccessResponse[ManagementReviewResponse]:
    review = await service.create_review(
        review_number=payload.review_number,
        title=payload.title,
        scheduled_date=payload.scheduled_date,
        created_by=current_user.sub,
        facilitator_id=payload.facilitator_id,
        attendees=payload.attendees,
        agenda=payload.agenda,
        next_review_date=payload.next_review_date,
    )
    return SuccessResponse.of(ManagementReviewResponse.model_validate(review, from_attributes=True))


@router.get("/{review_id}", response_model=SuccessResponse[ManagementReviewResponse],
            dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_READ))],
            summary="Get management review details")
async def get_management_review(
    review_id: str,
    current_user: CurrentUser,
    service: Annotated[ManagementReviewDomainService, Depends(_get_service)],
) -> SuccessResponse[ManagementReviewResponse]:
    review = await service.get_review(review_id)
    return SuccessResponse.of(ManagementReviewResponse.model_validate(review, from_attributes=True))


@router.patch("/{review_id}", response_model=SuccessResponse[ManagementReviewResponse],
              dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
              summary="Update a management review")
async def update_management_review(
    review_id: str,
    payload: UpdateManagementReviewRequest,
    current_user: CurrentUser,
    service: Annotated[ManagementReviewDomainService, Depends(_get_service)],
) -> SuccessResponse[ManagementReviewResponse]:
    fields = payload.model_dump(exclude_none=True)
    review = await service.update_review(review_id, **fields)
    return SuccessResponse.of(ManagementReviewResponse.model_validate(review, from_attributes=True))


@router.post("/{review_id}/complete", response_model=SuccessResponse[ManagementReviewResponse],
             dependencies=[Depends(require_permission(Permission.QUALITY_EVENT_WRITE))],
             summary="Mark management review as completed")
async def complete_management_review(
    review_id: str,
    current_user: CurrentUser,
    service: Annotated[ManagementReviewDomainService, Depends(_get_service)],
) -> SuccessResponse[ManagementReviewResponse]:
    review = await service.complete_review(review_id)
    return SuccessResponse.of(ManagementReviewResponse.model_validate(review, from_attributes=True))
