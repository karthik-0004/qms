"""Analytics Service — Application configuration."""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    service_name: str = "analytics-service"
    service_version: str = "0.1.0"
    rainer_env: str = "development"
    port: int = 8011
    log_level: str = "INFO"
    json_logs: bool = True

    database_url: str = "postgresql+asyncpg://rainer:rainer_dev_password@localhost:5432/rainer_master"
    db_pool_size: int = 5
    db_max_overflow: int = 10

    redis_url: str = "redis://localhost:6379/0"
    rainer_master_secret: str = "dev-master-secret-change-in-production"
    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    # JWT — same as other services
    jwt_secret_key: str = "dev-jwt-secret-change-in-production-min-32-chars"
    jwt_algorithm: str = "HS256"


def ensure_jwt_environment() -> None:
    """Expose JWT to os.environ so rainer_auth_lib.JWTSettings() works correctly.

    rainer_auth_lib only reads OS env for JWT (not analytics-service .env). Must run before any import
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
