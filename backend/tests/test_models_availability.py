"""Create and read weekly-hours and availability rows."""

from datetime import date, time

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models import Availability, AvailabilityDay, Base, WeeklyHours


def test_weekly_hours_create_and_read(
    test_engine: Engine,
    db_session: Session,
) -> None:
    Base.metadata.create_all(test_engine, tables=[WeeklyHours.__table__])

    row = WeeklyHours(
        weekday=0,
        start_time=time(9, 0),
        end_time=time(13, 0),
    )
    db_session.add(row)
    db_session.flush()

    loaded = db_session.scalars(
        select(WeeklyHours).where(WeeklyHours.id == row.id)
    ).one()
    assert loaded.weekday == 0
    assert loaded.start_time == time(9, 0)
    assert loaded.end_time == time(13, 0)


def test_availability_day_with_windows_create_and_read(
    test_engine: Engine,
    db_session: Session,
) -> None:
    Base.metadata.create_all(
        test_engine,
        tables=[AvailabilityDay.__table__, Availability.__table__],
    )

    day = AvailabilityDay(date=date(2026, 11, 8), confirmed=False)
    morning = Availability(
        date=day.date,
        start_time=time(9, 0),
        end_time=time(13, 0),
    )
    afternoon = Availability(
        date=day.date,
        start_time=time(16, 0),
        end_time=time(20, 0),
    )
    db_session.add_all([day, morning, afternoon])
    db_session.flush()

    loaded_day = db_session.get(AvailabilityDay, date(2026, 11, 8))
    assert loaded_day is not None
    assert loaded_day.confirmed is False
    assert len(loaded_day.windows) == 2

    windows = db_session.scalars(
        select(Availability)
        .where(Availability.date == date(2026, 11, 8))
        .order_by(Availability.start_time)
    ).all()
    assert windows[0].start_time == time(9, 0)
    assert windows[1].start_time == time(16, 0)
