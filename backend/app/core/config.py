"""Runtime configuration.

Environment-specific credentials and private infrastructure values come from the
environment. Repository defaults are development-only placeholders or public
application URLs; production secrets never belong in source control.
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

    # Development-only placeholder. Production requires SECRET_KEY from the
    # environment; keep the local default long enough to avoid weak-key warnings
    # while making it unmistakably unsuitable as a real secret.
    secret_key: str = "dev-only-not-a-secret-change-in-production-0001"
    access_token_ttl_minutes: int = 60 * 24 * 14

    # The public origin, for links inside emails. The frontend has its own copy
    # of this; the API needs one because nothing in a transactional email can be
    # a relative URL.
    site_url: str = "https://monashhub.secureview.tech"

    # --- Email verification -------------------------------------------------
    # Registration and password reset are both gated on a code sent to the
    # address, so the account can actually be recovered later.
    verification_code_ttl_seconds: int = 10 * 60
    verification_resend_interval_seconds: int = 60
    # Sends allowed per address, and per address per window, before we stop.
    verification_send_window_seconds: int = 60 * 60
    verification_send_max_per_window: int = 5
    verification_max_attempts: int = 5

    # console | resend | smtp. ``console`` writes the message to the log and is
    # for development only - nobody outside the server can complete a signup
    # with it, so production must set a real provider.
    email_provider: str = "console"
    email_from_address: str = "no-reply@monashhub.secureview.tech"
    email_from_name: str = "Monash Hub"
    email_reply_to: str | None = None
    email_timeout_seconds: int = 10

    resend_api_key: str = ""
    resend_api_url: str = "https://api.resend.com/emails"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False

    # --- Avatars ------------------------------------------------------------
    # Written by the API, served by nginx straight off disk - a request for a
    # profile picture should not wake Python up. The directory is a mounted
    # volume; see docker-compose.yml and deployment/nginx/monash-hub.conf.
    avatar_dir: str = "/data/avatars"
    avatar_url_prefix: str = "/avatars"

    # --- Database pool ------------------------------------------------------
    # Sized for one API container against one PostgreSQL: enough for concurrent
    # readers without letting a traffic spike open more connections than the
    # server will accept.
    db_pool_size: int = 10
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def email_is_deliverable(self) -> bool:
        """Whether a code can actually reach a stranger's inbox."""
        if self.email_provider == "resend":
            return bool(self.resend_api_key)
        if self.email_provider == "smtp":
            return bool(self.smtp_host)
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()
