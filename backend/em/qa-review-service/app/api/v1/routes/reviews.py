"""QA Review Service — QA review workflow API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....domain.services import QAReviewDomainService
from ....schemas.requests import AddCommentRequest, AssignReviewerRequest, CreateReviewRequest, TransitionStatusRequest
from ....schemas.responses import CommentResponse, ReviewResponse

router = APIRouter(prefix="/reviews", tags=["QA Reviews"])
logger = structlog.get_logger(__name__)

TenantId = Annotated[str, Header(alias="x-tenant-id")]
UserId = Annotated[str, Header(alias="x-user-id")]


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> QAReviewDomainService:
    return QAReviewDomainService(db)


@router.get("", response_model=dict, summary="List QA reviews (paginated)")
async def list_reviews(
    tenant_id: TenantId,
    service: Annotated[QAReviewDomainService, Depends(_get_service)],
    status: str | None = Query(default=None),
    reviewer_id: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    reviews, total = await service.list_reviews(
        tenant_id=tenant_id, status=status, reviewer_id=reviewer_id,
        priority=priority, offset=offset, limit=limit,
    )
    return {
        "data": [ReviewResponse.model_validate(r, from_attributes=True) for r in reviews],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("", response_model=ReviewResponse, status_code=201, summary="Create a QA review")
async def create_review(
    payload: CreateReviewRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[QAReviewDomainService, Depends(_get_service)],
) -> ReviewResponse:
    review = await service.create_review(
        tenant_id=tenant_id,
        plate_id=payload.plate_id,
        analysis_run_id=payload.analysis_run_id,
        created_by=user_id,
        priority=payload.priority,
        due_at=payload.due_at,
    )
    return ReviewResponse.model_validate(review, from_attributes=True)


@router.get("/{review_id}", response_model=ReviewResponse, summary="Get review details")
async def get_review(
    review_id: str,
    service: Annotated[QAReviewDomainService, Depends(_get_service)],
) -> ReviewResponse:
    review = await service.get_review(review_id)
    return ReviewResponse.model_validate(review, from_attributes=True)


@router.post("/{review_id}/assign", response_model=ReviewResponse, summary="Assign reviewer")
async def assign_reviewer(
    review_id: str,
    payload: AssignReviewerRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[QAReviewDomainService, Depends(_get_service)],
) -> ReviewResponse:
    review = await service.assign_reviewer(
        review_id=review_id, tenant_id=tenant_id,
        reviewer_id=payload.reviewer_id, assigned_by=user_id,
    )
    return ReviewResponse.model_validate(review, from_attributes=True)


@router.post("/{review_id}/transition", response_model=ReviewResponse, summary="Transition review status")
async def transition_status(
    review_id: str,
    payload: TransitionStatusRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[QAReviewDomainService, Depends(_get_service)],
) -> ReviewResponse:
    review = await service.transition_status(
        review_id=review_id,
        tenant_id=tenant_id,
        new_status=payload.new_status,
        changed_by=user_id,
        decision=payload.decision,
        review_notes=payload.review_notes,
        override_colony_count=payload.override_colony_count,
        override_reason=payload.override_reason,
        ai_result_accepted=payload.ai_result_accepted,
    )
    return ReviewResponse.model_validate(review, from_attributes=True)


@router.get("/{review_id}/comments", response_model=list[CommentResponse], summary="List review comments")
async def list_comments(
    review_id: str,
    service: Annotated[QAReviewDomainService, Depends(_get_service)],
) -> list[CommentResponse]:
    comments = await service.list_comments(review_id)
    return [CommentResponse.model_validate(c, from_attributes=True) for c in comments]


@router.post("/{review_id}/comments", response_model=CommentResponse, status_code=201,
             summary="Add comment to review")
async def add_comment(
    review_id: str,
    payload: AddCommentRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[QAReviewDomainService, Depends(_get_service)],
) -> CommentResponse:
    comment = await service.add_comment(
        review_id=review_id, tenant_id=tenant_id,
        author_id=user_id, body=payload.body, is_internal=payload.is_internal,
    )
    return CommentResponse.model_validate(comment, from_attributes=True)
