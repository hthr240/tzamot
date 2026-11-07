"""The shared seed dataset is deterministic and idempotent."""

from collections import Counter
from datetime import time

from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models import (
    Appointment,
    AppointmentStatus,
    Availability,
    AvailabilityDay,
    Base,
    Service,
)
from scripts.seed_test_db import CLOSED_DAY, SPLIT_SHIFT_DAY, seed


def test_seed_counts_and_calendar_facts(
    test_engine: Engine,
    db_session: Session,
) -> None:
    Base.metadata.create_all(test_engine)
    seed(db_session)
    seed(db_session)

    services = db_session.scalars(
        select(Service).order_by(Service.duration_minutes)
    ).all()
    assert len(services) == 5
    assert services[0].duration_minutes == 30
    assert services[-1].duration_minutes == 240
    assert all(30 <= service.duration_minutes <= 240 for service in services)

    days = db_session.scalars(select(AvailabilityDay)).all()
    assert len(days) == 14

    windows_by_day = Counter(db_session.scalars(select(Availability.date)).all())
    assert windows_by_day[SPLIT_SHIFT_DAY] == 2
    assert windows_by_day[CLOSED_DAY] == 0
    split_windows = db_session.scalars(
        select(Availability)
        .where(Availability.date == SPLIT_SHIFT_DAY)
        .order_by(Availability.start_time)
    ).all()
    assert (split_windows[0].start_time, split_windows[0].end_time) == (
        time(9, 0),
        time(13, 0),
    )
    assert (split_windows[1].start_time, split_windows[1].end_time) == (
        time(16, 0),
        time(20, 0),
    )

    appointments = db_session.scalars(
        select(Appointment).order_by(Appointment.starts_at)
    ).all()
    booked = [row for row in appointments if row.status == AppointmentStatus.BOOKED]
    cancelled = [
        row for row in appointments if row.status == AppointmentStatus.CANCELLED
    ]
    assert len(booked) == 3
    assert len(cancelled) == 1
    assert booked[0].ends_at == booked[1].starts_at
    assert booked[2].starts_at.hour == 13
    assert cancelled[0].cancelled_at is not None

    assert db_session.scalar(select(func.count()).select_from(Service)) == 5
