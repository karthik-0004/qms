"""File Service — Application configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    service_name: str = "file-service"
    service_version: str = "0.1.0"
    rainer_env: str = "development"
    port: int = 8009
    log_level: str = "INFO"
    json_logs: bool = True

    database_url: str = "postgresql+asyncpg://rainer:rainer_dev_password@localhost:5432/rainer_master"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"

    # S3 / MinIO
    s3_endpoint_url: str | None = None
    s3_access_key_id: str = "rainer_minio"
    s3_secret_access_key: str = "rainer_minio_dev_secret"
    s3_bucket_name: str = "rainer-files"
    s3_region: str = "us-east-1"
    s3_use_ssl: bool = False
    max_file_size_mb: int = 100
    allowed_mime_types: list[str] = [
        "application/pdf",
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain", "text/csv",
    ]

    # ClamAV virus scanning
    clamav_host: str = "localhost"
    clamav_port: int = 3310
    enable_virus_scan: bool = False  # Disabled by default in dev

    rainer_master_secret: str = "dev-master-secret-change-in-production"
    cors_allowed_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
