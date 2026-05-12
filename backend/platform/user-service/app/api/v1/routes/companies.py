"""User Service — Company management API routes."""

from typing import Annotated

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_role
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.config import Settings, get_settings
from ....core.database import get_db
from ....domain.services import UserDomainService
from ....infra.db.repositories import (
    CompanyRepository,
    RoleRepository,
    UserRepository,
    UserRoleRepository,
)
from ....schemas.requests import (
    AssignRoleRequest,
    CreateCompanyRequest,
    CreateCompanyUserRequest,
    CreateRoleRequest,
    UpdateCompanyRequest,
    UpdateRoleRequest,
)
from ....schemas.responses import (
    CompanyResponse,
    CompanyUserCreatedResponse,
    CompanyWithAdminResponse,
    RoleResponse,
    UserResponse,
    UserRoleResponse,
)

router = APIRouter(tags=["Companies"])
logger = structlog.get_logger(__name__)


def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserDomainService:
    return UserDomainService(
        user_repo=UserRepository(db),
        role_repo=RoleRepository(db),
        user_role_repo=UserRoleRepository(db),
        company_repo=CompanyRepository(db),
    )


def _assert_company_access(current_user: CurrentUser, company_id: str) -> None:
    """Raise 403 if company_admin is trying to access a different company.

    Passes through for super_admin and tenant_admin (they have no company_id restriction).
    For company_admin: token's company_id must match the requested company_id.
    """
    logger.info(
        "company_access_check",
        role=current_user.role,
        user_company_id=current_user.company_id,
        target_company_id=company_id,
        is_company_admin=current_user.role == "company_admin",
        company_ids_match=current_user.company_id == company_id,
    )
    if current_user.role == "company_admin":
        if not current_user.company_id:
            logger.warning(
                "company_access_denied_no_company_id",
                user_sub=current_user.sub,
                target_company_id=company_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Your account has no company assigned. Contact your tenant admin."},
            )
        if current_user.company_id != company_id:
            logger.warning(
                "company_access_denied_mismatch",
                user_sub=current_user.sub,
                user_company_id=current_user.company_id,
                target_company_id=company_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Access denied to this company"},
            )


# ── Company CRUD ─────────────────────────────────────────────────────────────

@router.get("/companies", response_model=PaginatedResponse[CompanyResponse])
async def list_companies(
    current_user: Annotated[CurrentUser, Depends(require_role("super_admin", "tenant_admin"))],
    service: Annotated[UserDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    is_active: bool | None = Query(default=None),
) -> PaginatedResponse[CompanyResponse]:
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id
    companies, total = await service.list_companies(
        tenant_id=tenant_id,
        is_active=is_active,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[CompanyResponse.model_validate(c, from_attributes=True) for c in companies],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


@router.post("/companies", response_model=SuccessResponse[CompanyWithAdminResponse], status_code=201)
async def create_company(
    payload: CreateCompanyRequest,
    request: Request,
    current_user: Annotated[CurrentUser, Depends(require_role("super_admin", "tenant_admin"))],
    service: Annotated[UserDomainService, Depends(_get_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> SuccessResponse[CompanyWithAdminResponse]:
    tenant_id = (
        current_user.tenant_id
        if current_user.role != "super_admin"
        else current_user.tenant_id or ""
    )
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "BAD_REQUEST", "message": "tenant_id required"},
        )

    company = await service.create_company(
        tenant_id=tenant_id,
        name=payload.name,
        email=str(payload.email),
        phone=payload.phone,
        address=payload.address,
        company_code=payload.company_code,
        employee_limit=payload.employee_limit,
    )

    auth_header = request.headers.get("Authorization", "")
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{settings.auth_service_url}/api/v1/auth/bootstrap/company-admin",
            json={
                "email": str(payload.admin.email),
                "first_name": payload.admin.first_name,
                "last_name": payload.admin.last_name,
                "company_id": company.id,
            },
            headers={"Authorization": auth_header},
        )
    if resp.status_code != 201:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "AUTH_SERVICE_ERROR", "message": resp.json().get("detail", "Auth service error")},
        )
    auth_data = resp.json()["data"]
    platform_user_id = auth_data["platform_user_id"]
    temporary_password = auth_data["temporary_password"]

    admin = await service.create_user(
        platform_user_id=platform_user_id,
        tenant_id=tenant_id,
        first_name=payload.admin.first_name,
        last_name=payload.admin.last_name,
        company_id=company.id,
        phone=payload.admin.phone,
    )

    await service.set_company_admin(company.id, admin.id)
    company.admin_id = admin.id

    login_url = f"{settings.frontend_url}/login"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"{settings.notification_service_url}/api/v1/notifications/send-from-template",
                json={
                    "template_name": "company_admin_welcome",
                    "recipient_email": str(payload.admin.email),
                    "variables": {
                        "company_name": company.name,
                        "company_code": company.company_code,
                        "admin_first_name": payload.admin.first_name,
                        "admin_last_name": payload.admin.last_name,
                        "admin_email": str(payload.admin.email),
                        "temporary_password": temporary_password,
                        "login_url": login_url,
                    },
                    "tenant_id": tenant_id,
                    "user_id": admin.id,
                },
                headers={"Authorization": auth_header},
            )
    except Exception as exc:
        logger.warning("company_admin_welcome_email_failed", company_id=company.id, error=str(exc))

    logger.info(
        "company_created_with_admin",
        company_id=company.id,
        admin_id=admin.id,
        caller=current_user.sub,
    )
    return SuccessResponse.of(
        CompanyWithAdminResponse(
            company=CompanyResponse.model_validate(company, from_attributes=True),
            admin=UserResponse.model_validate(admin, from_attributes=True),
            temporary_password=temporary_password,
        )
    )


@router.get("/companies/{company_id}", response_model=SuccessResponse[CompanyResponse])
async def get_company(
    company_id: str,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[CompanyResponse]:
    if current_user.role not in ("super_admin", "tenant_admin"):
        _assert_company_access(current_user, company_id)
    company = await service.get_company(company_id)
    return SuccessResponse.of(CompanyResponse.model_validate(company, from_attributes=True))


@router.patch("/companies/{company_id}", response_model=SuccessResponse[CompanyResponse])
async def update_company(
    company_id: str,
    payload: UpdateCompanyRequest,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[CompanyResponse]:
    if current_user.role not in ("super_admin", "tenant_admin"):
        _assert_company_access(current_user, company_id)

    fields = payload.model_dump(exclude_none=True)
    if "email" in fields:
        fields["email"] = str(fields["email"])
    company = await service.update_company(company_id, **fields)
    return SuccessResponse.of(CompanyResponse.model_validate(company, from_attributes=True))


@router.delete("/companies/{company_id}", response_model=MessageResponse)
async def deactivate_company(
    company_id: str,
    _: Annotated[CurrentUser, Depends(require_role("super_admin", "tenant_admin"))],
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.deactivate_company(company_id)
    return MessageResponse(message="Company deactivated")


# ── Company users ─────────────────────────────────────────────────────────────

@router.get("/companies/{company_id}/users", response_model=PaginatedResponse[UserResponse])
async def list_company_users(
    company_id: str,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    is_active: bool | None = Query(default=None),
) -> PaginatedResponse[UserResponse]:
    if current_user.role not in ("super_admin", "tenant_admin"):
        _assert_company_access(current_user, company_id)

    users, total = await service.list_users(
        is_active=is_active,
        company_id=company_id,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[UserResponse.model_validate(u, from_attributes=True) for u in users],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


@router.post(
    "/companies/{company_id}/users",
    response_model=SuccessResponse[CompanyUserCreatedResponse],
    status_code=201,
)
async def create_company_user(
    company_id: str,
    payload: CreateCompanyUserRequest,
    request: Request,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> SuccessResponse[CompanyUserCreatedResponse]:
    logger.info(
        "create_company_user_entry",
        role=current_user.role,
        user_company_id=current_user.company_id,
        target_company_id=company_id,
        endpoint_reached=True,
    )
    if current_user.role not in ("super_admin", "tenant_admin"):
        _assert_company_access(current_user, company_id)

    tenant_id = current_user.tenant_id or ""
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "BAD_REQUEST", "message": "tenant_id required"},
        )

    auth_header = request.headers.get("Authorization", "")
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{settings.auth_service_url}/api/v1/auth/bootstrap/company-user",
            json={
                "email": str(payload.email),
                "first_name": payload.first_name,
                "last_name": payload.last_name,
                "company_id": company_id,
            },
            headers={"Authorization": auth_header},
        )
    if resp.status_code != 201:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "AUTH_SERVICE_ERROR", "message": resp.json().get("detail", "Auth service error")},
        )
    auth_data = resp.json()["data"]
    platform_user_id = auth_data["platform_user_id"]
    temporary_password = auth_data["temporary_password"]

    user = await service.create_user(
        platform_user_id=platform_user_id,
        tenant_id=tenant_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        company_id=company_id,
        display_name=payload.display_name,
        phone=payload.phone,
        department=payload.department,
    )

    if payload.role_id:
        await service.assign_role(
            user.id,
            payload.role_id,
            granted_by=current_user.sub,
            caller_company_id=current_user.company_id,
        )

    company = await service.get_company(company_id)
    login_url = f"{settings.frontend_url}/login"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f"{settings.notification_service_url}/api/v1/notifications/send-from-template",
                json={
                    "template_name": "company_user_welcome",
                    "recipient_email": str(payload.email),
                    "variables": {
                        "company_name": company.name,
                        "first_name": payload.first_name,
                        "last_name": payload.last_name,
                        "email": str(payload.email),
                        "temporary_password": temporary_password,
                        "login_url": login_url,
                    },
                    "tenant_id": tenant_id,
                    "user_id": user.id,
                },
                headers={"Authorization": auth_header},
            )
    except Exception as exc:
        logger.warning("company_user_welcome_email_failed", user_id=user.id, error=str(exc))

    logger.info("company_user_created", user_id=user.id, company_id=company_id, caller=current_user.sub)
    return SuccessResponse.of(
        CompanyUserCreatedResponse(
            user=UserResponse.model_validate(user, from_attributes=True),
            temporary_password=temporary_password,
        )
    )


# ── Company-scoped roles ──────────────────────────────────────────────────────

@router.get("/companies/{company_id}/roles", response_model=SuccessResponse[list[RoleResponse]])
async def list_company_roles(
    company_id: str,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[list[RoleResponse]]:
    if current_user.role not in ("super_admin", "tenant_admin"):
        _assert_company_access(current_user, company_id)

    # Return both company-specific roles AND the tenant-level company template roles
    company_roles = await service.list_roles(scope="company", company_id=company_id)
    template_roles = await service.list_roles(scope="company", company_id=None)
    all_roles = template_roles + company_roles
    return SuccessResponse.of([RoleResponse.model_validate(r, from_attributes=True) for r in all_roles])


@router.post(
    "/companies/{company_id}/roles",
    response_model=SuccessResponse[RoleResponse],
    status_code=201,
)
async def create_company_role(
    company_id: str,
    payload: CreateRoleRequest,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[RoleResponse]:
    if current_user.role not in ("super_admin", "tenant_admin"):
        _assert_company_access(current_user, company_id)

    role = await service.create_role(
        name=payload.name,
        permissions=payload.permissions,
        description=payload.description,
        product=payload.product,
        scope="company",
        company_id=company_id,
    )
    return SuccessResponse.of(RoleResponse.model_validate(role, from_attributes=True))


@router.patch(
    "/companies/{company_id}/roles/{role_id}",
    response_model=SuccessResponse[RoleResponse],
)
async def update_company_role(
    company_id: str,
    role_id: str,
    payload: UpdateRoleRequest,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[RoleResponse]:
    if current_user.role not in ("super_admin", "tenant_admin"):
        _assert_company_access(current_user, company_id)

    update_data = payload.model_dump(exclude_none=True)
    role = await service.update_role(role_id, **update_data)
    return SuccessResponse.of(RoleResponse.model_validate(role, from_attributes=True))


@router.post(
    "/companies/{company_id}/users/{user_id}/roles",
    response_model=SuccessResponse[UserRoleResponse],
    status_code=201,
)
async def assign_company_user_role(
    company_id: str,
    user_id: str,
    payload: AssignRoleRequest,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[UserRoleResponse]:
    if current_user.role not in ("super_admin", "tenant_admin"):
        _assert_company_access(current_user, company_id)

    user_role = await service.assign_role(
        user_id,
        payload.role_id,
        granted_by=current_user.sub,
        caller_company_id=current_user.company_id if current_user.role == "company_admin" else None,
    )
    return SuccessResponse.of(UserRoleResponse.model_validate(user_role, from_attributes=True))


@router.delete(
    "/companies/{company_id}/users/{user_id}/roles/{role_id}",
    response_model=MessageResponse,
)
async def remove_company_user_role(
    company_id: str,
    user_id: str,
    role_id: str,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> MessageResponse:
    if current_user.role not in ("super_admin", "tenant_admin"):
        _assert_company_access(current_user, company_id)

    await service.remove_role(user_id, role_id)
    return MessageResponse(message="Role removed from user")
