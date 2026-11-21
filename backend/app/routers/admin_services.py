"""Admin create/update/deactivate for services."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Service
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/services", tags=["admin-services"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(body: ServiceCreate, db: DbSession) -> Service:
    """Create a service. Soft-disable later with ``is_active=false``."""
    service = Service(
        name=body.name,
        duration_minutes=body.duration_minutes,
        price=body.price,
        is_active=body.is_active,
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    logger.info(
        "service.created id=%s name=%s duration_minutes=%s price=%s is_active=%s",
        service.id,
        service.name,
        service.duration_minutes,
        service.price,
        service.is_active,
    )
    return service


@router.patch("/{service_id}", response_model=ServiceRead)
def update_service(
    service_id: int,
    body: ServiceUpdate,
    db: DbSession,
) -> Service:
    """Update name, price, duration, or active flag."""
    service = db.scalars(select(Service).where(Service.id == service_id)).one_or_none()
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    was_active = service.is_active
    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(service, field, value)

    db.commit()
    db.refresh(service)

    logger.info(
        "service.updated id=%s fields=%s",
        service.id,
        ",".join(sorted(updates)) or "-",
    )
    if was_active and service.is_active is False:
        logger.info("service.disabled id=%s name=%s", service.id, service.name)

    return service
