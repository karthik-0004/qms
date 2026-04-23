"""Unit tests — TrainingDomainService business logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError

from app.domain.services import TrainingDomainService
from app.infra.db.models import TrainingAssignment, TrainingCourse


def make_course(**kwargs) -> TrainingCourse:
    defaults = dict(
        id=str(uuid4()), tenant_id="tenant-1", course_code="TRN-001",
        title="Safety Training", description=None, course_type="online",
        department="QA", document_id=None, duration_hours=2.0,
        passing_score=80, requires_certification=False, recurrence_days=365,
        is_mandatory=True, is_active=True, created_by=str(uuid4()),
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    c = MagicMock(spec=TrainingCourse)
    for k, v in defaults.items():
        setattr(c, k, v)
    return c


def make_assignment(**kwargs) -> TrainingAssignment:
    defaults = dict(
        id=str(uuid4()), tenant_id="tenant-1",
        course_id=str(uuid4()), user_id=str(uuid4()),
        assigned_by=str(uuid4()), due_date=None, status="assigned",
        score=None, passed=None, completed_at=None, cert_expiry_date=None,
        notes=None, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    a = MagicMock(spec=TrainingAssignment)
    for k, v in defaults.items():
        setattr(a, k, v)
    return a


@pytest.fixture
def course_repo():
    return AsyncMock()


@pytest.fixture
def assignment_repo():
    return AsyncMock()


@pytest.fixture
def svc(course_repo, assignment_repo):
    return TrainingDomainService(course_repo=course_repo, assignment_repo=assignment_repo, tenant_id="tenant-1")


class TestCreateCourse:
    @pytest.mark.asyncio
    async def test_creates_course(self, svc, course_repo):
        course_repo.get_by_code.return_value = None
        mock_course = make_course()
        course_repo.create.return_value = mock_course
        result = await svc.create_course("TRN-001", "Safety Training", str(uuid4()))
        assert result is mock_course

    @pytest.mark.asyncio
    async def test_raises_conflict_if_code_exists(self, svc, course_repo):
        course_repo.get_by_code.return_value = make_course()
        with pytest.raises(ConflictError):
            await svc.create_course("TRN-001", "Safety Training", str(uuid4()))


class TestAssignTraining:
    @pytest.mark.asyncio
    async def test_assigns_training_to_user(self, svc, course_repo, assignment_repo):
        course = make_course()
        course_repo.get_by_id.return_value = course
        assignment_repo.get_by_course_user.return_value = None
        mock_assignment = make_assignment()
        assignment_repo.create.return_value = mock_assignment

        result = await svc.assign_training(course.id, str(uuid4()), assigned_by=str(uuid4()))
        assert result is mock_assignment

    @pytest.mark.asyncio
    async def test_raises_conflict_if_already_assigned(self, svc, course_repo, assignment_repo):
        course = make_course()
        course_repo.get_by_id.return_value = course
        existing = make_assignment(status="assigned")
        assignment_repo.get_by_course_user.return_value = existing
        with pytest.raises(ConflictError):
            await svc.assign_training(course.id, str(uuid4()), str(uuid4()))


class TestCompleteTraining:
    @pytest.mark.asyncio
    async def test_passes_training_with_good_score(self, svc, course_repo, assignment_repo):
        user_id = str(uuid4())
        course_id = str(uuid4())
        assignment = make_assignment(user_id=user_id, course_id=course_id)
        course = make_course(id=course_id, passing_score=80)
        assignment_repo.get_by_id.return_value = assignment
        course_repo.get_by_id.return_value = course
        assignment_repo.complete.return_value = None
        completed = make_assignment(user_id=user_id, status="completed", passed=True)
        assignment_repo.get_by_id.side_effect = [assignment, completed]

        result = await svc.complete_training(assignment.id, user_id, score=90)
        assignment_repo.complete.assert_called_once()
        call_kwargs = assignment_repo.complete.call_args.kwargs
        assert call_kwargs["passed"] is True

    @pytest.mark.asyncio
    async def test_fails_training_with_low_score(self, svc, course_repo, assignment_repo):
        user_id = str(uuid4())
        course_id = str(uuid4())
        assignment = make_assignment(user_id=user_id, course_id=course_id)
        course = make_course(id=course_id, passing_score=80)
        assignment_repo.get_by_id.return_value = assignment
        course_repo.get_by_id.return_value = course
        assignment_repo.complete.return_value = None
        failed = make_assignment(user_id=user_id, status="completed", passed=False)
        assignment_repo.get_by_id.side_effect = [assignment, failed]

        result = await svc.complete_training(assignment.id, user_id, score=60)
        call_kwargs = assignment_repo.complete.call_args.kwargs
        assert call_kwargs["passed"] is False

    @pytest.mark.asyncio
    async def test_raises_forbidden_for_wrong_user(self, svc, assignment_repo):
        assignment = make_assignment(user_id=str(uuid4()))
        assignment_repo.get_by_id.return_value = assignment
        with pytest.raises(ForbiddenError):
            await svc.complete_training(assignment.id, user_id=str(uuid4()))
