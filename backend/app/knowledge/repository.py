"""Persist official pages with content-hash versioning."""
from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.knowledge.cleaner import content_hash
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
    applies_to: str = "australia",
) -> OfficialPage:
    """Register a seed URL before it has ever been fetched.

    The seed list is curated by hand, so a page exists in the table - with
    ``status='pending'`` - from the moment someone decides it is worth indexing.
    """
    page = db.scalar(select(OfficialPage).where(OfficialPage.canonical_url == url))
    if page is None:
        # Same slug, new address: Monash moved the page (study-abroad/overseas/...
        # became study-abroad/outbound/...) and the coverage rebuild kept its slug.
        # Inserting a second row broke the unique slug and failed every deploy, so
        # the existing row - and its translations - follows the page instead, and
        # is fetched from the new address on the next refresh.
        page = db.scalar(select(OfficialPage).where(OfficialPage.slug == slug))
        if page is not None:
            page.canonical_url = url
            page.source_id = source.id
            page.last_checked = None
    if page is None:
        page = OfficialPage(canonical_url=url, slug=slug, title=title, source_id=source.id)
        db.add(page)
    page.category = category
    page.applies_to = applies_to
    page.tags = tags
    page.refresh_tier = refresh_tier
    # The seed list's title, not the page's own: Monash Malaysia's student pass
    # page calls itself "Before You Arrive", and nobody searching "student pass"
    # found it. The page's own title is kept in its version history.
    page.title = title
    if not page.content_hash:
        page.status = "pending"
    db.flush()
    return page


def list_behind_sign_in(db: Session, page: OfficialPage, *, title: str,
                        description: str) -> None:
    """List a page Monash keeps behind sign-in: our description, never its text.

    The description is what search and translation see, so the page can be
    found in either language; ``requires_sign_in`` is what tells the reader the
    words are ours and the page itself needs a Monash login.
    """
    digest = content_hash(title, description)
    page.requires_sign_in = True
    page.title = title
    page.summary = description
    page.clean_text = description
    page.blocks = []
    page.headings = []
    page.status = "ok"
    page.fetch_error = None
    now = datetime.now(UTC)
    page.last_checked = now
    if page.content_hash != digest:
        page.content_hash = digest
        page.last_changed = now
    db.flush()


def record_fetch(db: Session, page: OfficialPage, cleaned: dict,
                 *, title: str | None = None) -> str:
    """Store a successful fetch. Returns ``new``, ``changed`` or ``unchanged``.

    ``title`` is the seed list's title for the page; when given it is what the
    page is called, whatever the fetched page calls itself.
    """
    now = datetime.now(UTC)
    page.last_checked = now
    page.status = "ok"
    page.fetch_error = None

    if title:
        page.title = title
    if page.content_hash == cleaned["content_hash"]:
        db.flush()
        return "unchanged"

    previous_hash = page.content_hash
    page.title = title or cleaned["title"] or page.title
    page.clean_text = cleaned["clean_text"]
    page.blocks = cleaned["blocks"]
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
            blocks=cleaned["blocks"],
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


def record_failure(db: Session, page: OfficialPage, message: str, *,
                   gone: bool = False) -> None:
    """Note a failed fetch without touching the last good copy.

    A page that has a good copy keeps serving it. Setting ``status='error'``
    on every failure took the page off the guides, search and the assistant
    until a later fetch worked, so one timeout or one bot challenge hid a page
    whose text was still right. ``last_checked`` is left alone too: it is the
    date readers are shown, and it should be the last time the page was read.
    ``fetch_error`` says the last attempt failed, which makes the page due on
    the next run.

    ``gone`` is for the answers that are about the page itself - a 404 or
    410 - and those still take it down: Monash removed it, so the copy is no
    longer something to quote.
    """
    page.fetch_error = message[:2000]
    if gone or not page.content_hash:
        page.status = "error"
        page.last_checked = datetime.now(UTC)
    elif page.status == "error":
        # Hidden by a transient failure before this rule; the copy is still
        # the last good one.
        page.status = "ok"
    db.flush()
