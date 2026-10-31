"""Course plan checking."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.handbook import plan as planner

router = APIRouter(prefix="/plan", tags=["plan"])


class PlanEntry(BaseModel):
    unit_code: str = Field(max_length=16)
    year: int = Field(ge=1990, le=2100)
    teaching_period: str = Field(max_length=120)


class PlanRequest(BaseModel):
    # Typed, so a malformed plan is a 422 that says what is wrong rather than
    # a 500 from deep inside the checker - "year": "next" used to be the latter.
    entries: list[PlanEntry] = Field(default_factory=list, max_length=planner.MAX_ENTRIES)
    year: int | None = Field(default=None, ge=1990, le=2100)
    campus: str | None = Field(default=None, max_length=64)


@router.post("/check")
def check_plan(
    body: PlanRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Check a plan and return every finding, without storing anything.

    The plan lives in the reader's browser. Checking it needs the Handbook and
    nothing about the reader, so this takes the plan as an argument rather than
    requiring an account - a planner you have to sign up for is a planner most
    students will not open.
    """
    return planner.check(
        db,
        [entry.model_dump() for entry in body.entries],
        academic_year=body.year or get_settings().current_academic_year,
        campus=body.campus or None,
    )
