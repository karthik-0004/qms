"""Training Service — Course and assignment API routes."""

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
from ....infra.db.repositories import TrainingAssignmentRepository, TrainingCourseRepository
from ....schemas.requests import AssignTrainingRequest, CompleteTrainingRequest, CreateCourseRequest
from ....schemas.responses import TrainingAssignmentResponse, TrainingCourseResponse

router = APIRouter(prefix="/training", tags=["Training"])
logger = structlog.get_logger(__name__)


def _get_service(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]) -> TrainingDomainService:
    return TrainingDomainService(
        course_repo=TrainingCourseRepository(db),
        assignment_repo=TrainingAssignmentRepository(db),
        tenant_id=current_user.tenant_id or "",
    )


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
    course = await service.create_course(
        course_code=payload.course_code,
        title=payload.title,
        created_by=current_user.sub,
        course_type=payload.course_type,
        description=payload.description,
        department=payload.department,
        document_id=payload.document_id,
        duration_hours=payload.duration_hours,
        passing_score=payload.passing_score,
        requires_certification=payload.requires_certification,
        recurrence_days=payload.recurrence_days,
        is_mandatory=payload.is_mandatory,
    )
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
        course_id=course_id,
        user_id=payload.user_id,
        assigned_by=current_user.sub,
        due_date=payload.due_date,
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
        assignment_id=assignment_id,
        user_id=current_user.sub,
        score=payload.score,
        notes=payload.notes,
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
