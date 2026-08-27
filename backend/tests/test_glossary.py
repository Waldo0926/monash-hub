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
    has_verbatim,
    is_only_placeholders,
    placeholder,
    placeholders_survived,
    protect,
    rendered_verbatim,
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


def test_an_email_address_never_reaches_the_translator():
    """servicedesk@Monash.edu was published as 服务台@Monash.edu."""
    masked, kept = protect("email servicedesk@Monash.edu with CUP merge", "zh")
    assert "servicedesk" not in masked
    assert "servicedesk@Monash.edu" in restore(masked, kept)


def test_re_enrolment_is_not_matched_as_enrolment():
    masked, kept = protect("under Enrolment/Re-enrolment in WES", "zh")
    assert "Re-" not in restore(masked, kept)


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


@pytest.mark.parametrize(
    "name",
    ["Monash", "Monash Abroad", "Monash Connect", "Monash Online", "Monash Indonesia"],
)
def test_the_universitys_own_names_keep_their_english(name):
    """Monash reads as *money* to the model.

    "Monash Abroad", the office a student goes to about exchange, was
    published as 国外货币 - foreign currency - as the heading of the study
    abroad guide, and the unit code MON1001 as 货币1001. The name never
    reaches the model, and what comes back still has the name in it.
    """
    masked, kept = protect(name, "zh")
    assert is_only_placeholders(masked)
    assert name in restore(masked, kept)


def test_a_service_says_what_it_is():
    # The name is what a student matches; the bracket is what it means.
    assert TERMS["Monash Abroad"]["zh"] == "Monash Abroad（海外学习与交换）"
    assert TERMS["Monash"]["zh"] == "Monash"


def test_a_faculty_is_named_not_described():
    # 法学院：, with the colon copied off "School of", was what the page said.
    assert TERMS["Faculty of Law"]["zh"] == "法学院"
    assert TERMS["Faculty of Information Technology"]["zh"] == "信息技术学院"


def test_a_period_inside_a_label_is_pinned_too():
    """ENUMS pins these as whole values; on the dates pages they arrive inside
    a label, where the model read Trimester 1 as 三月一日 and Semester 2 as
    学士2."""
    masked, kept = protect("Trimester 1 (Faculty of Law units only)", "zh")
    assert kept == ["第 1 学段", "法学院", "课程"]  # units is a term of its own
    assert "Trimester" not in masked


@pytest.mark.parametrize(
    "source,expected",
    [
        ("1 Apr 2026", "2026年4月1日"),          # was 2026年4月1日（英语）.
        ("1 Aug 2024", "2024年8月1日"),          # was 2024年8月1日纽约
        ("10 Apr", "4月10日"),                   # was 4月10日，纽约
        ("1 Jul – 30 Sep 2026", "2026年7月1日至9月30日"),  # was 2026年9月30日
        ("3–7 Jun 2026", "2026年6月3日至7日"),
        ("1 Nov 2027 – 11 Feb 2028", "2027年11月1日至2028年2月11日"),
        ("11.55pm", "23:55"),
        ("12.30am", "00:30"),                    # midnight, not noon
        ("5am", "05:00"),                        # was 下午5点, twelve hours out
    ],
)
def test_a_date_or_a_time_is_arithmetic_not_translation(source, expected):
    assert rendered_verbatim(source, "zh") == expected


@pytest.mark.parametrize("code", ["MON1001", "ATS1192", "S2-01", "MO-TP1-01"])
def test_a_code_is_kept_exactly_as_it_arrived(code):
    # ATS1192 came back as 1192奥地利先令: ATS was the Austrian schilling.
    assert rendered_verbatim(code, "zh") == code
    masked, kept = protect(code, "zh")
    assert is_only_placeholders(masked) and restore(masked, kept) == code


def test_a_sentence_keeps_its_dates_out_of_the_models_reach():
    masked, kept = protect("Applications close at 11.59pm for semester two (S2-01)", "zh")
    assert "11.59pm" not in masked and "S2-01" not in masked
    assert "23:59" in kept and "S2-01" in kept and "第二学期" in kept


def test_a_month_needs_its_capital_to_be_a_date():
    # "3 may be enough" is a sentence, not the third of May.
    assert not has_verbatim("3 may be enough to pass")
    assert has_verbatim("3 May 2026")


def test_the_frontend_dictionary_agrees_with_the_glossary():
    """The filter dropdown and the unit card must not name the same thing twice.

    Facet values come back from ``/units/filters`` in English and are labelled
    by ``frontend/i18n/handbook-terms.ts``; the values on a unit card come back
    already translated, through ENUMS. Two dictionaries for one closed list, and
    they had drifted on 37 of the 66 entries they share - including a straight
    swap, where *Term 1* was 第 1 学段 in the filter and *Trimester 1* was
    第 1 学段 on the card. Term and Trimester have different census dates.
    """
    import re
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[2] / "frontend" / "i18n" / "handbook-terms.ts"
    ).read_text(encoding="utf-8")

    disagree = {
        key: (written, ENUMS[key]["zh"])
        for key, written in re.findall(r"\n\s*'([^']+)':\s*'([^']*)'", source)
        if key in ENUMS and ENUMS[key].get("zh") and ENUMS[key]["zh"] != written
    }
    assert disagree == {}
