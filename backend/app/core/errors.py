"""Report unexpected HTTP errors without exposing their details to clients."""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.logging import request_id_context

logger = logging.getLogger(__name__)


async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    """Log the full traceback and return an error with a searchable request ID."""
    request_id: str = request.state.request_id
    # FastAPI calls this handler after request middleware has cleared its context.
    token = request_id_context.set(request_id)
    try:
        logger.error(
            "request.unhandled_exception method=%s path=%s",
            request.method,
            request.url.path,
            exc_info=exc,
        )
    finally:
        request_id_context.reset(token)

    # Keep exception messages and stack traces in server logs, not the response.
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "request_id": request_id},
        headers={"X-Request-ID": request_id},
    )
