"""The parser is the part that must not be wrong.

Everything downstream - search filters, the zero-AI answers, the Unit Detail
page - is a rendering of what this file produces, so these tests check the
actual values against saved Handbook pages rather than just that parsing ran.
"""
from __future__ import annotations

import pytest
from app.handbook.parser import (
    ParseError,
    compute_content_hash,
    derive_has_exam,
    html_to_text,
    parse_unit_page,
    unit_url,
)


def _parse(handbook_html, code: str) -> dict:
    return parse_unit_page(handbook_html(code), unit_url(code, 2026))


def test_identity_fields(handbook_html):
    unit = _parse(handbook_html, "FIT2102")
    assert unit["unit_code"] == "FIT2102"
    assert unit["academic_year"] == 2026
    assert unit["title"] == "Programming paradigms"
    assert unit["credit_points"] == "6"
    assert unit["subject_prefix"] == "FIT"
    assert unit["faculty"] == "Faculty of Information Technology"
    assert unit["source_url"].endswith("/2026/units/FIT2102")


def test_unit_without_a_listed_exam(handbook_html):
    unit = _parse(handbook_html, "FIT2102")
    assert unit["has_exam"] is False
    assert [a["assessment_type"] for a in unit["assessments"]] == [
        "Project", "Project", "Quiz / Test", "Exercise",
    ]


def test_unit_with_an_exam(handbook_html):
    unit = _parse(handbook_html, "BFF2140")
    assert unit["has_exam"] is True
    assert any(a["assessment_type"] == "Examination" for a in unit["assessments"])


def test_has_exam_is_none_when_nothing_is_published():
    assert derive_has_exam([], None) is None


def test_has_exam_ignores_explicit_non_exam_labels():
    assert derive_has_exam([{"assessment_type": "Non-exam assessment", "name": ""}], None) is False


def test_assessments_are_ordered_and_weighted(handbook_html):
    unit = _parse(handbook_html, "FIT2102")
    numbers = [a["number"] for a in unit["assessments"]]
    assert numbers == sorted(numbers)
    assert sum(int(a["weight"]) for a in unit["assessments"]) == 100


def test_offerings_capture_every_campus(handbook_html):
    unit = _parse(handbook_html, "FIT2102")
    campuses = {o["campus"] for o in unit["offerings"]}
    assert campuses == {"Clayton", "Malaysia"}
    assert all(o["teaching_period"] for o in unit["offerings"])


def test_requisites_keep_their_connector_and_members(handbook_html):
    unit = _parse(handbook_html, "FIT2102")
    prereq = [g for g in unit["requisite_groups"] if g["requisite_type"] == "prerequisite"]
    assert len(prereq) == 1
    assert prereq[0]["connector"] == "OR"
    assert "FIT1008" in {item["item_code"] for item in prereq[0]["items"]}


def test_requisite_types_are_canonicalised(handbook_html):
    unit = _parse(handbook_html, "BFF2140")
    kinds = {g["requisite_type"] for g in unit["requisite_groups"]}
    assert kinds == {"prerequisite", "prohibition"}


def test_text_only_enrolment_rule_keeps_every_unit_reference(handbook_html):
    """MTH2051-style Rules prose must not produce an empty dependency graph.

    Some Handbook pages publish the prerequisite as prose under Rules while
    only the prohibition is present in the structured requisite feed. We keep
    the exact prose and make its unit references traversable, but mark the
    connector TEXT rather than inventing AND/OR semantics.
    """
    unit = _parse(handbook_html, "MTH2051")
    prereq = [g for g in unit["requisite_groups"] if g["requisite_type"] == "prerequisite"]
    assert len(prereq) == 1
    assert prereq[0]["connector"] == "TEXT"
    assert "Alternatively" in prereq[0]["description"]
    assert {item["item_code"] for item in prereq[0]["items"]} == {
        "MTH2010", "MTH2015", "MTH2019", "ENG2005", "MAT1830",
        "MTH2021", "MTH2025", "MTH2040", "MAT1841", "SCI1022",
        "FIT1045", "FIT1053", "ENG1060", "ETC2440",
    }

    prohibition = [
        g for g in unit["requisite_groups"] if g["requisite_type"] == "prohibition"
    ]
    assert len(prohibition) == 1, "the prose fallback must not duplicate structured types"
    assert {item["item_code"] for item in prohibition[0]["items"]} == {"MTH3051"}


def test_enrolment_rule_metadata_does_not_leak_into_rule_text(handbook_html):
    """FIT1055 publishes its rule under enrolment_rules, wrapped in metadata.

    Each entry there nests the actual prose under ``description`` alongside
    ``academic_item`` (which restates the *current* unit's own code and an
    internal ``cl_id``), a ``type`` label/value pair, and another ``cl_id``.
    A blind flatten of that dict turned "code", "info", "Enrolment Rule" and
    both hex ids into rule text, and reintroduced FIT1055 as a reference
    inside its own prohibitions - so the plan checker flagged FIT1055 as
    conflicting with itself.
    """
    unit = _parse(handbook_html, "FIT1055")
    prohibition = [g for g in unit["requisite_groups"] if g["requisite_type"] == "prohibition"]
    assert len(prohibition) == 1
    codes = {item["item_code"] for item in prohibition[0]["items"]}
    assert codes == {"FIT1049", "FIT2003"}
    assert "FIT1055" not in codes

    for group in unit["requisite_groups"]:
        assert "cl_id" not in (group.get("description") or "")
        assert "Enrolment Rule" not in (group.get("description") or "")


def test_two_and_ed_choices_stay_two_choices(handbook_html):
    """FIT1008 needs (FIT1045 or FIT1053) *and* (FIT1058 or MAT1830).

    That is one AND over two OR groups. Read as a flat pair of groups it says
    the same thing only by accident - the same flattening turned FIT2099's
    top-level OR into an AND and told students to take units they never need.
    """
    unit = _parse(handbook_html, "FIT1008")
    prereq = [g for g in unit["requisite_groups"] if g["requisite_type"] == "prerequisite"]
    assert len(prereq) == 1
    assert prereq[0]["connector"] == "AND"

    choices = prereq[0]["groups"]
    assert [c["connector"] for c in choices] == ["OR", "OR"]
    assert [{i["item_code"] for i in c["items"]} for c in choices] == [
        {"FIT1045", "FIT1053"},
        {"FIT1058", "MAT1830"},
    ]


def test_a_top_level_or_survives_the_parser(handbook_html):
    """FIT2099: six programming units, OR an engineering pair.

    The pair is itself two OR choices joined by AND, so the rule is three
    levels deep. Flattened, a student holding FIT1045 was told they still
    needed two ENG units.
    """
    unit = _parse(handbook_html, "FIT2099")
    prereq = [g for g in unit["requisite_groups"] if g["requisite_type"] == "prerequisite"]
    assert len(prereq) == 1
    assert prereq[0]["connector"] == "OR"

    branches = prereq[0]["groups"]
    assert len(branches) == 2
    programming, engineering = branches
    assert "FIT1045" in {i["item_code"] for i in programming["items"]}
    assert engineering["connector"] == "AND"
    assert [c["connector"] for c in engineering["groups"]] == ["OR", "OR"]


def test_learning_outcomes_and_activities(handbook_html):
    unit = _parse(handbook_html, "FIT2102")
    assert len(unit["learning_outcomes"]) == 6
    assert all(o["description"] for o in unit["learning_outcomes"])
    assert {a["activity_type"] for a in unit["activities"]} == {"Applied sessions", "Workshops"}


def test_content_hash_is_stable_and_content_sensitive(handbook_html):
    first = _parse(handbook_html, "FIT2102")
    second = _parse(handbook_html, "FIT2102")
    assert first["content_hash"] == second["content_hash"]

    mutated = dict(first)
    mutated.pop("content_hash")
    mutated["title"] = "Something else"
    assert compute_content_hash(mutated) != first["content_hash"]


def test_parse_error_on_a_page_without_the_payload():
    with pytest.raises(ParseError):
        parse_unit_page("<html><body>maintenance</body></html>", "https://example.invalid")


def test_html_to_text_flattens_lists_and_entities():
    text = html_to_text("<p>First&nbsp;line</p><ul><li>one</li><li>two</li></ul>")
    assert "First line" in text
    assert "• one" in text and "• two" in text
    assert "<" not in text
