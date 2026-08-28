"""Course and area-of-study crawl runner.

    python -m crawler.handbook.run_courses --all
    python -m crawler.handbook.run_courses --courses C2001,C2000
    python -m crawler.handbook.run_courses --all --skip-fresh 24   # resumable

914 pages for 2026 - 503 courses and 411 areas of study - at the same polite
interval as the unit crawl. That is under an hour, so unlike ``--all`` on units
this is a job you can run in one sitting.

Courses are fetched before areas of study on purpose. A course names the
specialisations it offers, so crawling in that order means that by the time an
area of study is stored, the course pointing at it already exists and the join
is live from the first row rather than from the end of the run.

A page that cannot be parsed *or* cannot be stored keeps its last good row and
is recorded as ``failed``. Both halves matter: catching only ParseError let one
oversized column stop a 914-page crawl at page 87, which is a far worse outcome
than a gap in one row.
"""
from __future__ import annotations

import argparse
import logging
import time
from datetime import UTC, datetime, timedelta

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.handbook.course_parser import (
    aos_url,
    course_url,
    parse_aos_page,
    parse_course_page,
)
from app.handbook.course_repository import upsert_area_of_study, upsert_course
from app.handbook.parser import ParseError
from app.models.curriculum import AreaOfStudy, Course
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from crawler.handbook.discover import discover_aos_codes, discover_course_codes
from crawler.handbook.fetch import HandbookFetcher
from crawler.sync.pipeline import crawl_job, record
from crawler.throttling.limiter import RateLimit, Throttle

log = logging.getLogger("crawler.courses")

PROGRESS_EVERY = 25

# Everything that differs between the two page kinds, in one place, so the
# crawl loop below is written once instead of twice.
KINDS = {
    "course": {
        "model": Course,
        "code_column": "course_code",
        "url": course_url,
        "parse": parse_course_page,
        "upsert": upsert_course,
        "target_type": "handbook_course",
        "discover": discover_course_codes,
    },
    "aos": {
        "model": AreaOfStudy,
        "code_column": "aos_code",
        "url": aos_url,
        "parse": parse_aos_page,
        "upsert": upsert_area_of_study,
        "target_type": "handbook_aos",
        "discover": discover_aos_codes,
    },
}


def _already_fresh(kind: str, codes: list[str], year: int, hours: float) -> set[str]:
    """Codes crawled within the last ``hours``, so a resumed run can skip them."""
    if hours <= 0:
        return set()
    spec = KINDS[kind]
    model = spec["model"]
    column = getattr(model, spec["code_column"])
    cutoff = datetime.now(UTC) - timedelta(hours=hours)
    with SessionLocal() as db:
        return set(
            db.scalars(
                select(column).where(
                    model.academic_year == year,
                    column.in_(codes),
                    model.last_crawled >= cutoff,
                )
            ).all()
        )


def crawl(kind: str, codes: list[str], year: int, *, min_interval: float) -> dict[str, int]:
    spec = KINDS[kind]
    throttle = Throttle(RateLimit(min_interval=min_interval))
    summary = {"new": 0, "changed": 0, "unchanged": 0, "failed": 0}
    started_at = time.monotonic()

    with (
        SessionLocal() as db,
        HandbookFetcher(throttle) as fetcher,
        crawl_job(db, f"handbook_{kind}", targets=len(codes), transport="httpx") as job,
    ):
        for index, code in enumerate(codes, start=1):
            url = spec["url"](code, year)
            started = time.monotonic()
            result = fetcher.fetch(url)
            elapsed = int((time.monotonic() - started) * 1000)

            if not result.ok:
                summary["failed"] += 1
                record(db, job, target_type=spec["target_type"], target_key=code, url=url,
                       outcome="failed", http_status=result.status, transport=result.transport,
                       duration_ms=elapsed, message=result.error)
                log.error("%s: fetch failed (%s)", code, result.error)
                continue

            try:
                parsed = spec["parse"](result.html, url)
            except ParseError as exc:
                summary["failed"] += 1
                record(db, job, target_type=spec["target_type"], target_key=code, url=url,
                       outcome="failed", http_status=result.status, transport=result.transport,
                       duration_ms=elapsed, message=f"parse error: {exc}")
                log.error("%s: parse failed, keeping last valid record (%s)", code, exc)
                continue

            try:
                stored, outcome = spec["upsert"](db, parsed)
                db.commit()
            except SQLAlchemyError as exc:
                # A page that will not fit the schema is one row's problem, not
                # the run's. F2003 publishes two CRICOS codes with their names
                # in a column sized for one, and the whole crawl stopped at
                # page 87 because a DataError is not a ParseError and only
                # ParseError was being caught. Roll back, record it, keep going.
                db.rollback()
                summary["failed"] += 1
                record(db, job, target_type=spec["target_type"], target_key=code, url=url,
                       outcome="failed", http_status=result.status, transport=result.transport,
                       duration_ms=elapsed, message=f"database error: {exc}"[:2000])
                log.error("%s: could not be stored, skipping (%s)", code, type(exc).__name__)
                continue

            summary[outcome] += 1
            record(db, job, target_type=spec["target_type"], target_key=code, url=url,
                   outcome=outcome, http_status=200, content_hash=parsed["content_hash"],
                   transport=result.transport, duration_ms=elapsed)
            log.debug("%s: %s (%s)", code, outcome, stored.title)

            if index % PROGRESS_EVERY == 0 or index == len(codes):
                _log_progress(kind, index, len(codes), started_at, summary)
    return summary


def _log_progress(
    kind: str, done: int, total: int, started_at: float, summary: dict[str, int]
) -> None:
    elapsed = time.monotonic() - started_at
    rate = done / elapsed if elapsed else 0
    remaining = (total - done) / rate if rate else 0
    log.info(
        "%d/%d %s (%.0f%%) - %s - about %d min left",
        done, total, kind, 100 * done / total, summary, remaining / 60,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl Handbook courses and areas of study")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="every course and area of study")
    group.add_argument("--courses", help="comma separated course codes")
    group.add_argument("--aos", help="comma separated area-of-study codes")
    parser.add_argument("--year", type=int, default=None)
    parser.add_argument("--limit", type=int, default=0, help="stop after this many pages")
    parser.add_argument(
        "--skip-fresh",
        type=float,
        default=0,
        help="skip pages crawled within this many hours, to resume a run",
    )
    parser.add_argument(
        "--min-interval",
        type=float,
        default=3.0,
        help="minimum seconds between requests (floor: 1.0)",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")
    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    year = args.year or get_settings().current_academic_year
    interval = max(args.min_interval, 1.0)

    plan: list[tuple[str, list[str]]] = []
    if args.courses:
        plan.append(("course", [c.strip().upper() for c in args.courses.split(",") if c.strip()]))
    elif args.aos:
        plan.append(("aos", [c.strip().upper() for c in args.aos.split(",") if c.strip()]))
    else:
        throttle = Throttle(RateLimit(min_interval=interval))
        for kind in ("course", "aos"):
            plan.append((kind, KINDS[kind]["discover"](year, throttle)))

    totals: dict[str, dict[str, int]] = {}
    for kind, codes in plan:
        fresh = _already_fresh(kind, codes, year, args.skip_fresh)
        if fresh:
            log.info("skipping %d %s crawled in the last %.0fh", len(fresh), kind, args.skip_fresh)
            codes = [c for c in codes if c not in fresh]
        if args.limit:
            codes = codes[: args.limit]
        if not codes:
            log.info("nothing to crawl for %s", kind)
            continue
        log.info("crawling %d %s for %s", len(codes), kind, year)
        totals[kind] = crawl(kind, codes, year, min_interval=interval)

    for kind, summary in totals.items():
        log.info("%s: %s", kind, summary)


if __name__ == "__main__":
    main()
