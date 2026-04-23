"""Workflow Engine — API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.config import Settings, get_settings
from ....core.database import get_db
from ....domain.services import WorkflowDomainService
from ....infra.db.repositories import (
    WorkflowDefinitionRepository,
    WorkflowHistoryRepository,
    WorkflowInstanceRepository,
)
from ....schemas.requests import (
    CreateWorkflowDefinitionRequest,
    StartWorkflowRequest,
    TransitionRequest,
)
from ....schemas.responses import (
    AvailableTransition,
    WorkflowDefinitionResponse,
    WorkflowHistoryEntry,
    WorkflowInstanceResponse,
)

router = APIRouter(prefix="/workflows", tags=["Workflows"])


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> WorkflowDomainService:
    return WorkflowDomainService(
        definition_repo=WorkflowDefinitionRepository(db),
        instance_repo=WorkflowInstanceRepository(db),
        history_repo=WorkflowHistoryRepository(db),
    )


@router.post(
    "/definitions",
    response_model=SuccessResponse[WorkflowDefinitionResponse],
    status_code=201,
    summary="Create a new workflow definition",
)
async def create_definition(
    payload: CreateWorkflowDefinitionRequest,
    current_user: CurrentUser,
    service: Annotated[WorkflowDomainService, Depends(_get_service)],
) -> SuccessResponse[WorkflowDefinitionResponse]:
    defn = await service.create_definition(
        name=payload.name,
        entity_type=payload.entity_type,
        states=payload.states,
        transitions=payload.transitions,
    )
    return SuccessResponse.of(WorkflowDefinitionResponse.model_validate(defn, from_attributes=True))


@router.get(
    "/definitions",
    response_model=SuccessResponse[list[WorkflowDefinitionResponse]],
    summary="List all workflow definitions",
)
async def list_definitions(
    current_user: CurrentUser,
    service: Annotated[WorkflowDomainService, Depends(_get_service)],
) -> SuccessResponse[list[WorkflowDefinitionResponse]]:
    definitions = await service._definitions.list_all()
    return SuccessResponse.of(
        [WorkflowDefinitionResponse.model_validate(d, from_attributes=True) for d in definitions]
    )


@router.post(
    "/instances",
    response_model=SuccessResponse[WorkflowInstanceResponse],
    status_code=201,
    summary="Start a workflow instance for an entity",
)
async def start_workflow(
    payload: StartWorkflowRequest,
    current_user: CurrentUser,
    service: Annotated[WorkflowDomainService, Depends(_get_service)],
) -> SuccessResponse[WorkflowInstanceResponse]:
    instance = await service.start_workflow(
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        created_by=current_user.sub,
        assignee_id=payload.assignee_id,
        due_at=payload.due_at,
        context=payload.context,
    )
    return SuccessResponse.of(WorkflowInstanceResponse.model_validate(instance, from_attributes=True))


@router.get(
    "/instances",
    response_model=PaginatedResponse[WorkflowInstanceResponse],
    summary="List workflow instances",
)
async def list_instances(
    current_user: CurrentUser,
    service: Annotated[WorkflowDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    entity_type: str | None = Query(default=None),
    current_state: str | None = Query(default=None),
) -> PaginatedResponse[WorkflowInstanceResponse]:
    instances, total = await service.list_instances(
        entity_type=entity_type,
        current_state=current_state,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[WorkflowInstanceResponse.model_validate(i, from_attributes=True) for i in instances],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


@router.get(
    "/instances/my-tasks",
    response_model=SuccessResponse[list[WorkflowInstanceResponse]],
    summary="Get pending workflow tasks for current user",
)
async def my_tasks(
    current_user: CurrentUser,
    service: Annotated[WorkflowDomainService, Depends(_get_service)],
    state: str | None = Query(default=None),
) -> SuccessResponse[list[WorkflowInstanceResponse]]:
    tasks = await service.list_my_tasks(assignee_id=current_user.sub, state=state)
    return SuccessResponse.of(
        [WorkflowInstanceResponse.model_validate(t, from_attributes=True) for t in tasks]
    )


@router.get(
    "/instances/{instance_id}",
    response_model=SuccessResponse[WorkflowInstanceResponse],
    summary="Get workflow instance details",
)
async def get_instance(
    instance_id: str,
    current_user: CurrentUser,
    service: Annotated[WorkflowDomainService, Depends(_get_service)],
) -> SuccessResponse[WorkflowInstanceResponse]:
    instance = await service.get_instance(instance_id)
    return SuccessResponse.of(WorkflowInstanceResponse.model_validate(instance, from_attributes=True))


@router.get(
    "/instances/{instance_id}/history",
    response_model=SuccessResponse[list[WorkflowHistoryEntry]],
    summary="Get workflow instance history",
)
async def get_history(
    instance_id: str,
    current_user: CurrentUser,
    service: Annotated[WorkflowDomainService, Depends(_get_service)],
) -> SuccessResponse[list[WorkflowHistoryEntry]]:
    history = await service.get_instance_history(instance_id)
    return SuccessResponse.of(
        [WorkflowHistoryEntry.model_validate(h, from_attributes=True) for h in history]
    )


@router.get(
    "/instances/{instance_id}/transitions",
    response_model=SuccessResponse[list[AvailableTransition]],
    summary="Get available transitions from current state",
)
async def available_transitions(
    instance_id: str,
    current_user: CurrentUser,
    service: Annotated[WorkflowDomainService, Depends(_get_service)],
) -> SuccessResponse[list[AvailableTransition]]:
    transitions = await service.get_available_transitions(instance_id)
    return SuccessResponse.of([AvailableTransition(**t) for t in transitions])


@router.post(
    "/instances/{instance_id}/transition",
    response_model=SuccessResponse[WorkflowInstanceResponse],
    summary="Execute a state transition on workflow instance",
)
async def execute_transition(
    instance_id: str,
    payload: TransitionRequest,
    current_user: CurrentUser,
    service: Annotated[WorkflowDomainService, Depends(_get_service)],
) -> SuccessResponse[WorkflowInstanceResponse]:
    instance = await service.transition(
        instance_id=instance_id,
        action=payload.action,
        actor_id=current_user.sub,
        comment=payload.comment,
        signature=payload.signature,
        new_assignee_id=payload.new_assignee_id,
        metadata=payload.metadata,
    )
    return SuccessResponse.of(WorkflowInstanceResponse.model_validate(instance, from_attributes=True))
