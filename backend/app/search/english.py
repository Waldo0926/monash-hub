"""How students phrase things in English, and what Monash calls them.

``synonyms.py`` does this for Chinese. English needed it too: a student types
"supp exam", "drop a unit" or "comp sci", and Monash writes "supplementary
assessment", "withdraw" and "Computer Science". PostgreSQL's stemmer gets
"withdrawing" to "withdraw", but it cannot know that "drop" means the same
thing, so "supp exam" listed every page about eExams and "comp sci" found no
degree at all.

A matched phrase is never removed from the query. It is *replaced*, one
alternative at a time, to make extra phrasings that are ORed with what was
typed: "drop a unit" is searched as itself and as "withdraw a unit". The rest
of the sentence is untouched, so its AND semantics stay as they were.

The table is split the same way as the Chinese one. Admin words (fees,
visas, exams) tell the unit search to stay out of it: "how to enroll" is a
question for the official pages, and it used to list 331 units whose
overviews say "enrol".
"""
from __future__ import annotations

import re
from functools import lru_cache
from itertools import islice

from app.search.normalise import fold

EN_ADMIN_TERMS: dict[str, tuple[str, ...]] = {
    # --- assessment ---------------------------------------------------------
    "sc": ("special consideration",),
    "spec con": ("special consideration",),
    "special con": ("special consideration",),
    "supp": ("supplementary assessment",),
    "supps": ("supplementary assessment",),
    "supp exam": ("supplementary assessment", "supplementary exam"),
    "resit": ("supplementary assessment", "supplementary exam"),
    "re-sit": ("supplementary assessment", "supplementary exam"),
    "resit exam": ("supplementary assessment", "supplementary exam"),
    "retake exam": ("supplementary assessment", "supplementary exam"),
    "deferred exam": ("deferred assessment", "defer final assessment"),
    "defer exam": ("deferred assessment", "defer final assessment"),
    "defer my exam": ("deferred assessment", "defer final assessment"),
    "missed exam": ("deferred assessment", "defer final assessment"),
    # Monash calls its exams final assessments, and so does every page title.
    "exam": ("final assessment",),
    "exams": ("final assessments",),
    "exam timetable": ("final assessment timetable", "final assessment dates"),
    "exam schedule": ("final assessment timetable", "final assessment dates"),
    "exam dates": ("final assessment dates", "final assessment timetable"),
    "late submission": ("late penalty", "extension"),
    "submit late": ("late submission", "late penalty", "extension"),
    "late penalty": ("late submission", "extension"),
    "remark": ("review of results", "appeal"),
    "re-mark": ("review of results", "appeal"),
    "grade appeal": ("appeal", "review of results"),
    "results review": ("review of results", "appeal"),
    "results release": ("results",),
    "wam": ("weighted average mark",),
    "gpa": ("grade point average",),
    "cp": ("credit points",),
    "census": ("census date",),
    "census date": ("census date",),
    "census dates": ("census dates",),
    # --- enrolment ----------------------------------------------------------
    "drop": ("withdraw",),
    "drop out": ("discontinue",),
    "enroll": ("enrol",),
    "enrolling": ("enrol",),
    "enrollment": ("enrolment",),
    "enrollments": ("enrolments",),
    "rpl": ("recognition of prior learning", "credit", "advanced standing"),
    "credit transfer": ("credit", "advanced standing"),
    "exemption": ("credit", "advanced standing"),
    "exemptions": ("credit", "advanced standing"),
    "gap year": ("intermission",),
    "gap semester": ("intermission",),
    "take a break": ("intermission",),
    "semester off": ("intermission",),
    "take a semester off": ("intermission",),
    "take a year off": ("intermission",),
    "leave of absence": ("intermission",),
    "intermit": ("intermission",),
    "switch course": ("course transfer", "change course"),
    "switch degree": ("course transfer", "change course"),
    "change degree": ("course transfer", "change course"),
    "change course": ("course transfer",),
    "change my course": ("course transfer",),
    "transfer course": ("course transfer",),
    # What Malaysia campus students call it. Monash's own pages never use it.
    "icp": ("internal course transfer",),
    "change campus": ("campus transfer",),
    "switch campus": ("campus transfer",),
    "transfer campus": ("campus transfer",),
    "move campus": ("campus transfer",),
    "class timetable": ("timetable", "allocate+"),
    "allocate": ("allocate+",),
    "student letter": ("student letter", "enrolment verification"),
    "enrolment letter": ("student letter", "enrolment verification"),
    "enrollment letter": ("student letter", "enrolment verification"),
    # --- fees and dates -----------------------------------------------------
    "tuition": ("fees",),
    "uni fees": ("fees",),
    "pay fees": ("fee payment", "pay your fees"),
    "refund": ("refund", "fee reversal"),
    "key dates": ("important dates", "principal dates"),
    "semester dates": ("semester dates", "principal dates"),
    "semester start": ("semester dates", "principal dates", "orientation"),
    "o week": ("orientation",),
    "o-week": ("orientation",),
    # --- graduation ---------------------------------------------------------
    "grad": ("graduation",),
    "graduation ceremony": ("graduations", "graduation ceremony"),
    "graduation ceremonies": ("graduations", "graduation ceremony"),
    "graduate ceremony": ("graduation ceremony", "graduations"),
    "degree certificate": ("testamur", "award certificate"),
    "degree parchment": ("testamur", "award certificate"),
    "testamur": ("testamur", "award certificate"),
    # --- international students and campus life ---------------------------
    "ikad": ("i-kad",),
    "i kad": ("i-kad",),
    "health insurance": ("oshc", "medical insurance", "health cover"),
    "health cover": ("oshc", "medical insurance"),
    "ielts": ("english language requirements", "english language"),
    "english test": ("english language requirements", "english language"),
    "mpu": ("general studies",),
    "mpu units": ("general studies",),
    "general study": ("general studies",),
    "public transport": ("transport",),
    "shuttle": ("shuttle bus",),
    "student card": ("m-pass", "id card"),
    "student id": ("m-pass", "id card"),
    "id card": ("m-pass", "id card"),
    "counseling": ("counselling",),
    "counselor": ("counsellor",),
}

# Subjects and degrees: these reach units and degrees as well as pages.
EN_FIELD_TERMS: dict[str, tuple[str, ...]] = {
    "comp sci": ("computer science",),
    "compsci": ("computer science",),
    "cs": ("computer science",),
    "it": ("information technology",),
    "ai": ("artificial intelligence",),
    "ml": ("machine learning",),
    "os": ("operating systems",),
    "db": ("databases",),
    "se": ("software engineering",),
    "ds": ("data science",),
    "hci": ("human-computer interaction",),
    "oop": ("object oriented",),
    "dsa": ("algorithms", "data structures"),
    "algo": ("algorithms",),
    "algos": ("algorithms",),
    "cyber": ("cybersecurity",),
    "cyber security": ("cybersecurity",),
    "web dev": ("web development",),
    "ux": ("user experience", "interaction design"),
    "maths": ("mathematics",),
    "math": ("mathematics",),
    "stats": ("statistics",),
    "econ": ("economics",),
    "biz": ("business",),
    "psych": ("psychology",),
    "chem": ("chemistry",),
    "honors": ("honours",),
    "mba": ("master of business administration", "business administration"),
    "masters": ("master",),
    "bachelors": ("bachelor",),
    "undergrad": ("bachelor",),
    "postgrad": ("master", "graduate"),
    "phd": ("doctor of philosophy",),
    "double degree": ("and bachelor",),
    "double degrees": ("and bachelor",),
}

EN_TERMS: dict[str, tuple[str, ...]] = {**EN_ADMIN_TERMS, **EN_FIELD_TERMS}

# Two letters that are also ordinary words or pronouns. "IT" is a faculty,
# "it" is the end of "how do I do it". Typed in capitals, or in a query too
# short to be a sentence, they are the abbreviation.
AMBIGUOUS = frozenset({"it", "cs", "ai", "ml", "os", "db", "se", "ds"})
SHORT_QUERY_WORDS = 3

# Past this, every extra phrasing makes the query slower and finds nothing new.
MAX_VARIANTS = 8


@lru_cache(maxsize=1)
def _patterns() -> tuple[tuple[str, re.Pattern[str]], ...]:
    """Each phrase with its word-bounded pattern, longest phrase first."""
    return tuple(
        (phrase, re.compile(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9+])"))
        for phrase in sorted(EN_TERMS, key=len, reverse=True)
    )


def phrase_runs(term: str) -> list[tuple[str, tuple[int, int]]]:
    """The table phrases in ``term``, as (phrase, span), longest first, no overlaps."""
    typed = fold(term)
    text = typed.lower()
    if not text:
        return []
    short = len(text.split()) <= SHORT_QUERY_WORDS
    taken = [False] * len(text)
    found: list[tuple[str, tuple[int, int]]] = []
    for phrase, pattern in _patterns():
        for match in pattern.finditer(text):
            start, end = match.span()
            if any(taken[start:end]):
                continue
            if phrase in AMBIGUOUS and not short and not typed[start:end].isupper():
                continue
            for index in range(start, end):
                taken[index] = True
            found.append((phrase, (start, end)))
    return found


def alternatives(term: str) -> list[str]:
    """Every phrasing the table offers for ``term``, flattened."""
    flat: list[str] = []
    for phrase, _ in phrase_runs(term):
        for alternative in EN_TERMS[phrase]:
            if alternative not in flat:
                flat.append(alternative)
    return flat


def variants(term: str) -> list[str]:
    """``term`` rewritten in Monash's words, one phrase at a time.

    "drop a unit" gives "withdraw a unit". With two phrases in the query the
    first alternative of each is also substituted together, so "supp exam
    wam" can still meet a page that says both properly.
    """
    text = fold(term).lower()
    runs = sorted(phrase_runs(term), key=lambda run: run[1][0])
    if not runs:
        return []

    def rewrite(choice: dict[int, str]) -> str:
        out, last = [], 0
        for index, (_, (start, end)) in enumerate(runs):
            out.append(text[last:start])
            out.append(choice.get(index, text[start:end]))
            last = end
        out.append(text[last:])
        return " ".join("".join(out).split())

    def generate():
        for index, (phrase, _) in enumerate(runs):
            for alternative in EN_TERMS[phrase]:
                yield rewrite({index: alternative})
        if len(runs) > 1:
            yield rewrite({i: EN_TERMS[p][0] for i, (p, _) in enumerate(runs)})

    seen = {text}
    unique = (v for v in generate() if not (v in seen or seen.add(v)))
    return list(islice(unique, MAX_VARIANTS))


def is_admin(phrase: str) -> bool:
    return phrase in EN_ADMIN_TERMS
