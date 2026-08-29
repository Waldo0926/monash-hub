"""Flatten the stored Chinese onto the rows search actually queries.

    python -m app.search.reindex_zh                # everything
    python -m app.search.reindex_zh --what units
    python -m app.search.reindex_zh --stats        # what is indexed, no writes

Run it after a translation batch and after a crawl. A translation lives in
`content_translations`, keyed by target type and slug; search runs against
`units` and `official_pages`. Joining the two per query would mean a JSONB scan
on every search, so the text is copied onto the row once and indexed there.

That copy is a denormalisation, and the honest cost of one is that it goes
stale. Two things keep it cheap: it is idempotent, so running it twice is free,
and it only writes rows whose text actually changed, so a re-run after a crawl
that changed nothing writes nothing.

What goes in: every Chinese string the row has - the translated title, summary,
and every value in the string maps that translate its body. Not the English.
The English is already in `search_vector`, and duplicating it here would make
`search_zh` match English queries too and quietly double-rank them.
"""
from __future__ import annotations

import argparse
import logging
import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.handbook import Unit
from app.models.knowledge import OfficialPage
from app.models.translation import OFFICIAL_PAGE, PUBLISHED, UNIT, ContentTranslation
from app.search.chinese import has_cjk

log = logging.getLogger("reindex-zh")

# One row's worth of Chinese. Past this a page contributes more noise to every
# trigram query than it can possibly repay, and the first few thousand
# characters of a page are the part somebody searches for.
MAX_CHARS = 12_000

WHITESPACE = re.compile(r"\s+")


def _strings_from(row: ContentTranslation) -> list[str]:
    """The Chinese in one translation row, whatever shape it is stored in."""
    out: list[str] = []
    if row.text:
        out.append(row.text)
    data = row.data or {}
    strings = data.get("strings")
    if isinstance(strings, dict):
        out.extend(v for v in strings.values() if isinstance(v, str))
    return out


def _flatten(strings: list[str]) -> str | None:
    """One searchable blob, deduplicated and capped.

    Deduplicated because a page's grade name appears in every table on it, and
    a hundred copies of 高分优秀 makes the trigram index work harder for the
    same answer.
    """
    seen: set[str] = set()
    parts: list[str] = []
    total = 0
    for value in strings:
        text = WHITESPACE.sub(" ", value).strip()
        # Only Chinese is worth storing: the English is already in the tsvector.
        if not text or text in seen or not has_cjk(text):
            continue
        seen.add(text)
        parts.append(text)
        total += len(text)
        if total >= MAX_CHARS:
            break
    return " ".join(parts)[:MAX_CHARS] or None


def _translations_by_key(db: Session, target_type: str, locale: str) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    rows = db.scalars(
        select(ContentTranslation).where(
            ContentTranslation.locale == locale,
            ContentTranslation.status == PUBLISHED,
            ContentTranslation.target_type == target_type,
        )
    )
    for row in rows:
        grouped.setdefault(row.target_key, []).extend(_strings_from(row))
    return grouped


def reindex_units(db: Session, locale: str = "zh") -> tuple[int, int]:
    grouped = _translations_by_key(db, UNIT, locale)
    changed = 0
    total = 0
    for unit in db.scalars(select(Unit)):
        total += 1
        wanted = _flatten(grouped.get(unit.unit_code, []))
        if unit.search_zh != wanted:
            unit.search_zh = wanted
            changed += 1
    return changed, total


def reindex_official(db: Session, locale: str = "zh") -> tuple[int, int]:
    grouped = _translations_by_key(db, OFFICIAL_PAGE, locale)
    changed = 0
    total = 0
    for page in db.scalars(select(OfficialPage)):
        total += 1
        wanted = _flatten(grouped.get(page.slug, []))
        if page.search_zh != wanted:
            page.search_zh = wanted
            changed += 1
    return changed, total


def _count(db: Session, model, *where) -> int:
    return int(db.scalar(select(func.count()).select_from(model).where(*where)) or 0)


def stats(db: Session) -> dict[str, int]:
    return {
        "units": _count(db, Unit),
        "units_indexed": _count(db, Unit, Unit.search_zh.is_not(None)),
        "pages": _count(db, OfficialPage),
        "pages_indexed": _count(db, OfficialPage, OfficialPage.search_zh.is_not(None)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--what", default="all", choices=["units", "guides", "all"])
    parser.add_argument("--locale", default="zh")
    parser.add_argument("--stats", action="store_true", help="report coverage, write nothing")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    with SessionLocal() as db:
        if args.stats:
            log.info("coverage: %s", stats(db))
            return
        if args.what in ("units", "all"):
            changed, total = reindex_units(db, args.locale)
            log.info("units: %d of %d rewritten", changed, total)
        if args.what in ("guides", "all"):
            changed, total = reindex_official(db, args.locale)
            log.info("official pages: %d of %d rewritten", changed, total)
        db.commit()
        log.info("coverage: %s", stats(db))


if __name__ == "__main__":
    main()
