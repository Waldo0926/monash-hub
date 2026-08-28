"""The prerequisite graph.

The graph exists to answer "what must I pass first, and can I take it here" -
so the tests are about the two ways that answer goes wrong: a walk that loses
the shape of the rules, and a walk that quietly drops a unit the student
cannot actually enrol in.
"""
from __future__ import annotations

import pytest
from app.models.handbook import Unit, UnitOffering, UnitRequisiteGroup, UnitRequisiteItem


def _unit(db, code: str, title: str, campuses: tuple[str, ...] = ("Malaysia",)) -> Unit:
    unit = Unit(
        unit_code=code, academic_year=2026, title=title, credit_points=6,
        source_url=f"https://handbook.monash.edu/2026/units/{code}",
        content_hash=f"hash-{code}",
    )
    db.add(unit)
    db.flush()
    for campus in campuses:
        db.add(UnitOffering(unit_id=unit.id, campus=campus,
                            teaching_period="First semester", offered=True))
    return unit


def _requires(db, unit: Unit, *codes: str, kind: str = "prerequisite", connector: str = "AND"):
    group = UnitRequisiteGroup(unit_id=unit.id, requisite_type=kind, connector=connector)
    db.add(group)
    db.flush()
    for index, code in enumerate(codes):
        db.add(UnitRequisiteItem(group_id=group.id, item_code=code,
                                 item_name=code, item_type="Unit", order_index=index))


@pytest.fixture
def chain(db):
    """A1 -> B1 -> C1, with C1 also prohibited against X9 and coreq D1.

    D9 is named as a prerequisite of C1 but is not published for 2026, and E1
    is taught only at Clayton.
    """
    _unit(db, "AAA1001", "Foundations")
    b1 = _unit(db, "BBB2001", "Middle")
    c1 = _unit(db, "CCC3001", "Capstone")
    _unit(db, "DDD1001", "Alongside")
    _unit(db, "EEE1001", "Clayton only", campuses=("Clayton",))
    _unit(db, "XXX9001", "Prohibited twin")

    _requires(db, b1, "AAA1001")
    _requires(db, c1, "BBB2001", "DDD9999", connector="OR")
    _requires(db, c1, "DDD1001", kind="corequisite")
    _requires(db, c1, "XXX9001", kind="prohibitions")
    _requires(db, c1, "EEE1001")
    db.commit()
    return db


def test_upstream_walks_the_chain_and_signs_the_depth(client, chain):
    body = client.get("/api/v1/units/CCC3001/tree", params={"direction": "upstream"}).json()
    depth = {n["unit_code"]: n["depth"] for n in body["nodes"]}
    assert depth["CCC3001"] == 0
    assert depth["BBB2001"] == -1
    assert depth["AAA1001"] == -2, "the walk has to be transitive, not one hop"


def test_downstream_finds_what_a_unit_unlocks(client, chain):
    body = client.get("/api/v1/units/AAA1001/tree", params={"direction": "downstream"}).json()
    depth = {n["unit_code"]: n["depth"] for n in body["nodes"]}
    assert depth["BBB2001"] == 1
    assert depth["CCC3001"] == 2


def test_prohibitions_are_not_drawn_as_edges(client, chain):
    """An arrow from XXX9001 would read as "take this first" - the opposite."""
    body = client.get("/api/v1/units/CCC3001/tree", params={"direction": "upstream"}).json()
    assert "XXX9001" not in {n["unit_code"] for n in body["nodes"]}
    assert all(e["type"] != "prohibitions" for e in body["edges"])


def test_a_corequisite_is_an_edge_of_its_own_kind(client, chain):
    body = client.get("/api/v1/units/CCC3001/tree", params={"direction": "upstream"}).json()
    kinds = {(e["source"], e["target"]): e["type"] for e in body["edges"]}
    assert kinds[("DDD1001", "CCC3001")] == "corequisite"
    assert kinds[("BBB2001", "CCC3001")] == "prerequisite"


def test_the_or_connector_survives_into_the_payload(client, chain):
    """"BBB2001 or DDD9999" is a choice; drawn as two arrows it reads as both."""
    body = client.get("/api/v1/units/CCC3001/tree", params={"direction": "upstream"}).json()
    ors = [e for e in body["edges"] if e["connector"] == "OR"]
    assert {e["source"] for e in ors} == {"BBB2001", "DDD9999"}
    assert len({e["group"] for e in ors}) == 1, "one choice, so one group"


def test_a_requisite_missing_from_this_year_is_shown_not_dropped(client, chain):
    """Deleting the node would make an unsatisfiable rule look satisfiable."""
    body = client.get("/api/v1/units/CCC3001/tree", params={"direction": "upstream"}).json()
    ghost = next(n for n in body["nodes"] if n["unit_code"] == "DDD9999")
    assert ghost["in_year"] is False
    assert ghost["title"] is None


def test_campus_marks_a_node_it_does_not_hide_it(client, chain):
    """A prerequisite Malaysia does not teach is the thing to show most loudly."""
    body = client.get(
        "/api/v1/units/CCC3001/tree", params={"direction": "upstream", "campus": "Malaysia"}
    ).json()
    here = {n["unit_code"]: n["offered_at_campus"] for n in body["nodes"]}
    assert here["EEE1001"] is False, "Clayton-only, and still on the graph"
    assert here["BBB2001"] is True


def test_a_cycle_does_not_hang_the_walk(client, db):
    """The Handbook lists mutual requisites; a naive walk never returns."""
    left = _unit(db, "LLL1001", "Left")
    right = _unit(db, "RRR1001", "Right")
    _requires(db, left, "RRR1001")
    _requires(db, right, "LLL1001")
    db.commit()

    body = client.get("/api/v1/units/LLL1001/tree", params={"direction": "both"}).json()
    assert {n["unit_code"] for n in body["nodes"]} == {"LLL1001", "RRR1001"}
