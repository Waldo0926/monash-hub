"""Degree names.

These are the most-read strings on the site - every degree card, the planner's
picker, the heading of every degree page - and a general translator gets them
wrong in a way that is obvious to any Chinese reader: it renders the award as
大师 (a guru) or 师傅 (a craftsman), keeps English word order, or drops the
subject altogether. Each case below was taken off the live site.
"""
from __future__ import annotations

import pytest
from app.knowledge.degrees import compose

# A stand-in for the pipeline. The real one translates the subject with the
# glossary in front; here it answers for the subjects these cases need and
# nothing else, so a test passing means the composition did the work.
KNOWN = {
    "Applied Data Science": "应用数据科学",
    "Computer Science": "计算机科学",
    "Information Technology": "信息技术",
    "Global Studies": "全球研究",
    "Actuarial Studies": "精算研究",
    "Global Business": "全球商业",
    "Regulation and Compliance": "监管与合规",
}


def tr(subject: str) -> str | None:
    return KNOWN.get(subject)


@pytest.mark.parametrize(
    ("english", "chinese"),
    [
        # Reported: the subject disappeared entirely.
        ("Bachelor of Science", "理学学士"),
        # The award, read as a person rather than a qualification.
        ("Master of Teaching", "教育硕士"),
        ("Master of Accounting", "会计学硕士"),
        ("Master of Public Health", "公共卫生硕士"),
        ("Master of Philosophy", "哲学硕士"),
        ("Master of Fine Art", "美术硕士"),
        # English word order with Chinese words.
        ("Bachelor of Engineering (Honours)", "工程学士（荣誉学位）"),
        ("Bachelor of Nursing (Honours)", "护理学学士（荣誉学位）"),
        # "podiatric" had been read as "paediatric": a foot doctor became a
        # children's doctor.
        ("Doctor of Podiatric Medicine", "足病医学博士"),
        ("Bachelor of Speech Pathology (Honours)", "言语病理学学士（荣誉学位）"),
        ("Graduate Certificate of Addictive Behaviours", "成瘾行为研究生证书"),
        # The subject is not curated, so the pipeline supplies it.
        ("Bachelor of Applied Data Science", "应用数据科学学士"),
        ("Master of Computer Science", "计算机科学硕士"),
        # Both halves of a double degree, each composed.
        ("Bachelor of Arts and Bachelor of Music", "文学学士与音乐学士"),
        ("Master of Design (by Research)", "设计硕士（研究型）"),
    ],
)
def test_a_degree_is_named_the_way_a_degree_is_named(english, chinese):
    assert compose(english, "zh", tr) == chinese


def test_a_subject_containing_and_is_one_degree_not_two():
    """"Bachelor of Arts and Social Sciences" is a single award. Splitting on
    the word would invent a degree nobody can enrol in."""
    assert compose("Bachelor of Arts and Social Sciences", "zh", lambda s: "文学与社会科学") == (
        "文学与社会科学学士"
    )
    assert compose("Bachelor of Criminology and Policing", "zh", lambda s: "犯罪学与警务") == (
        "犯罪学与警务学士"
    )


def test_a_name_it_does_not_understand_is_left_alone():
    """Composing may only improve on the ordinary path, never invent a new way
    of being wrong. A subtitle after a dash, or a partner university in
    brackets, is not a shape this claims to read."""
    for name in (
        "Bachelor of Science Advanced - Global Challenges (Honours)",
        "Doctor of Philosophy (Monash - Warwick)",
        "Doctor of Philosophy (Clinical Psychology)",
        "Monash Transition Program",
        "Master of Advanced Study (Engineering Research)",
    ):
        assert compose(name, "zh", tr) is None, name


def test_a_subject_the_pipeline_cannot_translate_is_left_alone():
    """Half a name in Chinese and half in English is worse than all English."""
    assert compose("Bachelor of Underwater Basketry", "zh", lambda s: None) is None
    assert compose("Bachelor of Underwater Basketry", "zh", lambda s: s) is None


def test_a_double_degree_is_all_or_nothing():
    """One half composed and the other left in English would read as a degree
    that is half translated."""
    assert compose(
        "Bachelor of Arts and Bachelor of Underwater Basketry", "zh", lambda s: None
    ) is None


@pytest.mark.parametrize("locale", ["zh", "ja", "ko"])
def test_every_award_and_qualifier_is_written_in_every_locale(locale):
    from app.knowledge.degrees import AWARDS, DISCIPLINES, QUALIFIERS
    for table, name in ((AWARDS, "award"), (DISCIPLINES, "discipline"), (QUALIFIERS, "qualifier")):
        for term, renderings in table.items():
            assert renderings.get(locale), f"{name} {term!r} has no {locale}"


def test_an_unsupported_locale_gets_nothing():
    assert compose("Bachelor of Science", "fr", tr) is None


def test_a_double_degree_whose_second_subject_contains_and():
    """Split at one "and", not at every one. B6044 is two degrees, the second
    being "Regulation and Compliance". Cutting at every "and" made three
    fragments that paired up with nothing, so the whole string fell through to
    the single-degree path and its subject - award word included - went to the
    translator: 全球商业和监管与合规大师硕士, a guru in front of a master."""
    assert compose(
        "Master of Global Business and Master of Regulation and Compliance", "zh", tr
    ) == "全球商业硕士与监管与合规硕士"


def test_the_split_is_not_taken_when_the_right_half_is_not_a_degree():
    """Still one degree, even though the subject has an "and" in it."""
    assert compose("Bachelor of Arts and Social Sciences", "zh", lambda s: "文学与社会科学") == (
        "文学与社会科学学士"
    )
