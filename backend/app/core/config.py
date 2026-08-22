"""Runtime configuration.

Everything that differs between a laptop and the VPS lives here and comes from
the environment, so the repository never carries a credential or a host address.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # postgresql+psycopg://user:password@host:5432/dbname
    database_url: str = "postgresql+psycopg://monashhub:monashhub@localhost:5432/monashhub"

    app_name: str = "Monash Hub API"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    # The public origin the browser sees. Same-origin in production, so the list
    # only matters for a frontend running on a different dev port.
    cors_origins: str = "http://localhost:3000"

    # Handbook year the MVP treats as current.
    current_academic_year: int = 2026

    secret_key: str = "dev-only-change-me"
    access_token_ttl_minutes: int = 60 * 24 * 14

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
