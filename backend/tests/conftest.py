"""Shared pytest fixtures for API and database tests.

Integration fixtures talk only to ``tzamot_test``. They never point at the
developer ``tzamot`` database from Docker Compose.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.core.config import Settings
from app.core.db import get_db
from app.main import create_app

# Prefer an explicit test URL. The default is a sibling of the local Compose DB.
DEFAULT_TEST_DATABASE_URL = (
    "postgresql+psycopg://tzamot:tzamot@127.0.0.1:5432/tzamot_test"
)


def get_test_database_url() -> str:
    """Return the isolated database URL used by pytest."""
    return os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)


def _admin_url(database_url: str) -> str:
    """Connect to the server's ``postgres`` database to create sibling databases."""
    url = make_url(database_url)
    return url.set(database="postgres").render_as_string(hide_password=False)


def ensure_test_database_exists(database_url: str) -> None:
    """Create the test database once if the local Postgres role can do so."""
    parsed = make_url(database_url)
    database_name = parsed.database
    if not database_name:
        raise RuntimeError("TEST_DATABASE_URL must include a database name")

    admin_engine = create_engine(
        _admin_url(database_url),
        isolation_level="AUTOCOMMIT",
        pool_pre_ping=True,
        poolclass=NullPool,
        connect_args={"connect_timeout": 5},
    )
    try:
        with admin_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": database_name},
            ).scalar()
            if not exists:
                connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    finally:
        admin_engine.dispose()


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


@pytest.fixture(scope="session")
def test_engine() -> Iterator[Engine]:
    """Session-scoped engine bound only to the isolated test database."""
    url = get_test_database_url()
    ensure_test_database_exists(url)
    # Keep SQL echo off in the suite so assertion output stays readable.
    engine = create_engine(
        url,
        echo=False,
        pool_pre_ping=True,
        poolclass=NullPool,
        connect_args={"connect_timeout": 5},
    )
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Iterator[Session]:
    """Yield a session that rolls back after the test finishes."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, autoflush=False, autocommit=False)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def app_settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Build settings that always target the isolated test database."""
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    return Settings(
        env="local",
        database_url=get_test_database_url(),
        log_level="WARNING",
        _env_file=None,
    )


@pytest.fixture
def client(app_settings: Settings) -> Iterator[TestClient]:
    """Create an API client against the isolated test database."""
    with TestClient(create_app(app_settings)) as test_client:
        yield test_client


@pytest.fixture
def client_with_db_session(
    app_settings: Settings,
    db_session: Session,
) -> Iterator[TestClient]:
    """API client whose ``get_db`` dependency uses the rollback session."""

    app = create_app(app_settings)

    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
