"""FastAPI application creation and local Uvicorn entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import Settings
from app.core.db import create_db_engine, create_session_factory
from app.core.errors import handle_unhandled_exception
from app.core.logging import RequestLoggingMiddleware, configure_logging
from app.routers.health import router as health_router


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create an isolated application using validated settings."""
    app_settings = settings or Settings()
    docs_enabled = app_settings.env != "production"
    engine = create_db_engine(app_settings)
    session_factory = create_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        # Configure the process at startup, not every time this module is imported.
        startup_settings: Settings = app.state.settings
        configure_logging(startup_settings.log_level)
        try:
            yield
        finally:
            # Drop pooled connections when this app instance shuts down.
            app.state.engine.dispose()

    app = FastAPI(
        title="Tzamot API",
        lifespan=lifespan,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )
    # App state makes the same settings available to routers and middleware.
    app.state.settings = app_settings
    app.state.engine = engine
    app.state.SessionLocal = session_factory
    # FastAPI still uses its built-in handlers for HTTP errors and validation.
    app.add_exception_handler(Exception, handle_unhandled_exception)
    app.add_middleware(RequestLoggingMiddleware)
    # Added last so it wraps the stack and answers browser preflight requests.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    return app


# Uvicorn imports this object when run with `uvicorn app.main:app`.
app = create_app()
