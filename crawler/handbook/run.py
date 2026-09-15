"""Handbook crawl runner.

    python -m crawler.handbook.run --fixtures            # the 20 fixture units
    python -m crawler.handbook.run --units FIT2102,FIT3143
    python -m crawler.handbook.run --all                 # every 2026 unit
    python -m crawler.handbook.run --all --skip-fresh 24 # resume, skipping today's

``--all`` is a backfill, not a routine job: roughly six thousand units at a few
seconds each is hours of wall clock. It is sequential and rate limited like
everything else here, it logs progress as it goes, and ``--skip-fresh`` makes it
resumable - a run that dies halfway can be restarted without re-fetching what it
already has.

A parse failure keeps the last good row and is recorded as ``failed``. Silently
overwriting correct data with a blank record would be far worse than a gap in
today's crawl.
"""
from __future__ import annotations

import argparse
import logging
import time
from datetime import UTC, datetime, timedelta

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.handbook.parser import ParseError, parse_unit_page, unit_url
from app.handbook.repository import upsert_unit
from app.models.handbook import Unit
from sqlalchemy import select

from crawler.handbook.discover import discover_unit_codes
from crawler.handbook.fetch import HandbookFetcher
from crawler.handbook.seeds import FIXTURE_CODES
from crawler.sync.pipeline import crawl_job, record
from crawler.throttling.limiter import RateLimit, Throttle

log = logging.getLogger("crawler.handbook")

PROGRESS_EVERY = 25


def _already_fresh(codes: list[str], year: int, hours: float) -> set[str]:
    """Codes crawled within the last ``hours``, so a resumed run can skip them."""
    if hours <= 0:
        return set()
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    with SessionLocal() as db:
        rows = db.scalars(
            select(Unit.unit_code).where(
                Unit.academic_year == year,
                Unit.unit_code.in_(codes),
                Unit.last_crawled >= cutoff,
            )
        ).all()
    return set(rows)


def crawl(codes: list[str], year: int, *, min_interval: float) -> dict[str, int]:
    throttle = Throttle(RateLimit(min_interval=min_interval))
    summary = {"new": 0, "changed": 0, "unchanged": 0, "failed": 0}
    started_at = time.monotonic()

    with (
        SessionLocal() as db,
        HandbookFetcher(throttle) as fetcher,
        crawl_job(db, "handbook", targets=len(codes), transport="httpx") as job,
    ):
        for index, code in enumerate(codes, start=1):
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
            log.debug("%s: %s (%s, has_exam=%s)", code, outcome, unit.title, unit.has_exam)

            if index % PROGRESS_EVERY == 0 or index == len(codes):
                _log_progress(index, len(codes), started_at, summary)
    return summary


def _log_progress(done: int, total: int, started_at: float, summary: dict[str, int]) -> None:
    elapsed = time.monotonic() - started_at
    rate = done / elapsed if elapsed else 0
    remaining = (total - done) / rate if rate else 0
    log.info(
        "%d/%d units (%.0f%%) - %s - about %d min left",
        done, total, 100 * done / total, summary, remaining / 60,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl Monash Handbook unit pages")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fixtures", action="store_true", help="crawl the 20 fixture units")
    group.add_argument("--units", help="comma separated unit codes")
    group.add_argument("--all", action="store_true", help="crawl every unit published for the year")
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument(
        "--skip-fresh",
        type=float,
        default=0.0,
        help="skip units crawled within this many hours (use to resume a backfill)",
    )
    parser.add_argument("--limit", type=int, default=0, help="stop after this many units")
    parser.add_argument(
        "--min-interval",
        type=float,
        default=3.0,
        help="minimum seconds between requests (floor: 1.0)",
    )
    parser.add_argument(
        "--fail-on-errors",
        action="store_true",
        help="exit non-zero when any target failed, for verified repair/backfill jobs",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    # httpx logs a line per request; at six thousand units that is all the log.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    year = args.year or get_settings().current_academic_year

    if args.fixtures:
        codes = list(FIXTURE_CODES)
    elif args.units:
        codes = [c.strip().upper() for c in args.units.split(",") if c.strip()]
    else:
        codes = discover_unit_codes(year, Throttle(RateLimit(min_interval=1.0, jitter=0.5)))

    if args.skip_fresh:
        fresh = _already_fresh(codes, year, args.skip_fresh)
        if fresh:
            log.info("skipping %d units crawled in the last %.1fh", len(fresh), args.skip_fresh)
            codes = [c for c in codes if c not in fresh]
    if args.limit:
        codes = codes[: args.limit]

    if not codes:
        log.info("nothing to crawl")
        return

    # The floor is not negotiable from the command line.
    interval = max(args.min_interval, 1.0)
    log.info("crawling %d units at >= %.1fs apart (about %d min)",
             len(codes), interval, len(codes) * (interval + 0.75) / 60)

    summary = crawl(codes, year, min_interval=interval)
    log.info("summary: %s", summary)
    if args.fail_on_errors and summary["failed"]:
        raise SystemExit(f"{summary['failed']} Handbook target(s) failed")


if __name__ == "__main__":
    main()
