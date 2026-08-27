"""Official Knowledge Seed crawl runner.

    python -m crawler.official.run --register        # write the seed list only
    python -m crawler.official.run --all             # fetch every seed
    python -m crawler.official.run                   # fetch only pages that are due
    python -m crawler.official.run --slugs wam,gpa

Default behaviour is "only what is due": a page whose refresh interval has not
elapsed is not requested at all, and a page whose content hash is unchanged is
recorded and skipped without a write. That is what keeps a daily crawl close to
free for both sides.
"""
from __future__ import annotations

import argparse
import logging
import time

from app.core.db import SessionLocal
from app.knowledge.cleaner import clean_page
from app.knowledge.repository import (
    get_or_create_source,
    record_failure,
    record_fetch,
    upsert_seed_page,
)

from crawler.official.fetch import OfficialFetcher
from crawler.official.seeds import SEEDS, Seed
from crawler.sync.pipeline import crawl_job, record
from crawler.sync.refresh import is_due
from crawler.throttling.limiter import RateLimit, Throttle

log = logging.getLogger("crawler.official")

SOURCES = {
    "www.monash.edu": ("monash-students", "Monash University", "https://www.monash.edu"),
    "www.monash.edu.my": ("monash-malaysia", "Monash University Malaysia",
                          "https://www.monash.edu.my"),
}


def _source_key(url: str) -> tuple[str, str, str]:
    host = url.split("/")[2]
    return SOURCES.get(host, ("monash-other", "Monash University", f"https://{host}"))


def register(seeds: tuple[Seed, ...]) -> int:
    """Write the curated list into ``official_pages`` without fetching anything."""
    with SessionLocal() as db:
        for seed in seeds:
            key, name, base = _source_key(seed.url)
            source = get_or_create_source(db, key, name, base)
            upsert_seed_page(
                db,
                source=source,
                slug=seed.slug,
                url=seed.url,
                title=seed.title,
                category=seed.category,
                tags=list(seed.tags),
                refresh_tier=seed.tier,
                applies_to=seed.applies_to,
            )
        db.commit()
    log.info("registered %d seed pages", len(seeds))
    return len(seeds)


def crawl(seeds: tuple[Seed, ...], *, min_interval: float, transport: str) -> dict[str, int]:
    from app.models.knowledge import OfficialPage
    from sqlalchemy import select

    summary = {"new": 0, "changed": 0, "unchanged": 0, "failed": 0, "not_due": 0}
    throttle = Throttle(RateLimit(min_interval=min_interval))

    with (
        SessionLocal() as db,
        OfficialFetcher(throttle, transport=transport) as fetcher,
        crawl_job(db, "official", targets=len(seeds), transport=transport) as job,
    ):
        for seed in seeds:
            page = db.scalar(select(OfficialPage).where(OfficialPage.canonical_url == seed.url))
            if page is None:
                log.warning("%s is not registered - run --register first", seed.slug)
                continue
            if not is_due(page):
                summary["not_due"] += 1
                log.debug("%s: not due yet (tier=%s)", seed.slug, page.refresh_tier)
                continue

            started = time.monotonic()
            result = fetcher.fetch(seed.url)
            elapsed = int((time.monotonic() - started) * 1000)

            if not result.ok:
                summary["failed"] += 1
                record_failure(db, page, result.error or "fetch failed")
                db.commit()
                record(db, job, target_type="official_page", target_key=seed.slug,
                       url=seed.url, outcome="failed", http_status=result.status,
                       transport=result.transport, duration_ms=elapsed, message=result.error)
                log.error("%s: %s", seed.slug, result.error)
                continue

            cleaned = clean_page(result.html, url=seed.url)
            if len(cleaned["clean_text"] or "") < 200:
                # A page that suddenly extracts to almost nothing means the
                # template changed, not that Monash deleted the content.
                # Keep the last good version and shout about it.
                summary["failed"] += 1
                record_failure(db, page, "extracted text too short - selector may have changed")
                db.commit()
                record(db, job, target_type="official_page", target_key=seed.slug,
                       url=seed.url, outcome="failed", http_status=200,
                       transport=result.transport, duration_ms=elapsed,
                       message="suspiciously short extraction, kept last valid version")
                log.error("%s: extraction too short, keeping last valid version", seed.slug)
                continue

            outcome = record_fetch(db, page, cleaned)
            db.commit()
            summary[outcome] += 1
            record(db, job, target_type="official_page", target_key=seed.slug, url=seed.url,
                   outcome=outcome, http_status=200, content_hash=cleaned["content_hash"],
                   transport=result.transport, duration_ms=elapsed)
            log.info("%s: %s (%d chars, %s)", seed.slug, outcome,
                     len(cleaned["clean_text"]), result.transport)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl the Official Knowledge Seed pages")
    parser.add_argument("--register", action="store_true", help="register seeds, do not fetch")
    parser.add_argument("--all", action="store_true", help="ignore refresh intervals")
    parser.add_argument("--slugs", help="comma separated seed slugs")
    parser.add_argument("--transport", default="auto", choices=["auto", "httpx", "playwright"])
    parser.add_argument("--min-interval", type=float, default=4.0)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    seeds = SEEDS
    if args.slugs:
        wanted = {s.strip() for s in args.slugs.split(",") if s.strip()}
        seeds = tuple(s for s in SEEDS if s.slug in wanted)
        missing = wanted - {s.slug for s in seeds}
        if missing:
            parser.error(f"unknown slugs: {', '.join(sorted(missing))}")

    register(seeds)
    if args.register:
        return

    if args.all:
        # Clear the "checked recently" gate for this run only.
        from app.models.knowledge import OfficialPage
        from sqlalchemy import update

        with SessionLocal() as db:
            db.execute(
                update(OfficialPage)
                .where(OfficialPage.canonical_url.in_([s.url for s in seeds]))
                .values(last_checked=None)
            )
            db.commit()

    summary = crawl(seeds, min_interval=max(args.min_interval, 2.0), transport=args.transport)
    log.info("summary: %s", summary)


if __name__ == "__main__":
    main()
