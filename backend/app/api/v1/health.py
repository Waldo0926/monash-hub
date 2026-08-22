"""Liveness and a small data-freshness readout.

The reverse proxy and any monitor hit ``/api/health``; the same handler also
reports row counts and the last crawl, because "the API is up" and "the data is
current" are different questions and both get asked during a deploy.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.models.crawl import CrawlJob
from app.models.handbook import Unit
from app.models.knowledge import OfficialPage

router = APIRouter(tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    settings = get_settings()
    units = db.scalar(select(func.count(Unit.id))) or 0
    pages = db.scalar(select(func.count(OfficialPage.id)).where(OfficialPage.status == "ok")) or 0
    last_job = db.scalar(select(CrawlJob).order_by(CrawlJob.id.desc()).limit(1))
    return {
        "status": "ok",
        "environment": settings.environment,
        "academic_year": settings.current_academic_year,
        "data": {
            "units": units,
            "official_pages_ok": pages,
            "last_crawl": {
                "type": last_job.job_type,
                "status": last_job.status,
                "finished_at": last_job.finished_at.isoformat() if last_job.finished_at else None,
                "changed": last_job.changed,
                "skipped": last_job.skipped,
                "failed": last_job.failed,
            }
            if last_job
            else None,
        },
    }
