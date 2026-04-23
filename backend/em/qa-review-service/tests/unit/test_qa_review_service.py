"""Unit tests — QAReviewDomainService."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domain.services import (
    InvalidReviewTransitionError,
    QAReviewDomainService,
    ReviewNotFoundError,
)
from app.infra.db.models import QAReview, QAReviewComment


def _make_review(**kwargs) -> QAReview:
    defaults = dict(
        id=str(uuid4()),
        tenant_id=str(uuid4()),
        plate_id=str(uuid4()),
        analysis_run_id=str(uuid4()),
        reviewer_id=None,
        status="pending",
        decision=None,
        override_colony_count=None,
        override_reason=None,
        ai_result_accepted=None,
        annotations=[],
        review_notes=None,
        priority="normal",
        assigned_at=None,
        review_started_at=None,
        review_completed_at=None,
        due_at=None,
        created_by=str(uuid4()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted_at=None,
    )
    defaults.update(kwargs)
    return MagicMock(spec=QAReview, **defaults)


def _make_comment(**kwargs) -> QAReviewComment:
    defaults = dict(
        id=str(uuid4()),
        review_id=str(uuid4()),
        tenant_id=str(uuid4()),
        author_id=str(uuid4()),
        body="Looks good to me.",
        is_internal=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return MagicMock(spec=QAReviewComment, **defaults)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def service(mock_db):
    svc = QAReviewDomainService(mock_db)
    svc._repo = AsyncMock()
    svc._comment_repo = AsyncMock()
    return svc


# ─── create_review ───────────────────────────────────────────────────────────

class TestCreateReview:
    async def test_creates_review(self, service):
        review = _make_review(priority="urgent")
        service._repo.create.return_value = review

        result = await service.create_review(
            tenant_id=review.tenant_id,
            plate_id=review.plate_id,
            analysis_run_id=review.analysis_run_id,
            created_by=review.created_by,
            priority="urgent",
        )

        assert result.priority == "urgent"
        service._repo.create.assert_awaited_once()


# ─── get_review ───────────────────────────────────────────────────────────────

class TestGetReview:
    async def test_returns_review(self, service):
        review = _make_review()
        service._repo.get_by_id.return_value = review

        result = await service.get_review(review.id)
        assert result.id == review.id

    async def test_raises_if_not_found(self, service):
        service._repo.get_by_id.return_value = None

        with pytest.raises(ReviewNotFoundError):
            await service.get_review(str(uuid4()))


# ─── assign_reviewer ──────────────────────────────────────────────────────────

class TestAssignReviewer:
    async def test_assigns_reviewer(self, service):
        tenant_id = str(uuid4())
        reviewer_id = str(uuid4())
        review = _make_review(tenant_id=tenant_id)
        assigned = _make_review(tenant_id=tenant_id, reviewer_id=reviewer_id)
        service._repo.get_by_id.side_effect = [review, assigned]

        result = await service.assign_reviewer(
            review_id=review.id,
            tenant_id=tenant_id,
            reviewer_id=reviewer_id,
            assigned_by=str(uuid4()),
        )

        assert result.reviewer_id == reviewer_id

    async def test_cross_tenant_raises(self, service):
        review = _make_review(tenant_id=str(uuid4()))
        service._repo.get_by_id.return_value = review

        with pytest.raises(ReviewNotFoundError):
            await service.assign_reviewer(
                review_id=review.id,
                tenant_id=str(uuid4()),  # different tenant
                reviewer_id=str(uuid4()),
                assigned_by=str(uuid4()),
            )


# ─── transition_status ────────────────────────────────────────────────────────

class TestTransitionStatus:
    async def test_pending_to_in_review(self, service):
        tenant_id = str(uuid4())
        review = _make_review(tenant_id=tenant_id, status="pending")
        updated = _make_review(tenant_id=tenant_id, status="in_review")
        service._repo.get_by_id.side_effect = [review, updated]

        result = await service.transition_status(
            review_id=review.id,
            tenant_id=tenant_id,
            new_status="in_review",
            changed_by=str(uuid4()),
        )

        assert result.status == "in_review"
        service._repo.update.assert_awaited_once()

    async def test_in_review_to_approved(self, service):
        tenant_id = str(uuid4())
        review = _make_review(tenant_id=tenant_id, status="in_review")
        approved = _make_review(tenant_id=tenant_id, status="approved", decision="approved")
        service._repo.get_by_id.side_effect = [review, approved]

        result = await service.transition_status(
            review_id=review.id,
            tenant_id=tenant_id,
            new_status="approved",
            changed_by=str(uuid4()),
            decision="approved",
            ai_result_accepted=True,
        )

        assert result.status == "approved"

    async def test_invalid_transition_raises(self, service):
        tenant_id = str(uuid4())
        review = _make_review(tenant_id=tenant_id, status="approved")
        service._repo.get_by_id.return_value = review

        with pytest.raises(InvalidReviewTransitionError):
            await service.transition_status(
                review_id=review.id,
                tenant_id=tenant_id,
                new_status="pending",
                changed_by=str(uuid4()),
            )

    async def test_override_colony_count_stored(self, service):
        tenant_id = str(uuid4())
        review = _make_review(tenant_id=tenant_id, status="in_review")
        updated = _make_review(tenant_id=tenant_id, status="approved", override_colony_count=5)
        service._repo.get_by_id.side_effect = [review, updated]

        await service.transition_status(
            review_id=review.id,
            tenant_id=tenant_id,
            new_status="approved",
            changed_by=str(uuid4()),
            override_colony_count=5,
            override_reason="Manual count",
        )

        update_kwargs = service._repo.update.call_args.kwargs
        assert update_kwargs["override_colony_count"] == 5
        assert update_kwargs["override_reason"] == "Manual count"


# ─── add_comment ──────────────────────────────────────────────────────────────

class TestAddComment:
    async def test_adds_public_comment(self, service):
        review = _make_review()
        comment = _make_comment(review_id=review.id, is_internal=False)
        service._repo.get_by_id.return_value = review
        service._comment_repo.create.return_value = comment

        result = await service.add_comment(
            review_id=review.id,
            tenant_id=review.tenant_id,
            author_id=str(uuid4()),
            body="Colony count confirmed.",
        )

        assert result.is_internal is False
        service._comment_repo.create.assert_awaited_once()

    async def test_adds_internal_comment(self, service):
        review = _make_review()
        comment = _make_comment(review_id=review.id, is_internal=True)
        service._repo.get_by_id.return_value = review
        service._comment_repo.create.return_value = comment

        result = await service.add_comment(
            review_id=review.id,
            tenant_id=review.tenant_id,
            author_id=str(uuid4()),
            body="Internal QA note.",
            is_internal=True,
        )

        assert result.is_internal is True


# ─── list_comments ───────────────────────────────────────────────────────────

class TestListComments:
    async def test_returns_comments(self, service):
        comments = [_make_comment() for _ in range(3)]
        service._comment_repo.list_by_review.return_value = comments

        result = await service.list_comments(str(uuid4()))

        assert len(result) == 3
