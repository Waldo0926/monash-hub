"""Explicit programme-page notices, independent of fees and intake deadlines.

No network, no inferred 'open' from buttons or dates. Missing, stale or failed
sources remain unverified. This is current-page evidence, not approval for a
particular future intake or an individual student's application.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge import OfficialPage

BASE = "https://www.monash.edu.my/study/"
# Curated identity matches only. Similar titles/honours degrees never inherit
# another programme's notice. Expand only after reviewing the original page.
PROGRAMMES = {
    "master of professional counselling": (
        "malaysia-programme-professional-counselling",
        BASE
        + "postgraduate-and-research/medicine-health-sciences/master-of-professional-counselling",
    ),
    "bachelor of psychology": (
        "malaysia-programme-psychology",
        BASE + "undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-of-psychology",
    ),
    "bachelor of psychology and business": (
        "malaysia-programme-psychology-business",
        BASE
        + "undergraduate/jeffrey-cheah-school-medicine-health-sciences/"
        "bachelor-psychology-and-business",
    ),
}
# Codes linked by each programme's official Handbook link (reviewed 2026-11-03).
PROGRAMME_CODES = {
    "master of professional counselling": "D6006",
    "bachelor of psychology": "M2018",
    "bachelor of psychology and business": "M2015",
}
MAX_AGE = timedelta(days=30)


def normalise(title: str) -> str:
    return " ".join(title.split()).casefold()


def notice(text: str, title: str) -> str:
    """Match a complete, scoped statement; navigation/Apply now is not evidence."""
    subject = re.escape(" ".join(title.split()))
    normalized = "\n".join(" ".join(line.split()) for line in text.splitlines())
    statuses = set()
    for state in ("open", "closed", "suspended"):
        pattern = (
            rf"(?:^|[.!?\n]\s*)Applications\s+for\s+(?:the\s+)?{subject}"
            rf"\s+are\s+(?:currently\s+)?{state}\s*(?:[.!?](?=\s|$)|$)"
        )
        if re.search(pattern, normalized, re.I):
            statuses.add(state)
    return (
        next(iter(statuses)) if len(statuses) == 1 else "conflict" if statuses else "not_verified"
    )


def evidence(title: str, page: OfficialPage | None, *, now: datetime | None = None) -> dict:
    now = now or datetime.now(UTC)
    identity = PROGRAMMES.get(normalise(title))
    checked = page.last_checked if page else None
    if checked and checked.tzinfo is None:
        checked = checked.replace(tzinfo=UTC)
    expected_url = identity[1] if identity else None
    valid_identity = bool(identity) and page is not None and page.canonical_url == expected_url
    observed = notice(page.clean_text or "", title) if valid_identity else "not_verified"
    reason = "not_indexed" if identity else "no_reviewed_source"
    fresh = False
    if valid_identity:
        if page.status != "ok" or page.fetch_error or page.requires_sign_in:
            reason = "source_unavailable"
        elif checked is None or checked > now or now - checked > MAX_AGE:
            reason = "stale_source"
        else:
            fresh = True
            reason = "explicit_notice" if observed in {"open", "closed", "suspended"} else observed
    return {
        "course_code": PROGRAMME_CODES.get(normalise(title)),
        "status": observed if fresh else "not_verified",
        "observed_status": observed,
        "reason": reason,
        "source_url": expected_url,
        "last_checked": checked.isoformat() if checked else None,
        "valid_until": (checked + MAX_AGE).isoformat() if checked else None,
        "source_hash": page.content_hash if valid_identity else None,
        "scope": "current_programme_notice",
        "campus": "Malaysia",
        # A current notice cannot establish a future intake's application state.
        "intake_status": "not_verified",
    }


def for_titles(db: Session, titles: list[str]) -> dict[str, dict]:
    urls = {PROGRAMMES[normalise(t)][1] for t in titles if normalise(t) in PROGRAMMES}
    pages = (
        db.scalars(select(OfficialPage).where(OfficialPage.canonical_url.in_(urls))).all()
        if urls
        else []
    )
    by_url = {p.canonical_url: p for p in pages}
    return {
        title: evidence(title, by_url.get(PROGRAMMES.get(normalise(title), (None, None))[1]))
        for title in titles
    }
