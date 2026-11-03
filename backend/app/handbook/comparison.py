"""Availability of compared collections; legacy empty records stay unknown."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.handbook import Unit, UnitVersion


def collection_coverage(unit: Unit, payload: dict | None) -> dict[str, bool]:
    flags = (payload or {}).get("comparison_coverage")
    flags = flags if isinstance(flags, dict) else {}
    return {
        field: bool(getattr(unit, relation)) or flags.get(field) is True
        for field, relation in (
            ("offerings", "offerings"),
            ("assessments", "assessments"),
            ("requisites", "requisite_groups"),
        )
    }


def for_unit(db: Session, unit: Unit) -> dict[str, bool]:
    payload = db.scalar(
        select(UnitVersion.raw_payload).where(
            UnitVersion.unit_id == unit.id,
            UnitVersion.content_hash == unit.content_hash,
        )
    )
    return collection_coverage(unit, payload)
