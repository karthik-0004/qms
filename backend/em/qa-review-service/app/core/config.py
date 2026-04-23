"""QA Review Service — Application configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    service_name: str = "qa-review-service"
    service_version: str = "0.1.0"
    rainer_env: str = "development"
    port: int = 8034
    log_level: str = "INFO"
    json_logs: bool = True

    database_url: str = "postgresql+asyncpg://rainer:rainer_dev_password@localhost:5432/rainer_master"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "qa-review-service"

    rainer_master_secret: str = "dev-master-secret-change-in-production"
    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    plate_service_url: str = "http://plate-service:8030"
    ai_service_url: str = "http://ai-service:8032"
    notification_service_url: str = "http://notification-service:8005"
    audit_service_url: str = "http://audit-service:8004"


@lru_cache
def get_settings() -> Settings:
    return Settings()
