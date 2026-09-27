"""Which curated FAQ answers a question - and when none does.

Every case in the "wrong answer" list below was a real answer on the live site:
the question on the left was answered with the FAQ on the right. They are pure
tests against the real FAQ seed, so a keyword added later that brings any of
them back fails here before it reaches a student.
"""
from __future__ import annotations

import pytest
from app.knowledge.faq_seed import FAQ_SEEDS
from app.knowledge.translations_seed import FAQ_ZH
from app.search.faq_match import FaqCandidate, match, normalise, stem

CANDIDATES = [
    FaqCandidate(
        slug=seed.slug,
        question=seed.question,
        keywords=seed.keywords,
        tags=seed.tags,
        priority=seed.priority,
        translated_questions=(FAQ_ZH[seed.slug][0],) if seed.slug in FAQ_ZH else (),
    )
    for seed in FAQ_SEEDS
]


def answer(query: str, **kwargs) -> str | None:
    found = match(query, CANDIDATES, **kwargs)
    return found[0].candidate.slug if found and found[0].confident else None


# --- answers that were wrong on the live site -------------------------------

@pytest.mark.parametrize(
    "query,wrong",
    [
        ("学生签证续签", "how-to-withdraw-from-a-unit"),
        ("student visa renewal", "student-visa-work-hours"),
        ("visa extension", "how-to-apply-special-consideration"),
        ("签证延期", "how-to-apply-special-consideration"),
        ("scholarship", "what-is-gpa"),
        ("学术诚信", "when-do-results-come-out"),
        ("fail a unit", "how-to-withdraw-from-a-unit"),
        ("change course", "what-is-coe"),
        ("enrol in units", "how-to-withdraw-from-a-unit"),
        ("学分转换", "what-is-wam"),
        ("马来西亚校区", "student-visa-work-hours"),
    ],
)
def test_a_shared_word_is_not_an_answer(query, wrong):
    assert answer(query) != wrong
    # None of these has a curated answer at all; they belong to the official
    # page search, not to whichever FAQ shares a word with them.
    assert answer(query) is None


@pytest.mark.parametrize(
    "query,right",
    [
        ("成绩单", "how-to-get-a-transcript"),        # was: results come out
        ("休学", "apply-for-intermission"),            # was: CoE
        ("延期考试", "defer-a-final-assessment"),      # was: special consideration
    ],
)
def test_the_more_specific_entry_wins(query, right):
    assert answer(query) == right


# --- answers that must keep working -----------------------------------------

@pytest.mark.parametrize(
    "query,slug",
    [
        ("怎么申请特殊考虑", "how-to-apply-special-consideration"),
        ("怎么申请 SC", "how-to-apply-special-consideration"),
        ("how do I apply for special consideration", "how-to-apply-special-consideration"),
        ("申请延期", "how-to-apply-special-consideration"),
        ("sc 需要什么材料", "what-documents-for-sc"),
        ("what documents do I need for special consideration", "what-documents-for-sc"),
        ("WAM怎么算", "what-is-wam"),
        ("how is wam calculated", "what-is-wam"),
        ("GPA怎么算", "what-is-gpa"),
        ("what is census date", "census-date-meaning"),
        ("退课截止日期", "census-date-meaning"),
        ("我想退课", "how-to-withdraw-from-a-unit"),
        ("how to drop a unit", "how-to-withdraw-from-a-unit"),
        ("how do I withdraw from a unit", "how-to-withdraw-from-a-unit"),
        ("how many hours can i work on a student visa", "student-visa-work-hours"),
        ("can I work part-time on my visa", "student-visa-work-hours"),
        ("留学生可以打工吗", "student-visa-work-hours"),
        ("CoE是什么", "what-is-coe"),
        ("can i take a semester off", "apply-for-intermission"),
        ("可以休学一个学期吗", "apply-for-intermission"),
        ("成绩什么时候出", "when-do-results-come-out"),
        ("怎么开成绩单", "how-to-get-a-transcript"),
        ("how do i go on exchange", "exchange-eligibility"),
        ("can i defer my exam", "defer-a-final-assessment"),
        ("I am sick and missed my exam", "defer-a-final-assessment"),
        ("生病了没去考试", "defer-a-final-assessment"),
    ],
)
def test_a_question_the_faq_covers_gets_it(query, slug):
    assert answer(query) == slug


@pytest.mark.parametrize("seed", FAQ_SEEDS, ids=lambda s: s.slug)
def test_every_faq_answers_its_own_question(seed):
    """A suggestion chip is the FAQ's question; clicking it must open that FAQ."""
    assert answer(seed.question) == seed.slug
    if seed.slug in FAQ_ZH:
        assert answer(FAQ_ZH[seed.slug][0]) == seed.slug


# --- the negative space ------------------------------------------------------

@pytest.mark.parametrize(
    "query",
    ["签证", "visa", "考试", "exam", "工作量是什么", "where can I park a scooter",
     "is there a science building map", "group work", ""],
)
def test_a_topic_word_alone_answers_nothing(query):
    """签证 is a topic, not a question. It belongs to the official page list."""
    assert answer(query) is None


def test_an_uncovered_question_still_offers_the_faq_as_related():
    found = match("退课会影响签证吗", CANDIDATES)
    assert found and not found[0].confident
    assert found[0].candidate.slug == "how-to-withdraw-from-a-unit"


def test_a_unit_code_the_router_handles_is_not_residue():
    assert answer("FIT2004 怎么退课") is None
    assert answer("FIT2004 怎么退课", ignore={"fit2004", "fit", "2004"}) \
        == "how-to-withdraw-from-a-unit"


def test_priority_only_breaks_ties():
    """The entry with the higher hand-set priority used to win outright."""
    low = FaqCandidate("specific", "How do I get a transcript?", ("成绩单",), priority=1)
    high = FaqCandidate("general", "When do results come out?", ("成绩",), priority=100)
    assert match("成绩单", [high, low])[0].candidate.slug == "specific"


# --- plumbing ----------------------------------------------------------------

def test_normalise_folds_full_width_and_case():
    assert normalise("ＷＡＭ怎么算？") == "wam怎么算"


@pytest.mark.parametrize(
    "a,b", [("withdrawing", "withdraw"), ("dropped", "drop"), ("dropping", "drop"),
            ("applies", "apply"), ("units", "unit")],
)
def test_stem_meets_the_base_form(a, b):
    assert stem(a) == stem(b)


def test_latin_keywords_need_whole_words():
    assert answer("science") is None
    assert answer("scooter") is None


@pytest.mark.parametrize("seed", FAQ_SEEDS, ids=lambda s: s.slug)
def test_every_faq_has_a_chinese_translation(seed):
    """The answer card is drawn in the reader's language; a new FAQ without
    Chinese would be the one English paragraph on a Chinese page."""
    assert seed.slug in FAQ_ZH
