"""Create and read Appointment rows against the isolated test database."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models import Appointment, AppointmentStatus, Base, Service


def test_appointment_create_and_read(
    test_engine: Engine,
    db_session: Session,
) -> None:
    Base.metadata.create_all(
        test_engine,
        tables=[Service.__table__, Appointment.__table__],
    )

    service = Service(
        name="Cornrows",
        duration_minutes=90,
        price=Decimal("250.00"),
    )
    db_session.add(service)
    db_session.flush()

    starts_at = datetime(2026, 11, 8, 9, 0, tzinfo=UTC)
    appointment = Appointment(
        service_id=service.id,
        client_name="Dana",
        client_phone="0501234567",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(minutes=90),
        status=AppointmentStatus.BOOKED,
    )
    db_session.add(appointment)
    db_session.flush()

    loaded = db_session.scalars(
        select(Appointment).where(Appointment.id == appointment.id)
    ).one()

    assert loaded.client_name == "Dana"
    assert loaded.client_phone == "0501234567"
    assert loaded.status == AppointmentStatus.BOOKED
    assert loaded.service_id == service.id
    assert loaded.service.name == "Cornrows"
    assert loaded.cancelled_at is None
    assert loaded.starts_at == starts_at
