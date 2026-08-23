"""The terms the machine is not allowed to decide.

These are the words that cost a student money or a semester when they are
wrong, so the tests are about the specific renderings, not about the mechanism
in general.
"""
from __future__ import annotations

import pytest
from app.knowledge.glossary import (
    ENUMS,
    KEEP_IN_ENGLISH,
    LOCALES,
    TERMS,
    is_only_placeholders,
    placeholder,
    placeholders_survived,
    protect,
    restore,
    whole_value,
)


def test_every_term_covers_every_locale():
    missing = {
        term: [code for code in LOCALES if code not in translations]
        for term, translations in {**TERMS, **ENUMS}.items()
        if any(code not in translations for code in LOCALES)
    }
    assert missing == {}


def test_no_entry_translates_to_itself_by_accident():
    """A translation identical to the English is a gap wearing a costume.

    Except where it is deliberate: "Moodle" is called Moodle in every language a
    student will see it in, and translating it would make the app and the
    official site impossible to line up.
    """
    same = {
        term for term, values in TERMS.items()
        if values["zh"].strip().lower() == term.strip().lower()
    }
    assert same == set(KEEP_IN_ENGLISH)


def test_placeholders_are_distinct_past_the_alphabet():
    tokens = [placeholder(i) for i in range(60)]
    assert len(set(tokens)) == 60
    assert tokens[0] == "Zqa" and tokens[25] == "Zqz" and tokens[26] == "Zqaa"


def test_placeholders_are_letters_only():
    # Digits get rewritten by the model - XX1XX came back as X22XX - so a
    # placeholder must not contain any.
    assert all(token.isalpha() for token in (placeholder(i) for i in range(40)))


@pytest.mark.parametrize(
    "source,expected",
    [
        # English first, matching the reviewed translations: a student meets
        # this term in English in WES and on every official page.
        ("census date", "census date（学籍统计日）"),
        ("credit points", "学分"),
        ("hurdle", "及格门槛"),
        ("prerequisite", "先修课程"),
        ("prohibition", "互斥课程"),
        ("intermission", "休学（intermission）"),
    ],
)
def test_the_dangerous_terms_have_agreed_wording(source, expected):
    assert TERMS[source]["zh"] == expected


def test_protect_and_restore_round_trip():
    source = "The census date is the last day you can withdraw from a unit."
    masked, terms = protect(source, "zh")
    assert "census date" not in masked
    assert "Zqa" in masked
    restored = restore(masked, terms)
    assert "census date（学籍统计日）" in restored
    assert "课程" in restored


def test_longest_term_wins():
    _masked, terms = protect("your weighted average mark matters", "zh")
    # Not "mark" on its own, which is also a term.
    assert terms[0] == "加权平均分（WAM）"
    assert len(terms) == 1


def test_restore_does_not_confuse_zqa_with_zqaa():
    replacements = [f"T{i}" for i in range(30)]
    masked = " ".join(placeholder(i) for i in range(30))
    restored = restore(masked, replacements)
    assert restored.split() == replacements


def test_a_string_of_only_terms_never_reaches_the_model():
    # Asked to translate the bare token "Zqa" the model answers 兹卡.
    masked, _ = protect("Programming paradigms", "zh")
    assert is_only_placeholders(masked)


def test_prose_still_needs_the_model():
    masked, _ = protect("This unit explores the history of the census date.", "zh")
    assert not is_only_placeholders(masked)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Exercise", "练习"),          # not 锻炼, which is physical exercise
        ("Threshold", "分数门槛"),      # not 阈值, which is a numeric threshold
        ("Level 2", "第 2 级"),
        ("First semester", "第一学期"),
        ("Quiz / Test", "小测 / 测验"),
    ],
)
def test_closed_list_values_are_exact(value, expected):
    assert whole_value(value, "zh") == expected


def test_an_unknown_value_has_no_agreed_wording():
    assert whole_value("Some unit-specific assessment name", "zh") is None


def test_institution_names_are_left_in_english():
    # A student looking for the building needs the name on the building.
    assert whole_value("Bendigo", "zh") == "Bendigo"


def test_a_lost_placeholder_is_detectable():
    """The model sometimes transliterates the token instead of copying it.

    "What is Zqa?" came back as 什么是兹卡? on a live page. Restoring cannot find
    the token, so the reader was shown a nonsense word where a term should be.
    The engine checks for this and keeps the English instead.
    """
    assert placeholders_survived("学业进度审查是什么东西? Zqa", 1) is True
    assert placeholders_survived("什么是兹卡?", 1) is False
    assert placeholders_survived("Zqa 和 兹卡b", 2) is False
