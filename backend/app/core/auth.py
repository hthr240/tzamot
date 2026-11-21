"""Admin authentication for routes under ``/admin/*``."""

from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings

# auto_error=False so missing credentials become our 401, not FastAPI's default.
_bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(_bearer_scheme),
]


def require_admin(
    request: Request,
    credentials: BearerCredentials,
) -> None:
    """Reject requests that do not present the configured ``ADMIN_TOKEN``."""
    settings: Settings = request.app.state.settings
    expected = settings.admin_token
    provided = (
        credentials.credentials
        if credentials is not None and credentials.scheme.lower() == "bearer"
        else ""
    )

    if (
        not expected
        or not provided
        or len(provided) != len(expected)
        or not secrets.compare_digest(provided, expected)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
