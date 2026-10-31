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


# --- The change since last year ----------------------------------------------

from app.knowledge import tuition_2026  # noqa: E402

PRINTED = tu._printed(2026)


def _change(title, faculty=None, variant=None):
    hits = tu.match(_fees(), title, faculty)
    if variant:
        hits = [(f, t) for f, t in hits if f.variant == variant]
    assert len(hits) == 1, hits
    fee, matched = hits[0]
    return tu.change(fee, matched, PRINTED)


def _diffs(side):
    return [d and d["diff"] for d in side or []]


def test_a_degree_shows_both_rises():
    got = _change("Bachelor of Computer Science")
    assert got["year"] == 2026
    assert got["domestic"] == [{"previous": 47040, "diff": 1440, "pct": 3.1}]
    assert got["international"] == [{"previous": 54720, "diff": 2880, "pct": 5.3}]


def test_each_stream_is_compared_with_its_own_stream():
    got = _change("Diploma in Higher Education Studies")
    assert _diffs(got["domestic"]) == [960, 1440]
    assert _diffs(got["international"]) == [3360, 3840]


def test_monash_english_is_compared_by_length():
    assert _diffs(_change("Monash English", variant="20 weeks")["international"]) == [600]
    assert _diffs(_change("Monash English", variant="10 weeks")["domestic"]) == [200]


def test_an_unreadable_amount_has_no_change_but_the_other_side_does():
    got = _change("Bachelor of Pharmacy (Honours)")
    assert _diffs(got["domestic"]) == [1920]
    assert got["international"] is None


def test_an_unchanged_fee_says_zero():
    got = _change("Master of Philosophy", "Faculty of Pharmacy and Pharmaceutical Sciences")
    assert _diffs(got["domestic"]) == [0] and _diffs(got["international"]) == [0]


def test_a_shared_research_row_applies_to_every_school():
    got = _change("Doctor of Philosophy", "Faculty of Information Technology")
    assert _diffs(got["international"]) == [2880]


def test_a_full_course_fee_is_compared_with_a_full_course_fee():
    got = _change("Master of Data Science")
    assert _diffs(got["domestic"]) == [0]
    assert _diffs(got["international"]) == [3600]


def test_a_different_basis_is_not_a_rise():
    fee = _one("Master of Data Science")
    fee_per_year = tu.Fee(fee.titles, fee.school, fee.page, basis="per_year",
                          domestic=fee.domestic, international=fee.international)
    assert tu.change(fee_per_year, "Master of Data Science", PRINTED) is None


def test_no_baseline_means_no_change():
    assert tu.change(_one("Bachelor of Computer Science"), "Bachelor of Computer Science", None) is None
    assert tu._printed(2027) is None


# The international rises a 2027 fee list in circulation gives for undergraduate
# courses, against 2027 international fees from the official page. Every one
# has to come out of the printed 2026 table, or a 2026 row is wrong.
CIRCULATED = {
    "Bachelor of Arts and Social Sciences": (53280, 3360),
    "Bachelor of Digital Media and Communication": (53280, 3360),
    "Bachelor of Business and Commerce": (54240, 2400),
    "Bachelor of Digital Business": (54240, 2400),
    "Bachelor of Actuarial Analytics": (57600, 2880),
    "Bachelor of Business and Commerce and Bachelor of Computer Science": (57600, 2880),
    "Bachelor of Business and Commerce and Bachelor of Digital Media and Communication": (54240, 2400),
    "Bachelor of Computer Science": (57600, 2880),
    "Bachelor of Computer Science in Data Science": (57600, 2880),
    "Bachelor of Civil Engineering (Honours)": (68160, 3360),
    "Bachelor of Biomedical Engineering (Honours)": (68160, 3360),
    "Bachelor of Chemical Engineering (Honours)": (68160, 3360),
    "Bachelor of Materials Engineering (Honours)": (68160, 3360),
    "Bachelor of Electrical and Computer Systems Engineering (Honours)": (68160, 3360),
    "Bachelor of Mechanical Engineering (Honours)": (68160, 3360),
    "Bachelor of Robotics and Mechatronics Engineering (Honours)": (68160, 3360),
    "Bachelor of Software Engineering (Honours)": (68160, 3360),
    "Bachelor of Psychology": (53280, 3360),
    "Bachelor of Medical Science and Doctor of Medicine": (148320, 9600),
    "Bachelor of Human Nutrition": (63360, 2880),
    "Bachelor of Pharmacy (Honours)": (74400, 3360),
    "Bachelor of Pharmaceutical Science": (63360, 2880),
    "Bachelor of Science": (63360, 2880),
    "Bachelor of Applied Data Science": (63360, 2880),
    "Bachelor of Food Science and Technology": (63360, 2880),
    "Bachelor of Medical Bioscience": (64800, 4320),
    "Diploma of Business": (42240, 1920),
}


def test_the_printed_2026_table_matches_the_circulated_rises():
    for title, (fee_2027, rise) in CIRCULATED.items():
        rows = PRINTED.rows[(tu.norm(title), "")]
        assert fee_2027 - rows[0].international[0] == rise, title
    dhes = PRINTED.rows[(tu.norm("Diploma of Higher Education Studies"), "")][0]
    assert (49440 - dhes.international[0], 55680 - dhes.international[1]) == (3360, 3840)


def test_every_printed_row_names_a_source():
    for row in tuition_2026.ROWS:
        assert row.source in tuition_2026.SOURCES
        assert len(row.domestic) == len(row.international)
        assert all(d < i for d, i in zip(row.domestic, row.international, strict=True))


def test_a_stored_version_from_last_year_wins_over_the_printed_table(db):
    from app.models.knowledge import OfficialPageVersion

    _store(db)
    page = db.scalar(select_page("malaysia-ugfees"))
    old = [
        _p("2026 tuition fees are outlined in the dropdown menu below for undergraduate courses."),
        _h("School of Information Technology"),
        _t(UG_COLS, [UG_HEAD, ["Bachelor of Computer Science", "3", "47,000", "54,000"]]),
    ]
    db.add(OfficialPageVersion(page_id=page.id, content_hash="old", title=page.title,
                               blocks=old, headings=[],
                               captured_at=datetime(2025, 11, 1, tzinfo=UTC)))
    db.commit()
    card = tu.for_course(db, "Bachelor of Computer Science",
                         "Faculty of Information Technology", ["Malaysia"])
    got = card["rows"][0]["change"]
    assert _diffs(got["international"]) == [3600]
    assert got["source"] == "malaysia-ugfees@2025-11-01"
    assert card["previous"]["year"] == 2026
    assert card["previous"]["kind"] == "versions"


def test_the_endpoint_falls_back_to_the_printed_table(client, db):
    _store(db)
    body = client.get("/api/v1/fees").json()
    assert body["previous"]["year"] == 2026
    assert body["previous"]["kind"] == "printed"
    assert set(body["previous"]["sources"]) == set(tuition_2026.SOURCES)
    it = next(g for g in body["sections"][0]["schools"] if g["school"] == "it")
    assert it["rows"][0]["change"]["international"][0]["diff"] == 2880


def select_page(slug):
    from sqlalchemy import select

    return select(OfficialPage).where(OfficialPage.slug == slug)
