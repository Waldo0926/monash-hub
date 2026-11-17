"""Monash Malaysia tuition fees, read from the indexed fee pages."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.knowledge import admissions, tuition

router = APIRouter(tags=["courses"])


@router.get("/fees")
def list_fees(
    year: int | None = Query(None, ge=1990, le=2100),
    intake: Literal["february", "july", "october"] | None = None,
    campus: Literal["Malaysia"] = "Malaysia",
    db: Session = Depends(get_db),
) -> dict:
    """Every row on /ugfees and /pgfees, grouped the way the pages group them."""
    result = tuition.table(db)
    rows = [
        row
        for section in result["sections"]
        for group in section["schools"]
        for row in group["rows"]
    ]
    result["selection"] = {"year": year, "intake": intake, "campus": campus}
    result["admissions_coverage"] = admissions.for_rows(
        db, rows, intake_year=year, intake_period=intake
    )
    for section in result["sections"]:
        source = result["sources"].get(section["source"], {})
        for group in section["schools"]:
            for row in group["rows"]:
                row["fee_publication"] = fee_publication(row, section.get("year"), year, source)
    return result


def fee_publication(row: dict, published_year: int | None, selected_year: int | None,
                    source: dict, *, now: datetime | None = None) -> dict:
    """Fee evidence is independent from application/intake evidence."""
    now = now or datetime.now(UTC)
    try:
        checked = datetime.fromisoformat(source.get("last_checked") or "")
        if checked.tzinfo is None:
            checked = checked.replace(tzinfo=UTC)
    except ValueError:
        checked = None
    reason = None
    if published_year is None:
        reason = "unknown_fee_year"
    elif selected_year is not None and published_year != selected_year:
        reason = "different_fee_year"
    elif row.get("unreadable") or row.get("basis") not in {"per_year", "full_course"}:
        reason = "unreadable_fee"
    elif source.get("refresh_failed"):
        reason = "refresh_failed"
    elif checked is None or checked > now or now - checked > admissions.MAX_AGE:
        reason = "stale_source"
    return {
        "status": "not_verified" if reason else "published",
        "reason": reason, "published_year": published_year, "selected_year": selected_year,
        "campus": "Malaysia", "basis": row.get("basis"),
        "source_url": source.get("url"), "source_hash": source.get("source_hash"),
        "last_checked": source.get("last_checked"),
    }
