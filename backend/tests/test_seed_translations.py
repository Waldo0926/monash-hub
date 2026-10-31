"""Merging a baseline title into a unit's machine translation row.

No database here - constructing a bare ``ContentTranslation`` and checking its
attributes is enough, and it keeps this independent of whatever
``seed_translations`` itself needs (official pages, FAQ rows, ...) to run.
"""
from __future__ import annotations

from app.knowledge.seed import _merge_baseline_title
from app.models.translation import PUBLISHED, ContentTranslation


def test_a_new_row_gets_the_baseline_attribution():
    row = _merge_baseline_title(
        None, unit_code="FIT1099", title="Some unit", zh_title="某课程",
    )
    assert row.data["strings"]["Some unit"] == "某课程"
    assert row.status == PUBLISHED
    assert row.translator == "google-translate-baseline"
    assert row.source_hash is None
    assert "基线" in row.note


def test_an_existing_translation_pass_keeps_its_coverage_tracking():
    """The bug: this row also belongs to crawler.translate.run, and the
    baseline import used to stamp its own note/source_hash over whatever a
    real `--fields all` pass had already written - on every deploy, since
    this seed step runs every time. That told the translator's up-to-date
    check every one of those units had gone stale, forcing full
    re-translation to fix a single unit.
    """
    row = ContentTranslation(
        locale="zh", target_type="unit", target_key="FIT1099", field="content",
        data={"strings": {"Overview text": "简介译文"}},
        status=PUBLISHED, provenance="machine",
        translator="machine:argos+glossary",
        note="fields=all", source_hash="fit1099-hash",
    )
    merged = _merge_baseline_title(
        row, unit_code="FIT1099", title="Some unit", zh_title="某课程",
    )
    assert merged is row
    # The title is still allowed to gain the baseline's rendering...
    assert row.data["strings"]["Some unit"] == "某课程"
    # ...but the real pass's own work and coverage tracking must survive.
    assert row.data["strings"]["Overview text"] == "简介译文"
    assert row.note == "fields=all"
    assert row.source_hash == "fit1099-hash"
    assert row.translator == "machine:argos+glossary"


def test_no_two_seeds_write_the_same_row():
    """Two seeds for one row used to overwrite each other on every deploy: the
    GPA page kept 55 of its 117 hand-translated sentences."""
    from collections import Counter

    from app.knowledge.translations_seed import GPA_PAGE, GUIDE_BODIES, TRANSLATION_SEEDS

    keys = Counter(
        (s.locale, s.target_type, s.target_key, s.field) for s in TRANSLATION_SEEDS
    )
    assert [k for k, n in keys.items() if n > 1] == []

    gpa = next(
        s for s in TRANSLATION_SEEDS
        if s.target_key == "gpa" and s.field == "body"
    )
    assert set(GPA_PAGE) | set(GUIDE_BODIES["gpa"]) == set(gpa.strings)
