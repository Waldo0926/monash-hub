"""Official guide pages and the curated FAQ behind them."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import requested_locale
from app.api.serializers import faq_brief, official_brief, official_detail
from app.core.db import get_db
from app.knowledge import translations
from app.models.knowledge import FaqEntry, OfficialPage
from app.models.translation import FAQ_ENTRY, OFFICIAL_PAGE
from app.search import service

router = APIRouter(tags=["guides"])


@router.get("/guides")
def list_guides(
    q: str = "",
    category: str | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    pages, total = service.search_official(db, q, limit=limit, offset=offset, category=category)
    # One query for the whole page of results, not one per row.
    page_translations = translations.load_many(
        db, locale, OFFICIAL_PAGE, [p.slug for p in pages],
        source_hashes={p.slug: p.content_hash for p in pages},
    )
    categories = db.execute(
        select(OfficialPage.category, func.count(OfficialPage.id))
        .where(OfficialPage.status == "ok")
        .group_by(OfficialPage.category)
        .order_by(OfficialPage.category)
    ).all()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "categories": [{"key": key, "count": count} for key, count in categories],
        "results": [official_brief(p, page_translations[p.slug]) for p in pages],
    }


@router.get("/guides/{slug}")
def get_guide(
    slug: str,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    page = db.scalar(select(OfficialPage).where(OfficialPage.slug == slug))
    if page is None or page.status != "ok":
        raise HTTPException(404, "That guide is not indexed yet")

    related_faq = db.scalars(
        select(FaqEntry).where(FaqEntry.official_page_id == page.id).limit(5)
    ).all()
    if not related_faq:
        # No FAQ cites this page, so offer the ones on the same topic: any whose
        # curated vocabulary shares a tag with the page. A page title is not a
        # question, and feeding it to the FAQ matcher as one finds nothing.
        page_tags = {tag.lower() for tag in page.tags or []}
        related_faq = [
            entry
            for entry in db.scalars(select(FaqEntry).order_by(FaqEntry.priority.desc()))
            if page_tags & {word.lower() for word in (*entry.tags, *entry.keywords)}
        ][:3]
    posts, _ = service.search_community(db, page.title, limit=4)

    tr = translations.load(db, locale, OFFICIAL_PAGE, page.slug, source_hash=page.content_hash)
    faq_tr = translations.load_many(
        db, locale, FAQ_ENTRY, [f.slug for f in related_faq], global_key=None)
    return {
        **official_detail(page, tr),
        "related_faq": [faq_brief(f, faq_tr[f.slug]) for f in related_faq],
        "related_community": [
            {"id": p.id, "title": p.title, "answer_count": p.answer_count} for p in posts
        ],
    }


@router.get("/faq")
def list_faq(
    q: str = "",
    limit: int = Query(50, le=200),
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    entries = service.search_faq(db, q, limit=limit)
    tr = translations.load_many(db, locale, FAQ_ENTRY, [f.slug for f in entries], global_key=None)
    return {"total": len(entries), "results": [faq_brief(f, tr[f.slug]) for f in entries]}
