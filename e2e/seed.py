"""Load the handful of synthetic units the browser tests run against.

Run after ``alembic upgrade head``, against a database that holds
nothing else: it empties the Handbook and rating tables first, so a rerun starts
from the same state. The units are invented in the same way as the parser
fixtures in backend/tests: real-looking codes and periods, no Handbook text.

    python e2e/seed.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.core.db import SessionLocal
from app.handbook.course_repository import upsert_course
from app.handbook.parser import compute_content_hash
from app.handbook.repository import upsert_unit
from app.knowledge import teach_out
from app.knowledge.repository import get_or_create_source, upsert_seed_page
from sqlalchemy import text

YEAR = 2026
S1 = "First semester"
S2 = "Second semester"


def offering(campus: str, period: str) -> dict:
    prefix = {"Malaysia": "MY", "Clayton": "CL"}[campus]
    short = {S1: "S1", S2: "S2"}[period]
    return {
        "offering_code": f"{prefix}-{short}",
        "display_name": f"{campus} {short}",
        "campus": campus,
        "teaching_period": period,
        "attendance_mode": "On-campus",
        "study_level": "Undergraduate",
        "offered": True,
    }


def requires(*codes: str) -> list[dict]:
    return [{
        "requisite_type": "prerequisite",
        "connector": "AND",
        "title": None,
        "description": None,
        "raw_text": None,
        "order_index": 0,
        "groups": [],
        "items": [
            {
                "item_code": code,
                "item_name": code,
                "item_type": "subject",
                "item_url": f"https://handbook.monash.edu/{YEAR}/units/{code}",
                "credit_points": 6,
                "order_index": index,
            }
            for index, code in enumerate(codes)
        ],
    }]


def assessment(number: int, name: str, weight: str) -> dict:
    return {
        "number": number, "name": name, "assessment_type": name, "weight": weight,
        "hurdle": None, "description": None, "learning_outcomes": None, "offering_scope": None,
    }


def unit(code: str, title: str, offerings: list[dict], *,
         prerequisites: tuple[str, ...] = ()) -> dict:
    record = {
        "unit_code": code,
        "academic_year": YEAR,
        "title": title,
        "credit_points": "6",
        "level": None,
        "faculty": "Faculty of Information Technology",
        "school": None,
        "subject_prefix": code[:3],
        "source_url": f"https://handbook.monash.edu/{YEAR}/units/{code}",
        "overview": f"Synthetic overview for {code}, written for the browser tests.",
        "areas_of_study": None,
        "teaching_approach": None,
        "workload_requirements": None,
        "assessment_summary": None,
        "assessment_static_text": None,
        "handbook_version": None,
        "sca_band": None,
        "study_abroad": None,
        "offerings": offerings,
        "assessments": [assessment(1, "Assignment", "40"), assessment(2, "Examination", "60")],
        "has_exam": True,
        "requisite_groups": requires(*prerequisites) if prerequisites else [],
        "learning_outcomes": [],
        "activities": [],
        "learning_resources": None,
    }
    record["content_hash"] = compute_content_hash(record)
    return record


UNITS = [
    unit("FIT1008", "Synthetic introduction to computer science",
         [offering("Malaysia", S1), offering("Malaysia", S2), offering("Clayton", S1)]),
    unit("FIT2004", "Synthetic algorithms and data structures",
         [offering("Malaysia", S1), offering("Malaysia", S2)], prerequisites=("FIT1008",)),
    unit("FIT2102", "Synthetic programming paradigms",
         [offering("Malaysia", S2), offering("Clayton", S2)]),
    unit("FIT2085", "Synthetic systems programming",
         [offering("Malaysia", S1)], prerequisites=("FIT1008",)),
]


def course_item(code: str, title: str) -> dict:
    return {
        "item_code": code, "item_name": title, "item_type": "unit",
        "item_url": f"https://handbook.monash.edu/{YEAR}/units/{code}",
        "credit_points": 6, "connector": None,
    }


#: One synthetic degree, so the course map has a structure to score and the
#: add-unit dialog has a list to offer. Part A names three of the units above;
#: Part B is a free elective part, which lists nothing.
COURSE = {
    "course_code": "C9001",
    "academic_year": YEAR,
    "title": "Synthetic Bachelor of Testing",
    "abbreviated_name": "BTest",
    "credit_points": 144,
    "cricos_code": None,
    "aqf_level": "Level 7 - Bachelor Degree",
    "course_type": "UG specialist",
    "faculty": "Faculty of Information Technology",
    "school": None,
    "campuses": ["Malaysia", "Clayton"],
    "duration_years": 3,
    "overview": "A synthetic degree, written for the browser tests.",
    "structure_text": None,
    "requirements_text": None,
    "handbook_version": None,
    "source_url": f"https://handbook.monash.edu/{YEAR}/courses/C9001",
    "content_hash": "e2e-C9001",
    "containers": [
        {
            "title": "Part A. Synthetic core", "description": None, "footnote": None,
            "credit_points": 18, "credit_points_max": None, "connector": None,
            "items": [
                course_item("FIT1008", "Synthetic introduction to computer science"),
                course_item("FIT2004", "Synthetic algorithms and data structures"),
                course_item("FIT2085", "Synthetic systems programming"),
            ],
            "containers": [],
        },
        {
            "title": "Part B. Free electives",
            "description": "Any units from across the University.",
            "footnote": None, "credit_points": 126, "credit_points_max": None, "connector": None,
            "items": [], "containers": [],
        },
    ],
}


HEADER = ["Unit Code", "Unit Title", "Change", "Course", "Teach out plan"]

#: The two faculty teach-out tables, one per campus, with invented replacements.
#: They disagree on purpose: FIT2004 closes on different dates, and FIT2102 is on
#: the Australian list only.
TEACH_OUT = [
    (teach_out.SOURCES[0], "https://www.monash.edu/it/e2e-teach-out", "australia", [
        HEADER,
        ["FIT2004", "Synthetic algorithms", "No longer offered", "BCS",
         "Replace with FIT3901 (S1 and S2)"],
        ["FIT2102", "Synthetic paradigms", "Final offering S2 2026", "BCS",
         "Replace with FIT3902 from 2027"],
    ]),
    (teach_out.SOURCES[1], "https://www.monash.edu.my/it/e2e-teach-out", "malaysia", [
        HEADER,
        ["FIT2004", "Synthetic algorithms", "Final offering S2 2026", "BCS",
         "Replace with FIT3901 from 2027 (S1)"],
    ]),
]


def seed_teach_out(db) -> None:
    for slug, url, campus, rows in TEACH_OUT:
        source = get_or_create_source(db, "monash-students", "Monash University",
                                      "https://www.monash.edu")
        page = upsert_seed_page(
            db, source=source, slug=slug, url=url, title=f"IT teach-out ({campus})",
            category="enrolment", tags=[], refresh_tier="dynamic", applies_to=campus,
        )
        page.blocks = [{"type": "table", "rows": rows}]
        page.status = "ok"
        page.content_hash = f"e2e-{slug}"


def main() -> None:
    with SessionLocal() as db:
        db.execute(text(
            "TRUNCATE units, unit_reviews, courses, areas_of_study RESTART IDENTITY CASCADE"
        ))
        for record in UNITS:
            upsert_unit(db, record)
        upsert_course(db, COURSE)
        seed_teach_out(db)
        db.commit()
    print(f"seeded {len(UNITS)} units and 1 course for {YEAR}")


if __name__ == "__main__":
    main()
