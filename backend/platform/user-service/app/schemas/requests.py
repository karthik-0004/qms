"""User Service — Pydantic request schemas."""

from pydantic import BaseModel, EmailStr, Field, model_validator


class CreateUserRequest(BaseModel):
    """Create a tenant user profile.

    Two modes:
    - **Bootstrap mode**: omit `platform_user_id`, supply `email` — auth account is
      created automatically and a welcome email is sent with the temporary password.
    - **Pre-provisioned mode**: supply `platform_user_id` (used by internal services
      such as tenant-service that already created the auth account).
    """
    platform_user_id: str | None = None
    email: EmailStr | None = Field(
        default=None,
        description="Required when platform_user_id is omitted (bootstrap mode)",
    )
    tenant_id: str | None = Field(
        default=None,
        description="Target tenant (super_admin provisioning only; otherwise ignored)",
    )
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    display_name: str | None = None
    phone: str | None = None
    department: str | None = None
    job_title: str | None = None

    @model_validator(mode="after")
    def _check_id_or_email(self) -> "CreateUserRequest":
        if not self.platform_user_id and not self.email:
            raise ValueError("Either platform_user_id or email must be provided")
        return self


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
    scope: str = Field(default="tenant", pattern="^(tenant|company)$")
    company_id: str | None = None


class UpdateRoleRequest(BaseModel):
    permissions: list[str] | None = None
    description: str | None = None


class AssignRoleRequest(BaseModel):
    role_id: str


# ── Company schemas ───────────────────────────────────────────────────────────

class CompanyAdminRequest(BaseModel):
    """Details of the admin user — auth account is created automatically."""
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: str | None = None


class CreateCompanyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str | None = None
    address: str | None = None
    company_code: str | None = Field(
        default=None,
        description="Short code for the company (auto-derived from name if omitted)",
        max_length=50,
    )
    employee_limit: int = Field(default=10, ge=1, le=10000)
    admin: CompanyAdminRequest


class UpdateCompanyRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    employee_limit: int | None = Field(default=None, ge=1, le=10000)


class CreateCompanyUserRequest(BaseModel):
    """Create a user scoped to a company — auth account is created automatically."""
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    display_name: str | None = None
    phone: str | None = None
    department: str | None = None
    role_id: str | None = Field(
        default=None,
        description="Optional company-scoped role to assign on creation",
    )
