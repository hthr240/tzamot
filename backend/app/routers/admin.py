"""Protected admin API surface under ``/admin``."""

from fastapi import APIRouter, Depends

from app.core.auth import require_admin

# Router-level dependency covers every route mounted under this prefix.
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/ping")
def admin_ping() -> dict[str, str]:
    """Lightweight auth check used by tests and the admin UI later."""
    return {"status": "ok"}
