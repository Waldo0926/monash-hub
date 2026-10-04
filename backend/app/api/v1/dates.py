"""Upcoming key dates for one campus, read from the official date pages."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.knowledge import key_dates

router = APIRouter(tags=["guides"])


@router.get("/key-dates")
def list_key_dates(
    campus: str = Query("malaysia", pattern="^(australia|malaysia)$"),
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db),
) -> dict:
    return key_dates.collect(db, campus, limit)
