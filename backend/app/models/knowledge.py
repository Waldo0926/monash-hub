"""Official Monash knowledge: sources, pages, versions and curated FAQ.

These tables hold *official* material only. Student experience lives in the
community tables and the two must never be merged into one answers table -
the product's whole trust story is that a reader can tell them apart.
"""
from datetime import datetime

from sqlalchemy import (
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class OfficialSource(Base):
    """A publisher we are willing to index, e.g. Monash Handbook or monash.edu."""

    __tablename__ = "official_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    base_url: Mapped[str] = mapped_column(String(300))
    notes: Mapped[str | None] = mapped_column(Text)

    pages: Mapped[list["OfficialPage"]] = relationship(back_populates="source")


class OfficialPage(Base):
    """One public Monash page, stored as clean text plus metadata.

    We deliberately keep only text, headings, and the link back to the source:
    no images, no PDFs, no JS/CSS. The Hub is an index, not a mirror.
    """

    __tablename__ = "official_pages"
    __table_args__ = (
        Index("ix_official_pages_search_vector", "search_vector", postgresql_using="gin"),
        Index(
            "ix_official_pages_title_trgm",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("official_sources.id"), index=True)

    slug: Mapped[str] = mapped_column(String(160), unique=True)
    canonical_url: Mapped[str] = mapped_column(String(600), unique=True)
    title: Mapped[str] = mapped_column(String(400))
    category: Mapped[str] = mapped_column(String(64), index=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(64)), default=list)

    summary: Mapped[str | None] = mapped_column(Text)
    clean_text: Mapped[str | None] = mapped_column(Text)
    headings: Mapped[list] = mapped_column(JSONB, default=list)

    # ``dynamic`` pages (dates, deadlines) are re-checked far more often than
    # ``stable`` policy text; see crawler/sync/refresh.py.
    refresh_tier: Mapped[str] = mapped_column(String(16), default="medium")

    content_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(24), default="pending")
    fetch_error: Mapped[str | None] = mapped_column(Text)

    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_checked: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_changed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('english', coalesce(title, '') || ' ' || "
            "coalesce(summary, '') || ' ' || coalesce(category, '') || ' ' || "
            "coalesce(clean_text, ''))",
            persisted=True,
        ),
    )

    source: Mapped[OfficialSource] = relationship(back_populates="pages")
    versions: Mapped[list["OfficialPageVersion"]] = relationship(
        back_populates="page", cascade="all, delete-orphan", order_by="OfficialPageVersion.id")


class OfficialPageVersion(Base):
    __tablename__ = "official_page_versions"

    id: Mapped[int] = mapped_column(primary_key=True)
    page_id: Mapped[int] = mapped_column(
        ForeignKey("official_pages.id", ondelete="CASCADE"), index=True)
    content_hash: Mapped[str] = mapped_column(String(64))
    title: Mapped[str | None] = mapped_column(String(400))
    clean_text: Mapped[str | None] = mapped_column(Text)
    headings: Mapped[list] = mapped_column(JSONB, default=list)
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    page: Mapped[OfficialPage] = relationship(back_populates="versions")


class FaqEntry(Base):
    """Hand-curated question -> answer -> official source.

    Curated, not generated: every answer has to be traceable to a page a student
    can open themselves.
    """

    __tablename__ = "faq_entries"
    __table_args__ = (
        Index("ix_faq_entries_search_vector", "search_vector", postgresql_using="gin"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    question: Mapped[str] = mapped_column(String(400))
    answer: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(64), index=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(64)), default=list)
    keywords: Mapped[list[str]] = mapped_column(ARRAY(String(64)), default=list)
    official_page_id: Mapped[int | None] = mapped_column(
        ForeignKey("official_pages.id", ondelete="SET NULL"))
    official_url: Mapped[str | None] = mapped_column(String(600))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('english', coalesce(question, '') || ' ' || coalesce(answer, ''))",
            persisted=True,
        ),
    )

    official_page: Mapped[OfficialPage | None] = relationship()
