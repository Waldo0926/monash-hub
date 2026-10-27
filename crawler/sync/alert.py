"""Whether the last scheduled crawl needs a person to look at it.

    python -m crawler.sync.alert official
    python -m crawler.sync.alert handbook handbook_courses handbook_aos

Prints one line per problem with the last run of each job type, and nothing
when they all look fine. scheduled-refresh.sh mails whatever it prints. A
failed Handbook week, or a refresh where Cloudflare refused half the official
pages, used to be visible only to someone reading journalctl.
"""
from __future__ import annotations

import re
import sys
from collections import Counter

from app.core.db import SessionLocal
from app.models.crawl import CrawlHistory, CrawlJob
from sqlalchemy import select

#: A run where more than this share of the targets it tried failed is worth a
#: look...
FAILED_SHARE = 0.05
#: ...as long as it is more than a few pages: three 403s out of ten due pages
#: is an ordinary afternoon.
FAILED_AT_LEAST = 5
#: Kinds of failure listed under the line, most common first.
TOP_REASONS = 3
#: Failures that are the host turning this server away, not a page that broke.
#: robots.txt answered with a 403 closes the host before any page is asked for.
REFUSED = ("robots.txt unavailable", "HTTP 403")

_URL = re.compile(r"https?://\S+")


def tried(job: CrawlJob) -> int:
    """Targets the run actually asked about.

    ``targets`` is the whole list the run was handed. The official refresh
    only asks about the pages that are due, so on 2026-10-27 a run where every
    one of its 194 pages failed was reported as 194 of 2917, and a run with
    fewer than 146 due pages could fail all of them without a mail.
    ``fetched`` leaves the failed ones out, so they are added back.
    """
    return (job.fetched or 0) + job.failed


def reason(message: str | None) -> str:
    """One label per kind of failure. Playwright errors carry a page of call
    log and the address, which would make every failure its own kind."""
    lines = (message or "").strip().splitlines()
    if not lines:
        return "no message"
    return _URL.sub("<url>", lines[0])[:100]


def failure_reasons(db, job: CrawlJob) -> list[tuple[str, int]]:
    messages = db.scalars(
        select(CrawlHistory.message)
        .where(CrawlHistory.job_id == job.id, CrawlHistory.outcome == "failed")
    )
    return Counter(reason(m) for m in messages).most_common()


def _refused(reasons: list[tuple[str, int]]) -> bool:
    total = sum(count for _, count in reasons)
    refused = sum(count for text, count in reasons if text.startswith(REFUSED))
    return total > 0 and refused * 2 > total


def problems(job: CrawlJob | None, job_type: str,
             reasons: list[tuple[str, int]] | None = None) -> list[str]:
    if job is None:
        return [f"{job_type}: no run on record"]
    when = job.started_at.strftime("%Y-%m-%d %H:%M %Z") if job.started_at else "?"
    if job.status == "failed":
        return [f"{job_type} run #{job.id} ({when}) failed: {job.notes or 'no reason recorded'}"]
    if job.status == "running":
        return [f"{job_type} run #{job.id} ({when}) is still marked running"]
    asked = max(tried(job), 1)
    if job.failed < FAILED_AT_LEAST or job.failed <= FAILED_SHARE * asked:
        return []
    found = [f"{job_type} run #{job.id} ({when}): {job.failed} of the {asked} targets it "
             f"tried failed ({job.targets} on its list); SELECT target_key, message "
             f"FROM crawl_history WHERE job_id = {job.id} AND outcome = 'failed'"]
    found += [f"  {count} x {text}" for text, count in (reasons or [])[:TOP_REASONS]]
    if job_type == "official" and _refused(reasons or []):
        found.append("  Most of them were refused: the site is turning this server away. "
                     "Read the pages on a computer it answers with crawler.official.harvest "
                     "and store them with deployment/crawl.sh official-harvest.")
    return found


def main(job_types: list[str]) -> None:
    found: list[str] = []
    with SessionLocal() as db:
        for job_type in job_types:
            job = db.scalar(select(CrawlJob).where(CrawlJob.job_type == job_type)
                            .order_by(CrawlJob.id.desc()).limit(1))
            reasons = failure_reasons(db, job) if job is not None and job.failed else []
            found += problems(job, job_type, reasons)
    print("\n".join(found))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python -m crawler.sync.alert JOB_TYPE [JOB_TYPE ...]")
    main(sys.argv[1:])
