"""Bookable time windows on a specific date."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.availability_day import AvailabilityDay


class Availability(Base):
    """One working window clients can book into. Several rows = split shift."""

    __tablename__ = "availability"
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="availability_window_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(
        Date,
        ForeignKey("availability_days.date", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    day: Mapped[AvailabilityDay] = relationship(
        "AvailabilityDay",
        back_populates="windows",
    )
