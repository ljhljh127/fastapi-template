from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "dev", "prod"]

INSECURE_DB_PASSWORDS = frozenset({"postgres", "password", "changeme", ""})


class Settings(BaseSettings):
    """필드를 추가하면 .env.example과 README 환경변수 표도 같이 고친다."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "fastapi-template"
    app_env: Environment = "local"
    debug: bool = False
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=list)

    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "app"
    db_pool_size: int = Field(default=5, ge=1)
    db_max_overflow: int = Field(default=10, ge=0)
    db_pool_recycle: int = Field(default=1800, ge=-1)
    db_echo: bool = False

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{quote_plus(self.db_user)}:{quote_plus(self.db_password)}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def is_prod(self) -> bool:
        return self.app_env == "prod"

    @model_validator(mode="after")
    def _reject_insecure_prod(self) -> "Settings":
        if not self.is_prod:
            return self
        if self.db_password in INSECURE_DB_PASSWORDS:
            raise ValueError("DB_PASSWORD must be set to a non-default value when APP_ENV=prod")
        if self.debug:
            raise ValueError("DEBUG must be false when APP_ENV=prod")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
