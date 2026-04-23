"""Contract Service — Contract lifecycle API routes."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.service import ContractDomainService
from app.schemas.requests import AddLineItemRequest, CreateContractRequest, TransitionStatusRequest
from app.schemas.responses import ContractHistoryResponse, ContractLineItemResponse, ContractResponse

router = APIRouter(prefix="/contracts", tags=["Contracts"])
logger = structlog.get_logger(__name__)

TenantId = Annotated[UUID, Header(alias="x-tenant-id")]
UserId = Annotated[UUID, Header(alias="x-user-id")]


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ContractDomainService:
    return ContractDomainService(db)


@router.get("", response_model=list[ContractResponse], summary="List contracts")
async def list_contracts(
    tenant_id: TenantId,
    service: Annotated[ContractDomainService, Depends(_get_service)],
    customer_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[ContractResponse]:
    contracts = await service.list_contracts(
        tenant_id=tenant_id, customer_id=customer_id, status=status, skip=skip, limit=limit,
    )
    return [ContractResponse.model_validate(c, from_attributes=True) for c in contracts]


@router.post("", response_model=ContractResponse, status_code=201, summary="Create contract")
async def create_contract(
    payload: CreateContractRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[ContractDomainService, Depends(_get_service)],
) -> ContractResponse:
    fields = payload.model_dump(exclude={"customer_id", "contract_number", "title", "contract_type"})
    contract = await service.create_contract(
        tenant_id=tenant_id, customer_id=payload.customer_id, created_by=user_id,
        contract_number=payload.contract_number, title=payload.title,
        contract_type=payload.contract_type, **fields,
    )
    return ContractResponse.model_validate(contract, from_attributes=True)


@router.get("/{contract_id}", response_model=ContractResponse, summary="Get contract")
async def get_contract(
    contract_id: UUID,
    tenant_id: TenantId,
    service: Annotated[ContractDomainService, Depends(_get_service)],
) -> ContractResponse:
    contract = await service.get_contract(contract_id, tenant_id)
    return ContractResponse.model_validate(contract, from_attributes=True)


@router.post("/{contract_id}/status", response_model=ContractResponse, summary="Transition contract status")
async def transition_status(
    contract_id: UUID,
    payload: TransitionStatusRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[ContractDomainService, Depends(_get_service)],
) -> ContractResponse:
    contract = await service.transition_status(
        contract_id, tenant_id, payload.new_status, user_id, comment=payload.comment,
    )
    return ContractResponse.model_validate(contract, from_attributes=True)


@router.get("/{contract_id}/history", response_model=list[ContractHistoryResponse],
            summary="Get contract status history")
async def get_history(
    contract_id: UUID,
    tenant_id: TenantId,
    service: Annotated[ContractDomainService, Depends(_get_service)],
) -> list[ContractHistoryResponse]:
    history = await service.get_history(contract_id, tenant_id)
    return [ContractHistoryResponse.model_validate(h, from_attributes=True) for h in history]


# ─── Line Items ──────────────────────────────────────────────────────────

@router.get("/{contract_id}/line-items", response_model=list[ContractLineItemResponse],
            summary="List contract line items")
async def list_line_items(
    contract_id: UUID,
    tenant_id: TenantId,
    service: Annotated[ContractDomainService, Depends(_get_service)],
) -> list[ContractLineItemResponse]:
    items = await service.list_line_items(contract_id, tenant_id)
    return [ContractLineItemResponse.model_validate(i, from_attributes=True) for i in items]


@router.post("/{contract_id}/line-items", response_model=ContractLineItemResponse, status_code=201,
             summary="Add line item to contract")
async def add_line_item(
    contract_id: UUID,
    payload: AddLineItemRequest,
    tenant_id: TenantId,
    service: Annotated[ContractDomainService, Depends(_get_service)],
) -> ContractLineItemResponse:
    item = await service.add_line_item(
        contract_id=contract_id, tenant_id=tenant_id,
        description=payload.description, unit_price=payload.unit_price,
        quantity=payload.quantity, unit=payload.unit, sort_order=payload.sort_order,
    )
    return ContractLineItemResponse.model_validate(item, from_attributes=True)
