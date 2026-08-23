"""Terms a translation service is not allowed to have an opinion about.

Machine translation of a course description is low stakes: the prose is
descriptive, an approximation reads fine, and no translation at all reads worse.
Machine translation of Monash's *vocabulary* is not low stakes, and it fails in
a specific, repeatable way.

The worst of it is a pair that every general-purpose translator gets backwards,
because outside this university the words mean the other thing:

    unit    → a subject you enrol in         (not 单元)
    course  → the whole degree               (not 课程)

Translate those two the obvious way and "you must pass this unit to progress in
your course" comes out saying something close to the opposite. Everything else
in this file is here for the same reason at lower volume: `hurdle` is not an
obstacle, `census date` is not a population survey, `intermission` is not an
interval, and a student who acts on the wrong reading of any of them loses money
or a semester.

How it is enforced: each term is wrapped in a tag the service is told to leave
alone, and the tag is swapped for our Chinese afterwards. The output is then
checked - if a protected term somehow survived in English, or a known-bad
rendering appears anyway, the translation is rejected rather than stored. A gap
is recoverable; a confidently wrong sentence about census dates is not.
"""
from __future__ import annotations

import re

# Longest first, so "Weighted Average Mark" wins over "Mark" and
# "Confirmation of Enrolment" wins over "Enrolment". The regex is built in this
# order for the same reason.
GLOSSARY: dict[str, str] = {
    # --- the pair that matters most ---------------------------------------
    "unit": "课程",
    "units": "课程",
    "course": "学位课程",
    "courses": "学位课程",
    # --- marks and grades -------------------------------------------------
    # Monash writes the long form with its acronym after it, and both halves are
    # in this table. Matching them separately expands each one and produces
    # "累计平均绩点（CGPA）（累计平均绩点（CGPA））", so the pair is an entry of
    # its own - longest-first ordering makes it win.
    "Weighted Average Mark (WAM)": "加权平均分（WAM）",
    "Grade Point Average (GPA)": "平均绩点（GPA）",
    "Cumulative Grade Point Average (CGPA)": "累计平均绩点（CGPA）",
    "Web Enrolment System (WES)": "选课系统（WES）",
    "Weighted Average Mark": "加权平均分（WAM）",
    "WAM": "加权平均分（WAM）",
    "Grade Point Average": "平均绩点（GPA）",
    "GPA": "平均绩点（GPA）",
    "Cumulative Grade Point Average": "累计平均绩点（CGPA）",
    "CGPA": "累计平均绩点（CGPA）",
    "credit point": "学分",
    "credit points": "学分",
    "hurdle": "必过项",
    "hurdle requirement": "必过项要求",
    "learning outcome": "学习成果",
    "learning outcomes": "学习成果",
    # --- enrolment and the calendar ---------------------------------------
    "census date": "census date（学籍统计日）",
    "census dates": "census date（学籍统计日）",
    "teaching period": "教学期",
    "intermission": "休学（intermission）",
    "prerequisite": "先修要求",
    "prerequisites": "先修要求",
    "corequisite": "同修要求",
    "corequisites": "同修要求",
    "prohibition": "互斥课程",
    "prohibitions": "互斥课程",
    "special consideration": "特殊考虑（special consideration）",
    "academic progress": "学业进度",
    "academic integrity": "学术诚信",
    "academic record": "学业记录（成绩单）",
    "transcript": "成绩单",
    # --- international ----------------------------------------------------
    "Confirmation of Enrolment (CoE)": "入学确认书（CoE）",
    "Overseas Student Health Cover (OSHC)": "海外学生医疗保险（OSHC）",
    "Confirmation of Enrolment": "入学确认书（CoE）",
    "CoE": "入学确认书（CoE）",
    "Overseas Student Health Cover": "海外学生医疗保险（OSHC）",
    "OSHC": "海外学生医疗保险（OSHC）",
    # --- named systems, which are not translated at all -------------------
    "Handbook": "Handbook",
    "Moodle": "Moodle",
    "Allocate+": "Allocate+",
    "WES": "选课系统（WES）",
    "Web Enrolment System": "选课系统（WES）",
    "Monash": "Monash",
}

# Renderings that mean the term was translated as ordinary English rather than
# as Monash's use of it. Finding one in the output means the protection failed,
# and the translation is thrown away rather than stored.
FORBIDDEN_RENDERINGS: dict[str, tuple[str, ...]] = {
    "unit": ("单元", "单位"),
    "course": ("课程",),  # only wrong when it was 'course'; see _check below
    "hurdle": ("障碍", "跨栏", "栏架"),
    "census date": ("人口普查", "普查日"),
    "intermission": ("中场休息", "幕间"),
    "credit points": ("信用点", "学分点数", "信用积分"),
}

PROTECT_TAG = "x"

_TERMS = sorted(GLOSSARY, key=len, reverse=True)
# Case-insensitive, because "Units are worth credit points" starts a sentence
# and "units" is what is in the table. `restore` resolves case-insensitively to
# match.
#
# Known limitation: a term is matched wherever it appears as a word, including
# as a homograph - "the river courses through the valley" would be protected and
# come back as 学位课程. In Handbook prose that does not occur; if it ever does,
# the failure is one odd noun in a course description, not a wrong instruction.
#
# \b does not help for "Allocate+", so the boundary is only asserted where the
# term itself starts and ends with a word character.
_PATTERN = re.compile(
    "|".join(
        (rf"\b{re.escape(t)}\b" if t[:1].isalnum() and t[-1:].isalnum() else re.escape(t))
        for t in _TERMS
    ),
    re.IGNORECASE,
)
_PLACEHOLDER = re.compile(rf"<{PROTECT_TAG}>(.*?)</{PROTECT_TAG}>", re.DOTALL)


def protect(text: str) -> str:
    """Wrap every glossary term so the service leaves it alone."""
    return _PATTERN.sub(lambda m: f"<{PROTECT_TAG}>{m.group(0)}</{PROTECT_TAG}>", text)


# "累计平均绩点（CGPA）（累计平均绩点（CGPA））" - the same expansion twice, the
# second time in brackets. The explicit pair entries above stop most of these at
# the source; this catches the shapes nobody enumerated.
_DOUBLED = re.compile(r"(?P<term>[^（）\s][^（）]*?)\s*（(?P=term)）")


def restore(text: str) -> str:
    """Swap each protected term for its required Chinese."""

    def replace(match: re.Match[str]) -> str:
        term = match.group(1)
        if term in GLOSSARY:
            return GLOSSARY[term]
        # Case differs (start of a sentence): try the lowercase form.
        lowered = term.lower()
        for candidate, translated in GLOSSARY.items():
            if candidate.lower() == lowered:
                return translated
        return term

    return _DOUBLED.sub(r"\g<term>", _PLACEHOLDER.sub(replace, text))


class GlossaryViolation(ValueError):
    """The output translated a term this file reserves."""


def repair(source: str, translated: str) -> tuple[str, list[str]]:
    """Force the reserved terms back to their required Chinese.

    The batch used to discard a passage that failed the check, which kept the
    page honest at the cost of leaving it in English. The instruction now is
    full coverage, so a failed passage is repaired instead of dropped: the
    known-bad rendering is substituted for the required one, which for these
    terms is a safe edit because the two are the same part of speech and the
    surrounding sentence does not change shape.

    Returns the repaired text and the list of terms that needed repairing, so a
    run can report how often the protection failed rather than hiding it.
    """
    repaired = translated
    fixed: list[str] = []
    for term, bad_renderings in FORBIDDEN_RENDERINGS.items():
        if not re.search(rf"\b{re.escape(term)}\b", source, re.IGNORECASE):
            continue
        required = GLOSSARY[term]
        for bad in bad_renderings:
            if bad in repaired and required not in repaired:
                repaired = repaired.replace(bad, required)
                fixed.append(term)
    return repaired, fixed


def check(source: str, translated: str) -> None:
    """Raise if a protected term leaked, or came back rendered the wrong way.

    Only terms that were actually in the source are checked. "课程" is the
    correct translation of `unit` and the wrong translation of `course`, so a
    forbidden rendering is only forbidden when its own term is present and its
    required Chinese is not.
    """
    for term, bad_renderings in FORBIDDEN_RENDERINGS.items():
        if not re.search(rf"\b{re.escape(term)}\b", source, re.IGNORECASE):
            continue
        required = GLOSSARY[term]
        for bad in bad_renderings:
            if bad in translated and required not in translated:
                raise GlossaryViolation(
                    f"{term!r} came back as {bad!r}; expected {required!r}"
                )

    leaked = [
        term
        for term in _TERMS
        # A term that is itself English in the required output (Moodle, Monash)
        # is allowed to appear in English.
        if GLOSSARY[term] != term
        and re.search(rf"\b{re.escape(term)}\b", translated)
        and re.search(rf"\b{re.escape(term)}\b", source)
    ]
    # "GPA" inside "平均绩点（GPA）" is not a leak, so only flag a term whose
    # required Chinese never made it into the output at all.
    leaked = [term for term in leaked if GLOSSARY[term] not in translated]
    if leaked:
        raise GlossaryViolation(f"untranslated glossary terms in output: {sorted(set(leaked))}")
