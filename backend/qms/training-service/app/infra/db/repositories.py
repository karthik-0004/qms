"""Training Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import TrainingAssignment, TrainingCourse


class TrainingCourseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, course_id: str) -> TrainingCourse | None:
        result = await self._db.execute(select(TrainingCourse).where(TrainingCourse.id == course_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, tenant_id: str, course_code: str) -> TrainingCourse | None:
        result = await self._db.execute(
            select(TrainingCourse).where(
                TrainingCourse.tenant_id == tenant_id,
                TrainingCourse.course_code == course_code,
            )
        )
        return result.scalar_one_or_none()

    async def list_courses(
        self, tenant_id: str, department: str | None = None,
        is_mandatory: bool | None = None, offset: int = 0, limit: int = 20,
    ) -> tuple[list[TrainingCourse], int]:
        query = select(TrainingCourse).where(TrainingCourse.tenant_id == tenant_id, TrainingCourse.is_active.is_(True))
        count_q = select(func.count()).select_from(TrainingCourse).where(TrainingCourse.tenant_id == tenant_id, TrainingCourse.is_active.is_(True))

        if department:
            query = query.where(TrainingCourse.department == department)
            count_q = count_q.where(TrainingCourse.department == department)
        if is_mandatory is not None:
            query = query.where(TrainingCourse.is_mandatory == is_mandatory)
            count_q = count_q.where(TrainingCourse.is_mandatory == is_mandatory)

        query = query.offset(offset).limit(limit).order_by(TrainingCourse.title)
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(self, tenant_id: str, course_code: str, title: str, created_by: str, **kwargs) -> TrainingCourse:
        now = datetime.now(timezone.utc)
        course = TrainingCourse(
            id=str(uuid4()), tenant_id=tenant_id, course_code=course_code, title=title,
            created_by=created_by, is_active=True, created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(course)
        await self._db.flush()
        return course

    async def update(self, course_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(update(TrainingCourse).where(TrainingCourse.id == course_id).values(**fields))


class TrainingAssignmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, assignment_id: str) -> TrainingAssignment | None:
        result = await self._db.execute(select(TrainingAssignment).where(TrainingAssignment.id == assignment_id))
        return result.scalar_one_or_none()

    async def get_by_course_user(self, course_id: str, user_id: str) -> TrainingAssignment | None:
        result = await self._db.execute(
            select(TrainingAssignment).where(
                TrainingAssignment.course_id == course_id,
                TrainingAssignment.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, tenant_id: str, user_id: str, status: str | None = None,
        offset: int = 0, limit: int = 20,
    ) -> tuple[list[TrainingAssignment], int]:
        query = select(TrainingAssignment).where(
            TrainingAssignment.tenant_id == tenant_id,
            TrainingAssignment.user_id == user_id,
        )
        count_q = select(func.count()).select_from(TrainingAssignment).where(
            TrainingAssignment.tenant_id == tenant_id,
            TrainingAssignment.user_id == user_id,
        )
        if status:
            query = query.where(TrainingAssignment.status == status)
            count_q = count_q.where(TrainingAssignment.status == status)
        query = query.offset(offset).limit(limit).order_by(TrainingAssignment.due_date.asc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def get_overdue(self, tenant_id: str) -> list[TrainingAssignment]:
        now = datetime.now(timezone.utc)
        result = await self._db.execute(
            select(TrainingAssignment).where(
                TrainingAssignment.tenant_id == tenant_id,
                TrainingAssignment.status.in_(["assigned", "in_progress"]),
                TrainingAssignment.due_date < now,
            )
        )
        return list(result.scalars().all())

    async def create(self, tenant_id: str, course_id: str, user_id: str, assigned_by: str, **kwargs) -> TrainingAssignment:
        now = datetime.now(timezone.utc)
        assignment = TrainingAssignment(
            id=str(uuid4()), tenant_id=tenant_id, course_id=course_id,
            user_id=user_id, assigned_by=assigned_by, status="assigned",
            created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(assignment)
        await self._db.flush()
        return assignment

    async def complete(self, assignment_id: str, score: int | None, passed: bool, **kwargs) -> None:
        await self._db.execute(
            update(TrainingAssignment)
            .where(TrainingAssignment.id == assignment_id)
            .values(
                status="completed", score=score, passed=passed,
                completed_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                **kwargs,
            )
        )
