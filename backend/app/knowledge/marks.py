"""The rules behind WAM and GPA.

The tables here are transcribed from the two official pages this platform
already crawls - `guides/wam` and `guides/gpa` - and the tests check the
arithmetic against Monash's own worked examples from those same pages. That is
the point of keeping them in the backend rather than in the calculator's
JavaScript: a number that decides whether somebody thinks they are on track for
honours should be pinned by a test, not by whoever last edited a component.

The calculator itself runs in the browser. It fetches these tables once and does
the two weighted averages locally, so a student's marks never leave their
machine. This module is where the tables come from and where the maths is
proved; `frontend/utils/marks.ts` is the copy that runs.

Four rules that are easy to get wrong, and all four are in the official worked
examples:

* **A fail counts, at its actual mark.** MON1003 scored 40 and is in the WAM at
  40, not dropped. Most homemade calculators drop it and flatter the student.
* **A withdrawn fail counts as zero, and stays in the denominator.** MON2002 has
  no mark at all; it contributes 0 to the top and its full weighted credit
  points to the bottom.
* **First-year undergraduate units are weighted 0.5.** Not "the year you took
  it" - the level of the unit. A Level 1 unit taken in third year is still 0.5.
* **Credit points weight both.** The 0.5 must appear in the numerator *and* the
  denominator; halving only the top is the classic error that turns a 90 into
  a 45.

Malaysia is a different scale. CGPA is not GPA with different rounding - Credit
is 2.85 rather than 2.0 - and a platform serving both campuses cannot use one
table for both.
"""
from __future__ import annotations

from dataclasses import dataclass

AUSTRALIA = "australia"
MALAYSIA = "malaysia"

# From guides/gpa, "Grades and their GPA grade value" and "...CGPA grade value".
GRADE_POINTS: dict[str, dict[str, float]] = {
    AUSTRALIA: {
        "HD": 4.0,
        "D": 3.0,
        "C": 2.0,
        "P": 1.0,
        "NP": 0.7,
        "N": 0.3,
        "NH": 0.3,
        "WN": 0.0,
    },
    MALAYSIA: {
        "HD": 4.0,
        "D": 3.67,
        "C": 2.85,
        "P": 2.15,
        "NP": 1.7,
        "N": 1.15,
        "NH": 1.15,
        "WN": 0.0,
    },
}

# The code Monash prints on a transcript, and what it is called in full.
GRADE_NAMES: dict[str, str] = {
    "HD": "High distinction",
    "D": "Distinction",
    "C": "Credit",
    "P": "Pass",
    "NP": "Near pass",
    "N": "Fail",
    "NH": "Hurdle fail",
    "WN": "Withdrawn fail",
}

# Mark bands, for turning a mark into a grade. Monash rounds the final mark
# first, so 79.5 is a Distinction and 79.4 is not.
GRADE_BANDS: tuple[tuple[int, str], ...] = (
    (80, "HD"),
    (70, "D"),
    (60, "C"),
    (50, "P"),
    (45, "NP"),
    (0, "N"),
)

# Grades carrying no grade point at all: excluded from both averages, top and
# bottom. From the "Grades not included in the calculation" list on guides/gpa.
EXCLUDED_GRADES: tuple[str, ...] = (
    "SFR", "NE", "NAS", "WI", "PGO", "NPGO", "WNGO",
)

FIRST_YEAR_WEIGHT = 0.5
OTHER_YEAR_WEIGHT = 1.0


class MarkError(ValueError):
    """The entry cannot be scored - an unknown grade, or a mark out of range."""


@dataclass(frozen=True, slots=True)
class Entry:
    """One completed unit: what it was worth, and how it went."""

    unit_code: str
    credit_points: float
    # 1 for a first-year undergraduate unit. Anything else weights 1.0.
    level: int | None = None
    mark: float | None = None
    grade: str | None = None

    @property
    def level_weight(self) -> float:
        return FIRST_YEAR_WEIGHT if self.level == 1 else OTHER_YEAR_WEIGHT


def round_mark(mark: float) -> int:
    """Monash rounds the final mark, so 79.51 is 80 and an HD.

    Python's round() is banker's rounding - round(79.5) is 80 but round(78.5) is
    78 - which is not what a student sees on a transcript.
    """
    return int(mark + 0.5) if mark >= 0 else int(mark - 0.5)


def grade_for_mark(mark: float) -> str:
    rounded = round_mark(mark)
    if not 0 <= rounded <= 100:
        raise MarkError(f"a mark of {mark} is not between 0 and 100")
    for floor, grade in GRADE_BANDS:
        if rounded >= floor:
            return grade
    raise MarkError(f"no grade band for {mark}")  # pragma: no cover - unreachable


def resolve_grade(entry: Entry) -> str | None:
    """The grade this entry scores under, or None when it does not count."""
    if entry.grade:
        code = entry.grade.strip().upper()
        if code in EXCLUDED_GRADES:
            return None
        if code not in GRADE_NAMES:
            raise MarkError(f"unknown grade: {entry.grade}")
        return code
    if entry.mark is None:
        return None
    return grade_for_mark(entry.mark)


def wam(entries: list[Entry]) -> float | None:
    """Σ(mark × credit points × level weight) ÷ Σ(credit points × level weight).

    A withdrawn fail has no mark and scores 0, but its credit points stay in the
    denominator - that is what makes a WN so expensive.
    """
    top = 0.0
    bottom = 0.0
    for entry in entries:
        grade = resolve_grade(entry)
        if grade is None:
            continue
        weight = entry.credit_points * entry.level_weight
        mark = 0.0 if grade == "WN" else entry.mark
        if mark is None:
            # A grade with no mark that is not a WN - nothing to average.
            continue
        top += mark * weight
        bottom += weight
    return top / bottom if bottom else None


def gpa(entries: list[Entry], scale: str = AUSTRALIA) -> float | None:
    """Σ(grade value × credit points) ÷ Σ credit points.

    Note what is *not* here: the level weight. GPA does not use it - only WAM
    does. Applying it to both is a common and quiet mistake.
    """
    points = GRADE_POINTS[scale]
    top = 0.0
    bottom = 0.0
    for entry in entries:
        grade = resolve_grade(entry)
        if grade is None:
            continue
        top += points[grade] * entry.credit_points
        bottom += entry.credit_points
    return top / bottom if bottom else None


def mark_needed(
    entries: list[Entry], planned: list[Entry], target: float
) -> float | None:
    """The same mark in every planned unit that would reach ``target`` WAM.

    This is the question students actually ask - "what do I need this semester?"
    - and the answer is often outside 0-100, which is itself the useful answer:
    it means the target is already out of reach, or already guaranteed.

    Returns None when the planned units carry no weight at all.
    """
    done_top = 0.0
    done_bottom = 0.0
    for entry in entries:
        grade = resolve_grade(entry)
        if grade is None:
            continue
        weight = entry.credit_points * entry.level_weight
        mark = 0.0 if grade == "WN" else entry.mark
        if mark is None:
            continue
        done_top += mark * weight
        done_bottom += weight

    planned_weight = sum(e.credit_points * e.level_weight for e in planned)
    if planned_weight <= 0:
        return None
    # target = (done_top + x·planned_weight) / (done_bottom + planned_weight)
    return (target * (done_bottom + planned_weight) - done_top) / planned_weight


def reference() -> dict:
    """The tables, for the calculator to fetch once and compute against."""
    return {
        "grade_points": GRADE_POINTS,
        "grade_names": GRADE_NAMES,
        "grade_bands": [{"floor": floor, "grade": grade} for floor, grade in GRADE_BANDS],
        "excluded_grades": list(EXCLUDED_GRADES),
        "level_weights": {"first_year": FIRST_YEAR_WEIGHT, "other": OTHER_YEAR_WEIGHT},
    }
