"""Tenant Service — Application configuration."""

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    service_name: str = "tenant-service"
    service_version: str = "0.1.0"
    rainer_env: str = "development"
    port: int = 8002
    debug: bool = False
    log_level: str = "INFO"
    json_logs: bool = True

    database_url: str = "postgresql+asyncpg://rainer:rainer_dev_password@localhost:5432/rainer_master"
    postgres_admin_url: str = "postgresql://rainer:rainer_dev_password@localhost:5432/postgres"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "tenant-service"

    rainer_master_secret: str = "dev-master-secret-change-in-production"

    # JWT settings (for validation)
    jwt_secret_key: str = "dev-jwt-secret-change-in-production-min-32-chars"
    jwt_algorithm: str = "HS256"

    default_tenant_db_host: str = "postgres"
    default_tenant_db_port: int = 5432

    # In docker-compose these resolve via service DNS.
    # Local dev can still override via env to point at localhost ports.
    auth_service_url: str = "http://localhost:8001"
    user_service_url: str = "http://localhost:8003"
    notification_service_url: str = "http://localhost:8005"
    public_web_login_url: str = "http://localhost:3000/login"

    cors_allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    @property
    def is_testing(self) -> bool:
        return self.rainer_env == "testing"


def ensure_jwt_environment() -> None:
    """Expose JWT to os.environ so rainer_auth_lib.JWTSettings() works correctly.

    rainer_auth_lib only reads OS env for JWT (not tenant-service .env). Must run before any import
    that triggers get_settings()/database setup if JWT_* is only defined in .env.
    """
    s = Settings()
    if not os.environ.get("JWT_SECRET_KEY", "").strip():
        os.environ["JWT_SECRET_KEY"] = s.jwt_secret_key
    if not os.environ.get("JWT_ALGORITHM", "").strip():
        os.environ["JWT_ALGORITHM"] = s.jwt_algorithm


@lru_cache
def get_settings() -> Settings:
    return Settings()
