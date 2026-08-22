"""Unified search: one query, results grouped by how much they can be trusted."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.serializers import faq_brief, official_brief, post_brief, unit_brief
from app.core.config import get_settings
from app.core.db import get_db
from app.search import service

router = APIRouter(tags=["search"])


@router.get("/search")
def unified_search(
    q: str = Query("", description="Free text: unit code, policy keyword or question"),
    year: int | None = None,
    limit: int = Query(8, le=50),
    db: Session = Depends(get_db),
) -> dict:
    resolved_year = year or get_settings().current_academic_year

    units, unit_total = service.search_units(db, q, year=resolved_year, limit=limit)
    pages, page_total = service.search_official(db, q, limit=limit)
    posts, post_total = service.search_community(db, q, limit=limit)
    faqs = service.search_faq(db, q, limit=3)

    return {
        "query": q,
        "academic_year": resolved_year,
        "groups": [
            {
                "kind": "handbook",
                "label": "Official Handbook",
                "badge": "official-handbook",
                "total": unit_total,
                "results": [unit_brief(u) for u in units],
            },
            {
                "kind": "official",
                "label": "Official Monash guides",
                "badge": "official-source",
                "total": page_total,
                "results": [official_brief(p) for p in pages],
            },
            {
                "kind": "faq",
                "label": "Curated answers",
                "badge": "official-source",
                "total": len(faqs),
                "results": [faq_brief(f) for f in faqs],
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
    db: Session = Depends(get_db),
) -> dict:
    pages, total = service.search_official(db, q, limit=limit, offset=offset, category=category)
    return {
        "query": q,
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [official_brief(p) for p in pages],
    }
