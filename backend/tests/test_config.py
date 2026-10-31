"""Tests for the two supported settings sources: the environment and `.env`."""

from pathlib import Path

import pytest

from app.core.config import Settings

# Clear every supported variable so a developer's machine cannot affect tests.
SETTING_NAMES = (
    "ENV",
    "DATABASE_URL",
    "LOG_LEVEL",
    "CORS_ORIGINS",
    "TZ",
    "ADMIN_TOKEN",
)


@pytest.fixture(autouse=True)
def clear_settings_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Start each test without configuration inherited from the computer."""
    for name in SETTING_NAMES:
        monkeypatch.delenv(name, raising=False)


def test_settings_load_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Set every value explicitly to prove environment loading and validation.
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://tzamot:secret@db:5432/tzamot",
    )
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://tzamot.co.il, https://admin.tzamot.co.il",
    )
    monkeypatch.setenv("TZ", "Asia/Jerusalem")
    monkeypatch.setenv("ADMIN_TOKEN", "production-token")

    settings = Settings(_env_file=None)  # Do not read a developer's local `.env`.

    assert settings.env == "production"
    assert settings.database_url == (
        "postgresql+psycopg://tzamot:secret@db:5432/tzamot"
    )
    assert settings.log_level == "INFO"
    assert settings.cors_origins == [
        "https://tzamot.co.il",
        "https://admin.tzamot.co.il",
    ]
    assert settings.tz == "Asia/Jerusalem"
    assert settings.admin_token == "production-token"


def test_settings_load_from_dotenv(tmp_path: Path) -> None:
    # Use a temporary file so the test never creates or changes backend/.env.
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "ENV=ci",
                "DATABASE_URL=postgresql+psycopg://tzamot:tzamot@localhost:5432/tzamot_test",
                "LOG_LEVEL=INFO",
                "CORS_ORIGINS=http://ci.example.test,http://ci-admin.example.test",
                "TZ=Asia/Jerusalem",
                "ADMIN_TOKEN=ci-token",
            ]
        ),
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.env == "ci"
    assert settings.database_url.endswith("/tzamot_test")
    assert settings.log_level == "INFO"
    assert settings.cors_origins == [
        "http://ci.example.test",
        "http://ci-admin.example.test",
    ]
    assert settings.tz == "Asia/Jerusalem"
    assert settings.admin_token == "ci-token"
