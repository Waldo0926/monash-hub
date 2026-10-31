"""Which Handbook a planned unit is checked against.

The site moved to the 2027 Handbook while students were still in 2026. A plan
with FIT1058 and FIT1043 in 2026 second semester was then checked against 2027,
where FIT1058 does not exist and FIT1043 runs only in first semester - so a
plan that matched what Monash actually taught came back with errors. Each unit
is now checked against the Handbook of the year it is placed in.
"""
from __future__ import annotations

import pytest
from app.core.config import get_settings
from app.handbook.plan import handbook_year_for
from app.models.handbook import Unit, UnitOffering, UnitRequisiteGroup, UnitRequisiteItem

S1 = "First semester"
S2 = "Second semester"


def _unit(db, code, year, *periods):
    unit = Unit(
        unit_code=code, academic_year=year, title=code, credit_points="6",
        source_url=f"https://handbook.monash.edu/{year}/units/{code}",
        content_hash=f"hash-{code}-{year}",
    )
    db.add(unit)
    db.flush()
    for period in periods:
        db.add(UnitOffering(unit_id=unit.id, campus="Malaysia", teaching_period=period,
                            offered=True))
    return unit


def _issues(client, entries):
    body = client.post(
        "/api/v1/plan/check", json={"campus": "Malaysia", "entries": entries}
    ).json()
    return body, {(i["unit_code"], i["year"]): i for i in body["issues"]}


@pytest.fixture
def two_handbooks(db, monkeypatch):
    monkeypatch.setattr(get_settings(), "current_academic_year", 2027)
    _unit(db, "FIT1058", 2026, S1, S2)          # gone in 2027
    _unit(db, "FIT1043", 2026, S1, S2)
    _unit(db, "FIT1043", 2027, S1)              # second semester dropped in 2027
    _unit(db, "FIT1045", 2026, S1, S2)
    later = _unit(db, "FIT2014", 2027, S1, S2)
    group = UnitRequisiteGroup(unit_id=later.id, requisite_type="prerequisite", connector="AND")
    db.add(group)
    db.flush()
    db.add(UnitRequisiteItem(group_id=group.id, item_code="FIT1058", item_name="FIT1058",
                             item_type="Unit", order_index=0))
    db.commit()
    return db


def test_a_2026_semester_is_checked_against_the_2026_handbook(client, two_handbooks):
    body, issues = _issues(client, [
        {"unit_code": "FIT1058", "year": 2026, "teaching_period": S2},
        {"unit_code": "FIT1043", "year": 2026, "teaching_period": S2},
    ])
    assert issues == {}
    assert body["handbook_years"] == {"2026": 2026}
    assert body["credit_points"] == 12


def test_the_same_units_in_2027_are_checked_against_2027(client, two_handbooks):
    _, issues = _issues(client, [
        {"unit_code": "FIT1058", "year": 2027, "teaching_period": S2},
        {"unit_code": "FIT1043", "year": 2027, "teaching_period": S2},
    ])
    assert issues[("FIT1058", 2027)]["kind"] == "not_in_year"
    assert issues[("FIT1058", 2027)]["detail"]["handbook_year"] == 2027
    assert issues[("FIT1043", 2027)]["kind"] == "not_offered_in_period"
    assert issues[("FIT1043", 2027)]["detail"]["offered_in"] == [S1]


def test_a_unit_from_2026_satisfies_a_2027_prerequisite(client, two_handbooks):
    _, issues = _issues(client, [
        {"unit_code": "FIT1058", "year": 2026, "teaching_period": S2},
        {"unit_code": "FIT2014", "year": 2027, "teaching_period": S1},
    ])
    assert issues == {}


def test_a_year_with_no_handbook_uses_the_nearest_one(client, two_handbooks):
    body, issues = _issues(client, [
        {"unit_code": "FIT1045", "year": 2025, "teaching_period": S1},
        {"unit_code": "FIT1043", "year": 2028, "teaching_period": S1},
    ])
    assert issues == {}
    assert body["handbook_years"] == {"2025": 2026, "2028": 2027}


@pytest.mark.parametrize(
    ("year", "loaded", "expected"),
    [(2026, [2026, 2027], 2026), (2028, [2026, 2027], 2027),
     (2024, [2026, 2027], 2026), (2026, [], 2027)],
)
def test_handbook_year_for(year, loaded, expected):
    assert handbook_year_for(year, loaded, 2027) == expected
