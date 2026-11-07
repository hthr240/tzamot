"""Load a fixed, realistic dataset into the application database.

Run from ``backend/``:

    uv run python scripts/seed_test_db.py

The script replaces rows in the domain tables, then inserts the same set again.
Running it twice leaves the same row counts. Dates are fixed, not "today", so
tests can assert exact days.
"""

from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.core.config import Settings
from app.models import (
    Appointment,
    AppointmentStatus,
    Availability,
    AvailabilityDay,
    Service,
    WeeklyHours,
)

# Sunday 1 November 2026. Two weeks run through Saturday 14 November 2026.
ANCHOR = date(2026, 11, 1)
SPLIT_SHIFT_DAY = date(2026, 11, 3)
CLOSED_DAY = date(2026, 11, 7)
APPOINTMENT_DAY = date(2026, 11, 2)

SERVICES: tuple[tuple[str, int, str], ...] = (
    ("Consultation", 30, "80.00"),
    ("Touch-up", 60, "150.00"),
    ("Cornrows", 90, "250.00"),
    ("Knotless braids", 180, "450.00"),
    ("Box braids", 240, "600.00"),
)


def _weeks() -> list[date]:
    return [ANCHOR + timedelta(days=offset) for offset in range(14)]


def _windows_for(day: date) -> list[tuple[time, time]]:
    if day == CLOSED_DAY:
        return []
    if day == SPLIT_SHIFT_DAY:
        return [(time(9, 0), time(13, 0)), (time(16, 0), time(20, 0))]
    return [(time(9, 0), time(17, 0))]


def _clear(session: Session) -> None:
    session.execute(delete(Appointment))
    session.execute(delete(Availability))
    session.execute(delete(AvailabilityDay))
    session.execute(delete(WeeklyHours))
    session.execute(delete(Service))


def seed(session: Session) -> None:
    """Replace domain rows with the fixed dataset. Does not commit."""
    _clear(session)

    for weekday, start, end in (
        (0, time(9, 0), time(17, 0)),
        (1, time(9, 0), time(17, 0)),
        (2, time(9, 0), time(17, 0)),
        (3, time(9, 0), time(17, 0)),
        (4, time(9, 0), time(17, 0)),
        (5, time(8, 0), time(13, 0)),
    ):
        session.add(WeeklyHours(weekday=weekday, start_time=start, end_time=end))

    services: dict[str, Service] = {}
    for name, duration, price in SERVICES:
        service = Service(
            name=name,
            duration_minutes=duration,
            price=Decimal(price),
            is_active=True,
        )
        services[name] = service
        session.add(service)

    for day in _weeks():
        session.add(AvailabilityDay(date=day, confirmed=True))
        for start, end in _windows_for(day):
            session.add(
                Availability(date=day, start_time=start, end_time=end),
            )

    session.flush()
    touch_up = services["Touch-up"]

    def at(hour: int, minute: int = 0) -> datetime:
        return datetime(
            APPOINTMENT_DAY.year,
            APPOINTMENT_DAY.month,
            APPOINTMENT_DAY.day,
            hour,
            minute,
            tzinfo=UTC,
        )

    session.add_all(
        [
            Appointment(
                service_id=touch_up.id,
                client_name="Dana",
                client_phone="0501111111",
                starts_at=at(9),
                ends_at=at(10),
                status=AppointmentStatus.BOOKED,
            ),
            Appointment(
                service_id=touch_up.id,
                client_name="Noa",
                client_phone="0502222222",
                starts_at=at(10),
                ends_at=at(11),
                status=AppointmentStatus.BOOKED,
            ),
            Appointment(
                service_id=touch_up.id,
                client_name="Maya",
                client_phone="0503333333",
                starts_at=at(13),
                ends_at=at(14),
                status=AppointmentStatus.BOOKED,
            ),
            Appointment(
                service_id=touch_up.id,
                client_name="Yael",
                client_phone="0504444444",
                starts_at=at(15),
                ends_at=at(16),
                status=AppointmentStatus.CANCELLED,
                cancelled_at=at(8),
            ),
        ]
    )
    session.flush()


def main() -> None:
    """Seed the database from ``DATABASE_URL`` and commit."""
    engine = create_engine(
        Settings().database_url,
        poolclass=NullPool,
        pool_pre_ping=True,
    )
    try:
        with Session(engine) as session:
            seed(session)
            session.commit()
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
