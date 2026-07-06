from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OTKRYTKA_", env_file=".env", extra="ignore")

    db_path: str = "otkrytka.db"
    frontend_dir: str = "frontend"
    upload_dir: str = "uploads"
    # Fixed public origin (e.g. https://otkrytka.agentspore.com) used to build the
    # absolute og:url / og:image. When set, client-supplied Host / X-Forwarded-*
    # headers are ignored so an attacker cannot inject a phishing domain into the
    # social unfurl. Empty (dev) falls back to the request-derived host.
    canonical_base_url: str = ""
    max_upload_mb: int = 3
    cors_origins: str = "*"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
