"""The intent dictionary decides which stored field answers a question."""
from __future__ import annotations

import pytest
from app.search.keywords import classify_intent, extract_unit_codes, is_subjective


@pytest.mark.parametrize(
    "query,expected",
    [
        ("FIT2102 有没有考试？", ["FIT2102"]),
        ("what are the prerequisites for fit 2102", ["FIT2102"]),
        ("compare FIT2102 and BFF2140", ["FIT2102", "BFF2140"]),
        ("how do I apply for special consideration", []),
        # Python's \b counts CJK as word characters, so these used to find nothing.
        ("FIT2004有期末考试吗？", ["FIT2004"]),
        ("请问FIT2004有期末考试吗", ["FIT2004"]),
        ("FIT2004和FIT2014哪个难", ["FIT2004", "FIT2014"]),
        ("fit 2102", ["FIT2102"]),
        ("FIT-2102", ["FIT2102"]),
        ("FIT12345678", []),
        ("学号12345678", []),
    ],
)
def test_extract_unit_codes(query, expected):
    assert extract_unit_codes(query) == expected


@pytest.mark.parametrize(
    "query,intent",
    [
        ("FIT2102 有没有考试", "assessment"),
        ("does FIT2102 have a final exam", "assessment"),
        ("FIT2102 前置课是什么", "requisite"),
        ("prerequisites for FIT2102", "requisite"),
        ("is FIT2102 offered in Malaysia", "offering"),
        ("FIT2102 马来西亚开吗", "offering"),
        ("FIT2102 contact hours", "workload"),
        ("how do I apply for special consideration", "official"),
        ("怎么申请 SC", "official"),
        ("what is my WAM", "official"),
    ],
)
def test_classify_intent(query, intent):
    assert classify_intent(query)[0] == intent


def test_sc_does_not_match_inside_another_word():
    # "sc" is a real abbreviation students use, but it must not fire on
    # "science" or every course question would route to policy pages.
    assert classify_intent("computer science units")[0] != "official"


def test_longest_keyword_wins():
    intent, matched = classify_intent("special consideration deadline")
    assert intent == "official"
    assert "special consideration" in matched


def test_unknown_query_has_no_intent():
    assert classify_intent("where can I park a scooter")[0] is None


def test_a_bare_topic_word_still_needs_a_unit_to_reach_the_handbook():
    # "campus" is an offering keyword, so this classifies - but with no unit
    # code the router falls through to official pages and the community.
    assert classify_intent("where is the best coffee on campus")[0] == "offering"


@pytest.mark.parametrize("query", ["FIT2102 难不难", "is FIT2102 hard", "FIT2102 怎么样"])
def test_subjective_questions_are_flagged(query):
    assert is_subjective(query) is True


def test_factual_question_is_not_subjective():
    assert is_subjective("does FIT2102 have an exam") is False
