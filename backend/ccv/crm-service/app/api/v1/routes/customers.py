"""CRM Service — Customer, Contact, and Interaction API routes."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.service import CRMDomainService
from app.schemas.requests import (
    AddContactRequest,
    CreateCustomerRequest,
    LogInteractionRequest,
    TransitionStatusRequest,
    UpdateCustomerRequest,
)
from app.schemas.responses import ContactResponse, CustomerResponse, InteractionResponse

router = APIRouter(prefix="/customers", tags=["Customers"])
logger = structlog.get_logger(__name__)

TenantId = Annotated[UUID, Header(alias="x-tenant-id")]
UserId = Annotated[UUID, Header(alias="x-user-id")]


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> CRMDomainService:
    return CRMDomainService(db)


@router.get("", response_model=list[CustomerResponse], summary="List customers")
async def list_customers(
    tenant_id: TenantId,
    service: Annotated[CRMDomainService, Depends(_get_service)],
    status: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[CustomerResponse]:
    customers = await service.list_customers(tenant_id=tenant_id, status=status, skip=skip, limit=limit)
    return [CustomerResponse.from_model(c) for c in customers]


@router.post("", response_model=CustomerResponse, status_code=201, summary="Create customer")
async def create_customer(
    payload: CreateCustomerRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[CRMDomainService, Depends(_get_service)],
) -> CustomerResponse:
    fields = payload.model_dump(exclude={"company_name"})
    customer = await service.create_customer(
        tenant_id=tenant_id, created_by=user_id, company_name=payload.company_name, **fields,
    )
    return CustomerResponse.from_model(customer)


@router.get("/{customer_id}", response_model=CustomerResponse, summary="Get customer")
async def get_customer(
    customer_id: UUID,
    tenant_id: TenantId,
    service: Annotated[CRMDomainService, Depends(_get_service)],
) -> CustomerResponse:
    customer = await service.get_customer(customer_id, tenant_id)
    return CustomerResponse.from_model(customer)


@router.patch("/{customer_id}", response_model=CustomerResponse, summary="Update customer")
async def update_customer(
    customer_id: UUID,
    payload: UpdateCustomerRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[CRMDomainService, Depends(_get_service)],
) -> CustomerResponse:
    fields = payload.model_dump(exclude_none=True)
    customer = await service.update_customer(customer_id, tenant_id, changed_by=user_id, **fields)
    return CustomerResponse.from_model(customer)


@router.post("/{customer_id}/status", response_model=CustomerResponse, summary="Transition customer status")
async def transition_status(
    customer_id: UUID,
    payload: TransitionStatusRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[CRMDomainService, Depends(_get_service)],
) -> CustomerResponse:
    customer = await service.transition_status(customer_id, tenant_id, payload.new_status, user_id)
    return CustomerResponse.from_model(customer)


# ─── Contacts ────────────────────────────────────────────────────────────

@router.get("/{customer_id}/contacts", response_model=list[ContactResponse], summary="List contacts")
async def list_contacts(
    customer_id: UUID,
    tenant_id: TenantId,
    service: Annotated[CRMDomainService, Depends(_get_service)],
) -> list[ContactResponse]:
    contacts = await service.list_contacts(customer_id, tenant_id)
    return [ContactResponse.model_validate(c, from_attributes=True) for c in contacts]


@router.post("/{customer_id}/contacts", response_model=ContactResponse, status_code=201,
             summary="Add contact to customer")
async def add_contact(
    customer_id: UUID,
    payload: AddContactRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[CRMDomainService, Depends(_get_service)],
) -> ContactResponse:
    fields = payload.model_dump(exclude={"first_name", "last_name", "is_primary"})
    contact = await service.add_contact(
        customer_id=customer_id, tenant_id=tenant_id, created_by=user_id,
        first_name=payload.first_name, last_name=payload.last_name, is_primary=payload.is_primary,
        **fields,
    )
    return ContactResponse.model_validate(contact, from_attributes=True)


# ─── Interactions ─────────────────────────────────────────────────────────

@router.get("/{customer_id}/interactions", response_model=list[InteractionResponse],
            summary="List interactions")
async def list_interactions(
    customer_id: UUID,
    tenant_id: TenantId,
    service: Annotated[CRMDomainService, Depends(_get_service)],
    limit: int = Query(default=50, ge=1, le=200),
) -> list[InteractionResponse]:
    interactions = await service.list_interactions(customer_id, tenant_id, limit=limit)
    return [InteractionResponse.from_model(i) for i in interactions]


@router.post("/{customer_id}/interactions", response_model=InteractionResponse, status_code=201,
             summary="Log interaction")
async def log_interaction(
    customer_id: UUID,
    payload: LogInteractionRequest,
    tenant_id: TenantId,
    user_id: UserId,
    service: Annotated[CRMDomainService, Depends(_get_service)],
) -> InteractionResponse:
    fields = payload.model_dump(exclude={"interaction_type", "subject"})
    interaction = await service.log_interaction(
        customer_id=customer_id, tenant_id=tenant_id, created_by=user_id,
        interaction_type=payload.interaction_type, subject=payload.subject, **fields,
    )
    return InteractionResponse.from_model(interaction)
