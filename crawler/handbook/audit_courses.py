"""Audit every stored degree/area, including all loaded Handbook years.

Run after a forced course refresh. Emits JSON counts and actionable gaps; no
network access or writes. An open elective pool is reported, not called invalid.
"""
import json

from app.core.db import SessionLocal
from app.handbook.electives import elective_browse
from app.models.curriculum import AreaOfStudy, Course, CurriculumContainer
from sqlalchemy import select


def audit(db) -> dict:
    owners = {}
    for model, kind, code_field in ((Course, 'course', 'course_code'),
                                     (AreaOfStudy, 'aos', 'aos_code')):
        for row in db.scalars(select(model).where(model.is_active)).all():
            owners[(kind, row.id)] = {
                'kind': kind, 'code': getattr(row, code_field), 'year': row.academic_year,
                'unrefreshed_links': row.reference_links is None,
            }
    groups = db.scalars(select(CurriculumContainer)).all()
    pools, missing, seen = [], [], set()
    unstructured = []
    for group in groups:
        key = ('course', group.course_id) if group.course_id else ('aos', group.area_of_study_id)
        owner = owners.get(key)
        if owner is None:
            continue
        seen.add(key)
        scope = elective_browse(group.title, group.description)
        if scope:
            pools.append({**owner, 'part': group.title, **scope})
        if group.reference_links is None:
            missing.append({**owner, 'part': group.title, 'issue': 'references_not_refreshed'})
    for key, owner in owners.items():
        if key not in seen:
            unstructured.append(owner)
        if owner['unrefreshed_links']:
            missing.append({**owner, 'issue': 'references_not_refreshed'})
    return {'owners': len(owners), 'groups': len(groups), 'elective_pools': pools, 'gaps': missing,
            'unstructured': unstructured}


def main() -> None:
    with SessionLocal() as db:
        result = audit(db)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result['gaps']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
