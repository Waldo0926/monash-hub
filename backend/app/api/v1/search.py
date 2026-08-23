"""Unified search: one query, results grouped by how much they can be trusted."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import requested_locale
from app.api.serializers import faq_brief, official_brief, post_brief, unit_brief
from app.core.config import get_settings
from app.core.db import get_db
from app.knowledge import translations
from app.models.translation import FAQ_ENTRY, OFFICIAL_PAGE, UNIT
from app.search import service

router = APIRouter(tags=["search"])


@router.get("/search")
def unified_search(
    q: str = Query("", description="Free text: unit code, policy keyword or question"),
    year: int | None = None,
    limit: int = Query(8, le=50),
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    resolved_year = year or get_settings().current_academic_year

    units, unit_total = service.search_units(db, q, year=resolved_year, limit=limit)
    pages, page_total = service.search_official(db, q, limit=limit)
    posts, post_total = service.search_community(db, q, limit=limit)
    faqs = service.search_faq(db, q, limit=3)

    # Three lookups for the whole page rather than one per result. Community
    # posts are what a student wrote, so they are never translated.
    unit_tr = translations.load_many(
        db, locale, UNIT, [u.unit_code for u in units],
        source_hashes={u.unit_code: u.content_hash for u in units},
    )
    page_tr = translations.load_many(
        db, locale, OFFICIAL_PAGE, [p.slug for p in pages],
        source_hashes={p.slug: p.content_hash for p in pages},
    )
    faq_tr = translations.load_many(db, locale, FAQ_ENTRY, [f.slug for f in faqs])

    return {
        "query": q,
        "academic_year": resolved_year,
        "groups": [
            {
                "kind": "handbook",
                "label": "Official Handbook",
                "badge": "official-handbook",
                "total": unit_total,
                "results": [unit_brief(u, unit_tr[u.unit_code]) for u in units],
            },
            {
                "kind": "official",
                "label": "Official Monash guides",
                "badge": "official-source",
                "total": page_total,
                "results": [official_brief(p, page_tr[p.slug]) for p in pages],
            },
            {
                "kind": "faq",
                "label": "Curated answers",
                "badge": "official-source",
                "total": len(faqs),
                "results": [faq_brief(f, faq_tr[f.slug]) for f in faqs],
            },
            {
                "kind": "community",
                "label": "Community",
                "badge": "community",
                "total": post_total,
                "results": [post_brief(p) for p in posts],
            },
        ],
    }


@router.get("/official/search")
def official_search(
    q: str = "",
    category: str | None = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    pages, total = service.search_official(db, q, limit=limit, offset=offset, category=category)
    page_tr = translations.load_many(
        db, locale, OFFICIAL_PAGE, [p.slug for p in pages],
        source_hashes={p.slug: p.content_hash for p in pages},
    )
    return {
        "query": q,
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [official_brief(p, page_tr[p.slug]) for p in pages],
    }
