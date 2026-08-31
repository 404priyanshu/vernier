import os
from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "Vernier"
    database_url: str = Field(
        default="postgresql+psycopg://vernier:vernier@localhost:5433/vernier",
        validation_alias=AliasChoices("DATABASE_URL", "POSTGRES_URL", "POSTGRES_PRISMA_URL"),
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("REDIS_URL", "KV_URL", "UPSTASH_REDIS_URL"),
    )

    xai_api_key: str = ""
    openai_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = "grok-4.6"

    github_token: str = ""
    github_webhook_secret: str = ""
    github_api_url: str = "https://api.github.com"

    cache_ttl_seconds: int = 60 * 60 * 24 * 7
    prompt_version: str = "review-v1"
    batch_max_chars: int = 8000
    cors_origins: str = "http://localhost:3000"

    seed_on_startup: bool = True

    @property
    def llm_api_key(self) -> str:
        return self.xai_api_key or self.openai_api_key

    @property
    def resolved_llm_base_url(self) -> str:
        if self.llm_base_url:
            return self.llm_base_url.rstrip("/")
        if self.xai_api_key or not self.openai_api_key:
            return "https://api.x.ai/v1"
        return "https://api.openai.com/v1"

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [part.strip() for part in self.cors_origins.split(",") if part.strip()]
        host = os.getenv("VERCEL_PROJECT_PRODUCTION_URL") or os.getenv("VERCEL_URL")
        if host:
            origins.append(f"https://{host.removeprefix('https://')}")
        return origins

    @property
    def sqlalchemy_url(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://") :]
        if url.startswith("postgresql://") and "+psycopg" not in url.split("://", 1)[0]:
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
