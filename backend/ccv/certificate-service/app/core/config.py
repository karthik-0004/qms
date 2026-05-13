from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    rainer_env: str = "development"
    service_name: str = "certificate-service"
    service_version: str = "0.1.0"
    port: int = 8045
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Database
    database_url: str = "sqlite+aiosqlite://././certificates.db"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
