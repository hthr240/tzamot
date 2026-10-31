"""Shared console logging and request IDs for the API."""

import logging
from contextvars import ContextVar
from logging.config import dictConfig
from time import perf_counter
from uuid import uuid4

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import LogLevel

# ContextVar keeps each request's ID separate, even when requests overlap.
request_id_context: ContextVar[str] = ContextVar("request_id", default="-")
logger = logging.getLogger(__name__)


class RequestIdFilter(logging.Filter):
    """Attach the current request ID to every record sent to the console."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True


def configure_logging(level: LogLevel) -> None:
    """Configure one stdout handler shared by the API and Uvicorn."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {"request_id": {"()": RequestIdFilter}},
            "formatters": {
                "console": {
                    "format": (
                        "%(asctime)s.%(msecs)03d | %(levelname)-8s | "
                        "req=%(request_id)s | %(message)s"
                    ),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "console",
                    "filters": ["request_id"],
                    "level": level,
                }
            },
            "root": {"handlers": ["console"], "level": level},
            # Remove Uvicorn's own handlers to avoid duplicate log lines.
            "loggers": {
                name: {"handlers": [], "level": level, "propagate": True}
                for name in ("uvicorn", "uvicorn.error", "uvicorn.access")
            },
        }
    )


class RequestLoggingMiddleware:
    """Add an ID and timing to HTTP requests without changing their response."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # WebSocket connections and application startup are not HTTP requests.
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid4().hex
        token = request_id_context.set(request_id)
        scope.setdefault("state", {})["request_id"] = request_id
        started = perf_counter()
        status = 500
        completed = False

        async def send_with_request_id(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                MutableHeaders(scope=message)["X-Request-ID"] = request_id
            await send(message)

        try:
            logger.debug(
                "request.started method=%s path=%s", scope["method"], scope["path"]
            )
            await self.app(scope, receive, send_with_request_id)
            completed = True
        finally:
            # The global handler processes failures after request context is reset.
            try:
                logger.info(
                    "%s method=%s path=%s status=%s duration_ms=%.3f",
                    "request.completed" if completed else "request.failed",
                    scope["method"],
                    scope["path"],
                    status,
                    (perf_counter() - started) * 1000,
                )
            finally:
                request_id_context.reset(token)
