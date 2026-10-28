"""Fees read from the indexed /ugfees and /pgfees tables: app/knowledge/tuition.py.

The blocks below are small synthetic copies of the shapes the cleaner stores for
those two pages (October 2026): one table per school under a heading, the
"Malaysian | International" labels as the first body row, majors and the
engineering honours degrees listed inside the first cell, a fee cell with two
streams, and the per year or full course basis written inside postgraduate
cells. The amounts match the 2027 content handoff of 2026-10-28.
"""
from __future__ import annotations

from datetime import UTC, datetime

from app.knowledge import tuition as tu
from app.models.knowledge import OfficialPage, OfficialSource

UG_COLS = ["Course", "Duration (years)", "Tuition fees per year (RM)", ""]
UG_HEAD = ["", "", "Malaysian", "International"]
PG_COLS = ["Course", "Type", "Duration (years)", "Tuition fees (RM)", ""]
PG_HEAD = ["", "", "", "Malaysian", "International"]


def _h(text, level=2):
    return {"type": "heading", "level": level, "text": text}


def _t(columns, rows):
    return {"type": "table", "columns": columns, "rows": rows}


def _p(text):
    return {"type": "paragraph", "spans": [{"text": text}]}


def _l(*items):
    return {"type": "list", "ordered": False, "items": [[{"text": i}] for i in items]}


UG = [
    _p("2027 tuition fees are outlined in the dropdown menu below for undergraduate courses."),
    _h("School of Arts & Social Sciences"),
    _t(UG_COLS, [
        UG_HEAD,
        ["Bachelor of Arts and Social Sciences\nMajors in:\nCommunication\nPsychology", "3", "44,640", "53,280"],
        ["Bachelor of Arts (Honours)", "1", "44,640", "51,360"],
    ]),
    _h("School of Business"),
    _t(UG_COLS, [
        UG_HEAD,
        ["Bachelor in Actuarial Analytics", "3", "48,480", "57,600"],
        ["Double degrees", "", "", ""],
        ["Bachelor of Business and Commerce and Bachelor of Computer Science", "4", "48,480", "57,600"],
    ]),
    _h("School of Engineering"),
    _t(UG_COLS, [
        UG_HEAD,
        ["Bachelor of Engineering\nplus eight Honours programs\nBachelor of Biomedical Engineering (Honours)\n"
         "Bachelor of Software Engineering (Honours)", "4", "56,160", "68,160"],
    ]),
    _h("School of Information Technology"),
    _t(UG_COLS, [
        UG_HEAD,
        ["Bachelor of Computer Science", "3", "48,480", "57,600"],
        ["Bachelor of Computer Science (Honours)", "1", "48,000", "57,120"],
    ]),
    _h("School of Pharmacy"),
    _t(UG_COLS, [
        UG_HEAD,
        ["Bachelor of Pharmacy (Honours)", "4", "62,400", "74,40"],
    ]),
    _h("Other courses"),
    _t(UG_COLS, [
        UG_HEAD,
        ["Monash English", "20 weeks", "12,000", "12,600"],
        ["", "10 weeks", "7,100", "8,000"],
        ["Diploma in Higher Education Studies", "1 year",
         "40,800 (non-science stream) 46,560 (science stream)",
         "49,440 (non-science stream) 55,680 (science stream)"],
        ["Diploma in Business", "2 years", "36,000", "42,240"],
    ]),
    _h("General fees"),
    _h("Once-only fees", 3),
    _l("Application - RM100", "Registration - RM200"),
]

PHD = ["Doctor of Philosophy (PhD)", "Research",
       "The normal length of candidature is considered to be:\nFull-time: 3-4 years (6-8 semesters)",
       "49,920\n(per year)", "57,600\n(per year)"]

PG = [
    _p("2027 tuition fees are outlined below for postgraduate courses."),
    _h("School of Information Technology"),
    _t(PG_COLS, [
        PG_HEAD,
        ["Master of Data Science", "Coursework",
         "Full-time: 1.5-2 years (3-4 semesters)*\nPart-time: 3-4 years (6-8 semesters)*",
         "64,080\n(full course)", "77,760\n(full course)"],
        ["Master of Philosophy (MPhil)\nThe degree is a 100% research program.", "Research",
         "Full-time: 2 years (4 semesters)", "49,920\n(per year)", "57,600\n(per year)"],
        PHD,
    ]),
    _h("School of Pharmacy"),
    _t(PG_COLS, [
        PG_HEAD,
        ["Master of Pharmaceutical Science", "Coursework", "Full-time: 1-2 years (2-4 semesters)*",
         "49,920\n(per year)", "57,600\n(per year)"],
        ["Master of Philosophy", "Research", "Full-time: 2 years (4 semesters)",
         "48,480\n(per year)", "54,720\n(per year)"],
        PHD,
    ]),
    _h("General fees"),
    _h("Per-semester fee", 3),
    _l("General amenities - RM100"),
]


def _fees():
    return tu.parse_blocks(UG, "malaysia-ugfees") + tu.parse_blocks(PG, "malaysia-pgfees")


def _one(title, faculty=None):
    hits = tu.match(_fees(), title, faculty)
    assert len(hits) == 1, hits
    return hits[0][0]


def _values(amounts):
    return [a.value for a in amounts]


def test_undergraduate_rows_are_per_year_from_the_column_header():
    fee = _one("Bachelor of Computer Science")
    assert (_values(fee.domestic), _values(fee.international)) == ([48480], [57600])
    assert fee.basis == "per_year"
    assert fee.school == "it"


def test_majors_in_the_first_cell_are_not_degrees():
    fee = _one("Bachelor of Arts and Social Sciences")
    assert fee.titles == ("Bachelor of Arts and Social Sciences",)


def test_a_label_row_is_skipped_and_double_degrees_still_read():
    fee = _one("Bachelor of Business and Commerce and Bachelor of Computer Science")
    assert _values(fee.domestic) == [48480]
    assert not tu.match(_fees(), "Double degrees")


def test_bachelor_in_and_bachelor_of_are_the_same_degree():
    assert _values(_one("Bachelor of Actuarial Analytics").international) == [57600]
    assert _values(_one("Diploma of Business").domestic) == [36000]


def test_every_honours_degree_named_in_the_engineering_row_gets_its_fee():
    for title in ("Bachelor of Biomedical Engineering (Honours)",
                  "Bachelor of Software Engineering (Honours)"):
        fee = _one(title)
        assert (_values(fee.domestic), _values(fee.international)) == ([56160], [68160])


def test_a_number_that_does_not_read_is_kept_as_written():
    fee = _one("Bachelor of Pharmacy (Honours)")
    assert _values(fee.domestic) == [62400]
    assert fee.international[0].value is None
    assert fee.international[0].written == "74,40"
    assert tu._row(fee)["unreadable"] is True


def test_two_streams_in_one_cell_keep_their_labels():
    fee = _one("Diploma in Higher Education Studies")
    assert [(a.value, a.label) for a in fee.domestic] == [
        (40800, "non-science stream"), (46560, "science stream")]
    assert _values(fee.international) == [49440, 55680]


def test_a_row_without_a_title_continues_the_one_above():
    hits = tu.match(_fees(), "Monash English")
    rows = sorted((f.variant, _values(f.domestic), f.basis) for f, _ in hits)
    assert rows == [("10 weeks", [7100], "full_course"), ("20 weeks", [12000], "full_course")]


def test_the_cell_decides_full_course_or_per_year():
    assert _one("Master of Data Science").basis == "full_course"
    assert _one("Master of Pharmaceutical Science").basis == "per_year"
    assert _one("Master of Data Science").duration == "Full-time: 1.5-2 years (3-4 semesters)"


def test_a_title_several_schools_price_needs_the_faculty():
    assert tu.match(_fees(), "Master of Philosophy") == []
    it = _one("Master of Philosophy", "Faculty of Information Technology")
    pharmacy = _one("Master of Philosophy", "Faculty of Pharmacy and Pharmaceutical Sciences")
    assert (_values(it.domestic), _values(pharmacy.domestic)) == ([49920], [48480])
    assert _values(pharmacy.international) == [54720]
    assert tu.match(_fees(), "Doctor of Philosophy", "Faculty of Law") == []
    phd = _one("Doctor of Philosophy", "Faculty of Information Technology")
    assert phd.duration == "Full-time: 3-4 years (6-8 semesters)"


def test_arts_and_social_sciences_is_not_the_science_school():
    assert tu.school_of("School of Arts & Social Sciences") == "arts"
    assert tu.school_of("School of Science") == "science"
    assert tu.school_of("Jeffrey Cheah School of Medicine and Health Sciences") == "medicine"


def test_general_fees_keep_their_subheading():
    assert tu.general_fees(UG) == ["Once-only fees: Application - RM100",
                                   "Once-only fees: Registration - RM200"]
    assert tu.general_fees(PG) == ["Per-semester fee: General amenities - RM100"]


def test_an_unknown_degree_gets_nothing():
    assert tu.match(_fees(), "Bachelor of Laws (Honours)") == []
    assert tu.match(_fees(), None) == []


# --- Through the API, with the two pages stored --------------------------


def _store(db):
    source = OfficialSource(key="monash-malaysia", name="Monash Malaysia",
                            base_url="https://www.monash.edu.my")
    db.add(source)
    db.flush()
    for slug, blocks in (("malaysia-ugfees", UG), ("malaysia-pgfees", PG)):
        db.add(OfficialPage(
            source_id=source.id, slug=slug, canonical_url=f"https://www.monash.edu.my/{slug[9:]}",
            title=f"Fees ({slug[9:]})", category="support", status="ok", tags=[],
            applies_to="malaysia", blocks=blocks, content_hash=f"hash-{slug}",
            last_checked=datetime(2026, 10, 28, tzinfo=UTC),
        ))
    db.commit()


def test_the_fees_endpoint_groups_rows_by_page_and_school(client, db):
    _store(db)
    body = client.get("/api/v1/fees").json()
    assert body["year"] == 2027
    assert [s["source"] for s in body["sections"]] == ["malaysia-ugfees", "malaysia-pgfees"]
    schools = [g["school"] for g in body["sections"][0]["schools"]]
    assert schools == ["arts", "business", "engineering", "it", "pharmacy", "other"]
    assert body["sources"]["malaysia-pgfees"]["last_checked"].startswith("2026-10-28")
    assert "Per-semester fee: General amenities - RM100" in body["general"]


def test_the_fees_endpoint_is_empty_before_the_pages_are_read(client, db):
    body = client.get("/api/v1/fees").json()
    assert body["sections"] == [] and body["year"] is None


def test_the_card_needs_a_malaysia_degree(db):
    _store(db)
    assert tu.for_course(db, "Bachelor of Computer Science",
                         "Faculty of Information Technology", ["Clayton"]) is None
    card = tu.for_course(db, "Bachelor of Computer Science",
                         "Faculty of Information Technology", ["Clayton", "Malaysia"])
    assert card["rows"][0]["domestic"][0]["value"] == 48480
    assert list(card["sources"]) == ["malaysia-ugfees"]


def test_a_degree_known_to_be_unpriced_says_so(db):
    _store(db)
    card = tu.for_course(db, "Master of Professional Counselling",
                         "Faculty of Medicine, Nursing and Health Sciences", ["Malaysia"])
    assert card["rows"] == []
    assert "fee table" in card["not_listed"]["en"]
