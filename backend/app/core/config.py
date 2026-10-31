from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

Environment = Literal["local", "ci", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: Environment = "local"
    database_url: str = "postgresql+psycopg://tzamot:tzamot@localhost:5432/tzamot"
    log_level: LogLevel = "DEBUG"
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:5500",
            "http://localhost:5500",
        ]
    )
    tz: str = "Asia/Jerusalem"
    admin_token: str = "dev-token"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value
