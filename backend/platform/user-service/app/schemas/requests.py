"""User Service — Pydantic request schemas."""

from pydantic import BaseModel, EmailStr, Field


class CreateUserRequest(BaseModel):
    platform_user_id: str
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    display_name: str | None = None
    phone: str | None = None
    department: str | None = None
    job_title: str | None = None


class UpdateUserRequest(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    display_name: str | None = None
    phone: str | None = None
    department: str | None = None
    job_title: str | None = None


class CreateRoleRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    permissions: list[str] = Field(default_factory=list)
    description: str | None = None
    product: str | None = None


class UpdateRoleRequest(BaseModel):
    permissions: list[str] | None = None
    description: str | None = None


class AssignRoleRequest(BaseModel):
    role_id: str
