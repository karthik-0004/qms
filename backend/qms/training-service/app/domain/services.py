"""Training Service — Core training management domain service."""

from datetime import datetime, timedelta, timezone

import structlog

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError

from ..infra.db.models import TrainingAssignment, TrainingCourse
from ..infra.db.repositories import TrainingAssignmentRepository, TrainingCourseRepository

logger = structlog.get_logger(__name__)


class TrainingDomainService:
    """Training course management and assignment tracking."""

    def __init__(
        self,
        course_repo: TrainingCourseRepository,
        assignment_repo: TrainingAssignmentRepository,
        tenant_id: str,
    ) -> None:
        self._courses = course_repo
        self._assignments = assignment_repo
        self._tenant_id = tenant_id

    async def create_course(
        self,
        course_code: str,
        title: str,
        created_by: str,
        course_type: str = "online",
        description: str | None = None,
        department: str | None = None,
        document_id: str | None = None,
        duration_hours: float | None = None,
        passing_score: int = 80,
        requires_certification: bool = False,
        recurrence_days: int | None = None,
        is_mandatory: bool = False,
    ) -> TrainingCourse:
        existing = await self._courses.get_by_code(self._tenant_id, course_code)
        if existing:
            raise ConflictError(f"Course '{course_code}' already exists")

        course = await self._courses.create(
            tenant_id=self._tenant_id,
            course_code=course_code,
            title=title,
            created_by=created_by,
            course_type=course_type,
            description=description,
            department=department,
            document_id=document_id,
            duration_hours=duration_hours,
            passing_score=passing_score,
            requires_certification=requires_certification,
            recurrence_days=recurrence_days,
            is_mandatory=is_mandatory,
        )
        logger.info("training_course_created", course_id=course.id, code=course_code)
        return course

    async def get_course(self, course_id: str) -> TrainingCourse:
        course = await self._courses.get_by_id(course_id)
        if not course:
            raise NotFoundError("TrainingCourse", course_id)
        if course.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this training course")
        return course

    async def list_courses(
        self,
        department: str | None = None,
        is_mandatory: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[TrainingCourse], int]:
        return await self._courses.list_courses(
            tenant_id=self._tenant_id,
            department=department,
            is_mandatory=is_mandatory,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def assign_training(
        self,
        course_id: str,
        user_id: str,
        assigned_by: str,
        due_date: datetime | None = None,
    ) -> TrainingAssignment:
        course = await self.get_course(course_id)
        existing = await self._assignments.get_by_course_user(course_id, user_id)
        if existing and existing.status in ("assigned", "in_progress"):
            raise ConflictError("User already has this training assigned")

        # Calculate due date if not provided
        if due_date is None and course.recurrence_days:
            due_date = datetime.now(timezone.utc) + timedelta(days=course.recurrence_days)

        assignment = await self._assignments.create(
            tenant_id=self._tenant_id,
            course_id=course_id,
            user_id=user_id,
            assigned_by=assigned_by,
            due_date=due_date,
        )
        logger.info("training_assigned", course_id=course_id, user_id=user_id)
        return assignment

    async def complete_training(
        self,
        assignment_id: str,
        user_id: str,
        score: int | None = None,
        notes: str | None = None,
    ) -> TrainingAssignment:
        assignment = await self._assignments.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundError("TrainingAssignment", assignment_id)
        if assignment.user_id != user_id:
            raise ForbiddenError("Cannot complete another user's training")

        course = await self.get_course(assignment.course_id)
        passed = score is None or score >= course.passing_score

        cert_expiry = None
        if passed and course.requires_certification and course.recurrence_days:
            cert_expiry = datetime.now(timezone.utc) + timedelta(days=course.recurrence_days)

        await self._assignments.complete(
            assignment_id,
            score=score,
            passed=passed,
            cert_expiry_date=cert_expiry,
            notes=notes,
        )

        logger.info("training_completed", assignment_id=assignment_id, user_id=user_id, passed=passed)
        return await self._assignments.get_by_id(assignment_id)

    async def get_user_assignments(
        self,
        user_id: str,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[TrainingAssignment], int]:
        return await self._assignments.list_by_user(
            tenant_id=self._tenant_id,
            user_id=user_id,
            status=status,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def get_overdue_assignments(self) -> list[TrainingAssignment]:
        return await self._assignments.get_overdue(self._tenant_id)
