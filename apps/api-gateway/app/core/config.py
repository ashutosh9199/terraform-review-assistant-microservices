from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Terraform Review Assistant"
    environment: str = "local"
    database_url: str = "sqlite:///./data/review-assistant.db"
    jwt_secret_key: str = "local-dev-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    cors_origins: str = "http://localhost:5173"
    max_upload_mb: int = 50
    storage_backend: str = "local"
    local_storage_path: Path = Path("./data/storage")
    azure_storage_connection_string: str | None = None
    azure_storage_container: str = "terraform-projects"
    key_vault_url: str | None = None
    fernet_key: str | None = Field(default=None)

    # Downstream microservice URLs. Defaults target local uvicorn ports;
    # docker-compose overrides them with service DNS names.
    upload_service_url: str = "http://localhost:8001"
    parser_service_url: str = "http://localhost:8002"
    rules_service_url: str = "http://localhost:8003"
    ai_review_service_url: str = "http://localhost:8004"
    scoring_service_url: str = "http://localhost:8005"
    reporting_service_url: str = "http://localhost:8006"
    service_timeout_seconds: float = 120.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
