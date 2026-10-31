"""Check unexpected errors without adding failure routes to the real API."""

import asyncio
from uuid import UUID

import httpx
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.background import BackgroundTask

from app.core.config import Environment, Settings
from app.core.logging import configure_logging, request_id_context
from app.main import create_app


@pytest.mark.parametrize("env", ["local", "production"])
@pytest.mark.parametrize("async_route", [False, True])
def test_unhandled_error_has_correlated_traceback(
    env: Environment,
    async_route: bool,
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = create_app(Settings(env=env, log_level="INFO", _env_file=None))

    async def async_fail() -> None:
        raise RuntimeError("private error details")

    def sync_fail() -> None:
        raise RuntimeError("private error details")

    app.add_api_route("/fail", async_fail if async_route else sync_fail)

    # Starlette re-raises handled server errors so tests can choose to inspect them.
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/fail")

    request_id = response.headers["X-Request-ID"]
    assert UUID(request_id).version == 4
    assert response.status_code == 500
    assert response.json() == {
        "detail": "Internal server error",
        "request_id": request_id,
    }
    assert "private error details" not in response.text
    output = capsys.readouterr().out
    error_lines = [line for line in output.splitlines() if "| ERROR" in line]
    assert len(error_lines) == 1
    assert f"req={request_id} | request.unhandled_exception" in error_lines[0]
    assert "method=GET path=/fail" in error_lines[0]
    assert "Traceback (most recent call last):" in output
    assert "RuntimeError: private error details" in output
    assert "raise RuntimeError" in output
    assert request_id_context.get() == "-"


@pytest.mark.parametrize("status", [403, 404, 409])
def test_http_errors_keep_status_body_and_headers(
    status: int, capsys: pytest.CaptureFixture[str]
) -> None:
    app = create_app(Settings(env="local", log_level="INFO", _env_file=None))

    @app.get("/denied")
    def denied() -> None:
        raise HTTPException(
            status_code=status, detail="Denied", headers={"X-Error": "expected"}
        )

    with TestClient(app) as client:
        response = client.get("/denied")

    assert response.status_code == status
    assert response.json() == {"detail": "Denied"}
    assert response.headers["X-Error"] == "expected"
    assert UUID(response.headers["X-Request-ID"]).version == 4
    assert "request.unhandled_exception" not in capsys.readouterr().out


@pytest.mark.parametrize("path", ["/validate", "/validate?count=invalid"])
def test_validation_errors_remain_422(
    path: str, capsys: pytest.CaptureFixture[str]
) -> None:
    app = create_app(Settings(env="local", log_level="INFO", _env_file=None))

    @app.get("/validate")
    def validate(count: int) -> dict[str, int]:
        return {"count": count}

    with TestClient(app) as client:
        response = client.get(path)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "count"]
    assert UUID(response.headers["X-Request-ID"]).version == 4
    assert "request.unhandled_exception" not in capsys.readouterr().out


def test_concurrent_errors_keep_distinct_ids(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging("INFO")
    app = create_app(Settings(env="local", _env_file=None))

    @app.get("/fail/{index}")
    async def fail(index: int) -> None:
        await asyncio.sleep(0)
        raise RuntimeError(f"failure {index}")

    async def make_requests() -> list[httpx.Response]:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            return await asyncio.gather(
                *(client.get(f"/fail/{index}") for index in range(4))
            )

    responses = asyncio.run(make_requests())
    ids = {response.headers["X-Request-ID"] for response in responses}
    assert len(ids) == 4
    for response in responses:
        assert response.status_code == 500
        assert response.json()["request_id"] == response.headers["X-Request-ID"]

    error_lines = [
        line for line in capsys.readouterr().out.splitlines() if "| ERROR" in line
    ]
    assert len(error_lines) == 4
    for request_id in ids:
        assert sum(f"req={request_id} |" in line for line in error_lines) == 1
    assert request_id_context.get() == "-"


def test_background_error_does_not_replace_sent_response(
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = create_app(Settings(env="local", log_level="INFO", _env_file=None))

    def fail_after_response() -> None:
        raise RuntimeError("background failure")

    @app.get("/background")
    def background() -> JSONResponse:
        # Background work runs after the response has been sent to the client.
        return JSONResponse(
            {"status": "sent"}, background=BackgroundTask(fail_after_response)
        )

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/background")

    assert response.status_code == 200
    assert response.json() == {"status": "sent"}
    request_id = response.headers["X-Request-ID"]
    output = capsys.readouterr().out
    assert f"req={request_id} | request.unhandled_exception" in output
    assert "RuntimeError: background failure" in output


def test_test_client_can_still_raise_original_exception() -> None:
    app: FastAPI = create_app(Settings(env="local", _env_file=None))

    @app.get("/fail")
    def fail() -> None:
        raise RuntimeError("original failure")

    with TestClient(app) as client:
        with pytest.raises(RuntimeError, match="original failure"):
            client.get("/fail")
