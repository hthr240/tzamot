"""Default weekly working-hours template (ADR-008)."""

from datetime import time

from sqlalchemy import CheckConstraint, SmallInteger, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class WeeklyHours(Base):
    """One window in the owner's default week. Weekday 0 = Sunday."""

    __tablename__ = "weekly_hours"
    __table_args__ = (
        CheckConstraint("weekday >= 0 AND weekday <= 6", name="weekday_range"),
        CheckConstraint("end_time > start_time", name="weekly_window_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    weekday: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
