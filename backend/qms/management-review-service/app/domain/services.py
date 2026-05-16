"""Management Review Service — Management review domain service."""

from datetime import datetime, timezone

import structlog

from rainer_common.exceptions import ForbiddenError, NotFoundError

from ..infra.db.models import ManagementReview
from ..infra.db.repositories import ManagementReviewRepository

logger = structlog.get_logger(__name__)


class ManagementReviewDomainService:
    """Management review lifecycle: planned → in_progress → completed → approved."""

    def __init__(self, review_repo: ManagementReviewRepository, tenant_id: str) -> None:
        self._reviews = review_repo
        self._tenant_id = tenant_id

    async def list_reviews(
        self,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ManagementReview], int]:
        return await self._reviews.list_reviews(
            tenant_id=self._tenant_id,
            status=status,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def create_review(
        self,
        review_number: str,
        title: str,
        scheduled_date: datetime,
        created_by: str,
        facilitator_id: str | None = None,
        attendees: list | None = None,
        agenda: str | None = None,
        next_review_date: datetime | None = None,
    ) -> ManagementReview:
        review = await self._reviews.create(
            tenant_id=self._tenant_id,
            review_number=review_number,
            title=title,
            scheduled_date=scheduled_date,
            created_by=created_by,
            facilitator_id=facilitator_id,
            attendees=attendees or [],
            agenda=agenda,
            next_review_date=next_review_date,
        )
        logger.info("management_review_created", review_id=review.id, tenant=self._tenant_id)
        return review

    async def get_review(self, review_id: str) -> ManagementReview:
        review = await self._reviews.get_by_id(review_id)
        if not review:
            raise NotFoundError("ManagementReview", review_id)
        if review.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this management review")
        return review

    async def update_review(self, review_id: str, **fields) -> ManagementReview:
        await self.get_review(review_id)
        allowed = {"title", "scheduled_date", "facilitator_id", "attendees",
                   "status", "agenda", "minutes", "outcomes", "action_items",
                   "next_review_date"}
        filtered = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if filtered:
            await self._reviews.update(review_id, **filtered)
        return await self.get_review(review_id)

    async def complete_review(self, review_id: str) -> ManagementReview:
        await self.get_review(review_id)
        await self._reviews.update(
            review_id,
            completed_date=datetime.now(timezone.utc),
            status="completed",
        )
        logger.info("management_review_completed", review_id=review_id)
        return await self.get_review(review_id)
