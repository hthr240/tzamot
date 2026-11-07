"""Health endpoint used by developers, containers, and deployment checks."""

from typing import Literal

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.config import Environment, Settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Process status plus a live database check."""

    status: Literal["ok", "error"]
    env: Environment
    database: Literal["ok", "error"]


@router.get("/health", response_model=HealthResponse)
def health(request: Request, response: Response) -> HealthResponse:
    """Report that the API is running and whether the database answers."""
    settings: Settings = request.app.state.settings
    engine: Engine = request.app.state.engine
    database: Literal["ok", "error"] = "ok"

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        database = "error"
        response.status_code = 503

    return HealthResponse(
        status="ok" if database == "ok" else "error",
        env=settings.env,
        database=database,
    )
