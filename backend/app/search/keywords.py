"""The intent dictionary behind the zero-AI question router.

Students type Chinese and English in the same sentence, so every intent carries
both. This is a dictionary rather than a model on purpose: "does FIT2102 have an
exam" is a database lookup, and paying a language model to re-read a field we
already parsed would be slower, less accurate and not free.
"""
from __future__ import annotations

import re

# Bounded by "not a Latin letter or digit" rather than \b. Python's \b treats
# CJK as word characters, so "FIT2102有考试吗" - typed without a space, the way
# Chinese is written - had no boundary after the code and found no unit at all.
UNIT_CODE_RE = re.compile(
    r"(?<![A-Za-z0-9])([A-Z]{3,4})\s?-?\s?(\d{4})(?![A-Za-z0-9])", re.IGNORECASE
)

INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "assessment": (
        "exam", "examination", "final", "assessment", "assessments", "hurdle", "weight",
        "考试", "期末", "考核", "作业", "占比", "评估", "有没有考试", "考不考",
        # Japanese and Korean: the interface speaks both, and its own suggestion
        # chips ask in them - a chip the router cannot read answers nothing.
        "試験", "期末試験", "評価", "課題", "配点",
        "시험", "기말", "기말시험", "평가", "과제", "배점",
    ),
    "requisite": (
        "prerequisite", "prerequisites", "requisite", "pre-req", "prereq", "corequisite",
        "prohibition", "前置", "先修", "前提课", "先决条件", "读之前",
        "履修条件", "前提科目", "先修科目", "선수과목", "선수 과목", "선수", "이수 조건",
    ),
    "offering": (
        "offering", "offered", "semester", "s1", "s2", "teaching period", "campus",
        "malaysia", "clayton", "caulfield", "开课", "校区", "学期", "马来西亚", "开吗",
        "開講", "キャンパス", "マレーシア", "개설", "캠퍼스", "학기", "말레이시아",
    ),
    "workload": (
        "workload", "contact hour", "contact hours", "hours", "lecture", "tutorial", "lab",
        "applied session", "workshop", "课时", "工作量", "几个小时", "学时",
        "授業時間", "学習時間", "学習量", "講義", "수업 시간", "학습량", "강의", "워크로드",
    ),
    "outcomes": (
        "learning outcome", "outcomes", "ulo", "学习成果", "学完能",
        "学習成果", "학습 성과", "학습성과",
    ),
    "official": (
        "special consideration", "sc", "deferred", "wam", "gpa", "visa", "student visa",
        "i-kad", "ikad", "exchange", "abroad", "census", "fees", "enrolment", "enrollment",
        "withdraw", "intermission", "graduation", "results", "policy",
        "特殊考虑", "签证", "均分", "绩点", "交换", "海外", "退课", "选课", "学费",
        "毕业", "成绩", "政策", "怎么申请", "如何申请",
    ),
}

# Words that mean the answer is a matter of opinion. We route these to the
# community and to the published workload rather than inventing a difficulty
# score the Handbook never stated.
SUBJECTIVE_KEYWORDS: tuple[str, ...] = (
    "hard", "easy", "difficult", "worth it", "recommend", "good", "boring",
    "难不难", "难吗", "简单吗", "容易", "值得", "推荐", "怎么样", "体验",
    "難しい", "簡単", "おすすめ", "どう", "어렵", "어려운", "쉬운", "추천", "어때",
)


def extract_unit_codes(query: str) -> list[str]:
    """Pull unit codes out of free text. ``fit 2102`` and ``FIT-2102`` both count."""
    seen: list[str] = []
    for prefix, digits in UNIT_CODE_RE.findall(query or ""):
        code = f"{prefix.upper()}{digits}"
        if code not in seen:
            seen.append(code)
    return seen


def classify_intent(query: str) -> tuple[str | None, list[str]]:
    """Return ``(intent, matched_keywords)``.

    Longest keyword wins, so "special consideration" beats a bare "sc" and
    "contact hours" beats "hours". A tie between intents is broken by the order
    of ``INTENT_KEYWORDS``, which puts the Handbook-backed intents first.
    """
    text = (query or "").lower()
    best: tuple[str, int] | None = None
    matched: list[str] = []
    for intent, keywords in INTENT_KEYWORDS.items():
        hits = [kw for kw in keywords if _contains(text, kw)]
        if not hits:
            continue
        strength = max(len(kw) for kw in hits)
        if best is None or strength > best[1]:
            best = (intent, strength)
            matched = hits
    if best is None:
        return None, []
    return best[0], sorted(set(matched), key=len, reverse=True)


def is_subjective(query: str) -> bool:
    text = (query or "").lower()
    return any(_contains(text, kw) for kw in SUBJECTIVE_KEYWORDS)


def _contains(text: str, keyword: str) -> bool:
    """Word-boundary match for ASCII keywords, substring for CJK.

    Chinese has no spaces, so a boundary check would never fire; English needs
    one so that "sc" does not match inside "science".
    """
    if keyword.isascii():
        return re.search(rf"(?<![a-z0-9]){re.escape(keyword)}(?![a-z0-9])", text) is not None
    return keyword in text
