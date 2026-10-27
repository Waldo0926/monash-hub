"""Seed pages that are due on one host, for a harvest read on another machine.

    python -m crawler.official.due www.monash.edu.my
    deployment/crawl.sh official-due www.monash.edu.my

Prints their slugs on one line, comma separated, for
``crawler.official.harvest --slugs``. Nothing is printed when none are due.

With OFFICIAL_FETCH=harvest the server stops reading pages, but which pages
are due is still its decision: the refresh tiers and the last good read live
on its page rows. A harvest of every page each day would ask Monash for about
1,450 pages per site where the tiers ask for a few hundred.
"""
from __future__ import annotations

import sys
from collections.abc import Iterable, Mapping
from datetime import datetime
from urllib.parse import urlparse

from crawler.official.seeds import SEEDS, Seed
from crawler.sync.refresh import is_due


def due_slugs(seeds: Iterable[Seed], pages: Mapping[str, object], host: str,
              *, now: datetime | None = None) -> list[str]:
    """``pages`` maps a canonical URL to its ``official_pages`` row. A seed with
    no row yet is due: the import registers it before storing it."""
    found = []
    for seed in seeds:
        if seed.sign_in or urlparse(seed.url).netloc != host:
            continue
        page = pages.get(seed.url)
        if page is None or is_due(page, now=now):
            found.append(seed.slug)
    return found


def main(host: str) -> None:
    from app.core.db import SessionLocal
    from app.models.knowledge import OfficialPage
    from sqlalchemy import select

    with SessionLocal() as db:
        pages = {page.canonical_url: page for page in db.scalars(select(OfficialPage))}
        print(",".join(due_slugs(SEEDS, pages, host)))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m crawler.official.due HOST")
    main(sys.argv[1])
