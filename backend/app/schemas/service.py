"""Pydantic schemas for the services API."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    """Body for ``POST /admin/services``."""

    name: str = Field(min_length=1, max_length=255)
    duration_minutes: int = Field(gt=0)
    price: Decimal = Field(ge=0)
    is_active: bool = True


class ServiceUpdate(BaseModel):
    """Body for ``PATCH /admin/services/{id}`` — omit fields you leave unchanged."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    duration_minutes: int | None = Field(default=None, gt=0)
    price: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ServiceRead(BaseModel):
    """Service returned to clients and admins."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    duration_minutes: int
    price: Decimal
    is_active: bool
