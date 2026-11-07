"""Tests for the SQLAlchemy engine, session dependency, and rollback fixture."""

from collections.abc import Iterator

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.core.config import Settings
from app.core.db import create_db_engine, get_db
from app.main import create_app
from tests.conftest import get_test_database_url


def test_engine_echo_follows_debug_log_level() -> None:
    debug_settings = Settings(
        database_url=get_test_database_url(),
        log_level="DEBUG",
        _env_file=None,
    )
    quiet_settings = Settings(
        database_url=get_test_database_url(),
        log_level="INFO",
        _env_file=None,
    )

    debug_engine = create_db_engine(debug_settings)
    quiet_engine = create_db_engine(quiet_settings)
    try:
        assert debug_engine.echo is True
        assert quiet_engine.echo is False
    finally:
        debug_engine.dispose()
        quiet_engine.dispose()


def test_get_db_yields_session_and_closes_it(app_settings: Settings) -> None:
    app = create_app(app_settings)
    request = Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": [],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "app": app,
        }
    )

    generator: Iterator[Session] = get_db(request)
    session = next(generator)
    assert session.execute(text("SELECT 1")).scalar() == 1
    assert session.in_transaction()

    # Finishing the generator runs ``session.close()`` and ends the request transaction.
    with pytest.raises(StopIteration):
        next(generator)
    assert not session.in_transaction()

    app.state.engine.dispose()


def test_db_session_fixture_rolls_back(test_engine: Engine) -> None:
    """Mirror the ``db_session`` fixture pattern and prove the insert is undone."""
    with test_engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS rollback_probe"))
        connection.execute(text("CREATE TABLE rollback_probe (id INTEGER PRIMARY KEY)"))

    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, autoflush=False, autocommit=False)
    try:
        session.execute(text("INSERT INTO rollback_probe (id) VALUES (1)"))
        session.flush()
        assert (
            session.execute(text("SELECT count(*) FROM rollback_probe")).scalar() == 1
        )
    finally:
        session.close()
        transaction.rollback()
        connection.close()

    with test_engine.connect() as connection:
        count = connection.execute(text("SELECT count(*) FROM rollback_probe")).scalar()
    assert count == 0


def test_fixtures_use_isolated_test_database(
    app_settings: Settings,
    test_engine: Engine,
) -> None:
    assert "tzamot_test" in app_settings.database_url
    assert test_engine.url.database == "tzamot_test"
    assert app_settings.database_url != Settings(_env_file=None).database_url
