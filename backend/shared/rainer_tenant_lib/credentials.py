"""Rainer Tenant Lib — Derived credential generation for tenant DBs."""

import hashlib
import hmac
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class TenantCredentials:
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def sync_dsn(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


def derive_tenant_password(tenant_id: str, master_secret: str | None = None) -> str:
    """
    Derive a deterministic tenant DB password using HMAC-SHA256.
    The password is NEVER stored — it's always derived on the fly.

    Security:
    - master_secret should be a high-entropy secret from Vault/env
    - The derived password is 64-char hex string
    - Same tenant_id + master_secret always produces same password
    """
    secret = master_secret or os.environ.get("RAINER_MASTER_SECRET", "dev-master-secret")
    mac = hmac.new(
        secret.encode("utf-8"),
        tenant_id.encode("utf-8"),
        hashlib.sha256,
    )
    return mac.hexdigest()
