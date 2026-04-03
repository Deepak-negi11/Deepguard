from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DEEPGUARD_", extra="ignore")

    environment: str = "development"  # development|test|production
    app_name: str = "DeepGuard API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:////tmp/deepguard/deepguard.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3100,http://127.0.0.1:3100"
    upload_root: str = "/tmp/deepguard/uploads"
    max_upload_mb: int = 250
    auto_create_schema: bool = False
    enable_demo_analyzers: bool = True
    enable_celery_workers: bool = False
    enable_api_usage_logging: bool = True
    rate_limit_requests_per_hour: int = 100
    delete_uploads_after_processing: bool = True
    warm_news_model_on_startup: bool = True
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Auth cookies
    auth_cookie_name: str = "deepguard_access"
    csrf_cookie_name: str = "deepguard_csrf"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"  # lax|strict|none

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
