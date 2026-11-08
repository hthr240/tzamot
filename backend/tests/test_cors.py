"""CORS responses for allowed and disallowed frontend origins."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from tests.conftest import get_test_database_url


@pytest.fixture
def cors_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """API client with only the local Live Server origins allowed."""
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    settings = Settings(
        env="local",
        database_url=get_test_database_url(),
        cors_origins=[
            "http://127.0.0.1:5500",
            "http://localhost:5500",
        ],
        log_level="WARNING",
        _env_file=None,
    )
    with TestClient(create_app(settings)) as client:
        yield client


def test_cors_allows_configured_origin(cors_client: TestClient) -> None:
    response = cors_client.get(
        "/health",
        headers={"Origin": "http://127.0.0.1:5500"},
    )

    # Health may be 503 when Postgres is down; CORS must still apply.
    assert response.status_code in (200, 503)
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5500"


def test_cors_omits_header_for_unknown_origin(cors_client: TestClient) -> None:
    response = cors_client.get(
        "/health",
        headers={"Origin": "http://evil.example"},
    )

    assert response.status_code in (200, 503)
    assert "access-control-allow-origin" not in response.headers
