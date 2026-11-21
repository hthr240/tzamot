"""Services API: public active list and admin create/update/disable."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.db import get_db
from app.main import create_app
from app.models import Base, Service
from tests.conftest import get_test_database_url

ADMIN_HEADERS = {"Authorization": "Bearer test-admin-token"}


@pytest.fixture
def services_client(
    test_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    """API client with a savepoint session so route commits still roll back."""
    Base.metadata.create_all(test_engine, tables=[Service.__table__])
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(
        env="local",
        database_url=get_test_database_url(),
        log_level="INFO",
        admin_token="test-admin-token",
        _env_file=None,
    )
    app = create_app(settings)

    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        autoflush=False,
        autocommit=False,
        join_transaction_mode="create_savepoint",
    )

    def override_get_db() -> Iterator[Session]:
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        session.close()
        transaction.rollback()
        connection.close()


def test_list_services_returns_only_active(services_client: TestClient) -> None:
    # CI seeds realistic services; use unique names and assert filter behaviour.
    inactive = services_client.post(
        "/admin/services",
        headers=ADMIN_HEADERS,
        json={
            "name": "CI inactive twist",
            "duration_minutes": 240,
            "price": "600.00",
        },
    )
    assert inactive.status_code == 201
    inactive_id = inactive.json()["id"]

    services_client.patch(
        f"/admin/services/{inactive_id}",
        headers=ADMIN_HEADERS,
        json={"is_active": False},
    )
    active = services_client.post(
        "/admin/services",
        headers=ADMIN_HEADERS,
        json={
            "name": "CI active twist",
            "duration_minutes": 60,
            "price": "120.00",
        },
    )
    assert active.status_code == 201

    response = services_client.get("/services")
    assert response.status_code == 200
    names = [row["name"] for row in response.json()]
    assert "CI active twist" in names
    assert "CI inactive twist" not in names


def test_create_and_update_service_price(
    services_client: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO, logger="app.routers.admin_services"):
        created = services_client.post(
            "/admin/services",
            headers=ADMIN_HEADERS,
            json={
                "name": "Box braids",
                "duration_minutes": 240,
                "price": "600.00",
            },
        )
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "Box braids"
    assert body["duration_minutes"] == 240
    assert Decimal(body["price"]) == Decimal("600.00")
    assert body["is_active"] is True
    assert "service.created" in caplog.text

    with caplog.at_level(logging.INFO, logger="app.routers.admin_services"):
        updated = services_client.patch(
            f"/admin/services/{body['id']}",
            headers=ADMIN_HEADERS,
            json={"price": "650.00"},
        )
    assert updated.status_code == 200
    assert Decimal(updated.json()["price"]) == Decimal("650.00")
    assert "service.updated" in caplog.text


def test_disable_service_hides_from_public_list(
    services_client: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    created = services_client.post(
        "/admin/services",
        headers=ADMIN_HEADERS,
        json={
            "name": "CI disable me",
            "duration_minutes": 180,
            "price": "450.00",
        },
    )
    service_id = created.json()["id"]
    assert any(
        row["id"] == service_id for row in services_client.get("/services").json()
    )

    with caplog.at_level(logging.INFO, logger="app.routers.admin_services"):
        disabled = services_client.patch(
            f"/admin/services/{service_id}",
            headers=ADMIN_HEADERS,
            json={"is_active": False},
        )
    assert disabled.status_code == 200
    assert disabled.json()["is_active"] is False
    assert "service.disabled" in caplog.text

    listed = services_client.get("/services")
    assert listed.status_code == 200
    assert all(row["id"] != service_id for row in listed.json())


def test_create_requires_admin_token(services_client: TestClient) -> None:
    response = services_client.post(
        "/admin/services",
        json={
            "name": "Box braids",
            "duration_minutes": 240,
            "price": "600.00",
        },
    )
    assert response.status_code == 401


def test_validation_rejects_non_positive_duration(
    services_client: TestClient,
) -> None:
    response = services_client.post(
        "/admin/services",
        headers=ADMIN_HEADERS,
        json={
            "name": "Bad",
            "duration_minutes": 0,
            "price": "10.00",
        },
    )
    assert response.status_code == 422


def test_validation_rejects_negative_price(services_client: TestClient) -> None:
    response = services_client.post(
        "/admin/services",
        headers=ADMIN_HEADERS,
        json={
            "name": "Bad",
            "duration_minutes": 30,
            "price": "-1.00",
        },
    )
    assert response.status_code == 422


def test_update_missing_service_returns_404(services_client: TestClient) -> None:
    response = services_client.patch(
        "/admin/services/999999",
        headers=ADMIN_HEADERS,
        json={"name": "Missing"},
    )
    assert response.status_code == 404
