"""Notification Service — Application configuration."""

from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    service_name: str = "notification-service"
    service_version: str = "0.1.0"
    rainer_env: str = "development"
    port: int = 8005
    log_level: str = "INFO"
    json_logs: bool = True

    database_url: str = "postgresql+asyncpg://rainer:rainer_dev_password@localhost:5432/rainer_master"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "notification-service"

    # Email (SMTP) — notification-service sends tenant welcome / system mail here.
    # Port 465: set smtp_use_tls=true, smtp_start_tls=false.
    # Port 587 (most providers): set smtp_use_tls=false, smtp_start_tls=true.
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_use_tls: bool = False
    smtp_start_tls: bool = False
    smtp_username: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SMTP_USERNAME", "SMTP_USER"),
    )
    smtp_password: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SMTP_PASSWORD", "SMTP_PASS"),
    )
    smtp_from_email: str = Field(
        default="noreply@rainer.io",
        validation_alias=AliasChoices("SMTP_FROM_EMAIL", "SMTP_FROM"),
    )
    smtp_from_name: str = "Rainer Platform"

    rainer_master_secret: str = "dev-master-secret-change-in-production"

    @field_validator("smtp_password", mode="before")
    @classmethod
    def normalize_smtp_password(cls, v: object) -> str | None:
        """Gmail app passwords are 16 chars; pasted 'aaaa bbbb cccc dddd' must be contiguous."""
        if v is None:
            return None
        if not isinstance(v, str):
            return None
        s = v.replace(" ", "").strip()
        return s if s else None
    cors_allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
