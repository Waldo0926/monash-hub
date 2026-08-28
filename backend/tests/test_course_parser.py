"""Courses and areas of study, parsed and stored.

The fixtures are real pages: C2001 because it is the course the graph was built
against, and DATASCI11 because an area of study publishes the same structure one
level down and the parser has to read both with one function.
"""
from __future__ import annotations

import pytest
from app.handbook.course_parser import (
    aos_url,
    course_url,
    parse_aos_page,
    parse_course_page,
)
from app.handbook.course_repository import upsert_area_of_study, upsert_course
from app.models.curriculum import CurriculumContainer, CurriculumItem


@pytest.fixture
def course(handbook_html):
    return parse_course_page(handbook_html("course-C2001"), course_url("C2001", 2026))


@pytest.fixture
def aos(handbook_html):
    return parse_aos_page(handbook_html("aos-DATASCI11"), aos_url("DATASCI11", 2026))


def test_a_course_carries_what_a_student_chooses_it_by(course):
    assert course["course_code"] == "C2001"
    assert course["title"] == "Bachelor of Computer Science"
    assert course["credit_points"] == 144
    assert course["aqf_level"] == "Level 7 - Bachelor Degree"


def test_the_campuses_come_from_the_list_not_the_sentence(course):
    """Whether Malaysia teaches a degree is the first thing our reader needs."""
    assert set(course["campuses"]) == {"Clayton", "Malaysia"}


def test_the_duration_is_the_full_time_one(course):
    """``maximum_duration`` is 8 - the longest a part-time student may take.

    Printed as the duration it would tell every reader that a three-year
    bachelor takes eight years.
    """
    assert course["duration_years"] == 3


def test_the_parts_are_in_the_order_the_handbook_numbers_them(course):
    """C2001 publishes Part D at order 300 and Part A at 100.

    Read in payload order, the degree starts with its capstone.
    """
    titles = [c["title"] for c in course["containers"]]
    assert titles[0].startswith("Part A")
    assert titles == sorted(titles)


def test_a_group_of_groups_stays_nested(course):
    """Part D is "one of the following options", each option a group of units.

    Flattened, the five options read as one list of eleven units you must all
    pass - a different, and unfinishable, degree.
    """
    part_d = next(c for c in course["containers"] if c["title"].startswith("Part D"))
    assert part_d["items"] == []
    assert len(part_d["containers"]) == 5
    project = next(c for c in part_d["containers"] if "Algorithms" in c["title"])
    assert [i["item_code"] for i in project["items"]] == ["FIT3161", "FIT3162"]


def test_a_requirement_can_point_at_a_specialisation_not_only_a_unit(course):
    part_c = next(c for c in course["containers"] if c["title"].startswith("Part C"))
    kinds = {i["item_type"] for i in part_c["items"]}
    assert kinds == {"specialisation"}
    assert "DATASCI11" in {i["item_code"] for i in part_c["items"]}


def test_an_area_of_study_parses_with_the_same_function(aos):
    assert aos["aos_code"] == "DATASCI11"
    assert aos["aos_type"] == "UG specialisation"
    assert aos["credit_points"] == 36
    core = next(c for c in aos["containers"] if c["title"] == "Core units")
    assert core["credit_points"] == 24
    assert all(i["item_type"] == "unit" for i in core["items"])


def test_storing_a_course_keeps_the_tree(db, course):
    stored, outcome = upsert_course(db, course)
    db.commit()
    assert outcome == "new"

    roots = db.query(CurriculumContainer).filter_by(course_id=stored.id).all()
    assert next(r.title for r in roots).startswith("Part A")

    part_d = next(r for r in roots if r.title.startswith("Part D"))
    assert part_d.items == []
    assert len(part_d.children) == 5
    # A child carries the owner too, so the whole tree is one query - but it is
    # not a root, so it does not appear twice in the course's own list.
    assert all(child.course_id == stored.id for child in part_d.children)
    assert all(child.parent_id == part_d.id for child in part_d.children)


def test_restoring_an_unchanged_course_writes_nothing_new(db, course):
    upsert_course(db, course)
    db.commit()
    before = db.query(CurriculumContainer).count()

    _, outcome = upsert_course(db, course)
    db.commit()
    assert outcome == "unchanged"
    assert db.query(CurriculumContainer).count() == before


def test_a_changed_structure_replaces_the_old_one(db, course):
    """A requirement group has no id across versions, so it is replaced.

    Diffing on title and position would reparent a group the moment the
    Handbook inserts a Part between two others.
    """
    upsert_course(db, course)
    db.commit()

    trimmed = dict(course)
    trimmed["containers"] = course["containers"][:1]
    trimmed["content_hash"] = "different"
    upsert_course(db, trimmed)
    db.commit()

    assert db.query(CurriculumItem).count() > 0
    titles = [
        c.title
        for c in db.query(CurriculumContainer).filter(
            CurriculumContainer.parent_id.is_(None)
        )
    ]
    assert titles == [course["containers"][0]["title"]]


def test_storing_an_area_of_study_keeps_its_tree(db, aos):
    stored, outcome = upsert_area_of_study(db, aos)
    db.commit()
    assert outcome == "new"
    roots = db.query(CurriculumContainer).filter_by(area_of_study_id=stored.id).all()
    assert {r.title for r in roots} == {"Core units", "Level 3 elective units"}


def test_a_double_degree_carries_two_aqf_levels(db):
    """B6043 concatenates two, at 79 characters, and the column was 64.

    The crawl died on it mid-run rather than skipping the row, because a
    DataError is not a ParseError and nothing above caught it. The column is
    wider now; this pins the width so a narrowing does not pass review.
    """
    from app.models.curriculum import Course

    long_level = (
        "Level 9 - Master's Degree (Coursework) / Level 9 - Master's Degree (Coursework)"
    )
    assert len(long_level) > 64
    db.add(
        Course(
            course_code="B6043", academic_year=2026, title="Double degree",
            aqf_level=long_level, campuses=["Clayton"],
            source_url="https://handbook.monash.edu/2026/courses/B6043",
            content_hash="hash-b6043",
        )
    )
    db.commit()
    assert db.query(Course).filter_by(course_code="B6043").one().aqf_level == long_level
