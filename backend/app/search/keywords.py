"""The intent dictionary behind the zero-AI question router.

Students type Chinese and English in the same sentence, so every intent carries
both. This is a dictionary rather than a model on purpose: "does FIT2102 have an
exam" is a database lookup, and paying a language model to re-read a field we
already parsed would be slower, less accurate and not free.
"""
from __future__ import annotations

import re

# ASCII-only lookarounds instead of ``\b``: Python counts CJK characters as word
# characters, so "FIT2004有期末考试吗" has no word boundary after the digits and
# a ``\b`` pattern silently finds no unit at all. Explicit ranges instead of
# ``\d`` and IGNORECASE keep full-width digits and look-alike letters out of the
# code we hand to the database.
UNIT_CODE_RE = re.compile(r"(?<![A-Za-z0-9])([A-Za-z]{3,4})\s?-?\s?([0-9]{4})(?![0-9])")

INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "assessment": (
        "exam", "examination", "final", "assessment", "assessments", "hurdle", "weight",
        "考试", "期末", "考核", "作业", "占比", "评估", "有没有考试", "考不考",
    ),
    "requisite": (
        "prerequisite", "prerequisites", "requisite", "pre-req", "prereq", "corequisite",
        "prohibition", "前置", "先修", "前提课", "先决条件", "读之前",
    ),
    "offering": (
        "offering", "offered", "semester", "s1", "s2", "teaching period", "campus",
        "malaysia", "clayton", "caulfield", "开课", "校区", "学期", "马来西亚", "开吗",
    ),
    "workload": (
        "workload", "contact hour", "contact hours", "hours", "lecture", "tutorial", "lab",
        "applied session", "workshop", "课时", "工作量", "几个小时", "学时",
    ),
    "outcomes": (
        "learning outcome", "outcomes", "ulo", "学习成果", "学完能",
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
