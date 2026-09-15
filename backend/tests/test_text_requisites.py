"""Regression tests for requisite data that is not in the ideal Handbook shape."""
from __future__ import annotations

from app.models.handbook import Unit, UnitOffering, UnitRequisiteGroup, UnitRequisiteItem

S1 = "First semester"


def _unit(db, code: str) -> Unit:
    unit = Unit(
        unit_code=code,
        academic_year=2026,
        title=code,
        credit_points="6",
        source_url=f"https://handbook.monash.edu/2026/units/{code}",
        content_hash=f"hash-{code}",
    )
    db.add(unit)
    db.flush()
    db.add(UnitOffering(
        unit_id=unit.id,
        campus="Malaysia",
        teaching_period=S1,
        offered=True,
    ))
    return unit


def _requires(db, unit: Unit, code: str, *, kind: str, connector: str) -> None:
    group = UnitRequisiteGroup(
        unit_id=unit.id,
        requisite_type=kind,
        connector=connector,
    )
    db.add(group)
    db.flush()
    db.add(UnitRequisiteItem(
        group_id=group.id,
        item_code=code,
        item_name=code,
        item_type="Unit",
        order_index=0,
    ))


def test_tree_walks_legacy_plural_requisite_types(client, db):
    _unit(db, "AAA1001")
    target = _unit(db, "BBB2001")
    _requires(db, target, "AAA1001", kind="prerequisites", connector="AND")
    db.commit()

    body = client.get("/api/v1/units/BBB2001/tree", params={"direction": "upstream"}).json()
    assert {node["unit_code"] for node in body["nodes"]} == {"AAA1001", "BBB2001"}
    edge = next(edge for edge in body["edges"] if edge["source"] == "AAA1001")
    assert edge["type"] == "prerequisite"


def test_text_rule_references_are_drawn_but_not_enforced_as_fake_logic(client, db):
    _unit(db, "AAA1001")
    target = _unit(db, "BBB2001")
    _requires(db, target, "AAA1001", kind="prerequisite", connector="TEXT")
    db.commit()

    tree = client.get("/api/v1/units/BBB2001/tree", params={"direction": "upstream"}).json()
    assert "AAA1001" in {node["unit_code"] for node in tree["nodes"]}
    assert next(edge for edge in tree["edges"] if edge["source"] == "AAA1001")["connector"] == "TEXT"

    plan = client.post(
        "/api/v1/plan/check",
        json={
            "year": 2026,
            "campus": "Malaysia",
            "entries": [{"unit_code": "BBB2001", "year": 2026, "teaching_period": S1}],
        },
    ).json()
    assert "missing_prerequisite" not in {issue["kind"] for issue in plan["issues"]}
