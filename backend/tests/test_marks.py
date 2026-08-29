"""WAM and GPA, checked against Monash's own worked examples.

Both examples are transcribed from the tables on the pages the crawler already
indexes - `guides/wam` and `guides/gpa` - so if Monash changes a weighting the
crawl surfaces it and these tests are where the change has to be made explicit.
"""
from __future__ import annotations

import pytest
from app.knowledge.marks import (
    AUSTRALIA,
    MALAYSIA,
    Entry,
    MarkError,
    gpa,
    grade_for_mark,
    mark_needed,
    round_mark,
    wam,
)

# The nine units in the official WAM example, with the year levels and marks
# exactly as the table gives them. MON2002 is a withdrawn fail with no mark.
OFFICIAL_WAM_EXAMPLE = [
    Entry("MON1001", 6, level=1, mark=63),
    Entry("MON1002", 12, level=1, mark=80),
    Entry("MON1003", 6, level=1, mark=40),
    Entry("MON1004", 6, level=1, mark=85),
    Entry("MON2001", 24, level=2, mark=96),
    Entry("MON2002", 6, level=2, grade="WN"),
    Entry("MON3001", 6, level=3, mark=65),
    Entry("MON3002", 6, level=3, mark=77),
    Entry("MON4001", 6, level=4, mark=82),
]


def test_the_official_wam_example():
    """Monash's own table: weighted marks total 4692 over 63 weighted points."""
    assert wam(OFFICIAL_WAM_EXAMPLE) == pytest.approx(4692 / 63, abs=1e-9)
    assert wam(OFFICIAL_WAM_EXAMPLE) == pytest.approx(74.476, abs=0.001)


def test_each_row_of_the_official_wam_example():
    """Row by row, because a single total can hide two errors cancelling out."""
    expected = {          # unit: (weighted mark, weighted credit points)
        "MON1001": (189, 3), "MON1002": (480, 6), "MON1003": (120, 3),
        "MON1004": (255, 3), "MON2001": (2304, 24), "MON2002": (0, 6),
        "MON3001": (390, 6), "MON3002": (462, 6), "MON4001": (492, 6),
    }
    for entry in OFFICIAL_WAM_EXAMPLE:
        weight = entry.credit_points * entry.level_weight
        mark = 0 if entry.grade == "WN" else entry.mark
        assert (mark * weight, weight) == expected[entry.unit_code], entry.unit_code


def test_a_fail_is_counted_at_its_actual_mark():
    """MON1003 scored 40 and is in the average at 40.

    Dropping it is the mistake that makes a homemade calculator flatter you.
    """
    without_the_fail = [e for e in OFFICIAL_WAM_EXAMPLE if e.unit_code != "MON1003"]
    assert wam(without_the_fail) > wam(OFFICIAL_WAM_EXAMPLE)


def test_a_withdrawn_fail_is_zero_and_stays_in_the_denominator():
    """This is what makes a WN expensive: no marks in, full weight out."""
    dropped = [e for e in OFFICIAL_WAM_EXAMPLE if e.unit_code != "MON2002"]
    assert wam(dropped) > wam(OFFICIAL_WAM_EXAMPLE)
    # And its weight really is in the bottom - removing it changes the divisor
    # by exactly its weighted credit points.
    assert wam(dropped) == pytest.approx(4692 / 57, abs=1e-9)


def test_a_first_year_unit_is_halved_in_both_halves():
    """Halving only the numerator turns a 90 into a 45. It must do neither."""
    one_unit = [Entry("MON1001", 6, level=1, mark=90)]
    assert wam(one_unit) == pytest.approx(90.0)


def test_the_level_is_the_units_not_the_year_you_took_it():
    """A Level 1 unit taken in third year still weights 0.5."""
    assert Entry("MON1001", 6, level=1).level_weight == 0.5
    assert Entry("MON2001", 6, level=2).level_weight == 1.0
    assert Entry("MON5001", 6, level=5).level_weight == 1.0


# --- GPA ------------------------------------------------------------------

OFFICIAL_GPA_EXAMPLE = [
    Entry("MON1001", 6, level=1, mark=63),    # C
    Entry("MON1002", 12, level=1, mark=80),   # HD
    Entry("MON1003", 6, level=1, grade="N"),
    Entry("MON1004", 6, level=1, mark=85),    # HD
    Entry("MON2001", 24, level=2, mark=96),   # HD
    Entry("MON2002", 6, level=2, grade="WN"),
    Entry("MON3001", 6, level=3, mark=52),    # P
    Entry("MON3002", 6, level=3, mark=77),    # D
    Entry("MON4001", 6, level=4, mark=82),    # HD
]


def test_the_official_gpa_example():
    """Monash's table totals 229.8 over 78 credit points."""
    assert gpa(OFFICIAL_GPA_EXAMPLE) == pytest.approx(229.8 / 78, abs=1e-9)
    assert gpa(OFFICIAL_GPA_EXAMPLE) == pytest.approx(2.946, abs=0.001)


def test_gpa_does_not_use_the_level_weight():
    """Only WAM weights by level. Applying it to GPA is a quiet mistake."""
    first_year = [Entry("MON1001", 6, level=1, mark=85)]
    later_year = [Entry("MON3001", 6, level=3, mark=85)]
    assert gpa(first_year) == gpa(later_year) == 4.0


def test_malaysia_is_a_different_scale_not_a_rounding_difference():
    """Credit is 2.0 in Australia and 2.85 in Malaysia."""
    credit = [Entry("MON1001", 6, level=1, mark=63)]
    assert gpa(credit, AUSTRALIA) == pytest.approx(2.0)
    assert gpa(credit, MALAYSIA) == pytest.approx(2.85)


def test_the_official_cgpa_example():
    """Same nine units, the Malaysian scale.

    The total is the sum of the weighted values in the official CGPA table:
    17.1 + 48 + 6.9 + 24 + 96 + 0 + 12.9 + 22.02 + 24 = 250.92 over 78.
    """
    weighted = 17.1 + 48.0 + 6.9 + 24.0 + 96.0 + 0.0 + 12.9 + 22.02 + 24.0
    assert weighted == pytest.approx(250.92)
    assert gpa(OFFICIAL_GPA_EXAMPLE, MALAYSIA) == pytest.approx(weighted / 78, abs=1e-9)


@pytest.mark.parametrize("grade", ["SFR", "NE", "NAS", "WI", "PGO", "NPGO", "WNGO"])
def test_an_excluded_grade_leaves_both_averages_untouched(grade):
    base = [Entry("MON1001", 6, level=1, mark=63)]
    with_excluded = [*base, Entry("MON9999", 6, level=1, grade=grade)]
    assert gpa(with_excluded) == gpa(base)
    assert wam(with_excluded) == wam(base)


# --- marks and grades -----------------------------------------------------

@pytest.mark.parametrize(
    "mark,grade",
    [(100, "HD"), (80, "HD"), (79, "D"), (70, "D"), (69, "C"), (60, "C"),
     (59, "P"), (50, "P"), (49, "NP"), (45, "NP"), (44, "N"), (0, "N")],
)
def test_the_mark_bands(mark, grade):
    assert grade_for_mark(mark) == grade


def test_monash_rounds_the_mark_before_grading_it():
    """79.51 is an 80 and an HD, which the official page states outright."""
    assert round_mark(79.51) == 80
    assert grade_for_mark(79.51) == "HD"
    # And 79.5 rounds up too - Python's banker's rounding would say 80 here but
    # 78 for 78.5, which is not what a transcript shows.
    assert round_mark(78.5) == 79
    assert grade_for_mark(79.49) == "D"


def test_a_mark_outside_the_scale_is_refused():
    for bad in (-1, 101, 150):
        with pytest.raises(MarkError):
            grade_for_mark(bad)


def test_an_unknown_grade_is_refused_rather_than_scored_as_zero():
    with pytest.raises(MarkError):
        gpa([Entry("MON1001", 6, level=1, grade="ZZ")])


# --- the question students actually ask -----------------------------------

def test_what_do_i_need_this_semester():
    done = [Entry("MON1001", 6, level=2, mark=68)]
    planned = [Entry("MON2001", 6, level=2)]
    # Two equal-weight units averaging 70 means the second must be 72.
    assert mark_needed(done, planned, 70) == pytest.approx(72.0)


def test_an_unreachable_target_says_so_by_exceeding_one_hundred():
    """Better than clamping to 100 and implying it is achievable."""
    done = [Entry("MON1001", 24, level=2, mark=50)]
    planned = [Entry("MON2001", 6, level=2)]
    assert mark_needed(done, planned, 80) > 100


def test_a_target_already_secured_comes_back_below_zero():
    """24 points at 95 with 6 to go: a 75 average survives even a zero."""
    done = [Entry("MON1001", 24, level=2, mark=95)]
    planned = [Entry("MON2001", 6, level=2)]
    assert mark_needed(done, planned, 75) < 0
    # 76 is the exact break-even: it needs precisely zero.
    assert mark_needed(done, planned, 76) == pytest.approx(0.0)


def test_nothing_planned_has_no_answer():
    assert mark_needed([Entry("MON1001", 6, level=2, mark=68)], [], 70) is None


def test_a_first_year_unit_moves_the_wam_half_as_much():
    done = [Entry("MON2001", 6, level=2, mark=60)]
    heavy = mark_needed(done, [Entry("MON2002", 6, level=2)], 70)
    light = mark_needed(done, [Entry("MON1002", 6, level=1)], 70)
    # The Level 1 unit carries half the weight, so it has to score higher.
    assert light > heavy


def test_an_empty_transcript_has_no_average():
    assert wam([]) is None
    assert gpa([]) is None
