from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "workorder-service"
    service_version: str = "0.1.0"
    port: int = 8042
    log_level: str = "INFO"
    json_logs: bool = True
    rainer_env: str = "development"

    database_url: str = "postgresql+asyncpg://rainer:rainer@localhost:5432/rainer_master"
    rainer_master_secret: str = "dev-master-secret"

    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"

    technician_service_url: str = "http://localhost:8043"

    allowed_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
