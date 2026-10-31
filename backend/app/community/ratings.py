"""Averages of student ratings, for the places that show a unit's stars.

Computed on read with one grouped query. A unit has tens of ratings, not
thousands, and a stored average is one more number that can drift from the
rows it summarises.
"""
from __future__ import annotations

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.review import SCORES, UnitReview

# Fewer ratings than this and a unit shows its count but not a sort position:
# one 5-star rating should not put a unit at the top of "highest rated".
MIN_FOR_RANKING = 3


def _visible():
    return UnitReview.is_hidden.is_(False)


def summaries(db: Session, codes: list[str]) -> dict[str, dict]:
    """``{code: {"average": 4.2, "count": 7}}`` for each code with a visible rating."""
    if not codes:
        return {}
    rows = db.execute(
        select(UnitReview.unit_code, func.avg(UnitReview.overall), func.count(UnitReview.id))
        .where(UnitReview.unit_code.in_(codes), _visible())
        .group_by(UnitReview.unit_code)
    ).all()
    return {
        code: {"average": round(float(avg), 2), "count": int(count)}
        for code, avg, count in rows
    }


def detail(db: Session, code: str) -> dict:
    """Everything the unit page draws above the list of reviews."""
    scores = SCORES
    row = db.execute(
        select(
            func.count(UnitReview.id),
            *(func.avg(getattr(UnitReview, name)) for name in scores),
            *(func.count(getattr(UnitReview, name)) for name in scores[1:]),
            *(func.sum(case((UnitReview.overall == star, 1), else_=0)) for star in range(1, 6)),
        ).where(UnitReview.unit_code == code, _visible())
    ).one()
    count = int(row[0] or 0)
    averages = row[1:7]
    answered = row[7:12]
    stars = row[12:17]
    return {
        "count": count,
        "average": round(float(averages[0]), 2) if count else None,
        # Each dimension is optional when rating, so each has its own count;
        # an average of two answers is labelled as two, not as the unit's total.
        "dimensions": {
            name: {
                "average": round(float(avg), 2) if avg is not None else None,
                "count": int(n or 0),
            }
            for name, avg, n in zip(scores[1:], averages[1:], answered, strict=True)
        },
        "distribution": {
            str(star): int(n or 0) for star, n in zip(range(1, 6), stars, strict=True)
        },
    }
