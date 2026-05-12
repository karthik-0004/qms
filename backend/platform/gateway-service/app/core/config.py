"""Gateway Service — Application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve `.env` next to this service (not process cwd) so `uvicorn` from repo root still loads
# `backend/platform/gateway-service/.env` on Windows/macOS hybrid dev.
_GATEWAY_SERVICE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_GATEWAY_SERVICE_DIR / ".env",
        case_sensitive=False,
        extra="ignore",
    )

    service_name: str = "gateway-service"
    service_version: str = "0.1.0"
    rainer_env: str = "development"
    port: int = 8000
    log_level: str = "INFO"
    json_logs: bool = True

    # Upstream services
    auth_service_url: str = "http://localhost:8001"
    tenant_service_url: str = "http://localhost:8002"
    user_service_url: str = "http://user-service:8003"
    audit_service_url: str = "http://audit-service:8004"
    notification_service_url: str = "http://notification-service:8005"
    document_service_url: str = "http://document-service:8020"
    crm_service_url: str = "http://crm-service:8040"
    contract_service_url: str = "http://contract-service:8041"
    workorder_service_url: str = "http://workorder-service:8042"
    technician_service_url: str = "http://technician-service:8043"
    billing_service_url: str = "http://billing-service:8044"

    # JWT settings (for validation)
    jwt_secret_key: str = "dev-jwt-secret-change-in-production-min-32-chars"
    jwt_algorithm: str = "HS256"

    # Rate limiting
    rate_limit_per_minute: int = 100
    rate_limit_per_minute_unauthenticated: int = 20

    # Redis for rate limiting
    redis_url: str = "redis://localhost:6379/0"

    rainer_master_secret: str = "dev-master-secret-change-in-production"
    # Comma-separated list (also settable via env CORS_ALLOWED_ORIGINS) — required when the
    # web app is served from another host or LAN IP (see .env.example).
    cors_allowed_origins: str = "http://localhost:3000,http://localhost:3001"

    def cors_origins_as_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
