"""QA Review Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import QAReview, QAReviewComment


class QAReviewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, review_id: str) -> QAReview | None:
        result = await self._db.execute(
            select(QAReview).where(
                QAReview.id == review_id,
                QAReview.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_plate(self, plate_id: str) -> QAReview | None:
        result = await self._db.execute(
            select(QAReview).where(
                QAReview.plate_id == plate_id,
                QAReview.deleted_at.is_(None),
            ).order_by(QAReview.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: str,
        status: str | None = None,
        reviewer_id: str | None = None,
        priority: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[QAReview], int]:
        query = select(QAReview).where(
            QAReview.tenant_id == tenant_id,
            QAReview.deleted_at.is_(None),
        )
        count_q = select(func.count()).select_from(QAReview).where(
            QAReview.tenant_id == tenant_id,
            QAReview.deleted_at.is_(None),
        )
        if status:
            query = query.where(QAReview.status == status)
            count_q = count_q.where(QAReview.status == status)
        if reviewer_id:
            query = query.where(QAReview.reviewer_id == reviewer_id)
            count_q = count_q.where(QAReview.reviewer_id == reviewer_id)
        if priority:
            query = query.where(QAReview.priority == priority)
            count_q = count_q.where(QAReview.priority == priority)

        query = query.offset(offset).limit(limit).order_by(
            QAReview.due_at.asc().nulls_last(),
            QAReview.created_at.desc(),
        )
        items = list((await self._db.execute(query)).scalars().all())
        total = (await self._db.execute(count_q)).scalar_one()
        return items, total

    async def create(
        self,
        tenant_id: str,
        plate_id: str,
        analysis_run_id: str,
        created_by: str,
        priority: str = "normal",
        due_at: datetime | None = None,
    ) -> QAReview:
        now = datetime.now(timezone.utc)
        review = QAReview(
            id=str(uuid4()),
            tenant_id=tenant_id,
            plate_id=plate_id,
            analysis_run_id=analysis_run_id,
            created_by=created_by,
            status="pending",
            priority=priority,
            due_at=due_at,
            annotations=[],
            created_at=now,
            updated_at=now,
        )
        self._db.add(review)
        await self._db.flush()
        return review

    async def update(self, review_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(QAReview).where(QAReview.id == review_id).values(**fields)
        )


class QAReviewCommentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_by_review(self, review_id: str) -> list[QAReviewComment]:
        result = await self._db.execute(
            select(QAReviewComment)
            .where(QAReviewComment.review_id == review_id)
            .order_by(QAReviewComment.created_at.asc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        review_id: str,
        tenant_id: str,
        author_id: str,
        body: str,
        is_internal: bool = False,
    ) -> QAReviewComment:
        now = datetime.now(timezone.utc)
        comment = QAReviewComment(
            id=str(uuid4()),
            review_id=review_id,
            tenant_id=tenant_id,
            author_id=author_id,
            body=body,
            is_internal=is_internal,
            created_at=now,
            updated_at=now,
        )
        self._db.add(comment)
        await self._db.flush()
        return comment
