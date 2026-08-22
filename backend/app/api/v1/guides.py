"""Official guide pages and the curated FAQ behind them."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.serializers import faq_brief, official_brief, official_detail
from app.core.db import get_db
from app.models.knowledge import FaqEntry, OfficialPage
from app.search import service

router = APIRouter(tags=["guides"])


@router.get("/guides")
def list_guides(
    q: str = "",
    category: str | None = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
) -> dict:
    pages, total = service.search_official(db, q, limit=limit, category=category)
    categories = db.execute(
        select(OfficialPage.category, func.count(OfficialPage.id))
        .where(OfficialPage.status == "ok")
        .group_by(OfficialPage.category)
        .order_by(OfficialPage.category)
    ).all()
    return {
        "total": total,
        "categories": [{"key": key, "count": count} for key, count in categories],
        "results": [official_brief(p) for p in pages],
    }


@router.get("/guides/{slug}")
def get_guide(slug: str, db: Session = Depends(get_db)) -> dict:
    page = db.scalar(select(OfficialPage).where(OfficialPage.slug == slug))
    if page is None or page.status != "ok":
        raise HTTPException(404, "That guide is not indexed yet")

    related_faq = db.scalars(
        select(FaqEntry).where(FaqEntry.official_page_id == page.id).limit(5)
    ).all()
    if not related_faq:
        related_faq = service.search_faq(db, page.title, limit=3)
    posts, _ = service.search_community(db, page.title, limit=4)

    return {
        **official_detail(page),
        "related_faq": [faq_brief(f) for f in related_faq],
        "related_community": [
            {"id": p.id, "title": p.title, "answer_count": p.answer_count} for p in posts
        ],
    }


@router.get("/faq")
def list_faq(q: str = "", limit: int = Query(50, le=200), db: Session = Depends(get_db)) -> dict:
    entries = service.search_faq(db, q, limit=limit)
    return {"total": len(entries), "results": [faq_brief(f) for f in entries]}
