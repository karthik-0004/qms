"""Management Review Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ManagementReview


class ManagementReviewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, review_id: str) -> ManagementReview | None:
        result = await self._db.execute(
            select(ManagementReview).where(ManagementReview.id == review_id)
        )
        return result.scalar_one_or_none()

    async def list_reviews(
        self,
        tenant_id: str,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[ManagementReview], int]:
        query = select(ManagementReview).where(ManagementReview.tenant_id == tenant_id)
        count_q = select(func.count()).select_from(ManagementReview).where(
            ManagementReview.tenant_id == tenant_id
        )
        if status:
            query = query.where(ManagementReview.status == status)
            count_q = count_q.where(ManagementReview.status == status)

        query = query.offset(offset).limit(limit).order_by(ManagementReview.scheduled_date.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(self, tenant_id: str, review_number: str, title: str,
                     scheduled_date: datetime, created_by: str, **kwargs) -> ManagementReview:
        now = datetime.now(timezone.utc)
        review = ManagementReview(
            id=str(uuid4()), tenant_id=tenant_id, review_number=review_number,
            title=title, scheduled_date=scheduled_date, status="planned",
            attendees=[], outcomes=[], action_items=[],
            created_by=created_by, created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(review)
        await self._db.flush()
        return review

    async def update(self, review_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(ManagementReview).where(ManagementReview.id == review_id).values(**fields)
        )
