"""Whether the last scheduled crawl needs a person to look at it.

    python -m crawler.sync.alert official
    python -m crawler.sync.alert handbook handbook_courses handbook_aos

Prints one line per problem with the last run of each job type, and nothing
when they all look fine. scheduled-refresh.sh mails whatever it prints. A
failed Handbook week, or a refresh where Cloudflare refused half the official
pages, used to be visible only to someone reading journalctl.
"""
from __future__ import annotations

import sys

from app.core.db import SessionLocal
from app.models.crawl import CrawlJob
from sqlalchemy import select

#: A run where more than this share of the targets failed is worth a look...
FAILED_SHARE = 0.05
#: ...as long as it is more than a few pages: three 403s out of ten due pages
#: is an ordinary afternoon.
FAILED_AT_LEAST = 5


def problems(job: CrawlJob | None, job_type: str) -> list[str]:
    if job is None:
        return [f"{job_type}: no run on record"]
    when = job.started_at.strftime("%Y-%m-%d %H:%M %Z") if job.started_at else "?"
    if job.status == "failed":
        return [f"{job_type} run #{job.id} ({when}) failed: {job.notes or 'no reason recorded'}"]
    if job.status == "running":
        return [f"{job_type} run #{job.id} ({when}) is still marked running"]
    if job.failed >= FAILED_AT_LEAST and job.failed > FAILED_SHARE * max(job.targets, 1):
        return [f"{job_type} run #{job.id} ({when}): {job.failed} of {job.targets} targets "
                f"failed; SELECT target_key, message FROM crawl_history "
                f"WHERE job_id = {job.id} AND outcome = 'failed'"]
    return []


def main(job_types: list[str]) -> None:
    found: list[str] = []
    with SessionLocal() as db:
        for job_type in job_types:
            job = db.scalar(select(CrawlJob).where(CrawlJob.job_type == job_type)
                            .order_by(CrawlJob.id.desc()).limit(1))
            found += problems(job, job_type)
    print("\n".join(found))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python -m crawler.sync.alert JOB_TYPE [JOB_TYPE ...]")
    main(sys.argv[1:])
