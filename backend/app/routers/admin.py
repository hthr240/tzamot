"""Protected admin API surface under ``/admin``."""

from fastapi import APIRouter, Depends

from app.core.auth import require_admin
from app.routers.admin_services import router as admin_services_router

# Router-level dependency covers every route mounted under this prefix.
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)
router.include_router(admin_services_router)


@router.get("/ping")
def admin_ping() -> dict[str, str]:
    """Lightweight auth check used by tests and the admin UI later."""
    return {"status": "ok"}
