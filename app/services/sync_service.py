from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.repositories.sync_repository import SyncRepository

ALLOWED_SYNC_TABLES = {
    "address",
    "billingtomodeofreceipt",
    "compcategory",
    "groupmaster",
    "modeofpayment",
    "panelrates",
    "subgroup",
    "test",
    "testcategory",
    "testprofile",
    "testprofilebreakuptestsdetails",
    "testspecimen",
}

BLOCKED_SYNC_TABLES = {
    "test_warning",
    "address_allowed_center",
}


@dataclass
class ParsedCursor:
    updated_at: datetime | None
    pk_value: str


class SyncService:
    def __init__(self, repository: SyncRepository) -> None:
        self.repository = repository

    def _parse_since(self, since: str) -> datetime:
        try:
            return datetime.fromisoformat(since.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Invalid 'since'. Use ISO-8601, e.g. 2026-01-01T00:00:00Z") from exc

    def _parse_cursor(self, cursor: str) -> ParsedCursor:
        if cursor.startswith("pk:"):
            pk_value = cursor[3:]
            if not pk_value:
                raise ValueError("Invalid 'cursor'. Expected format: pk:<pk_value>")
            return ParsedCursor(updated_at=None, pk_value=pk_value)

        try:
            updated_at_text, pk_value = cursor.split("|", 1)
            updated_at = datetime.fromisoformat(updated_at_text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Invalid 'cursor'. Expected: <iso_datetime>|<pk_value> or pk:<pk_value>") from exc
        return ParsedCursor(updated_at=updated_at, pk_value=pk_value)

    def get_table_sync_page(
        self,
        table_name: str,
        since: str,
        limit: int,
        cursor: str | None,
    ) -> dict[str, Any]:
        if table_name in BLOCKED_SYNC_TABLES:
            raise ValueError(f"Sync is disabled for table '{table_name}'")
        if table_name not in ALLOWED_SYNC_TABLES:
            raise ValueError(f"Unsupported table '{table_name}'")

        since_dt = self._parse_since(since)
        cursor_updated_at = None
        cursor_pk_value = None
        if cursor:
            parsed = self._parse_cursor(cursor)
            cursor_updated_at = parsed.updated_at
            cursor_pk_value = parsed.pk_value

        page = self.repository.fetch_incremental(
            table_name=table_name,
            since=since_dt,
            limit=limit,
            cursor_updated_at=cursor_updated_at,
            cursor_pk_value=cursor_pk_value,
        )

        return {
            "ok": True,
            "table": table_name,
            "since": since,
            "count": len(page.items),
            "items": page.items,
            "next_cursor": page.next_cursor,
            "max_updated_at": page.max_updated_at.isoformat() if page.max_updated_at else None,
        }
