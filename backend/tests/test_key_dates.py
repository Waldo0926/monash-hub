"""Key dates read from official date tables - app/knowledge/key_dates.py.

Rows are synthetic but keep the shapes the cleaner stores for the census,
final-assessment and principal-dates pages.
"""
from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest
from app.knowledge import key_dates as kd


@pytest.mark.parametrize(
    "text,expected",
    [
        ("31 Aug 2026", (date(2026, 8, 31), None)),
        ("Sat 28 Nov 2026", (date(2026, 11, 28), None)),
        ("2–18 Nov 2026", (date(2026, 11, 2), date(2026, 11, 18))),
        ("30 Oct – 17 Nov 2028", (date(2028, 10, 30), date(2028, 11, 17))),
        ("24–28 March 2025", (date(2025, 3, 24), date(2025, 3, 28))),
        ("28 Dec – 8 Jan 2027", (date(2026, 12, 28), date(2027, 1, 8))),
        ("2 Feb 2026 (if eExams are scheduled)", (date(2026, 2, 2), None)),
        ("N/A", None),
        ("TBA", None),
        ("Varied", None),
        ("31 Feb 2026", None),
    ],
)
def test_parse_range(text, expected):
    assert kd.parse_range(text) == expected


CENSUS_ROWS = [
    ["Financial penalties apply Academic penalties apply", "", "", "", "", ""],
    ["Semester two (S2-01)", "27 Jul – 18 Nov 2026", "31 Aug 2026", "1 Sep 2026",
     "6 Oct 2026", "23 Oct 2026"],
    ["Research Q4 (RES-Q4)", "1 Oct – 31 Dec 2026", "31 Dec 2026", "N/A", "N/A", "31 Dec 2026"],
]


def test_census_takes_census_withdraw_and_teaching_end():
    got = {(k.kind, k.period): k.start for k in kd.parse_census(CENSUS_ROWS)}
    assert got[("census", "S2-01")] == date(2026, 8, 31)
    assert got[("withdraw", "S2-01")] == date(2026, 10, 6)
    assert got[("teaching_end", "S2-01")] == date(2026, 10, 23)
    # N/A stays out rather than becoming a guess.
    assert ("withdraw", "RES-Q4") not in got


FINALS_ROWS = [
    ["Semester two (S2-01)", "26–30 Oct 2026", "14 Sep 2026", "2–18 Nov 2026", "3 Dec 2026"],
    ["October intake – Malaysia (OCT-MY-01)", "25 Jan – 29 Jan 2027", "4 Jan 2027",
     "1–12 Feb 2027", "1 Mar 2027"],
    # 2024 layout: the code has its own column. Past, and a different shape.
    ["Semester two", "S2-01", "16 Sep 2024", "28 Oct – 15 Nov 2024", "2 Dec 2024"],
]


def test_finals_reads_swot_exams_results():
    got = {(k.kind, k.period): (k.start, k.end) for k in kd.parse_finals(FINALS_ROWS)}
    assert got[("swot_vac", "S2-01")] == (date(2026, 10, 26), date(2026, 10, 30))
    assert got[("exams", "S2-01")] == (date(2026, 11, 2), date(2026, 11, 18))
    assert got[("results", "S2-01")] == (date(2026, 12, 3), None)
    assert got[("exams", "OCT-MY-01")] == (date(2027, 2, 1), date(2027, 2, 12))
    assert all(start.year >= 2026 for start, _ in got.values())


# monash.edu.my layout, months without a year: only the weekdays say 2026.
MY_ROWS = [
    ["Day", "Date", "Description"],
    ["October", "", ""],
    ["Sun", "25", "University closed: Sultan's Jubilee"],
    ["Mon", "26", "University closed: Sultan's Jubilee (replacement holiday)"],
    ["Mon", "26", "Teaching starts: October intake (OCT-MY-01)"],
    ["November", "", ""],
    ["Sun", "8", "University closed: Deepavali"],
    ["Mon", "9", "University closed: Deepavali (replacement holiday)"],
    ["December", "", ""],
    ["Fri", "25", "University closed: Christmas Day"],
    ["January 2027", "", ""],
    ["Fri", "1", "University closed: New Year's Day"],
]

# monash.edu layout: weekday and day in one cell.
AU_ROWS = [
    ["December", ""],
    ["Wed 23", "University closed: Reopens Monday 4 January 2027"],
    ["Fri 25", "University closed: Christmas Day"],
    ["Sat 26", "University closed: Boxing Day"],
]


def test_holiday_year_comes_from_the_weekdays():
    got = kd.parse_holidays([MY_ROWS], "my", around=2026)
    assert [(k.start, k.end, k.name) for k in got] == [
        (date(2026, 10, 25), date(2026, 10, 26), "Sultan's Jubilee"),
        (date(2026, 11, 8), date(2026, 11, 9), "Deepavali"),
        (date(2026, 12, 25), None, "Christmas Day"),
        (date(2027, 1, 1), None, "New Year's Day"),
    ]


def test_two_cell_layout_and_closedown_row():
    got = kd.parse_holidays([AU_ROWS], "au", around=2026)
    # "Reopens Monday..." is the closedown notice, not a named holiday.
    assert [(k.start, k.name) for k in got] == [
        (date(2026, 12, 25), "Christmas Day"),
        (date(2026, 12, 26), "Boxing Day"),
    ]


def test_table_whose_weekdays_fit_no_year_is_dropped():
    rows = [["October", "", ""], ["Mon", "1", "University closed: X"],
            ["Mon", "2", "University closed: Y"], ["Mon", "3", "University closed: Z"]]
    assert kd.parse_holidays([rows], "my", around=2026) == []


def _page(rows_list, status="ok"):
    return SimpleNamespace(status=status, blocks=[{"type": "table", "rows": r} for r in rows_list])


def test_upcoming_filters_campus_periods_and_past_dates():
    pages = {
        kd.CENSUS: _page([CENSUS_ROWS]),
        kd.FINALS: _page([FINALS_ROWS]),
        kd.PRINCIPAL["malaysia"]: _page([MY_ROWS]),
    }
    got = kd.upcoming(pages, "malaysia", date(2026, 10, 4), limit=20)
    kinds = [(k.kind, k.period or k.name) for k in got]
    assert kinds[:4] == [
        ("withdraw", "S2-01"),
        ("teaching_end", "S2-01"),
        ("holiday", "Sultan's Jubilee"),
        ("swot_vac", "S2-01"),
    ]
    # Census on 31 Aug has passed; RES-Q4 is not a period students take.
    assert ("census", "S2-01") not in kinds
    assert all(k.period != "RES-Q4" for k in got)
    # An exam period still running counts as upcoming.
    during = kd.upcoming(pages, "malaysia", date(2026, 11, 10), limit=20)
    assert ("exams", "S2-01") in [(k.kind, k.period) for k in during]


def test_page_that_failed_to_fetch_contributes_nothing():
    pages = {kd.CENSUS: _page([CENSUS_ROWS], status="error")}
    assert kd.upcoming(pages, "australia", date(2026, 1, 1), limit=20) == []


def test_key_dates_endpoint_names_its_sources(client, db):
    from app.knowledge.repository import get_or_create_source, upsert_seed_page

    source = get_or_create_source(db, "monash-students", "Monash University",
                                  "https://www.monash.edu")
    for slug, rows in ((kd.CENSUS, CENSUS_ROWS), (kd.FINALS, FINALS_ROWS),
                       (kd.PRINCIPAL["malaysia"], MY_ROWS)):
        page = upsert_seed_page(
            db, source=source, slug=slug, url=f"https://www.monash.edu/{slug}",
            title=slug, category="fees-dates", tags=[], refresh_tier="dynamic",
        )
        page.blocks = [{"type": "table", "rows": rows}]
        page.status = "ok"
    db.commit()

    body = client.get("/api/v1/key-dates", params={"campus": "malaysia", "limit": 20}).json()
    assert body["campus"] == "malaysia"
    assert body["items"] == sorted(body["items"], key=lambda i: i["date"])
    assert {i["source"] for i in body["items"]} <= set(body["sources"])
    assert all(body["sources"][s]["url"].startswith("https://") for s in body["sources"])
    assert client.get("/api/v1/key-dates", params={"campus": "mars"}).status_code == 422
