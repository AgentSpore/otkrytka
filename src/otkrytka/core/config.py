from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OTKRYTKA_", env_file=".env", extra="ignore")

    db_path: str = "otkrytka.db"
    frontend_dir: str = "frontend"
    upload_dir: str = "uploads"
    max_upload_mb: int = 3
    cors_origins: str = "*"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
