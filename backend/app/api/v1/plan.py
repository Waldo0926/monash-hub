"""Course plan checking."""
from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.handbook import plan as planner

router = APIRouter(prefix="/plan", tags=["plan"])


@router.post("/check")
def check_plan(
    body: dict = Body(...),
    db: Session = Depends(get_db),
) -> dict:
    """Check a plan and return every finding, without storing anything.

    The plan lives in the reader's browser. Checking it needs the Handbook and
    nothing about the reader, so this takes the plan as an argument rather than
    requiring an account - a planner you have to sign up for is a planner most
    students will not open.
    """
    year = body.get("year") or get_settings().current_academic_year
    return planner.check(
        db,
        body.get("entries") or [],
        academic_year=int(year),
        campus=(body.get("campus") or None),
    )
