"""Public services list (active only)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Service
from app.schemas.service import ServiceRead

router = APIRouter(prefix="/services", tags=["services"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[ServiceRead])
def list_active_services(db: DbSession) -> list[Service]:
    """Return only services clients can book."""
    return list(
        db.scalars(
            select(Service).where(Service.is_active.is_(True)).order_by(Service.id)
        ).all()
    )
