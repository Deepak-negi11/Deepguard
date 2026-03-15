from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DEEPGUARD_", extra="ignore")

    app_name: str = "DeepGuard API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./deepguard.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3100,http://127.0.0.1:3100"
    upload_root: str = "./uploads"
    max_upload_mb: int = 250
    auto_create_schema: bool = False
    enable_demo_analyzers: bool = True
    enable_celery_workers: bool = False
    enable_api_usage_logging: bool = True
    rate_limit_requests_per_hour: int = 100
    delete_uploads_after_processing: bool = True
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
