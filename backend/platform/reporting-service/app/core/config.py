"""Reporting Service — Application configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    service_name: str = "reporting-service"
    service_version: str = "0.1.0"
    rainer_env: str = "development"
    port: int = 8010
    log_level: str = "INFO"
    json_logs: bool = True

    database_url: str = "postgresql+asyncpg://rainer:rainer_dev_password@localhost:5432/rainer_master"
    db_pool_size: int = 5
    db_max_overflow: int = 10

    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"

    # S3 for report storage
    s3_endpoint_url: str | None = None
    s3_access_key_id: str = "rainer_minio"
    s3_secret_access_key: str = "rainer_minio_dev_secret"
    s3_reports_bucket: str = "rainer-reports"

    rainer_master_secret: str = "dev-master-secret-change-in-production"
    cors_allowed_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
