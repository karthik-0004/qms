"""Training Service — Course, Job Code, Exam, Trainer, and Dashboard API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_permission
from rainer_auth_lib.permissions import Permission
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.database import get_db
from ....domain.services import TrainingDomainService
from ....infra.db.repositories import (
    ExamAttemptRepository, ExamQuestionRepository, ExamRepository,
    JobCodeAssignmentRepository, JobCodeCourseRepository, JobCodeRepository,
    TrainingAssignmentRepository, TrainingCourseRepository, TrainerRepository,
)
from ....schemas.requests import (
    AssignJobCodeRequest, AssignTrainingRequest, CompleteTrainingRequest,
    CreateCourseRequest, CreateExamQuestionRequest, CreateExamRequest,
    CreateJobCodeRequest, CreateTrainerRequest, LinkCourseToJobCodeRequest,
    SubmitExamAttemptRequest, UpdateJobCodeRequest, UpdateTrainerRequest,
)
from ....schemas.responses import (
    ExamAttemptResponse, ExamQuestionResponse, ExamResponse,
    JobCodeAssignmentResponse, JobCodeCourseResponse, JobCodeResponse,
    TrainingAssignmentResponse, TrainingCourseResponse, TrainerResponse,
    TrainingDashboardStats,
)

router = APIRouter(prefix="/training", tags=["Training"])
logger = structlog.get_logger(__name__)


def _get_service(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]) -> TrainingDomainService:
    return TrainingDomainService(
        course_repo=TrainingCourseRepository(db),
        assignment_repo=TrainingAssignmentRepository(db),
        job_code_repo=JobCodeRepository(db),
        job_code_course_repo=JobCodeCourseRepository(db),
        job_code_assignment_repo=JobCodeAssignmentRepository(db),
        trainer_repo=TrainerRepository(db),
        exam_repo=ExamRepository(db),
        exam_question_repo=ExamQuestionRepository(db),
        exam_attempt_repo=ExamAttemptRepository(db),
        tenant_id=current_user.tenant_id or "",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Dashboard
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/dashboard", response_model=SuccessResponse[TrainingDashboardStats],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="Get training dashboard statistics")
async def training_dashboard(
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[TrainingDashboardStats]:
    stats = await service.get_dashboard_stats()
    return SuccessResponse.of(TrainingDashboardStats(**stats))


# ═══════════════════════════════════════════════════════════════════════════════
# Courses
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/courses", response_model=PaginatedResponse[TrainingCourseResponse],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="List training courses")
async def list_courses(
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    department: str | None = Query(default=None),
    is_mandatory: bool | None = Query(default=None),
) -> PaginatedResponse[TrainingCourseResponse]:
    courses, total = await service.list_courses(
        department=department, is_mandatory=is_mandatory,
        page=pagination.page, page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[TrainingCourseResponse.model_validate(c, from_attributes=True) for c in courses],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.post("/courses", response_model=SuccessResponse[TrainingCourseResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
             summary="Create a training course")
async def create_course(
    payload: CreateCourseRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[TrainingCourseResponse]:
    course = await service.create_course(**payload.model_dump(), created_by=current_user.sub)
    return SuccessResponse.of(TrainingCourseResponse.model_validate(course, from_attributes=True))


@router.get("/courses/{course_id}", response_model=SuccessResponse[TrainingCourseResponse],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="Get course details")
async def get_course(
    course_id: str,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[TrainingCourseResponse]:
    course = await service.get_course(course_id)
    return SuccessResponse.of(TrainingCourseResponse.model_validate(course, from_attributes=True))


@router.post("/courses/{course_id}/assign", response_model=SuccessResponse[TrainingAssignmentResponse],
             status_code=201,
             dependencies=[Depends(require_permission(Permission.TRAINING_ASSIGN))],
             summary="Assign training to a user")
async def assign_training(
    course_id: str,
    payload: AssignTrainingRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[TrainingAssignmentResponse]:
    assignment = await service.assign_training(
        course_id=course_id, user_id=payload.user_id,
        assigned_by=current_user.sub, due_date=payload.due_date,
    )
    return SuccessResponse.of(TrainingAssignmentResponse.model_validate(assignment, from_attributes=True))


@router.get("/assignments", response_model=PaginatedResponse[TrainingAssignmentResponse],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="List assignments for the current user")
async def my_assignments(
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    status: str | None = Query(default=None),
) -> PaginatedResponse[TrainingAssignmentResponse]:
    assignments, total = await service.get_user_assignments(
        user_id=current_user.sub, status=status,
        page=pagination.page, page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[TrainingAssignmentResponse.model_validate(a, from_attributes=True) for a in assignments],
        page=pagination.page, page_size=pagination.page_size, total=total,
    )


@router.post("/assignments/{assignment_id}/complete", response_model=SuccessResponse[TrainingAssignmentResponse],
             dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
             summary="Complete a training assignment")
async def complete_training(
    assignment_id: str,
    payload: CompleteTrainingRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[TrainingAssignmentResponse]:
    assignment = await service.complete_training(
        assignment_id=assignment_id, user_id=current_user.sub,
        score=payload.score, notes=payload.notes,
        e_signature=payload.e_signature,
    )
    return SuccessResponse.of(TrainingAssignmentResponse.model_validate(assignment, from_attributes=True))


@router.get("/assignments/overdue", response_model=SuccessResponse[list[TrainingAssignmentResponse]],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="Get overdue training assignments")
async def overdue_assignments(
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[list[TrainingAssignmentResponse]]:
    assignments = await service.get_overdue_assignments()
    return SuccessResponse.of(
        [TrainingAssignmentResponse.model_validate(a, from_attributes=True) for a in assignments]
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Job Codes
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/job-codes", response_model=SuccessResponse[list[JobCodeResponse]],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="List all job codes")
async def list_job_codes(
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
    department: str | None = Query(default=None),
) -> SuccessResponse[list[JobCodeResponse]]:
    codes = await service.list_job_codes(department=department)
    return SuccessResponse.of([_jc_to_response(c, service) for c in codes])


@router.post("/job-codes", response_model=SuccessResponse[JobCodeResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
             summary="Create a job code")
async def create_job_code(
    payload: CreateJobCodeRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[JobCodeResponse]:
    jc = await service.create_job_code(**payload.model_dump(), created_by=current_user.sub)
    return SuccessResponse.of(_jc_to_response(jc, service))


@router.get("/job-codes/{job_code_id}", response_model=SuccessResponse[JobCodeResponse],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="Get job code details")
async def get_job_code(
    job_code_id: str,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[JobCodeResponse]:
    jc = await service.get_job_code(job_code_id)
    return SuccessResponse.of(_jc_to_response(jc, service))


@router.patch("/job-codes/{job_code_id}", response_model=SuccessResponse[JobCodeResponse],
              dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
              summary="Update a job code")
async def update_job_code(
    job_code_id: str,
    payload: UpdateJobCodeRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[JobCodeResponse]:
    filtered = {k: v for k, v in payload.model_dump().items() if v is not None}
    if filtered:
        await service.update_job_code(job_code_id, **filtered)
    jc = await service.get_job_code(job_code_id)
    return SuccessResponse.of(_jc_to_response(jc, service))


@router.delete("/job-codes/{job_code_id}", response_model=MessageResponse,
               dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
               summary="Delete a job code")
async def delete_job_code(
    job_code_id: str,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.delete_job_code(job_code_id)
    return MessageResponse(message="Job code deleted")


@router.get("/job-codes/{job_code_id}/courses", response_model=SuccessResponse[list[JobCodeCourseResponse]],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="List courses linked to a job code")
async def get_job_code_courses(
    job_code_id: str,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[list[JobCodeCourseResponse]]:
    links = await service.get_job_code_courses(job_code_id)
    return SuccessResponse.of([
        JobCodeCourseResponse(
            id=l.id, job_code_id=l.job_code_id, course_id=l.course_id,
            course_title=l.course.title if l.course else None,
            is_required=l.is_required, sort_order=l.sort_order,
        ) for l in links
    ])


@router.post("/job-codes/{job_code_id}/courses", response_model=SuccessResponse[JobCodeCourseResponse],
             status_code=201,
             dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
             summary="Link a course to a job code")
async def link_course_to_job_code(
    job_code_id: str,
    payload: LinkCourseToJobCodeRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[JobCodeCourseResponse]:
    link = await service.link_course_to_job_code(
        job_code_id, payload.course_id,
        is_required=payload.is_required, sort_order=payload.sort_order,
    )
    return SuccessResponse.of(JobCodeCourseResponse(
        id=link.id, job_code_id=link.job_code_id, course_id=link.course_id,
        course_title=link.course.title if link.course else None,
        is_required=link.is_required, sort_order=link.sort_order,
    ))


@router.delete("/job-codes/{job_code_id}/courses/{course_id}", response_model=MessageResponse,
               dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
               summary="Unlink a course from a job code")
async def unlink_course_from_job_code(
    job_code_id: str,
    course_id: str,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.unlink_course_from_job_code(job_code_id, course_id)
    return MessageResponse(message="Course unlinked from job code")


@router.get("/job-codes/{job_code_id}/assignees", response_model=SuccessResponse[list[JobCodeAssignmentResponse]],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="List users assigned to a job code")
async def get_job_code_assignees(
    job_code_id: str,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[list[JobCodeAssignmentResponse]]:
    assignments = await service.get_job_code_assignees(job_code_id)
    return SuccessResponse.of([
        JobCodeAssignmentResponse(
            id=a.id, tenant_id=a.tenant_id, job_code_id=a.job_code_id,
            user_id=a.user_id, assigned_by=a.assigned_by,
            assigned_at=a.assigned_at, is_primary=a.is_primary,
        ) for a in assignments
    ])


@router.post("/job-codes/{job_code_id}/assignees", response_model=SuccessResponse[JobCodeAssignmentResponse],
             status_code=201,
             dependencies=[Depends(require_permission(Permission.TRAINING_ASSIGN))],
             summary="Assign a user to a job code")
async def assign_user_to_job_code(
    job_code_id: str,
    payload: AssignJobCodeRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[JobCodeAssignmentResponse]:
    a = await service.assign_user_to_job_code(
        job_code_id, payload.user_id,
        assigned_by=current_user.sub, is_primary=payload.is_primary,
    )
    return SuccessResponse.of(JobCodeAssignmentResponse(
        id=a.id, tenant_id=a.tenant_id, job_code_id=a.job_code_id,
        user_id=a.user_id, assigned_by=a.assigned_by,
        assigned_at=a.assigned_at, is_primary=a.is_primary,
    ))


@router.delete("/job-codes/{job_code_id}/assignees/{user_id}", response_model=MessageResponse,
               dependencies=[Depends(require_permission(Permission.TRAINING_ASSIGN))],
               summary="Remove a user from a job code")
async def unassign_user_from_job_code(
    job_code_id: str,
    user_id: str,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.unassign_user_from_job_code(job_code_id, user_id)
    return MessageResponse(message="User removed from job code")


@router.get("/job-codes/{job_code_id}/status", response_model=SuccessResponse[list],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="Get compliance matrix for a job code")
async def job_code_status_matrix(
    job_code_id: str,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[list]:
    jc = await service.get_job_code(job_code_id)
    courses = await service.get_job_code_courses(job_code_id)
    assignees = await service.get_job_code_assignees(job_code_id)

    course_ids = [c.course_id for c in courses]
    user_ids = [a.user_id for a in assignees]

    matrix = []
    for a in assignees:
        user_courses = []
        user_assignments = await service._assignments.get_all_by_user_and_courses(a.user_id, course_ids)
        assignment_map = {asgn.course_id: asgn for asgn in user_assignments}

        for link in courses:
            asgn = assignment_map.get(link.course_id)
            user_courses.append({
                "course_id": link.course_id,
                "course_title": link.course.title if link.course else "",
                "is_required": link.is_required,
                "assignment_id": asgn.id if asgn else None,
                "status": asgn.status if asgn else "not_assigned",
                "score": asgn.score if asgn else None,
                "passed": asgn.passed if asgn else None,
                "completed_at": asgn.completed_at.isoformat() if asgn and asgn.completed_at else None,
                "due_date": asgn.due_date.isoformat() if asgn and asgn.due_date else None,
            })

        matrix.append({
            "user_id": a.user_id,
            "user_name": None,
            "job_code_id": jc.id,
            "job_code_title": jc.title,
            "is_primary": a.is_primary,
            "courses": user_courses,
        })

    return SuccessResponse.of(matrix)


# ═══════════════════════════════════════════════════════════════════════════════
# Trainers
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/trainers", response_model=SuccessResponse[list[TrainerResponse]],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="List trainers")
async def list_trainers(
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
    is_active: bool | None = Query(default=None),
) -> SuccessResponse[list[TrainerResponse]]:
    trainers = await service.list_trainers(is_active=is_active)
    return SuccessResponse.of([
        TrainerResponse.model_validate(t, from_attributes=True) for t in trainers
    ])


@router.post("/trainers", response_model=SuccessResponse[TrainerResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
             summary="Register a trainer")
async def create_trainer(
    payload: CreateTrainerRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[TrainerResponse]:
    trainer = await service.create_trainer(**payload.model_dump(), created_by=current_user.sub)
    return SuccessResponse.of(TrainerResponse.model_validate(trainer, from_attributes=True))


@router.patch("/trainers/{trainer_id}", response_model=SuccessResponse[TrainerResponse],
              dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
              summary="Update a trainer")
async def update_trainer(
    trainer_id: str,
    payload: UpdateTrainerRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[TrainerResponse]:
    filtered = {k: v for k, v in payload.model_dump().items() if v is not None}
    if filtered:
        await service.update_trainer(trainer_id, **filtered)
    trainer = await service._trainers.get_by_id(trainer_id)
    if not trainer:
        from rainer_common.exceptions import NotFoundError
        raise NotFoundError("Trainer", trainer_id)
    return SuccessResponse.of(TrainerResponse.model_validate(trainer, from_attributes=True))


# ═══════════════════════════════════════════════════════════════════════════════
# Exams
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/exams", response_model=SuccessResponse[list[ExamResponse]],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="List exams")
async def list_exams(
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
    course_id: str | None = Query(default=None),
) -> SuccessResponse[list[ExamResponse]]:
    exams = await service.list_exams(course_id=course_id)
    return SuccessResponse.of([
        ExamResponse(
            id=e.id, tenant_id=e.tenant_id, course_id=e.course_id,
            course_title=None, title=e.title, description=e.description,
            passing_score=e.passing_score, duration_minutes=e.duration_minutes,
            is_active=e.is_active, created_by=e.created_by,
            created_at=e.created_at, updated_at=e.updated_at,
            question_count=len(e.questions) if hasattr(e, "questions") else 0,
        ) for e in exams
    ])


@router.post("/exams", response_model=SuccessResponse[ExamResponse], status_code=201,
             dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
             summary="Create an exam")
async def create_exam(
    payload: CreateExamRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[ExamResponse]:
    exam = await service.create_exam(**payload.model_dump(), created_by=current_user.sub)
    return SuccessResponse.of(ExamResponse(
        id=exam.id, tenant_id=exam.tenant_id, course_id=exam.course_id,
        course_title=None, title=exam.title, description=exam.description,
        passing_score=exam.passing_score, duration_minutes=exam.duration_minutes,
        is_active=exam.is_active, created_by=exam.created_by,
        created_at=exam.created_at, updated_at=exam.updated_at,
        question_count=0,
    ))


@router.get("/exams/{exam_id}", response_model=SuccessResponse[ExamResponse],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="Get exam details")
async def get_exam(
    exam_id: str,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[ExamResponse]:
    exam = await service.get_exam(exam_id)
    return SuccessResponse.of(ExamResponse(
        id=exam.id, tenant_id=exam.tenant_id, course_id=exam.course_id,
        course_title=None, title=exam.title, description=exam.description,
        passing_score=exam.passing_score, duration_minutes=exam.duration_minutes,
        is_active=exam.is_active, created_by=exam.created_by,
        created_at=exam.created_at, updated_at=exam.updated_at,
        question_count=len(exam.questions) if hasattr(exam, "questions") else 0,
    ))


@router.post("/exams/{exam_id}/questions", response_model=SuccessResponse[ExamQuestionResponse],
             status_code=201,
             dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
             summary="Add a question to an exam")
async def add_exam_question(
    exam_id: str,
    payload: CreateExamQuestionRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[ExamQuestionResponse]:
    q = await service.add_exam_question(
        exam_id, payload.question_text, payload.options,
        payload.correct_answer, payload.sort_order,
    )
    return SuccessResponse.of(ExamQuestionResponse(
        id=q.id, exam_id=q.exam_id, question_text=q.question_text,
        options=q.options, correct_answer=q.correct_answer, sort_order=q.sort_order,
    ))


@router.get("/exams/{exam_id}/questions", response_model=SuccessResponse[list[ExamQuestionResponse]],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="List exam questions")
async def list_exam_questions(
    exam_id: str,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[list[ExamQuestionResponse]]:
    questions = await service._exam_questions.list_by_exam(exam_id)
    return SuccessResponse.of([
        ExamQuestionResponse(
            id=q.id, exam_id=q.exam_id, question_text=q.question_text,
            options=q.options, correct_answer=q.correct_answer, sort_order=q.sort_order,
        ) for q in questions
    ])


@router.post("/exams/{exam_id}/attempts", response_model=SuccessResponse[ExamAttemptResponse],
             status_code=201,
             dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
             summary="Start an exam attempt")
async def start_exam_attempt(
    exam_id: str,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[ExamAttemptResponse]:
    attempt = await service.start_exam_attempt(exam_id, current_user.sub)
    return SuccessResponse.of(ExamAttemptResponse(
        id=attempt.id, tenant_id=attempt.tenant_id, exam_id=attempt.exam_id,
        user_id=attempt.user_id, score=attempt.score, passed=attempt.passed,
        answers=attempt.answers, started_at=attempt.started_at,
        completed_at=attempt.completed_at, status=attempt.status,
    ))


@router.post("/exam-attempts/{attempt_id}/submit", response_model=SuccessResponse[ExamAttemptResponse],
             dependencies=[Depends(require_permission(Permission.TRAINING_WRITE))],
             summary="Submit an exam attempt")
async def submit_exam_attempt(
    attempt_id: str,
    payload: SubmitExamAttemptRequest,
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[ExamAttemptResponse]:
    attempt = await service.submit_exam_attempt(attempt_id, current_user.sub, payload.answers)
    return SuccessResponse.of(ExamAttemptResponse(
        id=attempt.id, tenant_id=attempt.tenant_id, exam_id=attempt.exam_id,
        user_id=attempt.user_id, score=attempt.score, passed=attempt.passed,
        answers=attempt.answers, started_at=attempt.started_at,
        completed_at=attempt.completed_at, status=attempt.status,
    ))


@router.get("/my-exam-attempts", response_model=SuccessResponse[list[ExamAttemptResponse]],
            dependencies=[Depends(require_permission(Permission.TRAINING_READ))],
            summary="Get current user's exam attempts")
async def my_exam_attempts(
    current_user: CurrentUser,
    service: Annotated[TrainingDomainService, Depends(_get_service)],
) -> SuccessResponse[list[ExamAttemptResponse]]:
    attempts = await service.get_user_exam_attempts(current_user.sub)
    return SuccessResponse.of([
        ExamAttemptResponse(
            id=a.id, tenant_id=a.tenant_id, exam_id=a.exam_id,
            user_id=a.user_id, score=a.score, passed=a.passed,
            answers=a.answers, started_at=a.started_at,
            completed_at=a.completed_at, status=a.status,
        ) for a in attempts
    ])


# ── Helpers ──────────────────────────────────────────────────────────────────


async def _jc_to_response(jc, service) -> JobCodeResponse:
    courses = await service.get_job_code_courses(jc.id)
    assignees = await service.get_job_code_assignees(jc.id)
    return JobCodeResponse(
        id=jc.id, tenant_id=jc.tenant_id, code=jc.code, title=jc.title,
        description=jc.description, department=jc.department,
        requires_certification=jc.requires_certification, is_active=jc.is_active,
        created_by=jc.created_by, created_at=jc.created_at, updated_at=jc.updated_at,
        course_count=len(courses), user_count=len(assignees),
    )
