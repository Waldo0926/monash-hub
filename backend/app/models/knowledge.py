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
        Index(
            "ix_official_pages_search_zh_trgm",
            "search_zh",
            postgresql_using="gin",
            postgresql_ops={"search_zh": "gin_trgm_ops"},
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
    # ``clean_text`` is what the search vector reads; ``blocks`` is what a person
    # reads. They come from the same extraction and must not be written apart -
    # see app/knowledge/cleaner.py for the shape and for why one string was not
    # enough.
    clean_text: Mapped[str | None] = mapped_column(Text)
    blocks: Mapped[list] = mapped_column(JSONB, default=list)
    headings: Mapped[list] = mapped_column(JSONB, default=list)

    # Which campus the page is written for. Monash publishes a student site per
    # location and they do not agree: a student pass in Malaysia is issued by
    # the Immigration Department through EMGS, and has nothing to do with the
    # Australian subclass 500 visa the monash.edu pages describe. Telling a
    # Malaysian student they may work 48 hours a fortnight is not a translation
    # error - it is the wrong country's law.
    #
    # So the value records where the page came from, which is a fact, rather
    # than where it applies, which would be a judgement:
    #   ``australia`` - from monash.edu, the Australian student site
    #   ``malaysia``  - from monash.edu.my
    #   ``all``       - the page itself says it covers every campus
    applies_to: Mapped[str] = mapped_column(String(16), default="australia", index=True)

    # ``dynamic`` pages (dates, deadlines) are re-checked far more often than
    # ``stable`` policy text; see crawler/sync/refresh.py.
    refresh_tier: Mapped[str] = mapped_column(String(16), default="medium")

    content_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(24), default="pending")
    fetch_error: Mapped[str | None] = mapped_column(Text)

    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_checked: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_changed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Every Chinese string this row has, flattened out of content_translations
    # where an index can reach it. PostgreSQL cannot tokenise Chinese without a
    # server-side extension we cannot install, so this is matched with pg_trgm
    # rather than tsvector - which for a language with no word boundaries is the
    # right query anyway. Filled by `python -m app.search.reindex_zh`, never by
    # a generated column: the text it comes from lives in another table.
    search_zh: Mapped[str | None] = mapped_column(Text)

    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        Computed(
            # Weighted, so a page *about* a word outranks one that mentions it:
            # title A, summary B, category C, body D. See HEADLINE_WEIGHTS in
            # app/search/service.py for the query that relies on this.
            "setweight(to_tsvector('english', coalesce(title, '')), 'A') || "
            "setweight(to_tsvector('english', coalesce(summary, '')), 'B') || "
            "setweight(to_tsvector('english', coalesce(category, '')), 'C') || "
            "setweight(to_tsvector('english', coalesce(clean_text, '')), 'D')",
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
    blocks: Mapped[list] = mapped_column(JSONB, default=list)
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
            "setweight(to_tsvector('english', coalesce(question, '')), 'A') || "
            "setweight(to_tsvector('english', coalesce(answer, '')), 'D')",
            persisted=True,
        ),
    )

    official_page: Mapped[OfficialPage | None] = relationship()
