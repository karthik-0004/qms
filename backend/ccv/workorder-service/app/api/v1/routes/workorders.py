"""Work Order Service — Work order management API routes."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.service import WorkOrderDomainService
from app.schemas.requests import (
    AddNoteRequest,
    AddTaskRequest,
    AssignTechnicianRequest,
    CompleteTaskRequest,
    CreateWorkOrderRequest,
    TransitionStatusRequest,
)
from app.schemas.responses import WorkOrderNoteResponse, WorkOrderResponse, WorkOrderTaskResponse

router = APIRouter(prefix="/workorders", tags=["Work Orders"])
logger = structlog.get_logger(__name__)

TenantId = Annotated[UUID, Header(alias="x-tenant-id")]
UserId = Annotated[UUID, Header(alias="x-user-id")]


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> WorkOrderDomainService:
    return WorkOrderDomainService(db)


@router.get("", response_model=list[WorkOrderResponse], summary="List work orders")
async def list_workorders(
    tenant_id: TenantId,
    service: Annotated[WorkOrderDomainService, Depends(_get_service)],
    status: str | None = Query(default=None),
    customer_id: UUID | None = Query(default=None),
    technician_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[WorkOrderResponse]:
    workorders = await service.list_work_orders(
        tenant_id=tenant_id, status=status, customer_id=customer_id,
        technician_id=technician_id, skip=skip, limit=limit,
    )
    return [WorkOrderResponse.model_validate(w, from_attributes=True) for w in workorders]


@router.post("", response_model=WorkOrderResponse, status_code=201, summary="Create work order")
async def create_workorder(
    payload: CreateWorkOrderRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[WorkOrderDomainService, Depends(_get_service)],
) -> WorkOrderResponse:
    fields = payload.model_dump(exclude={"customer_id", "title", "work_type"})
    wo = await service.create_work_order(
        tenant_id=tenant_id, customer_id=payload.customer_id, created_by=user_id,
        title=payload.title, work_type=payload.work_type, **fields,
    )
    return WorkOrderResponse.model_validate(wo, from_attributes=True)


@router.get("/{wo_id}", response_model=WorkOrderResponse, summary="Get work order")
async def get_workorder(
    wo_id: UUID,
    tenant_id: TenantId,
    service: Annotated[WorkOrderDomainService, Depends(_get_service)],
) -> WorkOrderResponse:
    wo = await service.get_work_order(wo_id, tenant_id)
    return WorkOrderResponse.model_validate(wo, from_attributes=True)


@router.post("/{wo_id}/status", response_model=WorkOrderResponse, summary="Transition work order status")
async def transition_status(
    wo_id: UUID,
    payload: TransitionStatusRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[WorkOrderDomainService, Depends(_get_service)],
) -> WorkOrderResponse:
    wo = await service.transition_status(wo_id, tenant_id, payload.new_status, user_id, comment=payload.comment)
    return WorkOrderResponse.model_validate(wo, from_attributes=True)


@router.post("/{wo_id}/assign", response_model=WorkOrderResponse, summary="Assign technician")
async def assign_technician(
    wo_id: UUID,
    payload: AssignTechnicianRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[WorkOrderDomainService, Depends(_get_service)],
) -> WorkOrderResponse:
    wo = await service.assign_technician(wo_id, tenant_id, payload.technician_id, user_id)
    return WorkOrderResponse.model_validate(wo, from_attributes=True)


# ─── Tasks ────────────────────────────────────────────────────────────────

@router.get("/{wo_id}/tasks", response_model=list[WorkOrderTaskResponse], summary="List tasks")
async def list_tasks(
    wo_id: UUID,
    tenant_id: TenantId,
    service: Annotated[WorkOrderDomainService, Depends(_get_service)],
) -> list[WorkOrderTaskResponse]:
    tasks = await service.list_tasks(wo_id, tenant_id)
    return [WorkOrderTaskResponse.model_validate(t, from_attributes=True) for t in tasks]


@router.post("/{wo_id}/tasks", response_model=WorkOrderTaskResponse, status_code=201, summary="Add task")
async def add_task(
    wo_id: UUID,
    payload: AddTaskRequest,
    tenant_id: TenantId,
    service: Annotated[WorkOrderDomainService, Depends(_get_service)],
) -> WorkOrderTaskResponse:
    task = await service.add_task(
        wo_id, tenant_id, title=payload.title, description=payload.description, sort_order=payload.sort_order,
    )
    return WorkOrderTaskResponse.model_validate(task, from_attributes=True)


@router.post("/{wo_id}/tasks/{task_id}/complete", response_model=WorkOrderTaskResponse,
             summary="Complete task")
async def complete_task(
    wo_id: UUID,
    task_id: UUID,
    payload: CompleteTaskRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[WorkOrderDomainService, Depends(_get_service)],
) -> WorkOrderTaskResponse:
    task = await service.complete_task(wo_id, tenant_id, task_id, user_id, notes=payload.notes)
    return WorkOrderTaskResponse.model_validate(task, from_attributes=True)


# ─── Notes ────────────────────────────────────────────────────────────────

@router.get("/{wo_id}/notes", response_model=list[WorkOrderNoteResponse], summary="List notes")
async def list_notes(
    wo_id: UUID,
    tenant_id: TenantId,
    service: Annotated[WorkOrderDomainService, Depends(_get_service)],
) -> list[WorkOrderNoteResponse]:
    notes = await service.list_notes(wo_id, tenant_id)
    return [WorkOrderNoteResponse.model_validate(n, from_attributes=True) for n in notes]


@router.post("/{wo_id}/notes", response_model=WorkOrderNoteResponse, status_code=201, summary="Add note")
async def add_note(
    wo_id: UUID,
    payload: AddNoteRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[WorkOrderDomainService, Depends(_get_service)],
) -> WorkOrderNoteResponse:
    note = await service.add_note(wo_id, tenant_id, user_id, body=payload.body, is_internal=payload.is_internal)
    return WorkOrderNoteResponse.model_validate(note, from_attributes=True)
