"""Rainer Tenant Lib — Per-request tenant context management using contextvars."""

import contextvars
from dataclasses import dataclass


@dataclass
class TenantContext:
    tenant_id: str
    db_name: str | None = None
    db_host: str | None = None
    db_port: int = 5432


_tenant_context_var: contextvars.ContextVar[TenantContext | None] = contextvars.ContextVar(
    "tenant_context",
    default=None,
)


def get_tenant_context() -> TenantContext | None:
    """Get the current request's tenant context."""
    return _tenant_context_var.get()


def set_tenant_context(ctx: TenantContext) -> contextvars.Token:
    """Set tenant context for the current request. Returns token for cleanup."""
    return _tenant_context_var.set(ctx)


def clear_tenant_context(token: contextvars.Token) -> None:
    """Reset tenant context after request completes."""
    _tenant_context_var.reset(token)


def require_tenant_context() -> TenantContext:
    """Get tenant context or raise if not set."""
    ctx = get_tenant_context()
    if ctx is None:
        from rainer_common.exceptions import TenantNotFoundError

        raise TenantNotFoundError()
    return ctx

