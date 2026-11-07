"""One generated calendar date copied from the weekly template."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.availability import Availability


class AvailabilityDay(Base):
    """A concrete date. Confirmed days are not rebuilt when the template changes."""

    __tablename__ = "availability_days"

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    windows: Mapped[list[Availability]] = relationship(
        "Availability",
        back_populates="day",
        cascade="all, delete-orphan",
    )
