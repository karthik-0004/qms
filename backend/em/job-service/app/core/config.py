"""Job Service — Application configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    service_name: str = "job-service"
    service_version: str = "0.1.0"
    rainer_env: str = "development"
    port: int = 8033
    log_level: str = "INFO"
    json_logs: bool = True

    database_url: str = "postgresql+asyncpg://rainer:rainer_dev_password@localhost:5432/rainer_master"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "job-service"

    rainer_master_secret: str = "dev-master-secret-change-in-production"
    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    # Job execution settings
    max_retry_attempts: int = 3
    retry_backoff_seconds: int = 60
    job_timeout_seconds: int = 600
    worker_concurrency: int = 4
    dispatcher_interval_seconds: int = 5

    ai_service_url: str = "http://ai-service:8032"
    plate_service_url: str = "http://plate-service:8030"


@lru_cache
def get_settings() -> Settings:
    return Settings()
