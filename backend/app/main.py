"""FastAPI application creation and local Uvicorn entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import Settings
from app.core.errors import handle_unhandled_exception
from app.core.logging import RequestLoggingMiddleware, configure_logging
from app.routers.health import router as health_router


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create an isolated application using validated settings."""
    app_settings = settings or Settings()
    docs_enabled = app_settings.env != "production"

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        # Configure the process at startup, not every time this module is imported.
        startup_settings: Settings = app.state.settings
        configure_logging(startup_settings.log_level)
        yield

    app = FastAPI(
        title="Tzamot API",
        lifespan=lifespan,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )
    # App state makes the same settings available to routers and middleware.
    app.state.settings = app_settings
    # FastAPI still uses its built-in handlers for HTTP errors and validation.
    app.add_exception_handler(Exception, handle_unhandled_exception)
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(health_router)
    return app


# Uvicorn imports this object when run with `uvicorn app.main:app`.
app = create_app()
