"""Tests for API health reporting and documentation visibility."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from tests.conftest import get_test_database_url


def test_root_points_at_health_and_docs(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "tzamot-api",
        "health": "/health",
        "docs": "/docs",
    }


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "env": "local",
        "database": "ok",
    }


def test_health_reports_database_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(
        env="local",
        database_url=(
            "postgresql+psycopg://tzamot:tzamot@127.0.0.1:5432/"
            "tzamot_missing_health_db"
        ),
        log_level="WARNING",
        _env_file=None,
    )

    with TestClient(create_app(settings)) as client:
        response = client.get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "error"
    assert body["env"] == "local"
    assert body["database"] == "error"


def test_docs_are_available_outside_production(client: TestClient) -> None:
    response = client.get("/docs")

    assert response.status_code == 200


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_docs_are_hidden_in_production(
    path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(
        env="production",
        database_url=get_test_database_url(),
        log_level="WARNING",
        _env_file=None,
    )

    with TestClient(create_app(settings)) as client:
        response = client.get(path)

    assert response.status_code == 404
