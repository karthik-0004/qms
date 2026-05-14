"""Auth Service — Application configuration via Pydantic Settings."""

import os
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

    # JWT — same as gateway and user-service for consistency
    jwt_secret_key: str = "dev-jwt-secret-change-in-production-min-32-chars"
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
    # NOTE: When `cors_allow_credentials=True`, wildcard origins ("*") are invalid in browsers.
    # Keep this list explicit and override via env (`CORS_ALLOWED_ORIGINS`) when needed.
    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8001",
    ]
    cors_allow_credentials: bool = True

    # Observability
    otlp_endpoint: str = "http://jaeger:4317"
    enable_tracing: bool = True
    enable_perf_logs: bool = False

    # Validation
    # If true (recommended only for development/testing), allow reserved/special-use
    # email domains (e.g. ".local") during request validation.
    allow_reserved_email_domains: bool = False

    @field_validator("rainer_env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "testing", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"rainer_env must be one of {allowed}")
        return v

    @field_validator("cors_allowed_origins")
    @classmethod
    def normalize_cors_allowed_origins(cls, v: list[str]) -> list[str]:
        # Normalize, de-dupe, and strip trailing slashes so origins match browser `Origin` header.
        normalized: list[str] = []
        seen: set[str] = set()
        for origin in v:
            origin_value = (origin or "").strip()
            if not origin_value:
                continue
            origin_value = origin_value.rstrip("/")
            if origin_value not in seen:
                normalized.append(origin_value)
                seen.add(origin_value)
        return normalized

    @field_validator("cors_allow_credentials")
    @classmethod
    def validate_cors_credentials_with_origins(cls, allow_credentials: bool, info):
        # If credentials are allowed, "*" cannot be used as an allowed origin.
        cors_allowed_origins = info.data.get("cors_allowed_origins") or []
        if allow_credentials and "*" in cors_allowed_origins:
            raise ValueError(
                "Invalid CORS config: cors_allow_credentials=true cannot be used with '*' in cors_allowed_origins"
            )
        return allow_credentials

    @property
    def is_production(self) -> bool:
        return self.rainer_env == "production"

    @property
    def is_testing(self) -> bool:
        return self.rainer_env == "testing"


def ensure_jwt_environment() -> None:
    """Expose JWT to os.environ so rainer_auth_lib.JWTSettings() works correctly.

    rainer_auth_lib only reads OS env for JWT (not auth-service .env). Must run before any import
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
