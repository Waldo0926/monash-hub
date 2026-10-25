"""Faculty teach-out notices read from the indexed table - app/knowledge/teach_out.py."""
from __future__ import annotations

from app.knowledge import teach_out as to

ROWS = [
    ["Unit Code", "Unit Title", "Change", "Course - Major/Specialisation", "Teach out plan"],
    ["FIT2004", "Algorithms and data structures", "No longer offered", "BCS, BSE",
     "Replace with FIT3234 (S1 and S2)"],
    ["FIT2014", "Theory of computation", "Final offering S2 2027", "BCS",
     "Replace with FIT3235 from 2028"],
    ["FIT3152", "Data analytics", "Final offering S2 2027",
     "BCS - Data science", "To be confirmed"],
    ["", "", "", "BIT - Business information systems", "Replace with FIT3229 from 2028 (S1)"],
    ["72 of 72 units shown", "", "", "", ""],
    ["FIT1045  ", " Introduction to programming", "Renamed", "ALL", "New name:  Software"],
]


def test_rows_become_entries_and_headers_are_skipped():
    got = to.parse_rows(ROWS, "it")
    assert [e.code for e in got] == ["FIT2004", "FIT2014", "FIT3152", "FIT3152", "FIT1045"]
    assert got[0].plan == "Replace with FIT3234 (S1 and S2)"
    assert got[1].change == "Final offering S2 2027"


def test_a_row_without_a_code_continues_the_unit_above():
    got = [e for e in to.parse_rows(ROWS, "it") if e.code == "FIT3152"]
    assert [e.course for e in got] == ["BCS - Data science", "BIT - Business information systems"]
    assert got[1].change == "Final offering S2 2027"
    assert got[1].title == "Data analytics"


def test_cells_are_trimmed_and_unconfirmed_plans_are_kept_as_said():
    got = {e.code: e for e in to.parse_rows(ROWS, "it")}
    assert got["FIT1045"].title == "Introduction to programming"
    assert got["FIT1045"].plan == "New name: Software"
    first = next(e for e in to.parse_rows(ROWS, "it") if e.code == "FIT3152")
    assert first.plan == "To be confirmed"


def test_lookup_names_its_source_and_ignores_unlisted_codes(client, db):
    from app.knowledge.repository import get_or_create_source, upsert_seed_page

    source = get_or_create_source(db, "monash-students", "Monash University",
                                  "https://www.monash.edu")
    page = upsert_seed_page(
        db, source=source, slug=to.SOURCES[0], url="https://www.monash.edu/it/x",
        title="IT re-enrolment", category="enrolment", tags=[], refresh_tier="dynamic",
    )
    page.blocks = [{"type": "table", "rows": ROWS}]
    page.status = "ok"
    page.content_hash = "t1"
    db.commit()

    found = to.lookup(db, ["fit2004", "FIT9999"])
    assert set(found) == {"FIT2004"}
    assert found["FIT2004"]["entries"][0]["plan"] == "Replace with FIT3234 (S1 and S2)"
    assert found["FIT2004"]["sources"][to.SOURCES[0]]["url"] == "https://www.monash.edu/it/x"


MY_ROWS = [
    ["Unit Code", "Unit Title", "Change", "Course - Specialisation", "Teach out plan"],
    ["FIT2004", "Algorithms and data structures", "No longer offered",
     "BCS, BCS in DS, BCS in AI, BSE", "Replace with FIT3234 (S1 and S2)"],
    ["FIT1043", "Introduction to data science", "Final offering S1 2027", "BCS in DS",
     "Replace with FIT2132 (S2)"],
]


def _page(db, slug, url, rows, applies_to):
    from app.knowledge.repository import get_or_create_source, upsert_seed_page

    source = get_or_create_source(db, "monash-students", "Monash University",
                                  "https://www.monash.edu")
    page = upsert_seed_page(
        db, source=source, slug=slug, url=url, title=slug, category="enrolment",
        tags=[], refresh_tier="dynamic", applies_to=applies_to,
    )
    page.blocks = [{"type": "table", "rows": rows}]
    page.status = "ok"
    page.content_hash = slug
    return page


def test_each_campus_sees_its_own_faculty_page(client, db):
    _page(db, to.SOURCES[0], "https://www.monash.edu/it/x", ROWS, "australia")
    _page(db, to.SOURCES[1], "https://www.monash.edu.my/it/x", MY_ROWS, "malaysia")
    db.commit()

    here = to.lookup(db, ["FIT2004", "FIT1043", "FIT2014"], "Malaysia")
    assert set(here) == {"FIT2004", "FIT1043"}
    assert here["FIT1043"]["entries"][0]["plan"] == "Replace with FIT2132 (S2)"
    assert list(here["FIT2004"]["sources"]) == [to.SOURCES[1]]
    assert here["FIT2004"]["entries"][0]["applies_to"] == "malaysia"

    there = to.lookup(db, ["FIT2004", "FIT1043", "FIT2014"], "Clayton")
    assert set(there) == {"FIT2004", "FIT2014"}
    assert list(there["FIT2004"]["sources"]) == [to.SOURCES[0]]

    both = to.lookup(db, ["FIT2004"])
    assert [e["applies_to"] for e in both["FIT2004"]["entries"]] == ["australia", "malaysia"]
    assert both["FIT2004"]["sources"][to.SOURCES[1]]["applies_to"] == "malaysia"


def test_campus_names_map_to_a_faculty_page():
    assert to.region("Malaysia") == "malaysia"
    assert to.region("Clayton") == "australia"
    assert to.region(None) is None


def _unit(db, code, year):
    from app.models.handbook import Unit

    db.add(Unit(unit_code=code, academic_year=year, title=code, credit_points=6,
                subject_prefix=code[:3], source_url=f"https://handbook.monash.edu/{year}/units/{code}",
                content_hash=f"{code}-{year}"))


def test_searching_a_closed_unit_shows_what_replaces_it_on_both_campuses(client, db, monkeypatch):
    """FIT1008 left the 2027 Handbook; a student who searched it on 2026-10-25
    was told only that it was not there."""
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "current_academic_year", 2027)
    _page(db, to.SOURCES[0], "https://www.monash.edu/it/x", ROWS, "australia")
    _page(db, to.SOURCES[1], "https://www.monash.edu.my/it/x", MY_ROWS, "malaysia")
    _unit(db, "FIT2004", 2026)
    _unit(db, "FIT2014", 2027)
    _unit(db, "FIT1099", 2026)
    db.commit()

    body = client.post("/api/v1/ask", json={"query": "FIT2004", "locale": "zh"}).json()
    assert body["answer_type"] == "unit_closed"
    assert body["blocks"][0]["params"] == {"code": "FIT2004", "year": 2027, "last": 2026}
    notice = body["blocks"][1]
    assert notice["type"] == "teach_out"
    assert [e["applies_to"] for e in notice["entries"]] == ["australia", "malaysia"]
    assert notice["entries"][1]["plan"] == "Replace with FIT3234 (S1 and S2)"
    assert body["blocks"][2] == {"type": "link", "to": "/units/FIT2004", "label": "FIT2004"}
    assert {s["url"] for s in body["sources"]} == {"https://www.monash.edu/it/x",
                                                   "https://www.monash.edu.my/it/x"}

    # In an earlier Handbook with no faculty notice: say so, and send them to ask.
    body = client.post("/api/v1/ask", json={"query": "FIT1099"}).json()
    assert body["answer_type"] == "unit_closed"
    assert body["blocks"][0]["key"] == "answer.unitClosed.noNotice"
    assert [b["type"] for b in body["blocks"]] == ["verdict", "link"]

    # In no Handbook at all: a mistyped code, as before.
    assert client.post("/api/v1/ask", json={"query": "FIT9999"}).json()["answer_type"] \
        == "unit_not_found"
