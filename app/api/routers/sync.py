from fastapi import APIRouter, Depends, HTTPException, Query
import logging
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import get_settings
from app.core.database import get_catalog_db
from app.models.user import User
from app.repositories.sync_repository import SyncRepository
from app.services.sync_service import SyncService

router = APIRouter(prefix="/api/v1/sync", tags=["Sync"])
logger = logging.getLogger("sync")


@router.get("/{table_name}")
def get_sync_table_data(
    table_name: str,
    since: str = Query(...),
    limit: int = Query(default=1000, ge=1, le=5000),
    cursor: str | None = Query(default=None),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_catalog_db),
):
    settings = get_settings()
    service = SyncService(
        repository=SyncRepository(
            db=db,
            database_name=settings.catalog_mysql_db,
        )
    )
    try:
        result = service.get_table_sync_page(
            table_name=table_name,
            since=since,
            limit=limit,
            cursor=cursor,
        )
        logger.info(
            "sync table=%s since=%s limit=%s cursor=%s count=%s next_cursor=%s max_updated_at=%s",
            table_name,
            since,
            limit,
            cursor,
            result.get("count"),
            result.get("next_cursor"),
            result.get("max_updated_at"),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
