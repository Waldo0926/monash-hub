"""Faculty teach-out notices: which unit closes, and what replaces it.

When a faculty revises its degrees it publishes a table of the units that are
closing, renamed or changing, and the approved replacement for each. Students
read it to learn what to take instead. It is the faculty's own table, so it is
read from the indexed copy of the faculty's page (nothing is typed in here, and
nothing new is fetched at request time) and shown word for word, with the page it
came from and when that page was last checked.

The site never works out a replacement. A row says what the faculty says; a unit
with no row has no notice, which is not the same as being safe to rely on.

A source is one indexed page whose tables hold rows of
``unit code | unit title | change | course - major/specialisation | teach-out plan``.
Other faculties are added by listing their page in ``SOURCES``.

Each campus runs its own table. The Faculty of IT's page on monash.edu is for
the Australian campuses and the School of IT's page on monash.edu.my is for
Malaysia, and they do not agree (FIT1043 is gone in Australia but runs once more
in Malaysia). A page's ``applies_to`` says which campus it speaks for, and a
reader is shown the one for their campus.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge import OfficialPage

#: Slugs of indexed official pages that carry a teach-out table. Seeded in
#: crawler/official/seeds.py.
SOURCES = ("it-undergraduate-re-enrolment", "it-undergraduate-re-enrolment-malaysia")

_CODE = re.compile(r"^[A-Z]{3}\d{4}$")


@dataclass(frozen=True)
class Entry:
    code: str
    title: str
    change: str
    course: str
    plan: str
    source: str


def _clean(cell: str | None) -> str:
    return re.sub(r"[ \t]+", " ", (cell or "").strip())


def parse_rows(rows: list[list[str]], source: str) -> list[Entry]:
    """Entries from one table's rows.

    A row whose first cell is empty continues the unit above it: the faculty
    lists one unit once per course it affects, and the page can render the second
    course as a row of its own. Anything that is not five cells with a unit code
    at the front (headers, the "72 of 72 shown" line) is skipped.
    """
    out: list[Entry] = []
    last: Entry | None = None
    for row in rows:
        cells = [_clean(c) for c in row]
        if len(cells) < 5:
            continue
        code = cells[0]
        if _CODE.match(code):
            last = Entry(code, cells[1], cells[2], cells[3], cells[4], source)
            out.append(last)
        elif not code and last is not None and cells[3]:
            out.append(Entry(last.code, last.title, cells[2] or last.change,
                             cells[3], cells[4], source))
    return out


_cache: dict[tuple[str, str], list[Entry]] = {}


def _entries(page: OfficialPage) -> list[Entry]:
    key = (page.slug, page.content_hash or "")
    if key not in _cache:
        found: list[Entry] = []
        for block in page.blocks or []:
            if block.get("type") == "table":
                found += parse_rows(block.get("rows") or [], page.slug)
        if len(_cache) > 8:
            _cache.clear()
        _cache[key] = found
    return _cache[key]


def region(campus: str | None) -> str | None:
    """The ``applies_to`` value for a Handbook campus name, or None for no campus."""
    if not campus:
        return None
    return "malaysia" if campus == "Malaysia" else "australia"


def lookup(db: Session, codes: list[str], campus: str | None = None) -> dict[str, dict]:
    """``{code: {"entries": [...], "sources": {...}}}`` for the codes that have a notice.

    With a campus, only the pages for that campus (or for every campus) count.
    Without one, every page does, and each entry says which campus it is for.
    """
    wanted = {c.upper() for c in codes}
    if not wanted:
        return {}
    query = select(OfficialPage).where(
        OfficialPage.slug.in_(SOURCES), OfficialPage.status == "ok"
    )
    where = region(campus)
    if where:
        query = query.where(OfficialPage.applies_to.in_((where, "all")))
    pages = sorted(db.scalars(query).all(), key=lambda p: SOURCES.index(p.slug))
    result: dict[str, dict] = {}
    for page in pages:
        meta = {
            "title": page.title,
            "url": page.canonical_url,
            "last_checked": page.last_checked.isoformat() if page.last_checked else None,
            "applies_to": page.applies_to,
        }
        for entry in _entries(page):
            if entry.code not in wanted:
                continue
            slot = result.setdefault(entry.code, {"entries": [], "sources": {}})
            slot["entries"].append({
                "change": entry.change,
                "course": entry.course,
                "plan": entry.plan,
                "source": entry.source,
                "applies_to": page.applies_to,
            })
            slot["sources"][page.slug] = meta
    return result
