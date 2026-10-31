"""Crawl bookkeeping shared by both crawlers.

Every run opens a ``crawl_jobs`` row and every target writes a ``crawl_history``
row, including the ones that changed nothing. A run that fetched fifty pages and
skipped all fifty should be visible as exactly that, otherwise nobody can tell a
healthy no-op from a crawler that never started.
"""
from __future__ import annotations

import logging
import signal
import threading
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta

from app.models.crawl import CrawlHistory, CrawlJob
from sqlalchemy import update
from sqlalchemy.orm import Session

log = logging.getLogger(__name__)

#: Targets that may fail in a row before the run decides the upstream is down.
#: A Handbook outage used to cost three attempts and fifteen seconds of backoff
#: for each of five thousand units, far past the ten hours systemd allows.
MAX_FAILED_IN_A_ROW = 30
#: A job still "running" after this long was stopped without finishing.
STALE_AFTER = timedelta(hours=12)


class UpstreamDown(RuntimeError):
    """Too many targets failed in a row to keep asking."""


def _terminated(signum, frame):
    # systemd stops a run that outlives TimeoutStartSec with SIGTERM, which by
    # default ends Python without unwinding, so the job stayed "running".
    raise SystemExit(128 + signum)


@contextmanager
def crawl_job(db: Session, job_type: str, *, targets: int, transport: str | None = None,
              stop_after_failures: int | None = None):
    """Open a crawl_jobs row and close it whatever happens to the run.

    ``stop_after_failures`` ends the run with :class:`UpstreamDown` once that
    many targets fail in a row. The Handbook runs use it: one host, so a run of
    failures means the host is down. The official run does not, since one
    site refusing the VPS says nothing about the next site in the seed list.
    """
    stale = db.execute(
        update(CrawlJob)
        .where(CrawlJob.job_type == job_type, CrawlJob.status == "running",
               CrawlJob.started_at < datetime.now(UTC) - STALE_AFTER)
        .values(status="failed", notes="interrupted: never finished")
    ).rowcount
    if stale:
        log.warning("marked %d earlier %s job(s) that never finished as failed", stale, job_type)
    job = CrawlJob(job_type=job_type, targets=targets, transport=transport, status="running")
    db.add(job)
    db.commit()
    job._stop_after = stop_after_failures
    job._failed_in_a_row = 0
    previous = None
    if threading.current_thread() is threading.main_thread():
        previous = signal.signal(signal.SIGTERM, _terminated)
    try:
        yield job
    except BaseException as exc:
        # The failure may be the database's own (a flush that was refused),
        # in which case the session is waiting for a rollback and the commit
        # below would raise PendingRollbackError over the real error, leaving
        # the job marked running forever.
        db.rollback()
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
    finally:
        if previous is not None:
            signal.signal(signal.SIGTERM, previous)


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
    in_a_row = getattr(job, "_failed_in_a_row", 0)
    job._failed_in_a_row = in_a_row + 1 if outcome == "failed" else 0
    if outcome in ("new", "changed"):
        job.changed += 1
    elif outcome == "unchanged":
        job.skipped += 1
    elif outcome == "failed":
        job.failed += 1
        job.fetched -= 1
    db.commit()
    limit = getattr(job, "_stop_after", None)
    if limit and job._failed_in_a_row >= limit:
        raise UpstreamDown(
            f"{job._failed_in_a_row} targets failed in a row, last {target_key}: {message}"
        )
