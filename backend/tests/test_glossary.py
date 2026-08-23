"""The terms a translation service is not allowed to have an opinion about.

These tests are the reason machine translation is allowed near this product at
all. If the protection does not hold, the right outcome is an exception and a
unit that stays in English - never a stored sentence that says the wrong thing
confidently.
"""
from __future__ import annotations

import pytest
from app.knowledge import glossary
from app.knowledge.machine_translation import EchoTranslator, translate_prose

# --- protecting -----------------------------------------------------------

def test_the_pair_that_every_translator_gets_backwards():
    """At Monash a unit is a subject and a course is the whole degree."""
    protected = glossary.protect("You must pass this unit to progress in your course.")
    assert "<x>unit</x>" in protected
    assert "<x>course</x>" in protected

    restored = glossary.restore(protected)
    assert "课程" in restored          # unit
    assert "学位课程" in restored      # course
    assert "单元" not in restored


def test_the_longest_term_wins():
    """Otherwise 'Weighted Average Mark' is protected as three separate words."""
    protected = glossary.protect("Your Weighted Average Mark and your Grade Point Average")
    assert "<x>Weighted Average Mark</x>" in protected
    assert "<x>Grade Point Average</x>" in protected


def test_a_term_inside_a_longer_word_is_left_alone():
    """'unitary' is not 'unit'. A homograph like the verb 'courses' is matched,
    which is the documented limitation, so it is not part of this assertion."""
    assert "<x>" not in glossary.protect("The unitary system is disciplinary.")


def test_a_term_that_is_not_a_word_still_matches():
    """'Allocate+' does not end in a word character, so \\b would never fire."""
    assert "<x>Allocate+</x>" in glossary.protect("Check Allocate+ for your timetable.")


def test_a_long_form_with_its_acronym_expands_once_not_twice():
    """Monash writes "Cumulative Grade Point Average (CGPA)". Both halves are in
    the table, and matching them separately produced the expansion twice."""
    for source, expected in (
        ("Cumulative Grade Point Average (CGPA)", "累计平均绩点（CGPA）"),
        ("Grade Point Average (GPA)", "平均绩点（GPA）"),
        ("Weighted Average Mark (WAM)", "加权平均分（WAM）"),
        ("Confirmation of Enrolment (CoE)", "入学确认书（CoE）"),
        ("Overseas Student Health Cover (OSHC)", "海外学生医疗保险（OSHC）"),
        ("Web Enrolment System (WES)", "选课系统（WES）"),
    ):
        assert glossary.restore(glossary.protect(source)) == expected, source


def test_an_acronym_on_its_own_still_expands():
    restored = glossary.restore(glossary.protect("Your GPA and your WAM."))
    assert "平均绩点（GPA）" in restored
    assert "加权平均分（WAM）" in restored


def test_named_systems_come_back_as_themselves():
    restored = glossary.restore(glossary.protect("Check Moodle and the Handbook."))
    assert "Moodle" in restored
    assert "Handbook" in restored


def test_a_capitalised_term_at_the_start_of_a_sentence_still_resolves():
    restored = glossary.restore(glossary.protect("Units are worth credit points."))
    assert "课程" in restored
    assert "学分" in restored


# --- checking -------------------------------------------------------------

def test_a_hurdle_translated_as_an_obstacle_is_rejected():
    with pytest.raises(glossary.GlossaryViolation):
        glossary.check("This assessment is a hurdle.", "这项考核是一个障碍。")


def test_a_census_date_translated_as_a_population_survey_is_rejected():
    with pytest.raises(glossary.GlossaryViolation):
        glossary.check("Check the census date.", "请查看人口普查日期。")


def test_a_unit_translated_as_a_module_is_rejected():
    with pytest.raises(glossary.GlossaryViolation):
        glossary.check("This unit covers algorithms.", "本单元涵盖算法。")


def test_a_leaked_english_term_is_rejected():
    """The protection failing open is the failure this catches."""
    with pytest.raises(glossary.GlossaryViolation):
        glossary.check("Apply for special consideration.", "请申请 special consideration。")


def test_the_correct_rendering_passes():
    glossary.check(
        "You must pass this hurdle to pass the unit.",
        "你必须通过这个必过项才能通过这门课程。",
    )


def test_a_term_not_present_in_the_source_is_not_checked():
    """'课程' is right for 'unit' and wrong for 'course'; only the word that was
    actually there gets an opinion applied to it."""
    glossary.check("This unit covers algorithms.", "这门课程涵盖算法。")


def test_a_bracketed_term_is_not_read_as_a_leak():
    """'GPA' inside '平均绩点（GPA）' is the required output, not English left over."""
    glossary.check("Your GPA is calculated from grades.", "你的平均绩点（GPA）由成绩等级算出。")


# --- the pipeline ---------------------------------------------------------

def test_a_service_that_ignores_the_tags_is_repaired_not_dropped():
    """The passage is kept - full coverage was the instruction - but the terms
    that would actually mislead are put back."""

    class Careless:
        def translate(self, text: str, target: str) -> str:
            return "本单元有一个障碍要求。"

    result = translate_prose("This unit has a hurdle requirement.", Careless())
    assert "课程" in result.text
    assert "必过项" in result.text
    assert "单元" not in result.text
    assert "障碍" not in result.text
    # And the run is told it had to intervene, rather than this passing silently.
    assert set(result.repaired_terms) == {"unit", "hurdle"}
    assert result.clean is False


def test_a_clean_translation_reports_nothing_to_repair():
    class Careful:
        def translate(self, text: str, target: str) -> str:
            return text.replace("This ", "这门 ").replace(" has a ", " 有一个 ").replace(
                " requirement.", " 要求。"
            )

    result = translate_prose("This unit has a hurdle requirement.", Careful())
    assert result.clean is True
    assert result.repaired_terms == ()


def test_the_echo_translator_looks_fine_and_is_still_not_a_translation():
    """Echo plus the glossary yields English prose with Chinese terms in it.

    Nothing flags it, which is exactly why it is confined to dry runs and why
    `run()` refuses to commit with it - see the guard in translate_content.py.
    """
    result = translate_prose("This unit has a hurdle requirement.", EchoTranslator())
    assert "必过项" in result.text
    assert "has a" in result.text  # still English, and that is the point


def test_the_pipeline_refuses_empty_input():
    from app.knowledge.machine_translation import TranslationFailed

    with pytest.raises(TranslationFailed):
        translate_prose("   ", EchoTranslator())


def test_the_pipeline_restores_terms_a_service_left_wrapped():
    class Stub:
        """Stands in for a service that honoured ignore_tags."""

        def translate(self, text: str, target: str) -> str:
            return text.replace(
                "This ", "这门 "
            ).replace(" covers algorithms.", " 涵盖算法。")

    result = translate_prose("This unit covers algorithms.", Stub())
    assert "课程" in result.text
    assert "<x>" not in result.text
    assert result.clean is True


def test_repair_only_touches_a_term_that_was_in_the_source():
    """'课程' is the right translation of 'unit' and the wrong one of 'course',
    so repairing on the strength of the Chinese alone would break the good case."""
    repaired, fixed = glossary.repair("This unit covers algorithms.", "这门课程涵盖算法。")
    assert repaired == "这门课程涵盖算法。"
    assert fixed == []
