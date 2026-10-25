"""The searches people make, counted by day, for the home page to show.

The home page used to list six searches to try that someone had typed into
the code, under a label that made them sound like statistics. These are the
statistics. A term is counted when a search for it found something, once per
search, in a row that holds the term, the day and a count and nothing else.

What is shown is the top few terms of the last two weeks. Two guards keep one
person from putting words on the home page: a day counts for at most
DAILY_CAP searches of a term, and a term has to have been searched on two
different days. Terms that look like something personal (an address, a long
number, a sentence) are never counted at all.
"""
from __future__ import annotations

import logging
import re
import time
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.search_terms import SearchTerm

log = logging.getLogger(__name__)

MIN_LENGTH = 2
MAX_LENGTH = 60
MAX_WORDS = 4
# The window the home page reads, how many searches of a term one day may add,
# and on how many different days a term must have been searched to be shown.
DAYS = 14
DAILY_CAP = 20
MIN_DAYS = 2
# Rows older than this are dropped when the list is next rebuilt.
KEEP_DAYS = 60
CACHE_SECONDS = 600

_CODE = re.compile(r"^(?:[a-z]{3}\d{4}|[a-z]\d{4})$")
_LONG_NUMBER = re.compile(r"\d{6,}")

_cache: dict[int, tuple[float, list[dict]]] = {}


def normalise(query: str) -> str | None:
    """The term to count, or None when the query is not one to keep."""
    term = " ".join(query.split())
    if not MIN_LENGTH <= len(term) <= MAX_LENGTH:
        return None
    if len(term.split()) > MAX_WORDS:
        return None
    # An email address, a phone or student number, a pasted link: none of them
    # is a search anyone else should see, whatever it found.
    if "@" in term or "://" in term or _LONG_NUMBER.search(term):
        return None
    return term


def label_for(term: str) -> str:
    """How the term reads on the page: codes in capitals, the rest as typed."""
    return term.upper() if _CODE.match(term.lower()) else term


def record(db: Session, query: str) -> None:
    """Count one search of ``query`` today. Never raises: a count is not worth a failed search."""
    term = normalise(query)
    if term is None:
        return
    key = term.lower()
    try:
        statement = insert(SearchTerm).values(
            term=key, label=label_for(term), day=date.today(), hits=1
        )
        statement = statement.on_conflict_do_update(
            constraint="uq_search_terms_term_day", set_={"hits": SearchTerm.hits + 1}
        )
        db.execute(statement)
        db.commit()
    except Exception:
        log.warning("could not count search term", exc_info=True)
        db.rollback()


def popular(db: Session, limit: int = 6, *, today: date | None = None) -> list[dict]:
    """The most searched terms of the last DAYS days, most searched first."""
    now = time.monotonic()
    cached = _cache.get(limit)
    if cached and cached[0] > now and today is None:
        return cached[1]

    day = today or date.today()
    since = day - timedelta(days=DAYS - 1)
    capped = func.sum(func.least(SearchTerm.hits, DAILY_CAP))
    rows = db.execute(
        select(SearchTerm.term, func.max(SearchTerm.label), capped.label("hits"))
        .where(SearchTerm.day >= since)
        .group_by(SearchTerm.term)
        .having(func.count(func.distinct(SearchTerm.day)) >= MIN_DAYS)
        .order_by(capped.desc(), SearchTerm.term)
        .limit(limit)
    ).all()
    found = [{"term": term, "label": label, "hits": int(hits)} for term, label, hits in rows]

    try:
        db.query(SearchTerm).filter(SearchTerm.day < day - timedelta(days=KEEP_DAYS)).delete()
        db.commit()
    except Exception:
        log.warning("could not prune search terms", exc_info=True)
        db.rollback()

    if today is None:
        _cache[limit] = (now + CACHE_SECONDS, found)
    return found


def clear_cache() -> None:
    _cache.clear()
