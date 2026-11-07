"""Create and read Service rows against the isolated test database."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models import Base, Service


def test_service_create_and_read(test_engine: Engine, db_session: Session) -> None:
    Base.metadata.create_all(test_engine, tables=[Service.__table__])

    service = Service(
        name="Box braids",
        duration_minutes=240,
        price=Decimal("600.00"),
    )
    db_session.add(service)
    db_session.flush()

    loaded = db_session.scalars(select(Service).where(Service.id == service.id)).one()

    assert loaded.name == "Box braids"
    assert loaded.duration_minutes == 240
    assert loaded.price == Decimal("600.00")
    assert loaded.is_active is True
    assert loaded.created_at is not None
    assert loaded.updated_at is not None
