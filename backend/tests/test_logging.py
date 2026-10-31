"""Check real console output, request IDs, and logging isolation."""

import asyncio
import logging
import re
from uuid import UUID

import httpx
import pytest
from fastapi import Request, WebSocket
from fastapi.testclient import TestClient

from app.core import logging as app_logging
from app.core.config import LogLevel, Settings
from app.core.logging import configure_logging, request_id_context
from app.main import create_app


def test_request_log_matches_response_id(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Start and close the client inside capture so request cleanup has finished.
    app = create_app(Settings(env="local", _env_file=None))
    with TestClient(app) as client:
        response = client.get("/health")
    request_id = response.headers["X-Request-ID"]
    assert UUID(request_id).version == 4

    lines = [
        line
        for line in capsys.readouterr().out.splitlines()
        if "request.completed" in line
    ]
    assert len(lines) == 1
    match = re.fullmatch(
        rf"\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}:\d{{2}}\.\d{{3}}"
        rf" \| INFO\s+ \| req={request_id} \| request.completed"
        r" method=GET path=/health status=200 duration_ms=(\d+\.\d{3})",
        lines[0],
    )
    assert match is not None
    assert float(match.group(1)) >= 0
    assert response.json() == {"status": "ok", "env": "local"}


def test_request_ids_are_generated_not_trusted(client: TestClient) -> None:
    first = client.get("/health", headers={"X-Request-ID": "caller-supplied"})
    second = client.get("/health")

    assert first.headers["X-Request-ID"] != "caller-supplied"
    assert first.headers["X-Request-ID"] != second.headers["X-Request-ID"]


def test_duration_uses_elapsed_milliseconds(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # A controlled clock verifies the calculation, not just a plausible number.
    ticks = iter([100.0, 100.0125])
    monkeypatch.setattr(app_logging, "perf_counter", lambda: next(ticks))
    app = create_app(Settings(env="local", log_level="INFO", _env_file=None))
    with TestClient(app) as client:
        client.get("/health")

    assert "status=200 duration_ms=12.500" in capsys.readouterr().out


def test_uvicorn_logs_are_not_duplicated(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO")
    configure_logging("INFO")
    logging.getLogger("uvicorn.error").info("server.marker")

    assert capsys.readouterr().out.count("server.marker") == 1


@pytest.mark.parametrize("level", ["DEBUG", "INFO"])
def test_log_level_controls_debug_output(
    level: LogLevel, capsys: pytest.CaptureFixture[str]
) -> None:
    configure_logging(level)
    logging.getLogger("app.test").debug("debug.marker")
    logging.getLogger("app.test").info("info.marker")

    output = capsys.readouterr().out
    assert ("debug.marker" in output) == (level == "DEBUG")
    assert "info.marker" in output
    assert "req=- | info.marker" in output


@pytest.mark.parametrize("level", ["DEBUG", "INFO"])
def test_app_startup_uses_log_level(
    level: LogLevel,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LOG_LEVEL", level)
    settings = Settings(env="local", _env_file=None)
    with TestClient(create_app(settings)) as client:
        client.get("/health")

    output = capsys.readouterr().out
    assert "request.completed" in output
    assert ("request.started" in output) == (level == "DEBUG")


def test_route_logs_share_request_id(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = create_app(Settings(env="local", log_level="INFO", _env_file=None))

    @app.get("/log")
    def log_from_route() -> dict[str, str]:
        # A normal module logger gets request context without a manual ID argument.
        logging.getLogger("app.test").info("route.marker")
        return {"status": "ok"}

    with TestClient(app) as client:
        response = client.get("/log")

    request_id = response.headers["X-Request-ID"]
    assert f"req={request_id} | route.marker" in capsys.readouterr().out


def test_concurrent_requests_keep_separate_context(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging("INFO")
    app = create_app(Settings(env="local", _env_file=None))

    @app.get("/concurrent")
    async def concurrent(request: Request) -> dict[str, str]:
        before = request_id_context.get()
        await asyncio.sleep(0)
        assert request_id_context.get() == before
        assert request.state.request_id == before
        logging.getLogger("app.test").info("concurrent.marker")
        return {"request_id": before}

    async def make_requests() -> list[httpx.Response]:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await asyncio.gather(*(client.get("/concurrent") for _ in range(4)))

    responses = asyncio.run(make_requests())
    ids = {response.headers["X-Request-ID"] for response in responses}
    assert len(ids) == 4
    for response in responses:
        assert response.json()["request_id"] == response.headers["X-Request-ID"]
    output = capsys.readouterr().out
    for request_id in ids:
        assert f"req={request_id} | concurrent.marker" in output
    assert request_id_context.get() == "-"


def test_failed_request_does_not_leak_context(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = create_app(Settings(env="local", log_level="INFO", _env_file=None))

    @app.get("/fail")
    async def fail() -> None:
        raise RuntimeError("test failure")

    with TestClient(app, raise_server_exceptions=False) as client:
        failed = client.get("/fail")
        healthy = client.get("/health")

    assert failed.status_code == 500
    assert healthy.status_code == 200
    output = capsys.readouterr().out
    assert "request.failed method=GET path=/fail status=500" in output
    assert f"req={healthy.headers['X-Request-ID']} | request.completed" in output
    assert request_id_context.get() == "-"


def test_websocket_connections_are_not_logged_as_http(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = create_app(Settings(env="local", log_level="INFO", _env_file=None))

    @app.websocket("/socket")
    async def socket(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_json({"request_id": request_id_context.get()})
        await websocket.close()

    with TestClient(app) as client:
        with client.websocket_connect("/socket") as websocket:
            assert websocket.receive_json() == {"request_id": "-"}

    assert "request.completed" not in capsys.readouterr().out
