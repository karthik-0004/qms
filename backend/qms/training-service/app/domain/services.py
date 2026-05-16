"""Training Service — Core training management domain service."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import structlog

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError

from ..infra.db.models import (
    Exam, ExamAttempt, JobCode, JobCodeAssignment, TrainingAssignment,
    TrainingCourse, Trainer,
)
from ..infra.db.repositories import (
    ExamAttemptRepository, ExamQuestionRepository, ExamRepository,
    JobCodeAssignmentRepository, JobCodeCourseRepository, JobCodeRepository,
    TrainingAssignmentRepository, TrainingCourseRepository, TrainerRepository,
)
from ..events import (
    publish_course_completed, publish_training_assigned,
    publish_training_completed, publish_training_exam_failed,
    publish_training_exam_passed,
)

logger = structlog.get_logger(__name__)


class TrainingDomainService:
    """Training course management, job codes, exams, and assignment tracking."""

    def __init__(
        self,
        course_repo: TrainingCourseRepository,
        assignment_repo: TrainingAssignmentRepository,
        tenant_id: str,
        job_code_repo: JobCodeRepository | None = None,
        job_code_course_repo: JobCodeCourseRepository | None = None,
        job_code_assignment_repo: JobCodeAssignmentRepository | None = None,
        trainer_repo: TrainerRepository | None = None,
        exam_repo: ExamRepository | None = None,
        exam_question_repo: ExamQuestionRepository | None = None,
        exam_attempt_repo: ExamAttemptRepository | None = None,
    ) -> None:
        self._courses = course_repo
        self._assignments = assignment_repo
        self._job_codes = job_code_repo
        self._job_code_courses = job_code_course_repo
        self._job_code_assignments = job_code_assignment_repo
        self._trainers = trainer_repo
        self._exams = exam_repo
        self._exam_questions = exam_question_repo
        self._exam_attempts = exam_attempt_repo
        self._tenant_id = tenant_id

    # ── Courses ─────────────────────────────────────────────────────────────

    async def create_course(self, course_code: str, title: str, created_by: str, **kwargs) -> TrainingCourse:
        existing = await self._courses.get_by_code(self._tenant_id, course_code)
        if existing:
            raise ConflictError(f"Course '{course_code}' already exists")

        course = await self._courses.create(
            tenant_id=self._tenant_id, course_code=course_code, title=title,
            created_by=created_by, **kwargs,
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

    async def list_courses(self, department: str | None = None, is_mandatory: bool | None = None, page: int = 1, page_size: int = 20) -> tuple[list[TrainingCourse], int]:
        return await self._courses.list_courses(
            tenant_id=self._tenant_id, department=department,
            is_mandatory=is_mandatory, offset=(page - 1) * page_size, limit=page_size,
        )

    async def assign_training(self, course_id: str, user_id: str, assigned_by: str, due_date: datetime | None = None) -> TrainingAssignment:
        course = await self.get_course(course_id)
        existing = await self._assignments.get_by_course_user(course_id, user_id)
        if existing and existing.status in ("assigned", "in_progress"):
            raise ConflictError("User already has this training assigned")

        if due_date is None and course.recurrence_days:
            due_date = datetime.now(timezone.utc) + timedelta(days=course.recurrence_days)

        assignment = await self._assignments.create(
            tenant_id=self._tenant_id, course_id=course_id, user_id=user_id,
            assigned_by=assigned_by, due_date=due_date,
        )
        logger.info("training_assigned", course_id=course_id, user_id=user_id, assignment_id=assignment.id)

        await publish_training_assigned(
            tenant_id=self._tenant_id, course_id=course_id, user_id=user_id,
            assigned_by=assigned_by,
            due_date=due_date.isoformat() if due_date else None,
        )
        return assignment

    async def complete_training(self, assignment_id: str, user_id: str, score: int | None = None, notes: str | None = None, e_signature: str | None = None) -> TrainingAssignment:
        assignment = await self._assignments.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundError("TrainingAssignment", assignment_id)
        if assignment.user_id != user_id:
            raise ForbiddenError("Cannot complete another user's training")

        course = await self.get_course(assignment.course_id)
        if course.requires_certification and not (e_signature and e_signature.strip()):
            raise ValidationError("E-signature is required to complete certified training")

        passed = score is None or score >= course.passing_score

        cert_expiry = None
        if passed and course.requires_certification and course.recurrence_days:
            cert_expiry = datetime.now(timezone.utc) + timedelta(days=course.recurrence_days)

        combined_notes = notes
        if e_signature and e_signature.strip():
            tag = f"[e-signature:{e_signature.strip()}]"
            combined_notes = f"{notes or ''}\n{tag}".strip()

        await self._assignments.complete(assignment_id, score=score, passed=passed, cert_expiry_date=cert_expiry, notes=combined_notes)

        logger.info("training_completed", assignment_id=assignment_id, user_id=user_id, passed=passed)

        await publish_training_completed(
            tenant_id=self._tenant_id, assignment_id=assignment_id,
            course_id=assignment.course_id, user_id=user_id,
            score=score, passed=passed,
        )
        if passed:
            await publish_course_completed(
                tenant_id=self._tenant_id, assignment_id=assignment_id,
                course_id=assignment.course_id, user_id=user_id, score=score,
            )
        return await self._assignments.get_by_id(assignment_id)

    async def get_user_assignments(self, user_id: str, status: str | None = None, page: int = 1, page_size: int = 20) -> tuple[list[TrainingAssignment], int]:
        return await self._assignments.list_by_user(tenant_id=self._tenant_id, user_id=user_id, status=status, offset=(page - 1) * page_size, limit=page_size)

    async def get_overdue_assignments(self) -> list[TrainingAssignment]:
        return await self._assignments.get_overdue(self._tenant_id)

    # ── Job Codes ───────────────────────────────────────────────────────────

    async def create_job_code(self, code: str, title: str, created_by: str, **kwargs) -> JobCode:
        existing = await self._job_codes.get_by_code(self._tenant_id, code)
        if existing:
            raise ConflictError(f"Job code '{code}' already exists")
        obj = await self._job_codes.create(tenant_id=self._tenant_id, code=code, title=title, created_by=created_by, **kwargs)
        logger.info("job_code_created", code=code, job_code_id=obj.id)
        return obj

    async def get_job_code(self, job_code_id: str) -> JobCode:
        obj = await self._job_codes.get_by_id(job_code_id)
        if not obj:
            raise NotFoundError("JobCode", job_code_id)
        if obj.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied")
        return obj

    async def list_job_codes(self, department: str | None = None) -> list[JobCode]:
        return await self._job_codes.list_all(self._tenant_id, department=department)

    async def update_job_code(self, job_code_id: str, **fields) -> None:
        await self._job_codes.update(job_code_id, **fields)

    async def delete_job_code(self, job_code_id: str) -> None:
        await self._job_codes.delete(job_code_id)

    async def link_course_to_job_code(self, job_code_id: str, course_id: str, is_required: bool = True, sort_order: int = 0) -> None:
        await self.get_job_code(job_code_id)
        await self.get_course(course_id)
        await self._job_code_courses.link(job_code_id, course_id, is_required=is_required, sort_order=sort_order)

    async def unlink_course_from_job_code(self, job_code_id: str, course_id: str) -> None:
        await self._job_code_courses.unlink(job_code_id, course_id)

    async def get_job_code_courses(self, job_code_id: str) -> list:
        links = await self._job_code_courses.get_by_job_code(job_code_id)
        return links

    async def assign_user_to_job_code(self, job_code_id: str, user_id: str, assigned_by: str | None = None, is_primary: bool = False) -> JobCodeAssignment:
        await self.get_job_code(job_code_id)
        return await self._job_code_assignments.create(self._tenant_id, job_code_id, user_id, assigned_by, is_primary)

    async def unassign_user_from_job_code(self, job_code_id: str, user_id: str) -> None:
        await self._job_code_assignments.delete(user_id, job_code_id)

    async def get_job_code_assignees(self, job_code_id: str) -> list[JobCodeAssignment]:
        return await self._job_code_assignments.list_by_job_code(job_code_id)

    # ── Trainers ────────────────────────────────────────────────────────────

    async def create_trainer(self, user_id: str, created_by: str, **kwargs) -> Trainer:
        existing = await self._trainers.get_by_user(self._tenant_id, user_id)
        if existing:
            raise ConflictError("User is already a trainer")
        obj = await self._trainers.create(tenant_id=self._tenant_id, user_id=user_id, created_by=created_by, **kwargs)
        logger.info("trainer_created", trainer_id=obj.id, user_id=user_id)
        return obj

    async def list_trainers(self, is_active: bool | None = None) -> list[Trainer]:
        return await self._trainers.list_all(self._tenant_id, is_active=is_active)

    async def update_trainer(self, trainer_id: str, **fields) -> None:
        await self._trainers.update(trainer_id, **fields)

    # ── Exams ───────────────────────────────────────────────────────────────

    async def create_exam(self, course_id: str, title: str, created_by: str, **kwargs) -> Exam:
        await self.get_course(course_id)
        exam = await self._exams.create(tenant_id=self._tenant_id, course_id=course_id, title=title, created_by=created_by, **kwargs)
        logger.info("exam_created", exam_id=exam.id, course_id=course_id)
        return exam

    async def get_exam(self, exam_id: str) -> Exam:
        exam = await self._exams.get_by_id(exam_id)
        if not exam:
            raise NotFoundError("Exam", exam_id)
        return exam

    async def list_exams(self, course_id: str | None = None) -> list[Exam]:
        if course_id:
            return await self._exams.list_by_course(course_id)
        return await self._exams.list_by_tenant(self._tenant_id)

    async def add_exam_question(self, exam_id: str, question_text: str, options: list, correct_answer: str, sort_order: int = 0):
        await self.get_exam(exam_id)
        return await self._exam_questions.create(exam_id, question_text, options, correct_answer, sort_order)

    async def start_exam_attempt(self, exam_id: str, user_id: str) -> ExamAttempt:
        exam = await self.get_exam(exam_id)
        active = await self._exam_attempts.get_active(exam_id, user_id)
        if active:
            raise ConflictError("You already have an in-progress attempt for this exam")
        return await self._exam_attempts.create(self._tenant_id, exam_id, user_id)

    async def submit_exam_attempt(self, attempt_id: str, user_id: str, answers: dict) -> ExamAttempt:
        attempt = await self._exam_attempts.get_by_id(attempt_id)
        if not attempt:
            raise NotFoundError("ExamAttempt", attempt_id)
        if attempt.user_id != user_id:
            raise ForbiddenError("Cannot submit another user's attempt")
        if attempt.status != "in_progress":
            raise ValidationError("Exam attempt is already completed")

        exam = await self.get_exam(attempt.exam_id)
        score = 0
        for q in exam.questions:
            if answers.get(q.id) == q.correct_answer:
                score += 1
        total = len(exam.questions) or 1
        pct = int((score / total) * 100)
        passed = pct >= exam.passing_score

        await self._exam_attempts.complete(attempt_id, pct, passed, answers)
        logger.info("exam_attempt_completed", attempt_id=attempt_id, score=pct, passed=passed)

        if passed:
            await publish_training_exam_passed(
                tenant_id=self._tenant_id, exam_id=attempt.exam_id,
                course_id=exam.course_id, user_id=user_id, score=pct,
            )
        else:
            await publish_training_exam_failed(
                tenant_id=self._tenant_id, exam_id=attempt.exam_id,
                course_id=exam.course_id, user_id=user_id, score=pct,
            )

        result = await self._exam_attempts.get_by_id(attempt_id)

        if passed and exam.course_id:
            assignment = await self._assignments.get_by_course_user(exam.course_id, user_id)
            if assignment and assignment.status in ("assigned", "in_progress"):
                await self.complete_training(assignment.id, user_id, score=pct)

        return result

    async def get_user_exam_attempts(self, user_id: str) -> list[ExamAttempt]:
        return await self._exam_attempts.list_by_user(self._tenant_id, user_id)

    # ── Dashboard & Compliance ──────────────────────────────────────────────

    async def get_dashboard_stats(self) -> dict:
        courses = await self._courses.list_courses(self._tenant_id, limit=9999)
        total_courses = courses[1] if isinstance(courses, tuple) else len(courses)

        all_assignments_result = await self._assignments.list_by_user(self._tenant_id, user_id="", limit=9999)
        assignments_list, total = all_assignments_result if isinstance(all_assignments_result, tuple) else (all_assignments_result, 0)

        completed = sum(1 for a in assignments_list if a.status == "completed")
        overdue = sum(1 for a in assignments_list if a.status in ("assigned", "in_progress") and a.due_date and a.due_date < datetime.now(timezone.utc))
        in_progress = sum(1 for a in assignments_list if a.status == "in_progress")
        pending = sum(1 for a in assignments_list if a.status == "assigned")

        job_codes = await self._job_codes.list_all(self._tenant_id)
        trainers = await self._trainers.list_all(self._tenant_id)

        unique_users_with_overdue = set()
        for a in assignments_list:
            if a.status in ("assigned", "in_progress") and a.due_date and a.due_date < datetime.now(timezone.utc):
                unique_users_with_overdue.add(a.user_id)

        upcoming_recerts = sum(1 for a in assignments_list if a.cert_expiry_date and a.cert_expiry_date <= datetime.now(timezone.utc) + timedelta(days=30) and a.cert_expiry_date > datetime.now(timezone.utc))

        overall_pct = (completed / total * 100) if total > 0 else 100.0

        return {
            "total_courses": total_courses,
            "total_assignments": total,
            "completed_assignments": completed,
            "overdue_assignments": overdue,
            "in_progress_assignments": in_progress,
            "pending_assignments": pending,
            "total_job_codes": len(job_codes),
            "users_with_overdue": len(unique_users_with_overdue),
            "overall_compliance_pct": overall_pct,
            "upcoming_recertifications": upcoming_recerts,
            "total_trainers": len(trainers),
        }
