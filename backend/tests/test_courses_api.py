"""The degree endpoints.

Built on the real C2001 and DATASCI11 fixtures, plus a handful of units, so the
assertions are about the shape a reader meets rather than about invented data.
"""
from __future__ import annotations

import pytest
from app.api.v1.courses import _is_free_elective
from app.handbook.course_parser import (
    aos_url,
    course_url,
    parse_aos_page,
    parse_course_page,
)
from app.handbook.course_repository import upsert_area_of_study, upsert_course
from app.models.handbook import Unit, UnitOffering


def _unit(db, code: str, title: str, campuses: tuple[str, ...]) -> None:
    unit = Unit(
        unit_code=code, academic_year=2026, title=title, credit_points=6,
        source_url=f"https://handbook.monash.edu/2026/units/{code}",
        content_hash=f"hash-{code}",
    )
    db.add(unit)
    db.flush()
    for campus in campuses:
        db.add(
            UnitOffering(
                unit_id=unit.id, campus=campus,
                teaching_period="First semester", offered=True,
            )
        )


@pytest.fixture
def degrees(db, handbook_html):
    upsert_course(db, parse_course_page(handbook_html("course-C2001"), course_url("C2001", 2026)))
    upsert_area_of_study(
        db, parse_aos_page(handbook_html("aos-DATASCI11"), aos_url("DATASCI11", 2026))
    )
    # Two of Part A's units, one taught here and one not.
    _unit(db, "FIT1045", "Introduction to programming", ("Malaysia", "Clayton"))
    _unit(db, "FIT1047", "Introduction to computer systems", ("Clayton",))
    db.commit()
    return db


def test_the_picker_lists_a_degree_with_what_you_choose_it_by(client, degrees):
    body = client.get("/api/v1/courses").json()
    assert body["total"] == 1
    row = body["results"][0]
    assert row["course_code"] == "C2001"
    assert row["credit_points"] == 144
    assert row["duration_years"] == 3
    assert row["course_type_raw"] == "UG specialist"
    assert set(row["campuses"]) == {"Clayton", "Malaysia"}


def test_the_picker_searches_by_code_and_by_name(client, degrees):
    assert client.get("/api/v1/courses", params={"q": "C2001"}).json()["total"] == 1
    assert client.get("/api/v1/courses", params={"q": "computer"}).json()["total"] == 1
    assert client.get("/api/v1/courses", params={"q": "BCompSci"}).json()["total"] == 1
    assert client.get("/api/v1/courses", params={"q": "nursing"}).json()["total"] == 0


def test_a_campus_filters_the_picker_rather_than_marking_it(client, degrees):
    """A degree Malaysia does not teach is not one a Malaysia student can pick.

    This is the opposite of the unit graph, where an unavailable prerequisite
    is marked and kept - there the rule still names it, here there is no
    partial version of "you cannot enrol".
    """
    assert client.get("/api/v1/courses", params={"campus": "Malaysia"}).json()["total"] == 1
    assert client.get("/api/v1/courses", params={"campus": "Suzhou"}).json()["total"] == 0


def test_a_degree_comes_back_as_a_tree_not_a_list(client, degrees):
    body = client.get("/api/v1/courses/C2001").json()
    titles = [c["title"] for c in body["containers"]]
    assert titles[0].startswith("Part A")

    part_d = next(c for c in body["containers"] if c["title"].startswith("Part D"))
    assert part_d["items"] == []
    assert len(part_d["containers"]) == 5


def test_the_degree_view_names_the_units_it_lists(client, degrees):
    """A requirement group of bare codes is not something a student can read."""
    body = client.get("/api/v1/courses/C2001", params={"locale": "zh"}).json()
    assert body["units"]["FIT1045"]["title"] == "Introduction to programming"
    assert body["units"]["FIT1045"]["periods"] == ["S1"]


def test_a_unit_the_campus_does_not_teach_is_marked_in_the_degree(client, degrees):
    body = client.get("/api/v1/courses/C2001", params={"campus": "Malaysia"}).json()
    assert body["units"]["FIT1045"]["offered_at_campus"] is True
    assert body["units"]["FIT1047"]["offered_at_campus"] is False


def test_a_unit_missing_from_the_year_is_reported_not_omitted(client, degrees):
    """Part A names seven units and only two are loaded here.

    The rest have to come back as "not in this year" rather than absent, or the
    page renders a requirement with holes in it and no explanation.
    """
    body = client.get("/api/v1/courses/C2001").json()
    assert body["units"]["FIT1049"]["in_year"] is False


def test_a_degree_lists_the_specialisations_it_offers(client, degrees):
    body = client.get("/api/v1/courses/C2001").json()
    assert "DATASCI11" in {a["code"] for a in body["areas_of_study"]}


def test_an_unknown_degree_is_a_404(client, degrees):
    assert client.get("/api/v1/courses/Z9999").status_code == 404


def test_an_area_of_study_comes_back_with_its_units(client, degrees):
    body = client.get("/api/v1/courses/aos/DATASCI11").json()
    assert body["aos_type"] == "UG specialisation"
    assert body["credit_points"] == 36
    assert {c["title"] for c in body["containers"]} == {"Core units", "Level 3 elective units"}


def test_the_filters_come_from_the_data(client, degrees):
    body = client.get("/api/v1/courses/filters").json()
    assert "Malaysia" in body["campuses"]
    assert "UG specialist" in body["course_types"]


# --- a part that asks for a specialisation --------------------------------
#
# "Part C. Specialist studies" reported 0/36 for a student who had planned the
# whole specialisation. The part does not list units at all - it lists the four
# specialisations on offer - and a plan holds unit codes, so nothing downstream
# could ever match FIT2102 against ALGSFTWR01.

def test_a_specialisation_carries_the_units_inside_it(client, degrees):
    body = client.get("/api/v1/courses/C2001").json()
    by_code = {a["code"]: a for a in body["areas_of_study"]}
    assert "DATASCI11" in by_code, "the specialisation Part C names must be listed"

    codes = by_code["DATASCI11"]["unit_codes"]
    assert codes, "without this the part it satisfies can never be credited"
    assert all(code.isalnum() for code in codes)


def test_part_c_names_specialisations_not_units(client, degrees):
    """The shape that caused the bug, pinned so a refactor cannot quietly undo
    the fix by changing what Part C contains."""
    body = client.get("/api/v1/courses/C2001").json()
    part_c = next(c for c in body["containers"] if "Specialist" in (c["title"] or ""))
    kinds = {item["type"] for item in part_c["items"]}
    assert kinds == {"specialisation"}
    assert "unit" not in kinds


def test_the_facts_map_covers_the_specialisation_units(client, degrees):
    """A planned unit with no entry here contributes zero credit points, which
    is the same wrong answer by a different route."""
    body = client.get("/api/v1/courses/C2001").json()
    by_code = {a["code"]: a for a in body["areas_of_study"]}
    for code in by_code["DATASCI11"]["unit_codes"]:
        assert code in body["units"], code


# --- free elective parts ------------------------------------------------------
#
# A part that lists what counts and a part that counts anything are scored
# differently by the planner, and only the API knows which is which - the
# titles it decides from are English, and the planner may be reading Chinese.


@pytest.mark.parametrize(
    ("title", "description", "expected"),
    [
        # The Handbook's plainest form, and the one that was reported: Part E
        # of C2001, showing 0/48 for a student who had planned twelve units.
        ("Part E. Free elective studies", "48 credit points of free electives", True),
        ("Part D. Free electives", "", True),
        # No "free" in the title, but the description has the Handbook's phrase
        # for a part with no list. 31 parts across the catalogue look like this.
        ("Part D. Elective studies", "select any units from across the University", True),
        # Named lists. These are satisfied only by what they name.
        ("Part B. Specified elective studies", "from the following elective units", False),
        ("Discipline elective studies", "the units listed below", False),
        # Mentions the University in passing and is not an elective part at all.
        # Without the title clause, all three of these matched.
        ("Part A. Foundation studies", "units from across the University", False),
        ("Rules", "you may take units from across the University", False),
        ("Course requirements", "across the University", False),
        (None, "across the University", False),
    ],
)
def test_a_part_that_counts_anything_is_told_apart_from_one_that_lists(
    title, description, expected
):
    assert _is_free_elective(title, description) is expected


def test_the_flag_reaches_the_planner(client, degrees):
    """It is read off every container, so a missing key would silently score
    every free elective part as zero again."""
    body = client.get("/api/v1/courses/C2001").json()
    assert all("free_elective" in part for part in body["containers"])
    part_e = next(c for c in body["containers"] if "Free elective" in (c["title"] or ""))
    assert part_e["free_elective"] is True
    part_a = next(c for c in body["containers"] if "Foundation" in (c["title"] or ""))
    assert part_a["free_elective"] is False
