"""Persisting a crawled unit.

Focused on the one case ``test_api.py`` doesn't reach: a unit whose content
comes back to a hash it had several versions ago.
"""
from __future__ import annotations

from app.handbook.repository import upsert_unit
from app.models.handbook import UnitVersion


def _record(*, content_hash: str) -> dict:
    return {
        "unit_code": "FIT1090",
        "academic_year": 2026,
        "title": "Test unit",
        "source_url": "https://handbook.monash.edu/2026/units/FIT1090",
        "content_hash": content_hash,
    }


def test_a_unit_reverting_to_an_older_hash_does_not_crash(db):
    """A Handbook edit undone - or a parser fix making today's output match an
    even older, correct crawl - makes content_hash equal something already in
    unit_versions, just not the *most recent* row. upsert_unit only compared
    against the unit's current hash, so it tried to insert a second
    (unit_id, content_hash) row for a version already on file and crashed the
    whole pass under --fail-on-errors.
    """
    unit, outcome = upsert_unit(db, _record(content_hash="hash-a"))
    db.commit()
    assert outcome == "new"

    unit, outcome = upsert_unit(db, _record(content_hash="hash-b"))
    db.commit()
    assert outcome == "changed"

    # Back to hash-a - already recorded, just not as the latest version.
    unit, outcome = upsert_unit(db, _record(content_hash="hash-a"))
    db.commit()
    assert outcome == "changed"
    assert unit.content_hash == "hash-a"

    versions = db.query(UnitVersion).filter_by(unit_id=unit.id).all()
    assert sorted(v.content_hash for v in versions) == ["hash-a", "hash-b"]


def test_visiting_the_same_hash_twice_in_a_row_stays_unchanged(db):
    """The ordinary case this must not regress: no history row at all when
    nothing changed."""
    unit, outcome = upsert_unit(db, _record(content_hash="hash-a"))
    db.commit()
    assert outcome == "new"

    unit, outcome = upsert_unit(db, _record(content_hash="hash-a"))
    db.commit()
    assert outcome == "unchanged"

    versions = db.query(UnitVersion).filter_by(unit_id=unit.id).all()
    assert len(versions) == 1
