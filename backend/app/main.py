"""FastAPI application creation and local Uvicorn entry point."""

from fastapi import FastAPI

from app.core.config import Settings
from app.routers.health import router as health_router


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create an isolated application using validated settings."""
    app_settings = settings or Settings()
    docs_enabled = app_settings.env != "production"

    app = FastAPI(
        title="Tzamot API",
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )
    # App state makes the same settings available to routers and middleware.
    app.state.settings = app_settings
    app.include_router(health_router)
    return app


# Uvicorn imports this object when run with `uvicorn app.main:app`.
app = create_app()
