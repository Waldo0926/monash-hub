"""Liveness and a small data-freshness readout.

The reverse proxy and any monitor hit ``/api/health``; the same handler also
reports row counts and the last crawl, because "the API is up" and "the data is
current" are different questions and both get asked during a deploy.

``crawls`` has the last run of each kind. ``last_crawl`` alone was whichever ran
last, and the official refresh runs every six hours, so a Sunday Handbook run
that failed was out of sight by the afternoon.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.models.crawl import CrawlJob
from app.models.handbook import Unit
from app.models.knowledge import OfficialPage

router = APIRouter(tags=["health"])

#: The Handbook refresh is weekly; a day's grace covers a slow or resumed run.
HANDBOOK_OVERDUE_AFTER = timedelta(days=8)


def _job(job: CrawlJob | None) -> dict | None:
    if job is None:
        return None
    return {
        "type": job.job_type,
        "status": job.status,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        "changed": job.changed,
        "skipped": job.skipped,
        "failed": job.failed,
        "notes": job.notes if job.status == "failed" else None,
    }


def _handbook_overdue(db: Session) -> bool | None:
    """True when no Handbook run has finished in eight days; None if none ever ran."""
    if db.scalar(select(CrawlJob.id).where(CrawlJob.job_type == "handbook").limit(1)) is None:
        return None
    last_done = db.scalar(
        select(func.max(CrawlJob.finished_at)).where(
            CrawlJob.job_type == "handbook", CrawlJob.status.in_(("ok", "partial"))
        )
    )
    return last_done is None or last_done < datetime.now(UTC) - HANDBOOK_OVERDUE_AFTER


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    settings = get_settings()
    units = db.scalar(select(func.count(Unit.id))) or 0
    pages = db.scalar(select(func.count(OfficialPage.id)).where(OfficialPage.status == "ok")) or 0
    last_job = db.scalar(select(CrawlJob).order_by(CrawlJob.id.desc()).limit(1))
    latest = (
        select(func.max(CrawlJob.id)).group_by(CrawlJob.job_type).scalar_subquery()
    )
    per_type = db.scalars(
        select(CrawlJob).where(CrawlJob.id.in_(latest)).order_by(CrawlJob.job_type)
    ).all()
    return {
        "status": "ok",
        "environment": settings.environment,
        "commit": settings.app_commit or None,
        "academic_year": settings.current_academic_year,
        "data": {
            "units": units,
            "official_pages_ok": pages,
            "last_crawl": _job(last_job),
            "crawls": {job.job_type: _job(job) for job in per_type},
            "handbook_overdue": _handbook_overdue(db),
        },
    }
