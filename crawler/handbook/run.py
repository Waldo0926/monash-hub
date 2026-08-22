"""Handbook crawl runner.

    python -m crawler.handbook.run --fixtures
    python -m crawler.handbook.run --units FIT2102,FIT3143 --year 2026

A parse failure keeps the last good row and is recorded as ``failed``. Silently
overwriting correct data with a blank record would be far worse than a gap in
today's crawl.
"""
from __future__ import annotations

import argparse
import logging
import time

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.handbook.parser import ParseError, parse_unit_page, unit_url
from app.handbook.repository import upsert_unit

from crawler.handbook.fetch import HandbookFetcher
from crawler.handbook.seeds import FIXTURE_CODES
from crawler.sync.pipeline import crawl_job, record
from crawler.throttling.limiter import RateLimit, Throttle

log = logging.getLogger("crawler.handbook")


def crawl(codes: list[str], year: int, *, min_interval: float) -> dict[str, int]:
    throttle = Throttle(RateLimit(min_interval=min_interval))
    summary = {"new": 0, "changed": 0, "unchanged": 0, "failed": 0}

    with (
        SessionLocal() as db,
        HandbookFetcher(throttle) as fetcher,
        crawl_job(db, "handbook", targets=len(codes), transport="httpx") as job,
    ):
        for code in codes:
            url = unit_url(code, year)
            started = time.monotonic()
            result = fetcher.fetch(url)
            elapsed = int((time.monotonic() - started) * 1000)

            if not result.ok:
                summary["failed"] += 1
                record(db, job, target_type="handbook_unit", target_key=code, url=url,
                       outcome="failed", http_status=result.status, transport=result.transport,
                       duration_ms=elapsed, message=result.error)
                log.error("%s: fetch failed (%s)", code, result.error)
                continue

            try:
                parsed = parse_unit_page(result.html, url)
            except ParseError as exc:
                summary["failed"] += 1
                record(db, job, target_type="handbook_unit", target_key=code, url=url,
                       outcome="failed", http_status=result.status, transport=result.transport,
                       duration_ms=elapsed, message=f"parse error: {exc}")
                log.error("%s: parse failed, keeping last valid record (%s)", code, exc)
                continue

            unit, outcome = upsert_unit(db, parsed)
            db.commit()
            summary[outcome] += 1
            record(db, job, target_type="handbook_unit", target_key=code, url=url,
                   outcome=outcome, http_status=200, content_hash=parsed["content_hash"],
                   transport=result.transport, duration_ms=elapsed)
            log.info("%s: %s (%s, has_exam=%s)", code, outcome, unit.title, unit.has_exam)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl Monash Handbook unit pages")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixtures", action="store_true", help="crawl the 20 fixture units")
    group.add_argument("--units", help="comma separated unit codes")
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument(
        "--min-interval",
        type=float,
        default=3.0,
        help="minimum seconds between requests (floor: 1.0)",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    year = args.year or get_settings().current_academic_year
    codes = (
        list(FIXTURE_CODES)
        if args.fixtures
        else [c.strip().upper() for c in args.units.split(",") if c.strip()]
    )
    # The floor is not negotiable from the command line.
    interval = max(args.min_interval, 1.0)

    summary = crawl(codes, year, min_interval=interval)
    log.info("summary: %s", summary)


if __name__ == "__main__":
    main()
