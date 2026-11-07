"""Checking a course plan.

The interesting cases are all about time: a prerequisite in the same semester
is not satisfied, a corequisite in the same semester is, and a full-year unit
is finished by neither semester of its own year.
"""
from __future__ import annotations

import pytest
from app.models.handbook import Unit, UnitOffering, UnitRequisiteGroup, UnitRequisiteItem

S1 = "First semester"
S2 = "Second semester"


def _unit(db, code, *, campuses=(("Malaysia", S1), ("Malaysia", S2)), points=6):
    unit = Unit(
        unit_code=code, academic_year=2026, title=code, credit_points=str(points),
        source_url=f"https://handbook.monash.edu/2026/units/{code}",
        content_hash=f"hash-{code}",
    )
    db.add(unit)
    db.flush()
    for campus, period in campuses:
        db.add(UnitOffering(unit_id=unit.id, campus=campus, teaching_period=period, offered=True))
    return unit


def _requires(db, unit, *codes, kind="prerequisite", connector="AND"):
    group = UnitRequisiteGroup(unit_id=unit.id, requisite_type=kind, connector=connector)
    db.add(group)
    db.flush()
    for index, code in enumerate(codes):
        db.add(UnitRequisiteItem(group_id=group.id, item_code=code, item_name=code,
                                 item_type="Unit", order_index=index))


def _post(client, entries, campus="Malaysia"):
    return client.post(
        "/api/v1/plan/check",
        json={"year": 2026, "campus": campus, "entries": entries},
    ).json()


def kinds(body, code=None):
    return {i["kind"] for i in body["issues"] if code is None or i["unit_code"] == code}


@pytest.fixture
def chain(db):
    """AAA1001 -> BBB2001, with CCC3001 needing one of AAA1001 or DDD1001."""
    _unit(db, "AAA1001")
    b = _unit(db, "BBB2001")
    c = _unit(db, "CCC3001")
    _unit(db, "DDD1001")
    _unit(db, "EEE1001", campuses=(("Clayton", S1),))
    _unit(db, "FFF1001", campuses=(("Malaysia", S1),))
    _requires(db, b, "AAA1001")
    _requires(db, c, "AAA1001", "DDD1001", connector="OR")
    db.commit()
    return db


def test_a_plan_in_order_has_nothing_to_report(client, chain):
    body = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S1},
        {"unit_code": "BBB2001", "year": 2026, "teaching_period": S2},
    ])
    assert body["issues"] == []
    assert body["credit_points"] == 12


def test_a_prerequisite_in_the_same_semester_is_not_satisfied(client, chain):
    """You cannot have passed a unit you are sitting in right now."""
    body = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S1},
        {"unit_code": "BBB2001", "year": 2026, "teaching_period": S1},
    ])
    assert kinds(body, "BBB2001") == {"missing_prerequisite"}


def test_a_prerequisite_placed_later_is_reported(client, chain):
    body = _post(client, [
        {"unit_code": "BBB2001", "year": 2026, "teaching_period": S1},
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S2},
    ])
    assert kinds(body, "BBB2001") == {"missing_prerequisite"}


def test_an_or_group_needs_only_one_of_its_members(client, chain):
    body = _post(client, [
        {"unit_code": "DDD1001", "year": 2026, "teaching_period": S1},
        {"unit_code": "CCC3001", "year": 2026, "teaching_period": S2},
    ])
    assert kinds(body, "CCC3001") == set()


def test_an_unsatisfied_or_group_offers_the_whole_choice(client, chain):
    """Reporting one member would send the student to fix the wrong thing."""
    body = _post(client, [{"unit_code": "CCC3001", "year": 2026, "teaching_period": S1}])
    issue = next(i for i in body["issues"] if i["kind"] == "missing_prerequisite")
    assert set(issue["detail"]["any_of"]) == {"AAA1001", "DDD1001"}
    assert issue["detail"]["all_of"] == []


def test_a_corequisite_may_sit_in_the_same_semester(client, db):
    _unit(db, "AAA1001")
    b = _unit(db, "BBB2001")
    _requires(db, b, "AAA1001", kind="corequisite")
    db.commit()
    body = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S1},
        {"unit_code": "BBB2001", "year": 2026, "teaching_period": S1},
    ])
    assert body["issues"] == []


def test_a_unit_the_campus_does_not_teach_is_an_error(client, chain):
    """The failure this planner exists for, and the one that hides until enrolment."""
    body = _post(client, [{"unit_code": "EEE1001", "year": 2026, "teaching_period": S1}])
    issue = next(i for i in body["issues"] if i["kind"] == "not_offered_at_campus")
    assert issue["detail"]["elsewhere"] == ["Clayton"]


def test_a_unit_taught_here_but_not_that_semester_is_an_error(client, chain):
    body = _post(client, [{"unit_code": "FFF1001", "year": 2026, "teaching_period": S2}])
    issue = next(i for i in body["issues"] if i["kind"] == "not_offered_in_period")
    assert issue["detail"]["offered_in"] == [S1]


@pytest.fixture
def one_way(db):
    """AAA1001 prohibits ZZZ2001; ZZZ2001 lists nothing back (ETW1001 and ETW2001)."""
    a = _unit(db, "AAA1001")
    _unit(db, "ZZZ2001")
    _requires(db, a, "ZZZ2001", kind="prohibitions", connector="OR")
    db.commit()


def test_a_prohibited_unit_taken_first_blocks_the_unit_that_lists_it(client, one_way):
    body = _post(client, [
        {"unit_code": "ZZZ2001", "year": 2026, "teaching_period": S1},
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S2},
    ])
    issue = next(i for i in body["issues"] if i["kind"] == "prohibited_with")
    assert issue["unit_code"] == "AAA1001"
    assert issue["detail"]["units"] == ["ZZZ2001"]


def test_a_prohibition_does_not_run_backwards(client, one_way):
    """AAA1001 then ZZZ2001 is allowed: ZZZ2001 does not prohibit AAA1001."""
    body = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S1},
        {"unit_code": "ZZZ2001", "year": 2026, "teaching_period": S2},
    ])
    assert "prohibited_with" not in kinds(body)


def test_a_prohibited_unit_in_the_same_semester_is_a_clash(client, one_way):
    body = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S1},
        {"unit_code": "ZZZ2001", "year": 2026, "teaching_period": S1},
    ])
    assert "prohibited_with" in kinds(body, "AAA1001")


def test_a_two_way_prohibition_is_reported_on_the_later_unit(client, db):
    a = _unit(db, "AAA1001")
    b = _unit(db, "BBB1001")
    _requires(db, a, "BBB1001", kind="prohibitions")
    _requires(db, b, "AAA1001", kind="prohibitions")
    db.commit()
    body = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S1},
        {"unit_code": "BBB1001", "year": 2026, "teaching_period": S2},
    ])
    assert "prohibited_with" in kinds(body, "BBB1001")
    assert "prohibited_with" not in kinds(body, "AAA1001")


def test_a_full_year_unit_does_not_finish_before_its_own_second_semester(client, db):
    """It occupies both, so a dependant in semester 2 has not met it yet."""
    _unit(db, "AAA1001", campuses=(("Malaysia", "Full year"),))
    b = _unit(db, "BBB2001")
    _requires(db, b, "AAA1001")
    db.commit()
    body = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": "Full year"},
        {"unit_code": "BBB2001", "year": 2026, "teaching_period": S2},
    ])
    assert kinds(body, "BBB2001") == {"missing_prerequisite"}

    later = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": "Full year"},
        {"unit_code": "BBB2001", "year": 2027, "teaching_period": S1},
    ])
    assert kinds(later, "BBB2001") == {"not_in_year"} or kinds(later, "BBB2001") == set()


@pytest.mark.parametrize("period", [S1, S2])
def test_a_full_year_target_cannot_use_a_same_year_prerequisite(client, db, period):
    _unit(db, "AAA1001")
    target = _unit(db, "BBB2001", campuses=(("Malaysia", "Full year"),))
    _requires(db, target, "AAA1001")
    db.commit()
    body = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": period},
        {"unit_code": "BBB2001", "year": 2026, "teaching_period": "Full year"},
    ])
    assert kinds(body, "BBB2001") == {"missing_prerequisite"}


def test_a_unit_not_published_this_year_is_reported(client, chain):
    body = _post(client, [{"unit_code": "QQQ9999", "year": 2026, "teaching_period": S1}])
    assert kinds(body) == {"not_in_year"}


def test_the_same_unit_twice_is_a_warning_not_an_error(client, chain):
    """Repeating a failed unit is a real thing students do."""
    body = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S1},
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S2},
    ])
    duplicate = next(i for i in body["issues"] if i["kind"] == "duplicate")
    assert duplicate["severity"] == "warning"


def test_an_empty_plan_is_valid(client, chain):
    body = _post(client, [])
    assert body["issues"] == []
    assert body["credit_points"] == 0


def _group(db, unit, *, kind="prerequisite", connector="AND", parent=None, order=0):
    row = UnitRequisiteGroup(
        unit_id=unit.id, parent_id=parent.id if parent else None,
        requisite_type=kind, connector=connector, order_index=order,
    )
    db.add(row)
    db.flush()
    return row


def _in(db, group, *codes):
    for index, code in enumerate(codes):
        db.add(UnitRequisiteItem(group_id=group.id, item_code=code, item_name=code,
                                 item_type="Unit", order_index=index))


@pytest.fixture
def fit2099(db):
    """FIT2099's real rule, which is where the flattening was caught.

        one of six programming units
        OR
        (ENG1003 or ENG1013) AND (ENG1060 or ENG1014)

    Flattened into siblings this reads as "all of the above", and a student
    holding FIT1045 was told to go and take two ENG units.
    """
    for code in ("FIT1045", "FIT1048", "FIT1051", "ENG1003", "ENG1013", "ENG1060", "ENG1014"):
        _unit(db, code)
    target = _unit(db, "FIT2099")

    root = _group(db, target, connector="OR")
    _in(db, _group(db, target, connector="OR", parent=root, order=0),
        "FIT1045", "FIT1048", "FIT1051")
    engineering = _group(db, target, connector="AND", parent=root, order=1)
    _in(db, _group(db, target, connector="OR", parent=engineering, order=0), "ENG1003", "ENG1013")
    _in(db, _group(db, target, connector="OR", parent=engineering, order=1), "ENG1060", "ENG1014")
    db.commit()
    return db


def test_one_branch_of_a_top_level_or_is_enough(client, fit2099):
    """The bug this fixture is named after: FIT1045 alone satisfies FIT2099."""
    body = _post(client, [
        {"unit_code": "FIT1045", "year": 2026, "teaching_period": S1},
        {"unit_code": "FIT2099", "year": 2026, "teaching_period": S2},
    ])
    assert kinds(body, "FIT2099") == set(), body["issues"]


def test_the_other_branch_needs_both_of_its_halves(client, fit2099):
    body = _post(client, [
        {"unit_code": "ENG1003", "year": 2026, "teaching_period": S1},
        {"unit_code": "FIT2099", "year": 2026, "teaching_period": S2},
    ])
    assert kinds(body, "FIT2099") == {"missing_prerequisite"}

    both = _post(client, [
        {"unit_code": "ENG1003", "year": 2026, "teaching_period": S1},
        {"unit_code": "ENG1014", "year": 2026, "teaching_period": S1},
        {"unit_code": "FIT2099", "year": 2026, "teaching_period": S2},
    ])
    assert kinds(both, "FIT2099") == set(), both["issues"]


def test_an_empty_plan_still_names_every_way_in(client, fit2099):
    """With nothing taken, the reader needs the choice, not one arbitrary code."""
    body = _post(client, [{"unit_code": "FIT2099", "year": 2026, "teaching_period": S1}])
    issue = next(i for i in body["issues"] if i["kind"] == "missing_prerequisite")
    assert set(issue["detail"]["any_of"]) >= {"FIT1045", "FIT1048", "FIT1051"}
    # and the shape survives, so the UI can show which branch is closest
    assert issue["detail"]["rule"]["connector"] == "OR"
    assert len(issue["detail"]["rule"]["groups"]) == 2


# --- what each unit is worth -------------------------------------------------


def test_the_check_says_what_each_unit_is_worth(client, chain):
    """Not only the total. The planner scores a free elective part with the
    units the degree does not name, and those are exactly the units the course
    endpoint carries no facts for - so without this they counted as zero and
    "Part E. Free elective studies" read 0/48 for a full plan."""
    body = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S1},
        {"unit_code": "BBB2001", "year": 2026, "teaching_period": S2},
    ])
    assert body["unit_credit_points"] == {"AAA1001": 6, "BBB2001": 6}
    assert sum(body["unit_credit_points"].values()) == body["credit_points"]


def test_the_check_names_each_unit_it_found(client, chain):
    """The map shows a title under each code, and a code the Handbook does not
    have gets no title rather than a made-up one."""
    body = _post(client, [
        {"unit_code": "AAA1001", "year": 2026, "teaching_period": S1},
        {"unit_code": "ZZZ9999", "year": 2026, "teaching_period": S2},
    ])
    assert body["unit_titles"] == {"AAA1001": "AAA1001"}


def test_a_unit_that_is_not_in_the_year_is_worth_nothing_rather_than_guessed(
    client, chain
):
    """It is already reported as an error; inventing a number for it would put
    credit points on the bar for a unit that does not exist."""
    body = _post(client, [
        {"unit_code": "ZZZ9999", "year": 2026, "teaching_period": S1},
    ])
    assert body["unit_credit_points"] == {}
    assert body["credit_points"] == 0
