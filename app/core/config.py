"""
app config
"""

import os
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

allowed_envs = ["prod", "dev", "local"]
APP_ENV = os.getenv("APP_ENV")

if APP_ENV is None:
    print("WARN | APP_ENV is not set. Automatically set to dev.")
    APP_ENV = "dev"
if APP_ENV not in allowed_envs:
    raise ValueError(
        f"APP_ENV {APP_ENV} is not supported. Must be one of {allowed_envs}."
    )


@lru_cache()
class BaseConfig(BaseSettings):
    """
    Base Config for application
    """

    app_env: str = APP_ENV
    db_host: str
    db_user: str
    db_password: str
    db_port: int
    db_name: str

    model_config = SettingsConfigDict(env_file=f"app/env/.env.{APP_ENV}")

    def db_password_encoded(self):
        """
        db password encoding
        """

        return quote_plus(self.db_password)


conf = BaseConfig()
