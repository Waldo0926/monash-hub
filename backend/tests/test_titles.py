"""Unit titles that put their qualifier first in English and last in Chinese.

Every case here is a title in the 2026 catalogue whose stored Chinese had the
order wrong. 导论改为学术研究 does not merely read awkwardly - it says the
introduction was *changed to* academic research.
"""
from __future__ import annotations

import pytest
from app.knowledge.titles import compose

TOPICS = {
    "financial accounting": "财务会计",
    "anatomy": "解剖学",
    "public relations": "公共关系",
    "academic research": "学术研究",
    "computing": "计算",
    "marketing": "市场营销",
    "econometrics": "计量经济学",
}


def tr(topic: str) -> str | None:
    return TOPICS.get(topic)


@pytest.mark.parametrize(
    ("english", "chinese"),
    [
        ("Introduction to financial accounting", "财务会计导论"),
        ("Introduction to anatomy", "解剖学导论"),
        ("Introduction to public relations", "公共关系导论"),
        ("Introduction to academic research", "学术研究导论"),
        ("Foundations of computing", "计算基础"),
        ("Fundamentals of marketing", "市场营销基础"),
        ("Principles of econometrics", "计量经济学原理"),
    ],
)
def test_the_qualifier_goes_last(english, chinese):
    assert compose(english, "zh", tr) == chinese


def test_a_title_with_a_structure_of_its_own_is_left_alone():
    """Appending the qualifier to the end of a subtitle would attach it to the
    wrong half: "X：理论与实践导论" introduces the practice, not the subject."""
    for name in (
        "Introduction to anatomy: theory and practice",
        "Introduction to law and society",
        "Foundations of computing, networks and data",
    ):
        assert compose(name, "zh", tr) is None, name


def test_a_topic_the_pipeline_cannot_translate_is_left_alone():
    assert compose("Introduction to basket weaving", "zh", lambda s: None) is None
    assert compose("Introduction to basket weaving", "zh", lambda s: s) is None


def test_a_title_that_is_not_this_shape_is_left_alone():
    for name in ("Programming paradigms", "Advanced data structures", "Deep tech entrepreneurship"):
        assert compose(name, "zh", tr) is None, name


@pytest.mark.parametrize("locale", ["zh", "ja", "ko"])
def test_every_qualifier_is_written_in_every_locale(locale):
    from app.knowledge.titles import QUALIFIERS
    for qualifier, renderings in QUALIFIERS.items():
        assert renderings.get(locale), f"{qualifier!r} has no {locale}"


def test_an_unsupported_locale_gets_nothing():
    assert compose("Introduction to anatomy", "fr", tr) is None
