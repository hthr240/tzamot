"""Tests for API health reporting and documentation visibility."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "env": "local"}


def test_docs_are_available_outside_production(client: TestClient) -> None:
    response = client.get("/docs")

    assert response.status_code == 200


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_docs_are_hidden_in_production(
    path: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ENV", raising=False)
    settings = Settings(env="production", _env_file=None)

    with TestClient(create_app(settings)) as client:
        response = client.get(path)

    assert response.status_code == 404
