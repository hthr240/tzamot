"""SQLAlchemy engine and FastAPI database session dependency."""

import os
from collections.abc import Generator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import Settings


def create_db_engine(settings: Settings) -> Engine:
    """Build an engine from settings. SQL echo follows ``LOG_LEVEL=DEBUG``."""
    # Pytest creates many short-lived apps; a real pool can exhaust Postgres.
    engine_kwargs: dict[str, object] = {
        "echo": settings.log_level == "DEBUG",
        "pool_pre_ping": True,
        "connect_args": {"connect_timeout": 5},
    }
    if "PYTEST_VERSION" in os.environ:
        engine_kwargs["poolclass"] = NullPool

    return create_engine(settings.database_url, **engine_kwargs)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a session factory bound to ``engine``."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db(request: Request) -> Generator[Session]:
    """Yield one request-scoped session and always close it afterward."""
    session_factory: sessionmaker[Session] = request.app.state.SessionLocal
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
