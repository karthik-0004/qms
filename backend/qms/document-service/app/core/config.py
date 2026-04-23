"""Document Service — Application configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    service_name: str = "document-service"
    service_version: str = "0.1.0"
    rainer_env: str = "development"
    port: int = 8020
    log_level: str = "INFO"
    json_logs: bool = True

    database_url: str = "postgresql+asyncpg://rainer:rainer_dev_password@localhost:5432/rainer_master"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "document-service"

    rainer_master_secret: str = "dev-master-secret-change-in-production"
    workflow_service_url: str = "http://workflow-engine:8007"
    file_service_url: str = "http://file-service:8009"
    notification_service_url: str = "http://notification-service:8005"
    audit_service_url: str = "http://audit-service:8004"

    # Document lifecycle settings
    periodic_review_days_warning: int = 30
    max_document_versions: int = 100

    cors_allowed_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
