"""The home page's list of what people search for.

Counting happens inside the unified search and only when it found something;
the list is read from /v1/search/popular. Nothing about who searched is kept.
"""
from __future__ import annotations

from datetime import date, timedelta

import pytest
from app.handbook.parser import parse_unit_page, unit_url
from app.handbook.repository import upsert_unit
from app.models.search_terms import SearchTerm
from app.search import popular


def test_normalise_keeps_searches_and_drops_what_looks_personal():
    assert popular.normalise("  FIT2004 ") == "FIT2004"
    assert popular.normalise("census   date") == "census date"
    assert popular.normalise("特殊考虑") == "特殊考虑"
    assert popular.normalise("a") is None
    assert popular.normalise("someone@student.monash.edu") is None
    assert popular.normalise("0123456789") is None
    assert popular.normalise("https://monash.edu/students") is None
    assert popular.normalise("how do I apply for special consideration late") is None
    assert popular.normalise("x" * 61) is None


def test_label_capitalises_codes_only():
    assert popular.label_for("fit2004") == "FIT2004"
    assert popular.label_for("c2001") == "C2001"
    assert popular.label_for("Census date") == "Census date"


@pytest.fixture
def one_unit(db, handbook_html):
    upsert_unit(db, parse_unit_page(handbook_html("FIT2102"), unit_url("FIT2102", 2026)))
    db.commit()
    popular.clear_cache()
    return db


def test_a_search_that_finds_something_is_counted_once_per_search(client, one_unit):
    client.get("/api/v1/search", params={"q": "FIT2102"})
    client.get("/api/v1/search", params={"q": "fit2102 "})
    client.get("/api/v1/search", params={"q": "ZZZ9999"})
    client.get("/api/v1/search", params={"q": ""})
    rows = one_unit.query(SearchTerm).all()
    assert [(r.term, r.label, r.hits, r.day) for r in rows] == [("fit2102", "FIT2102", 2, date.today())]


def test_popular_needs_two_days_and_caps_one_day(one_unit):
    today = date.today()
    yesterday = today - timedelta(days=1)
    # One person hammering a term on one day: capped, and not shown at all
    # until it has been searched on another day.
    one_unit.add(SearchTerm(term="spam", label="spam", day=today, hits=500))
    # A term people come back to.
    one_unit.add(SearchTerm(term="fit2102", label="FIT2102", day=today, hits=15))
    one_unit.add(SearchTerm(term="fit2102", label="FIT2102", day=yesterday, hits=15))
    one_unit.add(SearchTerm(term="census date", label="census date", day=today, hits=2))
    one_unit.add(SearchTerm(term="census date", label="census date", day=yesterday, hits=3))
    # Outside the window: ignored.
    one_unit.add(SearchTerm(term="old", label="old", day=today - timedelta(days=20), hits=99))
    one_unit.add(SearchTerm(term="old", label="old", day=today - timedelta(days=21), hits=99))
    one_unit.commit()

    found = popular.popular(one_unit, 6, today=today)
    assert found == [
        {"term": "fit2102", "label": "FIT2102", "hits": 30},
        {"term": "census date", "label": "census date", "hits": 5},
    ]

    one_unit.add(SearchTerm(term="spam", label="spam", day=yesterday, hits=1))
    one_unit.commit()
    found = popular.popular(one_unit, 6, today=today)
    # Two days now, but one day's 500 searches count as DAILY_CAP.
    assert found[0]["term"] == "fit2102"
    assert {"term": "spam", "label": "spam", "hits": popular.DAILY_CAP + 1} in found


def test_popular_endpoint_shape_and_pruning(client, one_unit):
    today = date.today()
    one_unit.add(SearchTerm(term="fit2102", label="FIT2102", day=today, hits=3))
    one_unit.add(SearchTerm(term="fit2102", label="FIT2102", day=today - timedelta(days=1), hits=3))
    one_unit.add(SearchTerm(term="gone", label="gone", day=today - timedelta(days=popular.KEEP_DAYS + 1), hits=3))
    one_unit.commit()
    body = client.get("/api/v1/search/popular", params={"limit": 3}).json()
    assert body == {"days": popular.DAYS, "terms": [{"term": "fit2102", "label": "FIT2102", "hits": 6}]}
    assert one_unit.query(SearchTerm).filter(SearchTerm.term == "gone").count() == 0
