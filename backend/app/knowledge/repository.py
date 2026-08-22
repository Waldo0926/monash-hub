"""Persist official pages with content-hash versioning."""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crawl import SourceChangeEvent
from app.models.knowledge import OfficialPage, OfficialPageVersion, OfficialSource


def get_or_create_source(db: Session, key: str, name: str, base_url: str) -> OfficialSource:
    source = db.scalar(select(OfficialSource).where(OfficialSource.key == key))
    if source is None:
        source = OfficialSource(key=key, name=name, base_url=base_url)
        db.add(source)
        db.flush()
    return source


def upsert_seed_page(
    db: Session,
    *,
    source: OfficialSource,
    slug: str,
    url: str,
    title: str,
    category: str,
    tags: list[str],
    refresh_tier: str,
) -> OfficialPage:
    """Register a seed URL before it has ever been fetched.

    The seed list is curated by hand, so a page exists in the table - with
    ``status='pending'`` - from the moment someone decides it is worth indexing.
    """
    page = db.scalar(select(OfficialPage).where(OfficialPage.canonical_url == url))
    if page is None:
        page = OfficialPage(canonical_url=url, slug=slug, title=title, source_id=source.id)
        db.add(page)
    page.category = category
    page.tags = tags
    page.refresh_tier = refresh_tier
    if not page.content_hash:
        page.title = title
        page.status = "pending"
    db.flush()
    return page


def record_fetch(db: Session, page: OfficialPage, cleaned: dict) -> str:
    """Store a successful fetch. Returns ``new``, ``changed`` or ``unchanged``."""
    now = datetime.now(UTC)
    page.last_checked = now
    page.status = "ok"
    page.fetch_error = None

    if page.content_hash == cleaned["content_hash"]:
        db.flush()
        return "unchanged"

    previous_hash = page.content_hash
    page.title = cleaned["title"] or page.title
    page.clean_text = cleaned["clean_text"]
    page.summary = cleaned["summary"]
    page.headings = cleaned["headings"]
    page.content_hash = cleaned["content_hash"]
    page.last_changed = now

    db.add(
        OfficialPageVersion(
            page_id=page.id,
            content_hash=cleaned["content_hash"],
            title=cleaned["title"],
            clean_text=cleaned["clean_text"],
            headings=cleaned["headings"],
        )
    )
    db.add(
        SourceChangeEvent(
            target_type="official_page",
            target_key=page.canonical_url,
            previous_hash=previous_hash,
            new_hash=cleaned["content_hash"],
            diff_summary={"length": len(cleaned["clean_text"] or "")},
        )
    )
    db.flush()
    return "new" if previous_hash is None else "changed"


def record_failure(db: Session, page: OfficialPage, message: str) -> None:
    """Note a failed fetch without touching the last good copy."""
    page.last_checked = datetime.now(UTC)
    page.status = "error"
    page.fetch_error = message[:2000]
    db.flush()
