from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "InsightOS API"
    app_env: str = "local"
    database_url: str = "postgresql+psycopg://insightos:insightos@localhost:5432/insightos"
    redis_url: str = "redis://localhost:6379/0"
    backend_cors_origins: str = Field(default="http://localhost:3000")
    sec_user_agent: str = Field(default="InsightOS/0.1 contact=research@example.com")
    fred_api_key: str | None = None
    connector_timeout_seconds: float = 10.0
    connector_cache_ttl_seconds: int = 300

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @cached_property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


settings = Settings()
