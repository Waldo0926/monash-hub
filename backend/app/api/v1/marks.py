"""What the WAM/GPA calculator needs from the server.

Two things, and deliberately not a third: the scoring tables, and the credit
points and level of a list of units.

**The calculator does its own arithmetic.** It fetches these tables once and
computes in the browser, which means a student's marks never reach this server -
no request body full of somebody's failed unit, nothing in an access log. The
maths it runs is two weighted averages; the part worth being careful about is
the tables, and those are pinned by `tests/test_marks.py` against Monash's own
worked examples.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.knowledge import marks
from app.models.handbook import Unit

router = APIRouter(prefix="/marks", tags=["marks"])

# A transcript is a few dozen units; a request for more than this is not a
# student pasting their results.
MAX_LOOKUP = 120

LEVEL_PREFIX = "Level "


@router.get("/reference")
def reference() -> dict:
    """The grade scales, mark bands and level weights, with their sources.

    The URLs are in the payload because the calculator shows them: a student
    reading "your GPA is 2.9" deserves a one-click path to the page that says
    why, and we would rather they check us than trust us.
    """
    return {
        **marks.reference(),
        "sources": {
            "wam": "https://www.monash.edu/students/admin/assessments/results/wam",
            "gpa": "https://www.monash.edu/students/admin/assessments/results/gpa",
        },
        "guides": {"wam": "/guides/wam", "gpa": "/guides/gpa"},
    }


@router.get("/units")
def unit_weights(
    codes: str = Query(..., description="Comma separated unit codes"),
    year: int | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """Credit points and level for a list of unit codes.

    This is the bit a generic calculator cannot do. A student types FIT1008 and
    the weighting that decides their WAM - 6 credit points, Level 1, so 0.5 -
    comes from the Handbook rather than from them remembering it.

    An unknown code comes back in ``missing`` rather than silently scoring as
    something. A code that is not in our index is usually an older unit or a
    typo, and both need the student to say what it was worth.
    """
    wanted = [c.strip().upper() for c in codes.split(",") if c.strip()][:MAX_LOOKUP]
    if not wanted:
        return {"results": [], "missing": []}

    resolved = year or get_settings().current_academic_year
    rows = db.scalars(
        select(Unit).where(Unit.unit_code.in_(wanted), Unit.academic_year == resolved)
    ).all()

    found = {}
    for unit in rows:
        found[unit.unit_code] = {
            "unit_code": unit.unit_code,
            "title": unit.title,
            "credit_points": _number(unit.credit_points),
            "level": _level(unit.level),
            "level_weight": (
                marks.FIRST_YEAR_WEIGHT if _level(unit.level) == 1 else marks.OTHER_YEAR_WEIGHT
            ),
        }

    return {
        "academic_year": resolved,
        "results": [found[code] for code in wanted if code in found],
        "missing": [code for code in wanted if code not in found],
    }


def _number(value: str | None) -> float | None:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _level(value: str | None) -> int | None:
    """"Level 1" -> 1. The Handbook stores it as a label, not a number."""
    if not value:
        return None
    text = str(value).strip()
    if text.startswith(LEVEL_PREFIX):
        text = text[len(LEVEL_PREFIX):]
    try:
        return int(text)
    except ValueError:
        return None
