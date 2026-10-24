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
from app.handbook.parser import compute_content_hash
from app.handbook.repository import upsert_unit
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
]


def main() -> None:
    with SessionLocal() as db:
        db.execute(text("TRUNCATE units, unit_reviews RESTART IDENTITY CASCADE"))
        for record in UNITS:
            upsert_unit(db, record)
        db.commit()
    print(f"seeded {len(UNITS)} units for {YEAR}")


if __name__ == "__main__":
    main()
