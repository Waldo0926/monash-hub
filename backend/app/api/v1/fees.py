"""Monash Malaysia tuition fees, read from the indexed fee pages."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.knowledge import tuition

router = APIRouter(tags=["courses"])


@router.get("/fees")
def list_fees(db: Session = Depends(get_db)) -> dict:
    """Every row on /ugfees and /pgfees, grouped the way the pages group them."""
    return tuition.table(db)
