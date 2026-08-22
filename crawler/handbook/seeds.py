"""The Handbook fixture set: 20 units chosen to break the parser if it is wrong.

Not a random sample. Between them these units cover a unit with no listed exam,
units with a hurdle, an empty requisite list, a deep OR-joined prerequisite
chain, Malaysia-only and multi-campus offerings, and faculties outside IT so
that field names are not accidentally FIT-specific.

Expanding past this set is a Stage 1A exit criterion, not a day-one action -
the parser has to be right on twenty pages before it is pointed at thousands.
"""
from __future__ import annotations

FIXTURE_UNITS: tuple[tuple[str, str], ...] = (
    ("FIT1008", "core CS, long prerequisite chain"),
    ("FIT1045", "introductory, multi-campus"),
    ("FIT1055", "IT professional practice, non-standard assessment"),
    ("FIT2004", "algorithms, hurdle assessment"),
    ("FIT2014", "theory unit, exam listed"),
    ("FIT2099", "OO design, multi-campus"),
    ("FIT2102", "no final exam listed, Malaysia offering"),
    ("FIT2109", "IT unit with mixed delivery"),
    ("FIT3143", "parallel computing, project heavy"),
    ("FIT3155", "advanced algorithms"),
    ("FIT3161", "final year project part 1"),
    ("FIT3162", "final year project part 2"),
    ("FIT3171", "databases"),
    ("FIT3175", "usability"),
    ("MAT1830", "maths, cross-faculty field names"),
    ("ENG1005", "engineering, different assessment vocabulary"),
    ("ECC1000", "business faculty"),
    ("BFF2140", "corporate finance, exam weighted"),
    ("ACC1100", "accounting, multi-campus"),
    ("MKC1200", "marketing, Malaysia and Australia"),
)

FIXTURE_CODES: tuple[str, ...] = tuple(code for code, _ in FIXTURE_UNITS)
