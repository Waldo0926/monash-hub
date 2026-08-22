"""Crawl bookkeeping.

The sync pipeline is only trustworthy if a failed run is visible afterwards, so
every fetch attempt lands in ``crawl_history`` whether it changed anything or
not, and every real content change lands in ``source_change_events``.
"""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_type: Mapped[str] = mapped_column(String(48), index=True)  # handbook | official
    status: Mapped[str] = mapped_column(String(24), default="running")
    targets: Mapped[int] = mapped_column(Integer, default=0)
    fetched: Mapped[int] = mapped_column(Integer, default=0)
    changed: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    transport: Mapped[str | None] = mapped_column(String(24))
    notes: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class CrawlHistory(Base):
    __tablename__ = "crawl_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int | None] = mapped_column(Integer, index=True)
    target_type: Mapped[str] = mapped_column(String(24))
    target_key: Mapped[str] = mapped_column(String(600), index=True)
    url: Mapped[str] = mapped_column(String(600))
    outcome: Mapped[str] = mapped_column(String(24), index=True)  # changed|unchanged|failed|new
    http_status: Mapped[int | None] = mapped_column(Integer)
    content_hash: Mapped[str | None] = mapped_column(String(64))
    transport: Mapped[str | None] = mapped_column(String(24))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SourceChangeEvent(Base):
    __tablename__ = "source_change_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_type: Mapped[str] = mapped_column(String(24), index=True)
    target_key: Mapped[str] = mapped_column(String(600), index=True)
    previous_hash: Mapped[str | None] = mapped_column(String(64))
    new_hash: Mapped[str] = mapped_column(String(64))
    diff_summary: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
