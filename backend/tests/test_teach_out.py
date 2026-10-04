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
