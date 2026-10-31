"""Official pages that indexed pages link to, but the index does not hold.

    deployment/crawl.sh gaps            # a table, most linked first
    deployment/crawl.sh gaps --json     # the same as JSON

Discovery walks hub pages and reads sitemaps, and some pages are in neither:
the Malaysia re-enrolment dates and the "Let's Begin" pages for new students
were linked from pages we already had, and still missing. This reads only the
database - every link in the stored pages' blocks - and lists the addresses on
Monash's student sites that no seed covers, with how many stored pages point
at each. Nothing is fetched and nothing is written. What to add is decided by
a person, in ``coverage.EXTRA``.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Iterable, Iterator
from urllib.parse import urlparse

from crawler.official.coverage import LEAVE_OUT, outdated
from crawler.official.discover import NOT_FOR_STUDENTS, SITEMAPS, SITES, SKIP, _wanted, normalise

HOSTS = ("www.monash.edu", "www.monash.edu.my")


def links(value: object) -> Iterator[str]:
    """Every ``url`` in a page's blocks, however deep the block nests it."""
    if isinstance(value, dict):
        url = value.get("url")
        if isinstance(url, str):
            yield url
        for key, item in value.items():
            if key != "url":
                yield from links(item)
    elif isinstance(value, list):
        for item in value:
            yield from links(item)


def in_scope(url: str) -> bool:
    """On one of the student sections discovery covers, and a page of guidance."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc not in HOSTS:
        return False
    path = parsed.path
    if SKIP.search(path) or NOT_FOR_STUDENTS.search(path) or LEAVE_OUT.search(path):
        return False
    if outdated(url, ""):
        return False
    if any(_wanted(site, url) for site in SITES.values()):
        return True
    for sitemap in SITEMAPS.values():
        if parsed.netloc in sitemap["hosts"]:
            include = sitemap["include"]
            if include is None or include.search(path):
                return True
    return False


def gaps(pages: Iterable[tuple[str, list]], known: Iterable[str]) -> list[dict]:
    """``pages`` is (slug, blocks) per stored page; ``known`` every address
    already indexed or seeded. Most-linked first."""
    have = {normalise(url).lower() for url in known}
    linked_from: dict[str, set[str]] = defaultdict(set)
    spelling: dict[str, str] = {}
    for slug, blocks in pages:
        for raw in links(blocks):
            url = normalise(raw)
            key = url.lower()
            if key in have or not in_scope(url):
                continue
            spelling.setdefault(key, url)
            linked_from[key].add(slug)
    rows = [{"url": spelling[key], "links": len(slugs), "from": sorted(slugs)[:5]}
            for key, slugs in linked_from.items()]
    return sorted(rows, key=lambda row: (-row["links"], row["url"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="List linked official pages not yet indexed")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a table")
    parser.add_argument("--min-links", type=int, default=1,
                        help="only pages at least this many stored pages link to")
    args = parser.parse_args()

    from app.core.db import SessionLocal
    from app.models.knowledge import OfficialPage
    from sqlalchemy import select

    from crawler.official.seeds import SEEDS

    with SessionLocal() as db:
        stored = db.execute(select(OfficialPage.slug, OfficialPage.canonical_url,
                                   OfficialPage.blocks)).all()
    known = [seed.url for seed in SEEDS] + [url for _, url, _ in stored if url]
    rows = [row for row in gaps(((slug, blocks or []) for slug, _, blocks in stored), known)
            if row["links"] >= args.min_links]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return
    for row in rows:
        print(f"{row['links']:4d}  {row['url']}  <- {', '.join(row['from'])}")
    print(f"{len(rows)} linked pages are not indexed ({len(stored)} stored pages read)")


if __name__ == "__main__":
    main()
