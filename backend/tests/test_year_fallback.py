"""A page for a unit the current Handbook dropped.

When the site moved to the 2027 Handbook, FIT2004 and FIT1008 - in the 2026
Handbook, gone from 2027 - became "not found", and so did the prerequisite
graph, which opens on FIT2004. Students still sitting those units need them, so
without ``?year=`` the latest Handbook that lists a code is used, and the
response says which year it was missing from.
"""
from __future__ import annotations

import pytest
from app.core.config import get_settings
from app.handbook.course_parser import aos_url, course_url, parse_aos_page, parse_course_page
from app.handbook.course_repository import upsert_area_of_study, upsert_course
from app.models.handbook import Unit, UnitOffering, UnitRequisiteGroup, UnitRequisiteItem


def _unit(db, code: str, year: int) -> Unit:
    unit = Unit(
        unit_code=code, academic_year=year, title=f"{code} {year}", credit_points=6,
        source_url=f"https://handbook.monash.edu/{year}/units/{code}",
        content_hash=f"hash-{code}-{year}",
    )
    db.add(unit)
    db.flush()
    db.add(UnitOffering(unit_id=unit.id, campus="Malaysia",
                        teaching_period="First semester", offered=True))
    return unit


@pytest.fixture
def next_year(db, handbook_html, monkeypatch):
    """The site is on 2027; FIT2004 and its prerequisite FIT1008 exist only in 2026."""
    monkeypatch.setattr(get_settings(), "current_academic_year", 2027)
    _unit(db, "FIT1008", 2026)
    fit2004 = _unit(db, "FIT2004", 2026)
    group = UnitRequisiteGroup(unit_id=fit2004.id, requisite_type="prerequisite", connector="AND")
    db.add(group)
    db.flush()
    db.add(UnitRequisiteItem(group_id=group.id, item_code="FIT1008", item_name="FIT1008",
                             item_type="Unit", order_index=0))
    # In both years: the current one must win.
    _unit(db, "FIT2014", 2026)
    _unit(db, "FIT2014", 2027)
    upsert_course(db, parse_course_page(handbook_html("course-C2001"), course_url("C2001", 2026)))
    upsert_area_of_study(
        db, parse_aos_page(handbook_html("aos-DATASCI11"), aos_url("DATASCI11", 2026))
    )
    db.commit()
    return db


def test_a_unit_dropped_from_the_current_handbook_comes_from_the_last_one(client, next_year):
    response = client.get("/api/v1/units/FIT2004")
    assert response.status_code == 200
    body = response.json()
    assert body["academic_year"] == 2026
    assert body["not_in_year"] == 2027


def test_a_unit_in_the_current_handbook_does_not_fall_back(client, next_year):
    body = client.get("/api/v1/units/FIT2014").json()
    assert body["academic_year"] == 2027
    assert body["not_in_year"] is None


def test_the_prerequisite_graph_opens_on_a_dropped_unit(client, next_year):
    response = client.get(
        "/api/v1/units/FIT2004/tree",
        params={"direction": "upstream", "depth": 1, "campus": "Malaysia"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["academic_year"] == 2026
    assert body["not_in_year"] == 2027
    # The graph is read from the same Handbook as the seed, so its parent is there too.
    nodes = {n["unit_code"]: n for n in body["nodes"]}
    assert set(nodes) == {"FIT2004", "FIT1008"}
    assert all(n["in_year"] for n in nodes.values())


@pytest.mark.parametrize("path", ["assessment", "requisites", "offerings"])
def test_the_unit_sub_resources_fall_back_too(client, next_year, path):
    body = client.get(f"/api/v1/units/FIT2004/{path}").json()
    assert (body["academic_year"], body["not_in_year"]) == (2026, 2027)


def test_an_explicit_year_is_answered_exactly(client, next_year):
    response = client.get("/api/v1/units/FIT2004", params={"year": 2027})
    assert response.status_code == 404
    assert "2027" in response.json()["detail"]


def test_a_code_in_no_handbook_is_still_a_404(client, next_year):
    response = client.get("/api/v1/units/ZZZ9999")
    assert response.status_code == 404
    assert "2027" in response.json()["detail"]


def test_a_degree_and_an_area_of_study_fall_back_the_same_way(client, next_year):
    course = client.get("/api/v1/courses/C2001").json()
    assert (course["academic_year"], course["not_in_year"]) == (2026, 2027)
    aos = client.get("/api/v1/courses/aos/DATASCI11").json()
    assert (aos["academic_year"], aos["not_in_year"]) == (2026, 2027)


def test_a_page_lists_the_years_it_can_be_read_in(client, next_year):
    assert client.get("/api/v1/units/FIT2014").json()["available_years"] == [2027, 2026]
    assert client.get("/api/v1/units/FIT2004").json()["available_years"] == [2026]
    tree = client.get("/api/v1/units/FIT2004/tree", params={"depth": 1}).json()
    assert tree["available_years"] == [2026]
    assert client.get("/api/v1/courses/C2001").json()["available_years"] == [2026]
    assert client.get("/api/v1/courses/aos/DATASCI11").json()["available_years"] == [2026]


def test_an_explicit_year_reads_that_handbook(client, next_year):
    body = client.get("/api/v1/units/FIT2014", params={"year": 2026}).json()
    assert (body["academic_year"], body["not_in_year"]) == (2026, None)


def test_the_list_pages_offer_every_loaded_year(client, next_year):
    assert client.get("/api/v1/units/filters").json()["years"] == [2027, 2026]
    filters = client.get("/api/v1/courses/filters").json()
    assert filters["years"] == [2026]
    assert filters["academic_year"] == 2027
