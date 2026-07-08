from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Deployment envs allowed to run without a fixed canonical origin. Any other value
# is treated as "production-like" and MUST set canonical_base_url.
_NON_PROD_ENVS = frozenset({"dev", "local", "test"})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OTKRYTKA_", env_file=".env", extra="ignore")

    # Deployment environment. Anything not in _NON_PROD_ENVS is production-like and
    # is required to pin canonical_base_url (see the validator below).
    env: str = "dev"
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

    @model_validator(mode="after")
    def _require_canonical_in_prod(self) -> "Settings":
        """Fail closed in production if the canonical origin is not pinned.

        In dev/local/test an empty canonical_base_url falls back to the
        request-derived host (spoofable via X-Forwarded-Host) — acceptable for
        local work but unsafe in production, where the og:url / og:image and
        oEmbed must resolve to a fixed, trusted origin. Raising here surfaces the
        misconfiguration at startup instead of silently unfurling attacker hosts.
        """
        if self.env.strip().lower() not in _NON_PROD_ENVS and not self.canonical_base_url.strip():
            raise ValueError(
                "canonical_base_url must be set when env is production-like "
                f"(env={self.env!r}); set OTKRYTKA_CANONICAL_BASE_URL to the public origin"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
