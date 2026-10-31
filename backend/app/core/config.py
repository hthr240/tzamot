"""Application configuration.

Create ``Settings()`` wherever validated configuration is needed. Values are
loaded in this order: environment variables, ``.env``, then local defaults.
"""

from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Literal types reject spelling mistakes and unsupported values at startup.
Environment = Literal["local", "ci", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Settings shared by the API, database, logging, and CORS setup."""

    # `.env` is useful locally. Real environment variables still take priority.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # These defaults match the local Docker and frontend setup.
    env: Environment = "local"
    database_url: str = "postgresql+psycopg://tzamot:tzamot@localhost:5432/tzamot"
    log_level: LogLevel = "DEBUG"
    # NoDecode lets the validator parse the simple comma-separated value.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:5500",
            "http://localhost:5500",
        ]
    )
    tz: str = "Asia/Jerusalem"
    # This is only a local placeholder. Production must provide a secret value.
    admin_token: str = "dev-token"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        """Turn ``origin-one,origin-two`` into a list used by CORS middleware."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value
