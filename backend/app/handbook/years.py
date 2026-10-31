"""Which Handbook year to read a unit, degree or area of study from.

The site follows ``CURRENT_ACADEMIC_YEAR``, and that moves to next year's
Handbook as soon as it is loaded - in October, while students are still sitting
this year's units. Monash renumbers and withdraws units between years: FIT1008
and FIT2004 are in the 2026 Handbook and not in 2027. Reading only the current
year turned every such page, and the prerequisite graph that opens on FIT2004,
into "not found" for a unit a student may be enrolled in right now.

So an address without ``?year=`` falls back to the latest Handbook that does
list the code, and says so: the caller gets the year it was missing from, and
the page tells the reader the content is from an earlier Handbook. An explicit
``?year=`` is a precise question and still gets a plain 404.

The pages also offer a year picker, like the Handbook's own (2025, 2026 and
2027 are loaded): ``available_years`` is what a detail page offers, and
``loaded_years`` what a list page offers.
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.core.config import get_settings


def available_years(
    db: Session, code_column: InstrumentedAttribute, year_column: InstrumentedAttribute, code: str
) -> list[int]:
    """Every loaded Handbook year that lists the code, newest first - the page's year picker."""
    return list(
        db.scalars(
            select(year_column).where(code_column == code.upper()).distinct()
            .order_by(year_column.desc())
        )
    )


def loaded_years(db: Session, year_column: InstrumentedAttribute) -> list[int]:
    """Every Handbook year in the table, newest first - a list page's year picker."""
    return list(db.scalars(select(year_column).distinct().order_by(year_column.desc())))


def resolve_year(
    db: Session,
    code_column: InstrumentedAttribute,
    year_column: InstrumentedAttribute,
    code: str,
    year: int | None,
) -> tuple[int, int | None]:
    """``(year to read, year it is missing from)``; the second is None when nothing fell back."""
    if year is not None:
        return year, None
    current = get_settings().current_academic_year
    code = code.upper()
    if db.scalar(select(year_column).where(code_column == code, year_column == current).limit(1)):
        return current, None
    latest = db.scalar(select(func.max(year_column)).where(code_column == code))
    if latest is None:
        # Nowhere at all: let the caller's 404 name the current year, as before.
        return current, None
    return latest, current
