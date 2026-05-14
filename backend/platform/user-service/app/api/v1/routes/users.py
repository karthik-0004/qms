"""User Service — Users and Roles API routes."""

from typing import Annotated

import httpx
import structlog
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_role
from rainer_common.responses import MessageResponse, PaginatedResponse, SuccessResponse
from rainer_common.pagination import PaginationParams, pagination_params

from ....core.config import Settings, get_settings
from ....core.database import get_db
from ....domain.services import UserDomainService
from ....infra.db.repositories import CompanyRepository, RoleRepository, UserRepository, UserRoleRepository
from ....schemas.requests import (
    AssignRoleRequest,
    CreateRoleRequest,
    CreateUserRequest,
    UpdateRoleRequest,
    UpdateUserRequest,
)
from ....schemas.responses import (
    RoleResponse,
    UserPermissionsResponse,
    UserResponse,
    UserRoleResponse,
)

router = APIRouter(tags=["Users & Roles"])
logger = structlog.get_logger(__name__)


def _get_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserDomainService:
    return UserDomainService(
        user_repo=UserRepository(db),
        role_repo=RoleRepository(db),
        user_role_repo=UserRoleRepository(db),
        company_repo=CompanyRepository(db),
    )


# ── Users ────────────────────────────────────────────────────────────────
@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    service: Annotated[UserDomainService, Depends(_get_service)],
    pagination: Annotated[PaginationParams, Depends(pagination_params)],
    current_user: CurrentUser | None = None,
    is_active: bool | None = Query(default=None),
    department: str | None = Query(default=None),
) -> PaginatedResponse[UserResponse]:
    # If no authenticated user, return empty list
    if not current_user:
        return PaginatedResponse.of(
            data=[],
            page=pagination.page,
            page_size=pagination.page_size,
            total=0,
        )

    # Company admins see only their own company's users
    company_id = current_user.company_id if current_user.role == "company_admin" else None
    # Tenant-scoped callers see only their tenant
    tenant_id = None if current_user.role == "super_admin" else current_user.tenant_id

    users, total = await service.list_users(
        is_active=is_active,
        department=department,
        company_id=company_id,
        tenant_id=tenant_id,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return PaginatedResponse.of(
        data=[UserResponse.model_validate(u, from_attributes=True) for u in users],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


@router.post("/users", response_model=SuccessResponse[UserResponse], status_code=201)
async def create_user(
    payload: CreateUserRequest,
    request: Request,
    current_user: Annotated[CurrentUser, Depends(require_role("super_admin", "tenant_admin"))],
    service: Annotated[UserDomainService, Depends(_get_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> SuccessResponse[UserResponse]:
    from fastapi import HTTPException

    if current_user.role == "super_admin" and payload.tenant_id:
        target_tenant_id = payload.tenant_id
    else:
        target_tenant_id = current_user.tenant_id or ""

    if not target_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "BAD_REQUEST",
                "message": "tenant_id required for provisioning when caller has no tenant context",
            },
        )

    platform_user_id = payload.platform_user_id
    temporary_password: str | None = None

    # Bootstrap mode: no pre-existing auth account — create one now.
    if not platform_user_id:
        auth_header = request.headers.get("Authorization", "")
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{settings.auth_service_url}/api/v1/auth/bootstrap/tenant-user",
                json={
                    "email": str(payload.email),
                    "first_name": payload.first_name,
                    "last_name": payload.last_name,
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
        tenant_id=target_tenant_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        display_name=payload.display_name,
        phone=payload.phone,
        department=payload.department,
        job_title=payload.job_title,
    )

    # Send welcome email when a new auth account was bootstrapped.
    if temporary_password and payload.email:
        auth_header = request.headers.get("Authorization", "")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"{settings.notification_service_url}/api/v1/notifications/send-from-template",
                    json={
                        "template_name": "tenant_user_welcome",
                        "recipient_email": str(payload.email),
                        "variables": {
                            "first_name": payload.first_name,
                            "last_name": payload.last_name,
                            "email": str(payload.email),
                            "temporary_password": temporary_password,
                            "login_url": f"{settings.frontend_url}/login",
                        },
                        "tenant_id": target_tenant_id,
                        "user_id": user.id,
                    },
                    headers={"Authorization": auth_header},
                )
        except Exception as exc:
            logger.warning("tenant_user_welcome_email_failed", user_id=user.id, error=str(exc))

    return SuccessResponse.of(UserResponse.model_validate(user, from_attributes=True))


@router.get("/users/{user_id}", response_model=SuccessResponse[UserResponse])
async def get_user(
    user_id: str,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[UserResponse]:
    user = await service.get_user(user_id)
    return SuccessResponse.of(UserResponse.model_validate(user, from_attributes=True))


@router.patch("/users/{user_id}", response_model=SuccessResponse[UserResponse])
async def update_user(
    user_id: str,
    payload: UpdateUserRequest,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[UserResponse]:
    if current_user.sub != user_id and current_user.role not in ("super_admin", "tenant_admin"):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN"})
    update_data = payload.model_dump(exclude_none=True)
    user = await service.update_user(user_id, **update_data)
    return SuccessResponse.of(UserResponse.model_validate(user, from_attributes=True))


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def deactivate_user(
    user_id: str,
    _: Annotated[CurrentUser, Depends(require_role("super_admin", "tenant_admin"))],
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.deactivate_user(user_id)
    return MessageResponse(message="User deactivated")


@router.get("/users/{user_id}/permissions", response_model=SuccessResponse[UserPermissionsResponse])
async def get_user_permissions(
    user_id: str,
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[UserPermissionsResponse]:
    permissions = await service.get_user_permissions(user_id)
    return SuccessResponse.of(UserPermissionsResponse(user_id=user_id, permissions=permissions))


# ── Roles ────────────────────────────────────────────────────────────────
@router.get("/roles", response_model=SuccessResponse[list[RoleResponse]])
async def list_roles(
    current_user: CurrentUser,
    service: Annotated[UserDomainService, Depends(_get_service)],
    product: str | None = Query(default=None),
    scope: str | None = Query(default=None),
) -> SuccessResponse[list[RoleResponse]]:
    roles = await service.list_roles(product=product, scope=scope)
    return SuccessResponse.of([RoleResponse.model_validate(r, from_attributes=True) for r in roles])


@router.post("/roles", response_model=SuccessResponse[RoleResponse], status_code=201)
async def create_role(
    payload: CreateRoleRequest,
    _: Annotated[CurrentUser, Depends(require_role("super_admin", "tenant_admin"))],
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[RoleResponse]:
    role = await service.create_role(
        name=payload.name,
        permissions=payload.permissions,
        description=payload.description,
        product=payload.product,
    )
    return SuccessResponse.of(RoleResponse.model_validate(role, from_attributes=True))


@router.patch("/roles/{role_id}", response_model=SuccessResponse[RoleResponse])
async def update_role(
    role_id: str,
    payload: UpdateRoleRequest,
    _: Annotated[CurrentUser, Depends(require_role("super_admin", "tenant_admin"))],
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[RoleResponse]:
    update_data = payload.model_dump(exclude_none=True)
    role = await service.update_role(role_id, **update_data)
    return SuccessResponse.of(RoleResponse.model_validate(role, from_attributes=True))


# ── User Role Assignments ─────────────────────────────────────────────────
@router.post("/users/{user_id}/roles", response_model=SuccessResponse[UserRoleResponse], status_code=201)
async def assign_role(
    user_id: str,
    payload: AssignRoleRequest,
    current_user: Annotated[CurrentUser, Depends(require_role("super_admin", "tenant_admin", "company_admin"))],
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> SuccessResponse[UserRoleResponse]:
    user_role = await service.assign_role(
        user_id,
        payload.role_id,
        granted_by=current_user.sub,
        caller_company_id=current_user.company_id if current_user.role == "company_admin" else None,
    )
    return SuccessResponse.of(UserRoleResponse.model_validate(user_role, from_attributes=True))


@router.delete("/users/{user_id}/roles/{role_id}", response_model=MessageResponse)
async def remove_role(
    user_id: str,
    role_id: str,
    _: Annotated[CurrentUser, Depends(require_role("super_admin", "tenant_admin"))],
    service: Annotated[UserDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.remove_role(user_id, role_id)
    return MessageResponse(message="Role removed from user")
