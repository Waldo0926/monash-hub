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


def test_a_subtitle_after_a_colon_is_left_alone():
    """There the subject is only the part before the colon, and putting the
    qualifier at the very end would attach it to the subtitle: "X：理论与实践导论"
    introduces the practice, not the subject."""
    for name in (
        "Introduction to anatomy: theory and practice",
        "Foundations of computing; an overview",
    ):
        assert compose(name, "zh", tr) is None, name


def test_a_subject_that_is_a_list_is_still_one_subject():
    """A conjunction is not a subtitle. Excluding these left ten titles on the
    live site reading 导论对艺术的历史和理论 and 基础 of 解剖学和生理学."""
    cases = {
        "Introduction to the history and theory of art": ("艺术的历史和理论", "艺术的历史和理论导论"),
        "Introduction to computer systems, networks and security": (
            "计算机系统、网络和安全", "计算机系统、网络和安全导论",
        ),
        "Fundamentals of cancer and its management": ("癌症及其管理", "癌症及其管理基础"),
    }
    for english, (topic, expected) in cases.items():
        assert compose(english, "zh", lambda _s, t=topic: t) == expected


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


def test_a_full_stop_from_the_translator_does_not_land_inside_the_title():
    """Same fault as the degree names: the qualifier would go after the stop."""
    assert compose("Introduction to basket weaving", "zh", lambda s: "编织。") == "编织导论"
    assert compose("Introduction to basket weaving", "zh", lambda s: "。") is None


def test_reviewed_exact_titles_cover_reported_machine_failures():
    from app.knowledge.titles import ZH_TITLE_OVERRIDES

    assert ZH_TITLE_OVERRIDES["Accounting in business"] == "商业会计"
    assert ZH_TITLE_OVERRIDES["Assurance and audit services"] == "鉴证与审计服务"
    assert ZH_TITLE_OVERRIDES["Curating: Introduction"] == "策展导论"
    assert ZH_TITLE_OVERRIDES["Academic literacies"] == "学术素养"


def test_reviewed_exact_titles_are_real_translations():
    from app.knowledge.titles import ZH_TITLE_OVERRIDES

    assert all(english != chinese for english, chinese in ZH_TITLE_OVERRIDES.items())
