"""Tenant Service — Tenant management API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_super_admin
from rainer_common.pagination import PaginationParams, pagination_params
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse

from ....core.config import Settings, get_settings
from ....core.database import get_db
from ....domain.services import TenantDomainService
from ....integration.provision_welcome import (
    provision_tenant_admin_and_notify,
    resend_tenant_admin_welcome_email,
)
from ....infra.db.repositories import TenantRepository, TenantSettingsRepository
from ....schemas.create_payload import company_and_billing_profiles
from ....schemas.mappers import tenant_to_response
from ....schemas.requests import (
    CreateTenantRequest,
    ResendWelcomeEmailRequest,
    UpdateTenantRequest,
    UpdateTenantSettingsRequest,
)
from ....schemas.responses import TenantResponse, TenantSettingsResponse

router = APIRouter(prefix="/tenants", tags=["Tenants"])
logger = structlog.get_logger(__name__)


def _get_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TenantDomainService:
    return TenantDomainService(
        tenant_repo=TenantRepository(db),
        settings_repo=TenantSettingsRepository(db),
        settings=settings,
    )


@router.post(
    "",
    response_model=SuccessResponse[TenantResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create and provision a new tenant (super_admin only)",
)
async def create_tenant(
    payload: CreateTenantRequest,
    _: Annotated[CurrentUser, Depends(require_super_admin)],
    service: Annotated[TenantDomainService, Depends(_get_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
    app_settings: Annotated[Settings, Depends(get_settings)],
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> SuccessResponse[TenantResponse]:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Authorization header required"},
        )

    company_profile, billing_profile = company_and_billing_profiles(payload)
    td = payload.tenant_defaults
    tz = td.timezone if td else "UTC"
    locale = td.locale if td else "en-US"
    pc = payload.primary_contact

    tenant = await service.create_tenant(
        tenant_name=payload.tenant_name,
        products=payload.products,
        tier=payload.tier,
        region=payload.region,
        company_profile=company_profile,
        billing_profile=billing_profile,
        primary_contact_first_name=pc.first_name,
        primary_contact_last_name=pc.last_name,
        primary_contact_email=str(pc.email),
        primary_contact_phone=pc.phone,
        settings_timezone=tz,
        settings_locale=locale,
    )

    # Make the tenant visible to downstream services (auth/user/notification) before calling them.
    # `get_db` also commits at request end, but provision_welcome runs inside this request.
    await db.commit()

    try:
        await provision_tenant_admin_and_notify(
            settings=app_settings,
            authorization=authorization,
            tenant=tenant,
        )
    except Exception:
        logger.exception(
            "tenant_provision_post_commit_failed",
            tenant_id=tenant.id,
        )

    return SuccessResponse.of(tenant_to_response(tenant))


@router.post(
    "/resend-welcome-email",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend tenant admin welcome email with a new temporary password (super_admin only)",
)
async def resend_welcome_email(
    payload: ResendWelcomeEmailRequest,
    _: Annotated[CurrentUser, Depends(require_super_admin)],
    service: Annotated[TenantDomainService, Depends(_get_service)],
    app_settings: Annotated[Settings, Depends(get_settings)],
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> MessageResponse:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Authorization header required"},
        )
    tenant_id = str(payload.tenant_id)
    tenant = await service.get_tenant(tenant_id)
    await resend_tenant_admin_welcome_email(
        settings=app_settings,
        authorization=authorization,
        tenant=tenant,
    )
    return MessageResponse(message="Welcome email has been resent")


@router.get(
    "",
    response_model=PaginatedResponse[TenantResponse],
    summary="List all tenants (super_admin only)",
)
async def list_tenants(
    _: Annotated[CurrentUser, Depends(require_super_admin)],
    service: Annotated[TenantDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    status_filter: str | None = None,
) -> PaginatedResponse[TenantResponse]:
    tenants, total = await service.list_tenants(
        status=status_filter,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[tenant_to_response(t) for t in tenants],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


@router.get(
    "/by-slug/{slug}",
    response_model=SuccessResponse[TenantResponse],
    summary="Get tenant by URL slug (super_admin or member of tenant)",
)
async def get_tenant_by_slug(
    slug: str,
    current_user: CurrentUser,
    service: Annotated[TenantDomainService, Depends(_get_service)],
) -> SuccessResponse[TenantResponse]:
    tenant = await service.get_tenant_by_slug(slug)
    if current_user.role != "super_admin" and current_user.tenant_id != tenant.id:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Access denied"})
    return SuccessResponse.of(tenant_to_response(tenant))


@router.get(
    "/{tenant_id}",
    response_model=SuccessResponse[TenantResponse],
    summary="Get tenant details",
)
async def get_tenant(
    tenant_id: str,
    current_user: CurrentUser,
    service: Annotated[TenantDomainService, Depends(_get_service)],
) -> SuccessResponse[TenantResponse]:
    if current_user.role != "super_admin" and current_user.tenant_id != tenant_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Access denied"})
    tenant = await service.get_tenant(tenant_id)
    return SuccessResponse.of(tenant_to_response(tenant))


@router.patch(
    "/{tenant_id}",
    response_model=SuccessResponse[TenantResponse],
    summary="Update tenant (super_admin only)",
)
async def update_tenant(
    tenant_id: str,
    payload: UpdateTenantRequest,
    _: Annotated[CurrentUser, Depends(require_super_admin)],
    service: Annotated[TenantDomainService, Depends(_get_service)],
) -> SuccessResponse[TenantResponse]:
    update_data = payload.model_dump(exclude_none=True)
    if update_data:
        await service.update_tenant(tenant_id, **update_data)
    tenant = await service.get_tenant(tenant_id)
    return SuccessResponse.of(tenant_to_response(tenant))


@router.delete(
    "/{tenant_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Soft-delete tenant (super_admin only)",
)
async def delete_tenant(
    tenant_id: str,
    _: Annotated[CurrentUser, Depends(require_super_admin)],
    service: Annotated[TenantDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.delete_tenant(tenant_id)
    return MessageResponse(message="Tenant deleted successfully")


@router.post(
    "/{tenant_id}/suspend",
    response_model=MessageResponse,
    summary="Suspend tenant (super_admin only)",
)
async def suspend_tenant(
    tenant_id: str,
    _: Annotated[CurrentUser, Depends(require_super_admin)],
    service: Annotated[TenantDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.suspend_tenant(tenant_id)
    return MessageResponse(message="Tenant suspended")


@router.post(
    "/{tenant_id}/activate",
    response_model=MessageResponse,
    summary="Activate / reactivate tenant (super_admin only)",
)
async def activate_tenant(
    tenant_id: str,
    _: Annotated[CurrentUser, Depends(require_super_admin)],
    service: Annotated[TenantDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.activate_tenant(tenant_id)
    return MessageResponse(message="Tenant activated")


@router.get(
    "/{tenant_id}/settings",
    response_model=SuccessResponse[TenantSettingsResponse],
    summary="Get tenant settings",
)
async def get_settings_endpoint(
    tenant_id: str,
    current_user: CurrentUser,
    service: Annotated[TenantDomainService, Depends(_get_service)],
) -> SuccessResponse[TenantSettingsResponse]:
    if current_user.role != "super_admin" and current_user.tenant_id != tenant_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Access denied"})
    settings = await service.get_settings(tenant_id)
    return SuccessResponse.of(TenantSettingsResponse.model_validate(settings, from_attributes=True))


@router.patch(
    "/{tenant_id}/settings",
    response_model=MessageResponse,
    summary="Update tenant settings",
)
async def update_settings_endpoint(
    tenant_id: str,
    payload: UpdateTenantSettingsRequest,
    current_user: CurrentUser,
    service: Annotated[TenantDomainService, Depends(_get_service)],
) -> MessageResponse:
    if current_user.role not in ("super_admin", "tenant_admin"):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Admin required"})
    update_data = payload.model_dump(exclude_none=True)
    if update_data:
        await service.update_settings(tenant_id, **update_data)
    return MessageResponse(message="Settings updated successfully")
