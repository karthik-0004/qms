"""Training Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .models import (
    Exam, ExamAttempt, ExamQuestion, JobCode, JobCodeAssignment,
    JobCodeCourse, TrainingAssignment, TrainingCourse, Trainer,
)


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
        result = await self._db.execute(
            select(TrainingAssignment)
            .options(joinedload(TrainingAssignment.course))
            .where(TrainingAssignment.id == assignment_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_by_course_user(self, course_id: str, user_id: str) -> TrainingAssignment | None:
        result = await self._db.execute(
            select(TrainingAssignment)
            .options(joinedload(TrainingAssignment.course))
            .where(
                TrainingAssignment.course_id == course_id,
                TrainingAssignment.user_id == user_id,
            )
        )
        return result.unique().scalar_one_or_none()

    async def list_by_user(
        self, tenant_id: str, user_id: str, status: str | None = None,
        offset: int = 0, limit: int = 20,
    ) -> tuple[list[TrainingAssignment], int]:
        query = (
            select(TrainingAssignment)
            .options(joinedload(TrainingAssignment.course))
            .where(
                TrainingAssignment.tenant_id == tenant_id,
                TrainingAssignment.user_id == user_id,
            )
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
        return list(result.unique().scalars().all()), count_result.scalar_one()

    async def get_overdue(self, tenant_id: str) -> list[TrainingAssignment]:
        now = datetime.now(timezone.utc)
        result = await self._db.execute(
            select(TrainingAssignment)
            .options(joinedload(TrainingAssignment.course))
            .where(
                TrainingAssignment.tenant_id == tenant_id,
                TrainingAssignment.status.in_(["assigned", "in_progress"]),
                TrainingAssignment.due_date < now,
            )
            .order_by(TrainingAssignment.due_date.asc())
        )
        return list(result.unique().scalars().all())

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

    async def get_all_by_user_and_courses(self, user_id: str, course_ids: list[str]) -> list[TrainingAssignment]:
        result = await self._db.execute(
            select(TrainingAssignment)
            .options(joinedload(TrainingAssignment.course))
            .where(
                TrainingAssignment.user_id == user_id,
                TrainingAssignment.course_id.in_(course_ids),
            )
        )
        return list(result.unique().scalars().all())


# ── Phase 4: Job Code Repositories ───────────────────────────────────────────


class JobCodeRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, job_code_id: str) -> JobCode | None:
        result = await self._db.execute(select(JobCode).where(JobCode.id == job_code_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, tenant_id: str, code: str) -> JobCode | None:
        result = await self._db.execute(
            select(JobCode).where(JobCode.tenant_id == tenant_id, JobCode.code == code)
        )
        return result.scalar_one_or_none()

    async def list_all(self, tenant_id: str, department: str | None = None) -> list[JobCode]:
        query = select(JobCode).where(JobCode.tenant_id == tenant_id)
        if department:
            query = query.where(JobCode.department == department)
        query = query.order_by(JobCode.title)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def create(self, tenant_id: str, code: str, title: str, created_by: str, **kwargs) -> JobCode:
        now = datetime.now(timezone.utc)
        obj = JobCode(
            id=str(uuid4()), tenant_id=tenant_id, code=code, title=title,
            created_by=created_by, is_active=True, created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(obj)
        await self._db.flush()
        return obj

    async def update(self, job_code_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(update(JobCode).where(JobCode.id == job_code_id).values(**fields))

    async def delete(self, job_code_id: str) -> None:
        await self._db.execute(delete(JobCode).where(JobCode.id == job_code_id))


class JobCodeCourseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_job_code(self, job_code_id: str) -> list[JobCodeCourse]:
        result = await self._db.execute(
            select(JobCodeCourse)
            .options(joinedload(JobCodeCourse.course))
            .where(JobCodeCourse.job_code_id == job_code_id)
            .order_by(JobCodeCourse.sort_order)
        )
        return list(result.unique().scalars().all())

    async def get_by_job_code_and_course(self, job_code_id: str, course_id: str) -> JobCodeCourse | None:
        result = await self._db.execute(
            select(JobCodeCourse).where(
                JobCodeCourse.job_code_id == job_code_id,
                JobCodeCourse.course_id == course_id,
            )
        )
        return result.scalar_one_or_none()

    async def link(self, job_code_id: str, course_id: str, is_required: bool = True, sort_order: int = 0) -> JobCodeCourse:
        existing = await self.get_by_job_code_and_course(job_code_id, course_id)
        if existing:
            return existing
        obj = JobCodeCourse(
            id=str(uuid4()), job_code_id=job_code_id, course_id=course_id,
            is_required=is_required, sort_order=sort_order,
        )
        self._db.add(obj)
        await self._db.flush()
        return obj

    async def unlink(self, job_code_id: str, course_id: str) -> None:
        await self._db.execute(
            delete(JobCodeCourse).where(
                JobCodeCourse.job_code_id == job_code_id,
                JobCodeCourse.course_id == course_id,
            )
        )


class JobCodeAssignmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_user_and_job_code(self, user_id: str, job_code_id: str) -> JobCodeAssignment | None:
        result = await self._db.execute(
            select(JobCodeAssignment).where(
                JobCodeAssignment.user_id == user_id,
                JobCodeAssignment.job_code_id == job_code_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_job_code(self, job_code_id: str) -> list[JobCodeAssignment]:
        result = await self._db.execute(
            select(JobCodeAssignment)
            .where(JobCodeAssignment.job_code_id == job_code_id)
        )
        return list(result.scalars().all())

    async def list_by_user(self, tenant_id: str, user_id: str) -> list[JobCodeAssignment]:
        result = await self._db.execute(
            select(JobCodeAssignment).where(
                JobCodeAssignment.tenant_id == tenant_id,
                JobCodeAssignment.user_id == user_id,
            )
        )
        return list(result.scalars().all())

    async def list_by_tenant(self, tenant_id: str) -> list[JobCodeAssignment]:
        result = await self._db.execute(
            select(JobCodeAssignment).where(JobCodeAssignment.tenant_id == tenant_id)
        )
        return list(result.scalars().all())

    async def create(self, tenant_id: str, job_code_id: str, user_id: str, assigned_by: str | None = None, is_primary: bool = False) -> JobCodeAssignment:
        existing = await self.get_by_user_and_job_code(user_id, job_code_id)
        if existing:
            return existing
        obj = JobCodeAssignment(
            id=str(uuid4()), tenant_id=tenant_id, job_code_id=job_code_id,
            user_id=user_id, assigned_by=assigned_by,
            assigned_at=datetime.now(timezone.utc), is_primary=is_primary,
        )
        self._db.add(obj)
        await self._db.flush()
        return obj

    async def delete(self, user_id: str, job_code_id: str) -> None:
        await self._db.execute(
            delete(JobCodeAssignment).where(
                JobCodeAssignment.user_id == user_id,
                JobCodeAssignment.job_code_id == job_code_id,
            )
        )


# ── Phase 4: Trainer Repository ──────────────────────────────────────────────


class TrainerRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, trainer_id: str) -> Trainer | None:
        result = await self._db.execute(select(Trainer).where(Trainer.id == trainer_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, tenant_id: str, user_id: str) -> Trainer | None:
        result = await self._db.execute(
            select(Trainer).where(Trainer.tenant_id == tenant_id, Trainer.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, tenant_id: str, is_active: bool | None = None) -> list[Trainer]:
        query = select(Trainer).where(Trainer.tenant_id == tenant_id)
        if is_active is not None:
            query = query.where(Trainer.is_active == is_active)
        query = query.order_by(Trainer.created_at.desc())
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def create(self, tenant_id: str, user_id: str, created_by: str, **kwargs) -> Trainer:
        now = datetime.now(timezone.utc)
        obj = Trainer(
            id=str(uuid4()), tenant_id=tenant_id, user_id=user_id,
            created_by=created_by, is_active=True, created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(obj)
        await self._db.flush()
        return obj

    async def update(self, trainer_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(update(Trainer).where(Trainer.id == trainer_id).values(**fields))


# ── Phase 4: Exam Repositories ───────────────────────────────────────────────


class ExamRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, exam_id: str) -> Exam | None:
        result = await self._db.execute(
            select(Exam).options(joinedload(Exam.questions)).where(Exam.id == exam_id)
        )
        return result.unique().scalar_one_or_none()

    async def list_by_course(self, course_id: str) -> list[Exam]:
        result = await self._db.execute(
            select(Exam).where(Exam.course_id == course_id, Exam.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def list_by_tenant(self, tenant_id: str) -> list[Exam]:
        result = await self._db.execute(
            select(Exam).where(Exam.tenant_id == tenant_id).order_by(Exam.title)
        )
        return list(result.scalars().all())

    async def create(self, tenant_id: str, course_id: str, title: str, created_by: str, **kwargs) -> Exam:
        now = datetime.now(timezone.utc)
        obj = Exam(
            id=str(uuid4()), tenant_id=tenant_id, course_id=course_id, title=title,
            created_by=created_by, is_active=True, created_at=now, updated_at=now, **kwargs,
        )
        self._db.add(obj)
        await self._db.flush()
        return obj

    async def update(self, exam_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(update(Exam).where(Exam.id == exam_id).values(**fields))


class ExamQuestionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_by_exam(self, exam_id: str) -> list[ExamQuestion]:
        result = await self._db.execute(
            select(ExamQuestion).where(ExamQuestion.exam_id == exam_id).order_by(ExamQuestion.sort_order)
        )
        return list(result.scalars().all())

    async def create(self, exam_id: str, question_text: str, options: list, correct_answer: str, sort_order: int = 0) -> ExamQuestion:
        obj = ExamQuestion(
            id=str(uuid4()), exam_id=exam_id, question_text=question_text,
            options=options, correct_answer=correct_answer, sort_order=sort_order,
        )
        self._db.add(obj)
        await self._db.flush()
        return obj

    async def delete(self, question_id: str) -> None:
        await self._db.execute(delete(ExamQuestion).where(ExamQuestion.id == question_id))


class ExamAttemptRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, attempt_id: str) -> ExamAttempt | None:
        result = await self._db.execute(select(ExamAttempt).where(ExamAttempt.id == attempt_id))
        return result.scalar_one_or_none()

    async def get_active(self, exam_id: str, user_id: str) -> ExamAttempt | None:
        result = await self._db.execute(
            select(ExamAttempt).where(
                ExamAttempt.exam_id == exam_id,
                ExamAttempt.user_id == user_id,
                ExamAttempt.status == "in_progress",
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, tenant_id: str, user_id: str) -> list[ExamAttempt]:
        result = await self._db.execute(
            select(ExamAttempt).where(
                ExamAttempt.tenant_id == tenant_id,
                ExamAttempt.user_id == user_id,
            ).order_by(ExamAttempt.started_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, tenant_id: str, exam_id: str, user_id: str) -> ExamAttempt:
        obj = ExamAttempt(
            id=str(uuid4()), tenant_id=tenant_id, exam_id=exam_id,
            user_id=user_id, started_at=datetime.now(timezone.utc),
            status="in_progress",
        )
        self._db.add(obj)
        await self._db.flush()
        return obj

    async def complete(self, attempt_id: str, score: int, passed: bool, answers: dict) -> None:
        await self._db.execute(
            update(ExamAttempt)
            .where(ExamAttempt.id == attempt_id)
            .values(
                score=score, passed=passed, answers=answers,
                completed_at=datetime.now(timezone.utc),
                status="completed",
            )
        )
