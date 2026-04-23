"""SCIM 2.0 Routes — RFC 7644 compliant endpoints for user provisioning."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_db
from ...domain.services import UserDomainService
from ...infra.db.repositories import RoleRepository, UserRepository, UserRoleRepository

from .schemas import (
    SCIMErrorResponse,
    SCIMGroupMember,
    SCIMGroupResource,
    SCIMListResponse,
    SCIMMeta,
    SCIMPatchRequest,
    SCIMResourceType,
    SCIMServiceProviderConfig,
    SCIMUserResource,
)

router = APIRouter(tags=["SCIM 2.0"])
logger = structlog.get_logger(__name__)

SCIM_CONTENT_TYPE = "application/scim+json"


# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserDomainService:
    return UserDomainService(
        user_repo=UserRepository(db),
        role_repo=RoleRepository(db),
        user_role_repo=UserRoleRepository(db),
    )


def _user_to_scim(user, request: Request) -> dict:
    """Convert internal User model to SCIM User resource dict."""
    base_url = str(request.base_url).rstrip("/")
    return SCIMUserResource(
        id=user.id,
        externalId=user.platform_user_id,
        userName=user.platform_user_id,
        displayName=user.display_name or f"{user.first_name} {user.last_name}",
        name={
            "givenName": user.first_name,
            "familyName": user.last_name,
            "formatted": f"{user.first_name} {user.last_name}",
        },
        emails=[{"value": user.platform_user_id, "type": "work", "primary": True}],
        phoneNumbers=[{"value": user.phone, "type": "work"}] if user.phone else [],
        active=user.is_active,
        title=user.job_title,
        department=user.department,
        meta=SCIMMeta(
            resourceType="User",
            created=user.created_at,
            lastModified=user.updated_at,
            location=f"{base_url}/scim/v2/Users/{user.id}",
        ),
    ).model_dump(by_alias=True, exclude_none=True)


def _role_to_scim_group(role, request: Request) -> dict:
    """Convert internal Role model to SCIM Group resource dict."""
    base_url = str(request.base_url).rstrip("/")
    return SCIMGroupResource(
        id=role.id,
        displayName=role.name,
        meta=SCIMMeta(
            resourceType="Group",
            created=role.created_at,
            lastModified=role.updated_at,
            location=f"{base_url}/scim/v2/Groups/{role.id}",
        ),
    ).model_dump(by_alias=True, exclude_none=True)


def _parse_scim_filter(filter_str: str | None) -> dict:
    """Parse simple SCIM filter like 'userName eq "john"' into field+value."""
    if not filter_str:
        return {}
    match = re.match(r'(\w+)\s+eq\s+"([^"]*)"', filter_str.strip())
    if match:
        return {"field": match.group(1), "value": match.group(2)}
    return {}


def _scim_error(status_code: int, detail: str, scim_type: str | None = None):
    raise HTTPException(
        status_code=status_code,
        detail=SCIMErrorResponse(
            detail=detail,
            status=str(status_code),
            scimType=scim_type,
        ).model_dump(),
    )


# ── ServiceProviderConfig ───────────────────────────────────────────────────

@router.get("/ServiceProviderConfig")
async def get_service_provider_config() -> SCIMServiceProviderConfig:
    return SCIMServiceProviderConfig()


# ── ResourceTypes ────────────────────────────────────────────────────────────

@router.get("/ResourceTypes")
async def get_resource_types(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return [
        SCIMResourceType(
            id="User",
            name="User",
            description="User Account",
            endpoint="/scim/v2/Users",
            schema_="urn:ietf:params:scim:schemas:core:2.0:User",
            meta=SCIMMeta(
                resourceType="ResourceType",
                location=f"{base_url}/scim/v2/ResourceTypes/User",
            ),
        ).model_dump(by_alias=True, exclude_none=True),
        SCIMResourceType(
            id="Group",
            name="Group",
            description="Group (Role)",
            endpoint="/scim/v2/Groups",
            schema_="urn:ietf:params:scim:schemas:core:2.0:Group",
            meta=SCIMMeta(
                resourceType="ResourceType",
                location=f"{base_url}/scim/v2/ResourceTypes/Group",
            ),
        ).model_dump(by_alias=True, exclude_none=True),
    ]


# ── Users ────────────────────────────────────────────────────────────────────

@router.get("/Users")
async def list_users(
    request: Request,
    service: Annotated[UserDomainService, Depends(_get_service)],
    filter: str | None = Query(default=None),
    startIndex: int = Query(default=1, ge=1),
    count: int = Query(default=20, ge=1, le=200),
):
    """SCIM 2.0 — List or filter users."""
    parsed = _parse_scim_filter(filter)
    page = max(1, (startIndex - 1) // count + 1)

    users, total = await service.list_users(page=page, page_size=count)
    resources = [_user_to_scim(u, request) for u in users]

    return SCIMListResponse(
        totalResults=total,
        startIndex=startIndex,
        itemsPerPage=count,
        Resources=resources,
    ).model_dump(exclude_none=True)


@router.get("/Users/{user_id}")
async def get_user(
    user_id: str,
    request: Request,
    service: Annotated[UserDomainService, Depends(_get_service)],
):
    """SCIM 2.0 — Get a single user by ID."""
    try:
        user = await service.get_user(user_id)
    except Exception:
        _scim_error(404, f"User {user_id} not found", "invalidValue")
    return _user_to_scim(user, request)


@router.post("/Users", status_code=201)
async def create_user(
    payload: SCIMUserResource,
    request: Request,
    service: Annotated[UserDomainService, Depends(_get_service)],
):
    """SCIM 2.0 — Provision a new user."""
    if not payload.userName:
        _scim_error(400, "userName is required", "invalidValue")

    first_name = payload.name.givenName if payload.name else "Unknown"
    last_name = payload.name.familyName if payload.name else "User"

    try:
        user = await service.create_user(
            platform_user_id=payload.externalId or payload.userName,
            tenant_id=payload.externalId or str(uuid.uuid4()),
            first_name=first_name or "Unknown",
            last_name=last_name or "User",
            display_name=payload.displayName,
            phone=payload.phoneNumbers[0].value if payload.phoneNumbers else None,
            department=payload.department,
            job_title=payload.title,
        )
    except Exception as exc:
        if "already exists" in str(exc).lower() or "conflict" in str(exc).lower():
            _scim_error(409, "User already exists", "uniqueness")
        raise

    logger.info("scim_user_provisioned", user_id=user.id, userName=payload.userName)
    return _user_to_scim(user, request)


@router.put("/Users/{user_id}")
async def replace_user(
    user_id: str,
    payload: SCIMUserResource,
    request: Request,
    service: Annotated[UserDomainService, Depends(_get_service)],
):
    """SCIM 2.0 — Full replacement of user attributes."""
    try:
        await service.get_user(user_id)
    except Exception:
        _scim_error(404, f"User {user_id} not found", "invalidValue")

    first_name = payload.name.givenName if payload.name else None
    last_name = payload.name.familyName if payload.name else None
    update_fields = {}
    if first_name:
        update_fields["first_name"] = first_name
    if last_name:
        update_fields["last_name"] = last_name
    if payload.displayName is not None:
        update_fields["display_name"] = payload.displayName
    if payload.department is not None:
        update_fields["department"] = payload.department
    if payload.title is not None:
        update_fields["job_title"] = payload.title
    if payload.phoneNumbers:
        update_fields["phone"] = payload.phoneNumbers[0].value

    if update_fields:
        user = await service.update_user(user_id, **update_fields)
    else:
        user = await service.get_user(user_id)

    if not payload.active:
        await service.deactivate_user(user_id)
        user = await service.get_user(user_id)

    logger.info("scim_user_replaced", user_id=user_id)
    return _user_to_scim(user, request)


@router.patch("/Users/{user_id}")
async def patch_user(
    user_id: str,
    payload: SCIMPatchRequest,
    request: Request,
    service: Annotated[UserDomainService, Depends(_get_service)],
):
    """SCIM 2.0 — Partial update using PATCH operations."""
    try:
        await service.get_user(user_id)
    except Exception:
        _scim_error(404, f"User {user_id} not found", "invalidValue")

    update_fields: dict = {}
    for op in payload.Operations:
        if op.op not in ("replace", "add"):
            continue

        if op.path == "name.givenName":
            update_fields["first_name"] = op.value
        elif op.path == "name.familyName":
            update_fields["last_name"] = op.value
        elif op.path == "displayName":
            update_fields["display_name"] = op.value
        elif op.path == "title":
            update_fields["job_title"] = op.value
        elif op.path == "department":
            update_fields["department"] = op.value
        elif op.path == "active":
            if op.value is False or op.value == "false":
                await service.deactivate_user(user_id)
        elif op.path == "phoneNumbers":
            if isinstance(op.value, list) and len(op.value) > 0:
                phone_val = op.value[0]
                if isinstance(phone_val, dict):
                    update_fields["phone"] = phone_val.get("value", "")
                else:
                    update_fields["phone"] = str(phone_val)

    if update_fields:
        await service.update_user(user_id, **update_fields)

    user = await service.get_user(user_id)
    logger.info("scim_user_patched", user_id=user_id, operations=len(payload.Operations))
    return _user_to_scim(user, request)


@router.delete("/Users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    service: Annotated[UserDomainService, Depends(_get_service)],
):
    """SCIM 2.0 — Deprovision (deactivate) a user."""
    try:
        await service.deactivate_user(user_id)
    except Exception:
        _scim_error(404, f"User {user_id} not found", "invalidValue")
    logger.info("scim_user_deprovisioned", user_id=user_id)


# ── Groups ───────────────────────────────────────────────────────────────────

@router.get("/Groups")
async def list_groups(
    request: Request,
    service: Annotated[UserDomainService, Depends(_get_service)],
    filter: str | None = Query(default=None),
    startIndex: int = Query(default=1, ge=1),
    count: int = Query(default=20, ge=1, le=200),
):
    """SCIM 2.0 — List groups (mapped to Rainer roles)."""
    roles = await service.list_roles()
    resources = [_role_to_scim_group(r, request) for r in roles]
    total = len(resources)

    start = max(0, startIndex - 1)
    end = start + count
    page_resources = resources[start:end]

    return SCIMListResponse(
        totalResults=total,
        startIndex=startIndex,
        itemsPerPage=count,
        Resources=page_resources,
    ).model_dump(exclude_none=True)


@router.get("/Groups/{group_id}")
async def get_group(
    group_id: str,
    request: Request,
    service: Annotated[UserDomainService, Depends(_get_service)],
):
    """SCIM 2.0 — Get a single group (role) by ID."""
    roles = await service.list_roles()
    for role in roles:
        if role.id == group_id:
            return _role_to_scim_group(role, request)
    _scim_error(404, f"Group {group_id} not found", "invalidValue")


@router.patch("/Groups/{group_id}")
async def patch_group(
    group_id: str,
    payload: SCIMPatchRequest,
    request: Request,
    service: Annotated[UserDomainService, Depends(_get_service)],
):
    """SCIM 2.0 — Patch group membership (add/remove users from a role)."""
    roles = await service.list_roles()
    target_role = None
    for role in roles:
        if role.id == group_id:
            target_role = role
            break
    if not target_role:
        _scim_error(404, f"Group {group_id} not found", "invalidValue")

    for op in payload.Operations:
        members = op.value if isinstance(op.value, list) else [op.value] if op.value else []

        if op.op == "add" and op.path == "members":
            for member in members:
                member_id = member.get("value") if isinstance(member, dict) else str(member)
                if member_id:
                    try:
                        await service.assign_role(member_id, group_id, granted_by=None)
                        logger.info("scim_group_member_added", group_id=group_id, user_id=member_id)
                    except Exception:
                        pass

        elif op.op == "remove" and op.path == "members":
            for member in members:
                member_id = member.get("value") if isinstance(member, dict) else str(member)
                if member_id:
                    try:
                        await service.remove_role(member_id, group_id)
                        logger.info("scim_group_member_removed", group_id=group_id, user_id=member_id)
                    except Exception:
                        pass

    return _role_to_scim_group(target_role, request)
