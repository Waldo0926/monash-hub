"""Synthetic coverage proof is separate from unit content and user eligibility."""

import json
from types import SimpleNamespace

import pytest
from app.handbook.comparison import collection_coverage
from app.handbook.parser import compute_content_hash, parse_unit_page


def parse(**fields):
    content = {
        "unit_code": "TST1001",
        "implementation_year": 2026,
        "title": "Synthetic comparison unit",
        **fields,
    }
    html = (
        '<script id="__NEXT_DATA__" type="application/json">'
        + json.dumps({"props": {"pageProps": {"pageContent": content}}})
        + "</script>"
    )
    return parse_unit_page(html, "https://handbook.monash.edu/2026/units/TST1001")


@pytest.mark.parametrize(
    "source,field",
    [("unit_offering", "offerings"), ("assessments", "assessments"), ("requisites", "requisites")],
)
def test_missing_null_and_explicit_empty_collections_are_distinct(source, field):
    assert parse()["comparison_coverage"][field] is False
    assert parse(**{source: None})["comparison_coverage"][field] is False
    assert parse(**{source: []})["comparison_coverage"][field] is True


def test_unparsed_rule_prose_cannot_prove_an_empty_requisite_list():
    record = parse(requisites=[], handbook_rules="Prerequisites: permission of the coordinator.")
    assert record["comparison_coverage"]["requisites"] is False or record["requisite_groups"]


def test_coverage_metadata_does_not_change_semantic_content_hash():
    missing, explicit = parse(), parse(unit_offering=[], assessments=[], requisites=[])
    assert missing["content_hash"] == explicit["content_hash"]
    assert compute_content_hash({"title": "same"}) == compute_content_hash(
        {"title": "same", "comparison_coverage": {"requisites": True}}
    )


def test_legacy_empty_rows_are_unknown_until_the_source_supplies_proof():
    unit = SimpleNamespace(offerings=[], assessments=[], requisite_groups=[])
    assert collection_coverage(unit, {}) == dict.fromkeys(
        ["offerings", "assessments", "requisites"], False
    )
    result = collection_coverage(
        unit, {"comparison_coverage": {"requisites": True, "assessments": "true"}}
    )
    assert result["requisites"] is True and result["assessments"] is False


def test_known_nonempty_records_remain_comparable_without_new_metadata():
    unit = SimpleNamespace(offerings=[object()], assessments=[], requisite_groups=[])
    assert collection_coverage(unit, None)["offerings"] is True


def test_refresh_adds_proof_without_creating_policy_change_or_replacing_children(db):
    from app.handbook.repository import upsert_unit
    from app.models.crawl import SourceChangeEvent
    from app.models.handbook import UnitVersion
    from sqlalchemy import func, select

    base = parse()
    unit, result = upsert_unit(db, base)
    db.commit()
    first_hash = unit.content_hash
    count = db.scalar(select(func.count()).select_from(SourceChangeEvent))
    _, result = upsert_unit(db, parse(unit_offering=[], assessments=[], requisites=[]))
    db.commit()
    assert result == "unchanged" and unit.content_hash == first_hash
    assert db.scalar(select(func.count()).select_from(SourceChangeEvent)) == count
    versions = db.scalars(select(UnitVersion).where(UnitVersion.unit_id == unit.id)).all()
    assert (
        len(versions) == 1 and versions[0].raw_payload["comparison_coverage"]["requisites"] is True
    )


def test_unit_api_exposes_comparison_coverage_without_requiring_schema_changes(client, db):
    from app.handbook.repository import upsert_unit

    upsert_unit(db, parse(unit_offering=[], assessments=[], requisites=[]))
    db.commit()
    body = client.get("/api/v1/units/TST1001?year=2026").json()
    assert body["comparison_coverage"] == dict.fromkeys(
        ["offerings", "assessments", "requisites"], True
    )
