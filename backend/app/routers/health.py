"""Health endpoint used by developers, containers, and deployment checks."""

from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.config import Environment, Settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Stable response returned when the API process is available."""

    status: Literal["ok"] = "ok"
    env: Environment


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    """Report that the API is running and identify its environment."""
    settings: Settings = request.app.state.settings
    return HealthResponse(env=settings.env)
