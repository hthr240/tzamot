"""Shared pytest fixtures for API tests."""

import logging
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture(autouse=True)
def restore_logging() -> Iterator[None]:
    """Keep application startup from changing logging for later tests."""
    loggers = [
        logging.getLogger(name)
        for name in ("", "uvicorn", "uvicorn.error", "uvicorn.access")
    ]
    original = [
        (logger, logger.handlers[:], logger.level, logger.propagate, logger.disabled)
        for logger in loggers
    ]
    try:
        yield
    finally:
        for logger, handlers, level, propagate, disabled in original:
            logger.handlers = handlers
            logger.setLevel(level)
            logger.propagate = propagate
            logger.disabled = disabled


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Create a local API client that is isolated from the developer's `.env`."""
    monkeypatch.delenv("ENV", raising=False)
    settings = Settings(env="local", _env_file=None)

    with TestClient(create_app(settings)) as test_client:
        yield test_client
