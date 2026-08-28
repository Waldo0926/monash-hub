"""Persist parsed Handbook records.

Two rules drive this module:

1. If the ``content_hash`` matches what we already stored, do nothing. No
   delete, no insert, no reindex. Most crawls should be almost entirely skips.
2. A parse failure must never reach here. Callers keep the last valid row and
   log the failure instead - a broken parser silently blanking real data is the
   worst outcome available to us.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crawl import SourceChangeEvent
from app.models.handbook import (
    Unit,
    UnitActivity,
    UnitAssessment,
    UnitLearningOutcome,
    UnitOffering,
    UnitRequisiteGroup,
    UnitRequisiteItem,
    UnitVersion,
)

# Column names copied straight from the parsed record onto Unit.
SCALAR_FIELDS = (
    "title",
    "credit_points",
    "level",
    "faculty",
    "school",
    "subject_prefix",
    "source_url",
    "overview",
    "areas_of_study",
    "teaching_approach",
    "workload_requirements",
    "assessment_summary",
    "assessment_static_text",
    "has_exam",
    "handbook_version",
    "content_hash",
)


def get_unit(db: Session, unit_code: str, year: int) -> Unit | None:
    return db.scalar(
        select(Unit).where(Unit.unit_code == unit_code.upper(), Unit.academic_year == year)
    )


def upsert_unit(db: Session, record: dict[str, Any]) -> tuple[Unit, str]:
    """Insert or refresh one unit. Returns ``(unit, outcome)``.

    ``outcome`` is one of ``new``, ``changed`` or ``unchanged`` so the caller can
    report a crawl honestly.
    """
    now = datetime.now(UTC)
    unit = get_unit(db, record["unit_code"], record["academic_year"])

    if unit is not None and unit.content_hash == record["content_hash"]:
        unit.last_seen = now
        unit.last_crawled = now
        unit.is_active = True
        db.flush()
        return unit, "unchanged"

    previous_hash = unit.content_hash if unit else None
    outcome = "changed" if unit else "new"

    if unit is None:
        unit = Unit(
            unit_code=record["unit_code"],
            academic_year=record["academic_year"],
            content_hash=record["content_hash"],
            first_seen=now,
        )
        db.add(unit)

    for field in SCALAR_FIELDS:
        setattr(unit, field, record.get(field))
    unit.last_seen = now
    unit.last_crawled = now
    unit.is_active = True
    db.flush()

    _replace_children(db, unit, record)

    db.add(
        UnitVersion(
            unit_id=unit.id,
            version_name=record.get("handbook_version"),
            content_hash=record["content_hash"],
            raw_payload=_version_payload(record),
        )
    )
    db.add(
        SourceChangeEvent(
            target_type="handbook_unit",
            target_key=f"{record['unit_code']}:{record['academic_year']}",
            previous_hash=previous_hash,
            new_hash=record["content_hash"],
            diff_summary={
                "assessments": len(record.get("assessments") or []),
                "offerings": len(record.get("offerings") or []),
                "has_exam": record.get("has_exam"),
            },
        )
    )
    db.flush()
    return unit, outcome


def _version_payload(record: dict[str, Any]) -> dict[str, Any]:
    """Keep the normalised record, not the original HTML.

    Storing raw pages would turn the database into a mirror of the Handbook,
    which is exactly what the project said it would not build.
    """
    return {key: value for key, value in record.items() if key != "content_hash"}


def _replace_children(db: Session, unit: Unit, record: dict[str, Any]) -> None:
    """Rewrite the child rows for a unit whose content actually changed."""
    for child in (unit.offerings, unit.assessments, unit.learning_outcomes, unit.activities):
        for row in list(child):
            db.delete(row)
    for group in list(unit.requisite_groups):
        db.delete(group)
    db.flush()

    for offering in record.get("offerings") or []:
        db.add(UnitOffering(unit_id=unit.id, **offering))
    for assessment in record.get("assessments") or []:
        db.add(UnitAssessment(unit_id=unit.id, **assessment))
    for outcome in record.get("learning_outcomes") or []:
        db.add(UnitLearningOutcome(unit_id=unit.id, **outcome))
    for activity in record.get("activities") or []:
        db.add(UnitActivity(unit_id=unit.id, **activity))
    _write_requisites(db, unit, record.get("requisite_groups") or [], parent_id=None)
    db.flush()


def _write_requisites(
    db: Session, unit: Unit, groups: list[dict[str, Any]], *, parent_id: int | None
) -> None:
    """Depth first, so a nested group is written after the group it sits in.

    Every row carries its unit as well as its parent: the unit's own list
    selects the roots, and one indexed read still gets the whole tree.
    """
    for order, group in enumerate(groups):
        row = UnitRequisiteGroup(
            unit_id=unit.id,
            parent_id=parent_id,
            requisite_type=group["requisite_type"],
            connector=group.get("connector"),
            title=group.get("title"),
            description=group.get("description"),
            raw_text=group.get("raw_text"),
            order_index=group.get("order_index") or order,
        )
        db.add(row)
        db.flush()
        for item in group.get("items") or []:
            db.add(UnitRequisiteItem(group_id=row.id, **item))
        _write_requisites(db, unit, group.get("groups") or [], parent_id=row.id)
