"""Explicit programme-page notices, independent of fees and intake deadlines.

No network, no inferred 'open' from buttons or dates. Missing, stale or failed
sources remain unverified. This is current-page evidence, not approval for a
particular future intake or an individual student's application.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, tuple_
from sqlalchemy.orm import Session

from app.knowledge.malaysia_programmes import source_for
from app.knowledge.programme_sources import programme_url, title_key
from app.models.knowledge import OfficialPage, OfficialPageVersion

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
        BASE + "undergraduate/jeffrey-cheah-school-medicine-health-sciences/"
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


def evidence(
    title: str,
    page: OfficialPage | None,
    *,
    now: datetime | None = None,
    source_url: str | None = None,
    source_title: str | None = None,
) -> dict:
    now = now or datetime.now(UTC)
    identity = PROGRAMMES.get(normalise(title))
    checked = page.last_checked if page else None
    if checked and checked.tzinfo is None:
        checked = checked.replace(tzinfo=UTC)
    expected_url = (
        programme_url(source_url) if source_url is not None else identity[1] if identity else None
    )
    # A fee-cell link supplies identity only when the indexed programme title
    # independently agrees. Same-title degrees in different schools retain URLs.
    valid_identity = (
        expected_url is not None
        and page is not None
        and page.canonical_url == expected_url
        and bool(source_title)
        and title_key(source_title) == title_key(title)
    )
    observed = notice(page.clean_text or "", title) if valid_identity else "not_verified"
    reason = "not_indexed" if expected_url else "no_reviewed_source"
    if expected_url and page is not None and not valid_identity:
        reason = "source_identity_mismatch"
    fresh = False
    if valid_identity:
        if page.status != "ok" or page.fetch_error or page.requires_sign_in:
            reason = "source_unavailable"
        elif checked is None or checked > now or now - checked > MAX_AGE:
            reason = "stale_source"
        else:
            fresh = True
            reason = "explicit_notice" if observed in {"open", "closed", "suspended"} else observed
    course_code = _course_code(page) if valid_identity else None
    if course_code is None and source_url is None:
        course_code = PROGRAMME_CODES.get(normalise(title))
    return {
        "course_code": course_code,
        "programme_page_verified": fresh,
        "identity_basis": "programme_version_title_and_source_url",
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


def _source_titles(db: Session, pages: list[OfficialPage]) -> dict[int, str | None]:
    """Read fetched titles for current hashes in one query, never seed labels."""
    pairs = [(p.id, p.content_hash) for p in pages if p.content_hash]
    if not pairs:
        return {}
    rows = db.execute(
        select(OfficialPageVersion.page_id, OfficialPageVersion.title).where(
            tuple_(OfficialPageVersion.page_id, OfficialPageVersion.content_hash).in_(pairs)
        ).order_by(OfficialPageVersion.id)
    ).all()
    return dict(rows)


def _row_source(row: dict) -> tuple[str | None, bool]:
    reviewed = source_for(row["title"], row.get("school", ""))
    published = programme_url(row.get("programme_url"))
    curated = PROGRAMMES.get(normalise(row["title"]), (None, None))[1]
    approved = reviewed or curated
    return approved or published, bool(approved and published and approved != published)


def _course_code(page: OfficialPage | None) -> str | None:
    import re
    from urllib.parse import urlsplit

    codes: set[str] = set()

    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get("url"), str):
                u = urlsplit(value["url"])
                if u.scheme == "https" and u.netloc == "handbook.monash.edu":
                    m = re.fullmatch(
                        r"/(?:[0-9]{4}|current)/courses/([A-Z][0-9]{4})/?", u.path, re.I
                    )
                    if m:
                        codes.add(m[1].upper())
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for v in value:
                walk(v)

    walk(getattr(page, "blocks", None))
    return next(iter(codes)) if len(codes) == 1 else None


def for_rows(db: Session, rows: list[dict]) -> dict:
    """Enrich each fee row independently: title alone is not a programme key."""
    urls = {_row_source(row)[0] for row in rows} - {None}
    pages = (
        db.scalars(select(OfficialPage).where(OfficialPage.canonical_url.in_(urls))).all()
        if urls
        else []
    )
    by_url = {p.canonical_url: p for p in pages}
    titles = _source_titles(db, pages)
    for row in rows:
        url, link_conflict = _row_source(row)
        page = by_url.get(url)
        row["admissions"] = evidence(
            row["title"], page, source_url=url,
            source_title=titles.get(page.id) if page else None,
        )
        row["admissions"]["fee_link_conflict"] = link_conflict
    return {
        "rows": len(rows),
        "linked_programme_rows": sum(bool(row["admissions"]["source_url"]) for row in rows),
        "verified_programme_rows": sum(
            row["admissions"]["programme_page_verified"] for row in rows
        ),
        "explicit_notice_rows": sum(
            row["admissions"]["status"] in {"open", "closed", "suspended"} for row in rows
        ),
        "conflict_rows": sum(row["admissions"]["status"] == "conflict" for row in rows),
    }


def for_course(db: Session, title: str, fees: dict | None, campuses: list[str] | None) -> dict:
    if not campuses or not any("malaysia" in campus.casefold() for campus in campuses):
        result = evidence(title, None)
        result.update(
            status="not_verified", reason="campus_not_verified", programme_page_verified=False
        )
        return result
    rows = (fees or {}).get("rows", [])
    urls = {_row_source(row)[0] for row in rows} - {None}
    if len(urls) > 1:
        result = evidence(title, None)
        result.update(
            status="not_verified",
            reason="ambiguous_programme_sources",
            programme_page_verified=False,
        )
        return result
    source_url = next(iter(urls)) if urls else None
    expected = source_url or PROGRAMMES.get(normalise(title), (None, None))[1]
    page = (
        db.scalar(select(OfficialPage).where(OfficialPage.canonical_url == expected))
        if expected
        else None
    )
    titles = _source_titles(db, [page] if page else [])
    result = evidence(title, page, source_url=source_url,
                      source_title=titles.get(page.id) if page else None)
    result["fee_link_conflict"] = any(_row_source(row)[1] for row in rows)
    return result


def for_titles(db: Session, titles: list[str]) -> dict[str, dict]:
    urls = {PROGRAMMES[normalise(t)][1] for t in titles if normalise(t) in PROGRAMMES}
    pages = (
        db.scalars(select(OfficialPage).where(OfficialPage.canonical_url.in_(urls))).all()
        if urls
        else []
    )
    by_url = {p.canonical_url: p for p in pages}
    titles_by_id = _source_titles(db, pages)
    return {
        title: evidence(
            title, page,
            source_title=titles_by_id.get(page.id) if page else None,
        )
        for title in titles
        for page in [by_url.get(PROGRAMMES.get(normalise(title), (None, None))[1])]
    }
