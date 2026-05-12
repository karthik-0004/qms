"""User Service — Pydantic response schemas."""

from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    platform_user_id: str
    tenant_id: str
    company_id: str | None
    first_name: str
    last_name: str
    display_name: str | None
    phone: str | None
    department: str | None
    job_title: str | None
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RoleResponse(BaseModel):
    id: str
    name: str
    description: str | None
    permissions: list[str]
    is_system_role: bool
    product: str | None
    scope: str
    company_id: str | None
    created_at: datetime
    updated_at: datetime


class UserRoleResponse(BaseModel):
    id: str
    user_id: str
    role_id: str
    granted_by: str | None
    granted_at: datetime
    expires_at: datetime | None


class UserPermissionsResponse(BaseModel):
    user_id: str
    permissions: list[str]


class CompanyResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: str
    phone: str | None
    address: str | None
    company_code: str
    status: str
    admin_id: str | None
    employee_limit: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CompanyWithAdminResponse(BaseModel):
    company: CompanyResponse
    admin: UserResponse
    temporary_password: str


class CompanyUserCreatedResponse(BaseModel):
    user: UserResponse
    temporary_password: str
