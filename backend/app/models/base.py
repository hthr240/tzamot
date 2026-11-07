"""Shared SQLAlchemy declarative base for all table models."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Stable names help Alembic generate readable migrations later (#20).
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class every mapped table inherits from."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
