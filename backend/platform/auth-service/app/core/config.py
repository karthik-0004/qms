"""Auth Service — Application configuration via Pydantic Settings."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service
    service_name: str = "auth-service"
    service_version: str = "0.1.0"
    rainer_env: str = "development"
    port: int = 8001
    debug: bool = False

    # Logging
    log_level: str = "INFO"
    json_logs: bool = True

    # Database (Master DB)
    database_url: str = "postgresql+asyncpg://rainer:rainer_dev_password@localhost:5432/rainer_master"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_recycle: int = 3600
    db_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_pool_size: int = 10

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "auth-service"

    # JWT
    jwt_secret_key: str = "dev-secret-change-in-production-min-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # MFA
    mfa_issuer_name: str = "Rainer Platform"
    mfa_totp_digits: int = 6
    mfa_totp_interval: int = 30

    # Security
    rainer_master_secret: str = "dev-master-secret-change-in-production"
    max_failed_login_attempts: int = 5
    account_lockout_minutes: int = 30
    password_reset_expire_minutes: int = 60

    # Cookie (Refresh Token)
    cookie_domain: str | None = None  # None allows browser to set automatically
    cookie_secure: bool = False  # True in production (HTTPS)
    cookie_samesite: str = "lax"
    cookie_path: str = "/"
    refresh_token_cookie_name: str = "rainer_refresh_token"

    # CORS
    cors_allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8001", "*"]
    cors_allow_credentials: bool = True

    # Observability
    otlp_endpoint: str = "http://jaeger:4317"
    enable_tracing: bool = True

    @field_validator("rainer_env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "testing", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"rainer_env must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        return self.rainer_env == "production"

    @property
    def is_testing(self) -> bool:
        return self.rainer_env == "testing"


@lru_cache
def get_settings() -> Settings:
    return Settings()
