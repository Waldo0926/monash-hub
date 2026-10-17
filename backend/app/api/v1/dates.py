"""Upcoming key dates for one campus, read from the official date pages."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import requested_locale
from app.core.db import get_db
from app.knowledge import key_dates, translations
from app.models.knowledge import OfficialPage
from app.models.translation import OFFICIAL_PAGE

router = APIRouter(tags=["guides"])


@router.get("/key-dates")
def list_key_dates(
    campus: str = Query("malaysia", pattern="^(australia|malaysia)$"),
    limit: int = Query(6, ge=1, le=20),
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    result = key_dates.collect(db, campus, limit)
    sources = result["sources"]
    if locale and locale != "en" and sources:
        # The card links each source by its title, so it takes the title the
        # guide page itself shows in this language.
        hashes = dict(db.execute(
            select(OfficialPage.slug, OfficialPage.content_hash)
            .where(OfficialPage.slug.in_(list(sources)))
        ).all())
        tr = translations.load_many(
            db, locale, OFFICIAL_PAGE, list(sources), source_hashes=hashes
        )
        for slug, source in sources.items():
            source["title"] = tr[slug].field("title", source["title"]) or source["title"]
    return result
