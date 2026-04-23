"""QA Review Service — Domain service layer."""

from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from ..infra.db.repositories import QAReviewCommentRepository, QAReviewRepository
from ..infra.db.models import QAReview, QAReviewComment

logger = structlog.get_logger(__name__)

VALID_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["in_review", "cancelled"],
    "in_review": ["approved", "rejected", "on_hold"],
    "on_hold": ["in_review", "cancelled"],
    "approved": [],
    "rejected": [],
    "cancelled": [],
}


class QAReviewServiceError(Exception):
    pass


class ReviewNotFoundError(QAReviewServiceError):
    pass


class InvalidReviewTransitionError(QAReviewServiceError):
    pass


class QAReviewDomainService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = QAReviewRepository(db)
        self._comment_repo = QAReviewCommentRepository(db)

    async def create_review(
        self,
        tenant_id: str,
        plate_id: str,
        analysis_run_id: str,
        created_by: str,
        priority: str = "normal",
        due_at: datetime | None = None,
    ) -> QAReview:
        review = await self._repo.create(
            tenant_id=tenant_id,
            plate_id=plate_id,
            analysis_run_id=analysis_run_id,
            created_by=created_by,
            priority=priority,
            due_at=due_at,
        )
        logger.info(
            "qa_review.created",
            review_id=review.id,
            plate_id=plate_id,
            priority=priority,
            tenant_id=tenant_id,
        )
        return review

    async def get_review(self, review_id: str) -> QAReview:
        review = await self._repo.get_by_id(review_id)
        if not review:
            raise ReviewNotFoundError(f"Review '{review_id}' not found.")
        return review

    async def list_reviews(
        self,
        tenant_id: str,
        status: str | None = None,
        reviewer_id: str | None = None,
        priority: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[QAReview], int]:
        return await self._repo.list_by_tenant(
            tenant_id=tenant_id,
            status=status,
            reviewer_id=reviewer_id,
            priority=priority,
            offset=offset,
            limit=limit,
        )

    async def assign_reviewer(
        self,
        review_id: str,
        tenant_id: str,
        reviewer_id: str,
        assigned_by: str,
    ) -> QAReview:
        review = await self.get_review(review_id)
        if review.tenant_id != tenant_id:
            raise ReviewNotFoundError(f"Review '{review_id}' not found.")
        await self._repo.update(
            review_id,
            reviewer_id=reviewer_id,
            assigned_at=datetime.now(timezone.utc),
        )
        logger.info("qa_review.assigned", review_id=review_id, reviewer_id=reviewer_id)
        return await self.get_review(review_id)

    async def transition_status(
        self,
        review_id: str,
        tenant_id: str,
        new_status: str,
        changed_by: str,
        decision: str | None = None,
        review_notes: str | None = None,
        override_colony_count: int | None = None,
        override_reason: str | None = None,
        ai_result_accepted: bool | None = None,
    ) -> QAReview:
        review = await self.get_review(review_id)
        if review.tenant_id != tenant_id:
            raise ReviewNotFoundError(f"Review '{review_id}' not found.")

        allowed = VALID_TRANSITIONS.get(review.status, [])
        if new_status not in allowed:
            raise InvalidReviewTransitionError(
                f"Cannot transition review from '{review.status}' to '{new_status}'."
            )

        update_fields: dict = {"status": new_status}
        if new_status == "in_review":
            update_fields["review_started_at"] = datetime.now(timezone.utc)
        elif new_status in ("approved", "rejected"):
            update_fields["review_completed_at"] = datetime.now(timezone.utc)
            update_fields["decision"] = decision or new_status

        if review_notes is not None:
            update_fields["review_notes"] = review_notes
        if override_colony_count is not None:
            update_fields["override_colony_count"] = override_colony_count
        if override_reason is not None:
            update_fields["override_reason"] = override_reason
        if ai_result_accepted is not None:
            update_fields["ai_result_accepted"] = ai_result_accepted

        await self._repo.update(review_id, **update_fields)
        logger.info(
            "qa_review.status_changed",
            review_id=review_id,
            from_status=review.status,
            to_status=new_status,
            decision=decision,
        )
        return await self.get_review(review_id)

    async def add_comment(
        self,
        review_id: str,
        tenant_id: str,
        author_id: str,
        body: str,
        is_internal: bool = False,
    ) -> QAReviewComment:
        await self.get_review(review_id)
        comment = await self._comment_repo.create(
            review_id=review_id,
            tenant_id=tenant_id,
            author_id=author_id,
            body=body,
            is_internal=is_internal,
        )
        logger.info("qa_review.comment_added", review_id=review_id, comment_id=comment.id)
        return comment

    async def list_comments(self, review_id: str) -> list[QAReviewComment]:
        return await self._comment_repo.list_by_review(review_id)

    async def get_review_for_plate(self, plate_id: str) -> QAReview | None:
        return await self._repo.get_by_plate(plate_id)
