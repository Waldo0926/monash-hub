"""Which units a translation pass actually touches, and what it sends to the model.

No database or model here - just the selection logic that used to force every
`--fields all` run to walk the whole catalogue even when only one Handbook
page, like FIT1008's mid-year republish, needed re-translating.
"""
from __future__ import annotations

import threading

import pytest

from crawler.translate.engine import Translator
from crawler.translate.run import _select_codes, years_marker

CATALOGUE = ["FIT1008", "FIT1045", "FIT1055", "FIT2102"]


def test_no_units_filter_returns_everything():
    assert _select_codes(CATALOGUE, None, limit=0) == CATALOGUE


def test_limit_only_applies_without_a_units_filter():
    assert _select_codes(CATALOGUE, None, limit=2) == ["FIT1008", "FIT1045"]


def test_units_filter_scopes_to_the_given_codes():
    assert _select_codes(CATALOGUE, ["FIT1008"], limit=0) == ["FIT1008"]


def test_units_filter_is_case_insensitive_and_trims_whitespace():
    assert _select_codes(CATALOGUE, [" fit1008 ", "fit1055"], limit=0) == [
        "FIT1008", "FIT1055",
    ]


def test_units_filter_ignores_limit():
    """--limit is a full-catalogue safety valve; a --units list is already
    exactly what was asked for, so it is not silently truncated."""
    assert _select_codes(CATALOGUE, ["FIT1008", "FIT1055"], limit=1) == [
        "FIT1008", "FIT1055",
    ]


def test_an_unknown_unit_code_fails_loudly():
    with pytest.raises(ValueError, match="FIT9999"):
        _select_codes(CATALOGUE, ["FIT1008", "FIT9999"], limit=0)


# --- every Handbook year's English is translated -----------------------------



def test_one_year_is_stamped_with_its_own_hash():
    assert years_marker(["abc"]) == "abc"


def test_adding_a_year_changes_the_stamp():
    two = years_marker(["h2027", "h2026"])
    three = years_marker(["h2027", "h2026", "h2025"])
    assert len(two) == 64 and two != "h2027"
    assert three != two


def _translator(calls: list[str]) -> Translator:
    engine = Translator.__new__(Translator)
    engine.locale = "zh"
    engine.workers = 1
    engine._caches = {}
    engine._renderings = {}
    engine._lock = threading.Lock()
    engine.use_scope("handbook")
    engine._translate = lambda text: calls.append(text) or f"<{text}>"
    return engine


def test_primed_strings_are_not_sent_to_the_model_again():
    calls: list[str] = []
    engine = _translator(calls)
    engine.prime({"Students learn to model data.": "学生学习数据建模。"})
    out = engine.many(["Students learn to model data.", "A sentence new in 2025."])
    assert out["Students learn to model data."] == "学生学习数据建模。"
    assert calls == ["A sentence new in 2025."]


def test_a_reviewed_label_is_not_overridden_by_a_stored_machine_string():
    from app.knowledge.structure_zh import STRUCTURE_ZH

    label, reviewed = next(iter(STRUCTURE_ZH.items()))
    engine = _translator([])
    engine.prime({label: "旧的机器译文"})
    assert engine.text(label) == reviewed


def test_the_campus_in_a_title_is_never_the_models_to_translate():
    from crawler.translate.run import _campus_title_ok, translate_title

    calls: list[str] = []
    engine = _translator(calls)
    engine._translate = lambda text: calls.append(text) or "新国际学生常见问题"
    title = "FAQs for new international students (Monash Malaysia)"
    assert translate_title(engine, title, "zh") == "新国际学生常见问题（马来西亚校区）"
    assert calls and not any("Malaysia" in call for call in calls)
    # What the model once returned is recognised as needing another go.
    assert not _campus_title_ok(title, "常见问题解答（新国际学生（Monash Malaysia（马来西亚校区））学生）", "zh")
    assert _campus_title_ok(title, "新国际学生常见问题（马来西亚校区）", "zh")
    assert _campus_title_ok("Results", "成绩", "zh")
