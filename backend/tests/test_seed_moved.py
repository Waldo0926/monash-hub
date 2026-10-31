"""A seed whose page moved to a new address but kept its slug.

Monash moved study-abroad/overseas/safety/... to study-abroad/outbound/safety/...
and the coverage rebuild kept the page's slug. Registration looked the page up
by URL only, found nothing, and inserted a second row with the same slug - a
unique violation that failed every deploy from then on.
"""
from __future__ import annotations

from app.knowledge.cleaner import clean_page
from app.knowledge.repository import get_or_create_source, record_fetch, upsert_seed_page
from app.models.knowledge import OfficialPage
from sqlalchemy import func, select

OLD = "https://www.monash.edu/study-abroad/overseas/safety/health,-safety-and-security"
NEW = "https://www.monash.edu/study-abroad/outbound/safety/health,-safety-and-security"


def _register(db, source, url):
    return upsert_seed_page(
        db, source=source, slug="safety-health--safety-and-security", url=url,
        title="Travel health, safety and security", category="exchange",
        tags=["exchange"], refresh_tier="medium",
    )


def test_a_moved_page_keeps_its_row_and_takes_the_new_address(db, official_html):
    source = get_or_create_source(db, "monash-students", "Monash University",
                                  "https://www.monash.edu")
    page = _register(db, source, OLD)
    record_fetch(db, page, clean_page(official_html("sample-guide"), url=OLD))
    db.commit()
    first_id = page.id

    moved = _register(db, source, NEW)
    db.commit()

    assert moved.id == first_id
    assert moved.canonical_url == NEW
    # Fetched from the new address on the next refresh; the old text stays until then.
    assert moved.last_checked is None
    assert moved.content_hash is not None
    assert db.scalar(select(func.count()).select_from(OfficialPage)) == 1


def test_registering_the_same_address_twice_is_still_one_row(db):
    source = get_or_create_source(db, "monash-students", "Monash University",
                                  "https://www.monash.edu")
    _register(db, source, NEW)
    _register(db, source, NEW)
    db.commit()
    assert db.scalar(select(func.count()).select_from(OfficialPage)) == 1
