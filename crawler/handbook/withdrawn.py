"""Noticing that Monash has taken something out of the Handbook.

Nothing did. A unit or degree removed upstream stayed ``is_active`` here for
good, so the site kept listing a degree the Handbook answers with a 404 -
E7003 was one, found by the first scheduled refresh on 27 Sep 2026.

Only a 404 counts. A timeout or a DNS failure says nothing about the page, and
the rule that a failed crawl never overwrites good data still holds: the row is
kept exactly as it was, only marked inactive, and a later 200 makes it active
again through the normal upsert.
"""
from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.orm import Session


def mark_withdrawn(db: Session, model, code_column: str, code: str, year: int) -> bool:
    """Mark one row inactive. True when it was active until now."""
    column = getattr(model, code_column)
    result = db.execute(
        update(model)
        .where(column == code, model.academic_year == year, model.is_active.is_(True))
        .values(is_active=False)
    )
    db.commit()
    return bool(result.rowcount)


def recheck_candidates(db: Session, model, code_column: str, year: int,
                       discovered: list[str]) -> list[str]:
    """Active rows the Handbook index no longer lists.

    They are fetched once more rather than retired on the index's word alone -
    the index has been incomplete before - so only the page's own 404 retires
    them.
    """
    column = getattr(model, code_column)
    known = set(discovered)
    active = db.scalars(
        select(column).where(model.academic_year == year, model.is_active.is_(True))
    ).all()
    return sorted(code for code in active if code not in known)
