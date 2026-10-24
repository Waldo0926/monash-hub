"""Noticing that Monash has taken something out of the Handbook.

Nothing did. A unit or degree removed upstream stayed ``is_active`` here for
good, so the site kept listing a degree the Handbook answers with a 404 -
E7003 was one, found by the first scheduled refresh on 27 Sep 2026.

Only a 404 counts. A timeout or a DNS failure says nothing about the page, and
the rule that a failed crawl never overwrites good data still holds: the row is
kept exactly as it was, only marked inactive, and a later 200 makes it active
again through the normal upsert. Past ``withdrawal_cap`` a run stops acting
on 404s at all: the rest are recorded as failed and the rows stay active.
"""
from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.orm import Session

#: Fewest withdrawals one run may make, and the share of its targets above that.
#: Monash retires a handful of units a year; a run that sees hundreds of 404s is
#: looking at a Handbook outage or a changed URL scheme, and believing it would
#: take every unit off the site until the next week's crawl put them back.
WITHDRAWAL_FLOOR = 25
WITHDRAWAL_SHARE = 0.02


def withdrawal_cap(targets: int) -> int:
    """How many 404s one run of ``targets`` pages may act on."""
    return max(WITHDRAWAL_FLOOR, int(targets * WITHDRAWAL_SHARE))


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
