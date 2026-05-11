"""Auth Service — Authentication API routes."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rainer_auth_lib.dependencies import CurrentUser, require_super_admin
from rainer_common.exceptions import ConflictError, NotFoundError
from rainer_common.responses import MessageResponse, SuccessResponse

from ....core.bootstrap_password import generate_temporary_password
from ....core.config import Settings, get_settings
from ....core.database import get_db
from ....core.security import hash_password
from ....domain.services import AuthDomainService
from ....infra.db.models import Tenant
from ....infra.db.repositories import (
    AccessKeyRepository,
    AuditLogRepository,
    RefreshTokenRepository,
    UserRepository,
)
from ....schemas.requests import (
    BootstrapTenantAdminRequest,
    CreateAccessKeyRequest,
    LoginRequest,
    LogoutRequest,
    MFADisableRequest,
    MFAVerifyRequest,
    RefreshTokenRequest,
)
from ....schemas.responses import (
    AccessKeyResponse,
    BootstrapTenantAdminResponse,
    MFASetupResponse,
    RefreshResponse,
    ResendTenantAdminWelcomeResponse,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = structlog.get_logger(__name__)


def _set_refresh_cookie(response: JSONResponse, token: str, settings: Settings) -> None:
    """Set HttpOnly, Secure, SameSite cookie for the refresh token."""
    max_age = settings.jwt_refresh_token_expire_days * 86400
    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path=settings.cookie_path,
        domain=settings.cookie_domain,
    )


def _clear_refresh_cookie(response: JSONResponse, settings: Settings) -> None:
    """Delete the refresh token cookie."""
    response.delete_cookie(
        key=settings.refresh_token_cookie_name,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path=settings.cookie_path,
    )


def _get_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthDomainService:
    return AuthDomainService(
        user_repo=UserRepository(db),
        token_repo=RefreshTokenRepository(db),
        key_repo=AccessKeyRepository(db),
        audit_repo=AuditLogRepository(db),
        settings=settings,
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and get tokens",
)
async def login(
    payload: LoginRequest,
    request: Request,
    service: Annotated[AuthDomainService, Depends(_get_service)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    result = await service.login(
        email=payload.email,
        password=payload.password,
        mfa_code=payload.mfa_code,
        ip_address=ip,
        user_agent=user_agent,
    )
    refresh_token = result.pop("refresh_token")
    body = SuccessResponse.of(TokenResponse(**result, refresh_token="")).model_dump()
    response = JSONResponse(content=body, status_code=200)
    _set_refresh_cookie(response, refresh_token, settings)
    return response


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token and get new access token",
)
async def refresh_token(
    request: Request,
    service: Annotated[AuthDomainService, Depends(_get_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    payload: RefreshTokenRequest | None = None,
):
    cookie_token = request.cookies.get(settings.refresh_token_cookie_name)
    raw_token = cookie_token or (payload.refresh_token if payload else None)
    if not raw_token:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    ip = request.client.host if request.client else None
    result = await service.refresh_tokens(raw_token, ip_address=ip)
    new_refresh = result.pop("refresh_token")
    body = SuccessResponse.of(RefreshResponse(**result, refresh_token="")).model_dump()
    response = JSONResponse(content=body, status_code=200)
    _set_refresh_cookie(response, new_refresh, settings)
    return response


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Revoke refresh token (logout)",
)
async def logout(
    request: Request,
    service: Annotated[AuthDomainService, Depends(_get_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    payload: LogoutRequest | None = None,
):
    cookie_token = request.cookies.get(settings.refresh_token_cookie_name)
    raw_token = cookie_token or (payload.refresh_token if payload else None)
    if raw_token:
        await service.logout(raw_token)
    body = MessageResponse(message="Logged out successfully").model_dump()
    response = JSONResponse(content=body, status_code=200)
    _clear_refresh_cookie(response, settings)
    return response


@router.post(
    "/logout-all",
    status_code=status.HTTP_200_OK,
    summary="Revoke all refresh tokens for current user (logout all devices)",
)
async def logout_all(
    current_user: CurrentUser,
    service: Annotated[AuthDomainService, Depends(_get_service)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    await service.logout_all(current_user.sub)
    body = MessageResponse(message="Logged out from all devices").model_dump()
    response = JSONResponse(content=body, status_code=200)
    _clear_refresh_cookie(response, settings)
    return response


@router.post(
    "/mfa/setup",
    response_model=SuccessResponse[MFASetupResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate MFA TOTP secret and QR code",
)
async def setup_mfa(
    current_user: CurrentUser,
    service: Annotated[AuthDomainService, Depends(_get_service)],
) -> SuccessResponse[MFASetupResponse]:
    result = await service.setup_mfa(current_user.sub)
    return SuccessResponse.of(MFASetupResponse(**result))


@router.post(
    "/mfa/verify",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify TOTP code and enable MFA",
)
async def verify_mfa(
    payload: MFAVerifyRequest,
    current_user: CurrentUser,
    service: Annotated[AuthDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.verify_and_enable_mfa(current_user.sub, payload.code)
    return MessageResponse(message="MFA enabled successfully")


@router.post(
    "/mfa/disable",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Disable MFA (requires password confirmation)",
)
async def disable_mfa(
    payload: MFADisableRequest,
    current_user: CurrentUser,
    service: Annotated[AuthDomainService, Depends(_get_service)],
) -> MessageResponse:
    await service.disable_mfa(current_user.sub, payload.password)
    return MessageResponse(message="MFA disabled successfully")


@router.post(
    "/bootstrap/tenant-admin",
    response_model=SuccessResponse[BootstrapTenantAdminResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Provision platform user for tenant admin (super_admin only)",
)
async def bootstrap_tenant_admin(
    payload: BootstrapTenantAdminRequest,
    _: Annotated[CurrentUser, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse[BootstrapTenantAdminResponse]:
    if payload.role not in ("tenant_admin", "tenant_user"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "VALIDATION_ERROR", "message": "Unsupported role for bootstrap"},
        )

    row = await db.execute(
        select(Tenant).where(Tenant.id == payload.tenant_id, Tenant.deleted_at.is_(None))
    )
    tenant = row.scalar_one_or_none()
    if not tenant:
        raise NotFoundError("Tenant", payload.tenant_id)

    repo = UserRepository(db)
    if await repo.get_by_email(payload.email):
        raise ConflictError("Email already registered")

    temporary_password = generate_temporary_password()
    user = await repo.create(
        email=payload.email,
        password_hash=hash_password(temporary_password),
        tenant_id=payload.tenant_id,
        role=payload.role,
    )
    logger.info(
        "tenant_admin_bootstrapped",
        tenant_id=payload.tenant_id,
        platform_user_id=user.id,
    )
    return SuccessResponse.of(
        BootstrapTenantAdminResponse(
            platform_user_id=user.id,
            temporary_password=temporary_password,
        )
    )


@router.post(
    "/tenants/{tenant_id}/tenant-admin/resend-welcome-credentials",
    response_model=SuccessResponse[ResendTenantAdminWelcomeResponse],
    status_code=status.HTTP_200_OK,
    summary="Reset tenant admin password and return credentials for resending welcome email (super_admin only)",
)
async def resend_tenant_admin_welcome_credentials(
    tenant_id: str,
    _: Annotated[CurrentUser, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SuccessResponse[ResendTenantAdminWelcomeResponse]:
    row = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id, Tenant.deleted_at.is_(None))
    )
    tenant = row.scalar_one_or_none()
    if not tenant:
        raise NotFoundError("Tenant", tenant_id)

    user_repo = UserRepository(db)
    refresh_repo = RefreshTokenRepository(db)
    user = await user_repo.get_tenant_admin_for_tenant(tenant_id)
    if not user:
        raise NotFoundError("Tenant admin user", tenant_id)

    temporary_password = generate_temporary_password()
    await user_repo.update_password(user.id, hash_password(temporary_password))
    await refresh_repo.revoke_all_for_user(user.id)
    await db.commit()

    logger.info(
        "tenant_admin_welcome_credentials_reset",
        tenant_id=tenant_id,
        platform_user_id=user.id,
    )

    return SuccessResponse.of(
        ResendTenantAdminWelcomeResponse(
            platform_user_id=user.id,
            temporary_password=temporary_password,
            admin_email=user.email,
        )
    )


@router.post(
    "/access-keys",
    response_model=SuccessResponse[AccessKeyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create service-to-service access key (super_admin only)",
)
async def create_access_key(
    payload: CreateAccessKeyRequest,
    current_user: CurrentUser,
    service: Annotated[AuthDomainService, Depends(_get_service)],
) -> SuccessResponse[AccessKeyResponse]:
    if current_user.role != "super_admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Super admin required"})
    result = await service.create_access_key(
        service_name=payload.service_name,
        scopes=payload.scopes,
        expires_at=payload.expires_at,
    )
    return SuccessResponse.of(AccessKeyResponse(**result))


@router.delete(
    "/access-keys/{key_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke a service access key",
)
async def revoke_access_key(
    key_id: str,
    current_user: CurrentUser,
    service: Annotated[AuthDomainService, Depends(_get_service)],
) -> MessageResponse:
    if current_user.role != "super_admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Super admin required"})
    await service.revoke_access_key(key_id)
    return MessageResponse(message="Access key revoked")
