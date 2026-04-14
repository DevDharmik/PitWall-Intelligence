"""
app/core/config.py
──────────────────
Centralised settings loaded from environment variables via pydantic-settings.
All values can be overridden in .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    secret_key: str = "change-this-secret"

    # Database
    database_url: str = "postgresql+asyncpg://pitwall:changeme@localhost:5432/pitwall_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    bvi_cache_ttl: int = 86400  # 24 hours

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # ML model paths
    model_dir: str = "ml_models"
    constructor_points_model: str = "ml_models/constructor_points_gbr.joblib"
    podium_classifier_model: str  = "ml_models/podium_classifier_lr.joblib"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
