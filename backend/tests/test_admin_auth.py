"""Admin bearer-token protection for ``/admin/*`` routes."""

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from tests.conftest import get_test_database_url


def _client_with_token(admin_token: str) -> TestClient:
    settings = Settings(
        env="local",
        database_url=get_test_database_url(),
        log_level="WARNING",
        admin_token=admin_token,
        _env_file=None,
    )
    return TestClient(create_app(settings))


def test_admin_ping_requires_bearer_token() -> None:
    with _client_with_token("ci-token") as client:
        response = client.get("/admin/ping")

    assert response.status_code == 401
    assert response.headers.get("www-authenticate", "").lower().startswith("bearer")
    assert response.json()["detail"] == "Not authenticated"


def test_admin_ping_rejects_wrong_token() -> None:
    with _client_with_token("ci-token") as client:
        response = client.get(
            "/admin/ping",
            headers={"Authorization": "Bearer wrong-token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_admin_ping_accepts_configured_token() -> None:
    with _client_with_token("ci-token") as client:
        response = client.get(
            "/admin/ping",
            headers={"Authorization": "Bearer ci-token"},
        )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_public_routes_do_not_require_admin_token() -> None:
    with _client_with_token("ci-token") as client:
        root = client.get("/")
        health = client.get("/health")

    assert root.status_code == 200
    # Health may be 200 or 503 depending on the database; it must not be 401.
    assert health.status_code in {200, 503}
    assert health.status_code != 401
