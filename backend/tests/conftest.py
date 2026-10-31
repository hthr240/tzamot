"""Shared pytest fixtures for API tests."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Create a local API client that is isolated from the developer's `.env`."""
    monkeypatch.delenv("ENV", raising=False)
    settings = Settings(env="local", _env_file=None)

    with TestClient(create_app(settings)) as test_client:
        yield test_client
