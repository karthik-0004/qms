"""Image Service — Application configuration."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    service_name: str = "image-service"
    service_version: str = "0.1.0"
    rainer_env: str = "development"
    port: int = 8031
    log_level: str = "INFO"
    json_logs: bool = True

    database_url: str = "postgresql+asyncpg://rainer:rainer_dev_password@localhost:5432/rainer_master"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_group_id: str = "image-service"

    rainer_master_secret: str = "dev-master-secret-change-in-production"
    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    # S3/MinIO for image storage
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key_id: str = "rainer_minio"
    s3_secret_access_key: str = "rainer_minio_dev_secret"
    s3_images_bucket: str = "rainer-em-images"
    s3_presigned_url_expiry: int = 3600  # seconds

    # Max image file size (MB)
    max_image_size_mb: int = 100

    plate_service_url: str = "http://plate-service:8030"


@lru_cache
def get_settings() -> Settings:
    return Settings()
