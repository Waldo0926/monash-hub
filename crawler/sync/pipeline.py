"""Crawl bookkeeping shared by both crawlers.

Every run opens a ``crawl_jobs`` row and every target writes a ``crawl_history``
row, including the ones that changed nothing. A run that fetched fifty pages and
skipped all fifty should be visible as exactly that, otherwise nobody can tell a
healthy no-op from a crawler that never started.
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from datetime import UTC, datetime

from app.models.crawl import CrawlHistory, CrawlJob
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)


@contextmanager
def crawl_job(db: Session, job_type: str, *, targets: int, transport: str | None = None):
    job = CrawlJob(job_type=job_type, targets=targets, transport=transport, status="running")
    db.add(job)
    db.commit()
    try:
        yield job
    except BaseException as exc:
        job.status = "failed"
        job.notes = f"{type(exc).__name__}: {exc}"[:2000]
        job.finished_at = datetime.now(UTC)
        db.commit()
        raise
    else:
        job.status = "ok" if job.failed == 0 else "partial"
        job.finished_at = datetime.now(UTC)
        db.commit()
        log.info(
            "%s crawl finished: %d fetched, %d changed, %d skipped, %d failed",
            job_type, job.fetched, job.changed, job.skipped, job.failed,
        )


def record(
    db: Session,
    job: CrawlJob,
    *,
    target_type: str,
    target_key: str,
    url: str,
    outcome: str,
    http_status: int | None = None,
    content_hash: str | None = None,
    transport: str | None = None,
    duration_ms: int | None = None,
    message: str | None = None,
) -> None:
    db.add(
        CrawlHistory(
            job_id=job.id,
            target_type=target_type,
            target_key=target_key,
            url=url,
            outcome=outcome,
            http_status=http_status,
            content_hash=content_hash,
            transport=transport,
            duration_ms=duration_ms,
            message=message,
        )
    )
    job.fetched += 1
    if outcome in ("new", "changed"):
        job.changed += 1
    elif outcome == "unchanged":
        job.skipped += 1
    elif outcome == "failed":
        job.failed += 1
        job.fetched -= 1
    db.commit()
