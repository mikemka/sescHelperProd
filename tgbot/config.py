from __future__ import annotations

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TOKEN: str
    DEBUG: bool = False
    ADMIN_IDS: List[int] = [688003991]
    ADMIN_GROUP_ID: int = 0

    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "sesc_bot"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"

    REDIS_URL: str = "redis://redis:6379"
    PROXY: str = ""  # http://user:pass@ip:port

    @property
    def DATABASE_URL(self) -> str:
        return f"postgres://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
