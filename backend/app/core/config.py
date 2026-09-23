"""
Centralized application configuration.

Every setting a running instance of CodePilot needs — DB, Redis, JWT secrets,
LLM provider keys — is declared here as a typed field and read from the
environment (or a .env file in local dev). Nothing else in the codebase should
call os.environ directly; that keeps every config value validated in one
place and makes it trivial to see the full surface area of "things that
change between dev/staging/prod".
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- General ---
    PROJECT_NAME: str = "CodePilot"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "test", "staging", "production"] = "local"
    LOG_LEVEL: str = "INFO"

    # --- CORS ---
    # Comma-separated origins, e.g. "http://localhost:3000,https://app.example.com".
    # Kept as a plain string field (rather than list[AnyHttpUrl]) because
    # pydantic-settings tries to JSON-decode complex-typed env values before
    # any validator runs, which breaks on a plain comma-separated string.
    BACKEND_CORS_ORIGINS: str = ""

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    # --- Postgres ---
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "codepilot"
    POSTGRES_PASSWORD: str = "codepilot"
    POSTGRES_DB: str = "codepilot"

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """asyncpg driver — used by the FastAPI app at request time."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """psycopg2 driver — used by Alembic, which does not support async."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # --- Redis / Celery ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    @property
    def celery_broker_url(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def celery_result_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    # --- Auth ---
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # --- LLM provider (wired up in the RAG/agent step) ---
    LLM_PROVIDER: Literal["openai", "azure_openai"] = "openai"
    OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_API_VERSION: str = "2024-08-01-preview"

    # --- GitHub integration (wired up in the ingestion step) ---
    GITHUB_APP_ID: str | None = None
    GITHUB_APP_PRIVATE_KEY: str | None = None
    GITHUB_WEBHOOK_SECRET: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Cached so Settings() — which reads env vars and disk — runs once per process."""
    return Settings()


settings = get_settings()
