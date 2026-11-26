"""Reparse all stored active courses and areas across all loaded years.

Run once after the reference-links migration. Re-running is safe: hashing keeps
unchanged records intact, and fetch failures retain the previous valid data.
"""
import logging

from app.core.db import SessionLocal
from app.models.curriculum import AreaOfStudy, Course
from sqlalchemy import select

from crawler.handbook.audit_courses import audit
from crawler.handbook.run_courses import crawl


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    plan = []
    with SessionLocal() as db:
        for model, kind, column in ((Course, 'course', Course.course_code),
                                     (AreaOfStudy, 'aos', AreaOfStudy.aos_code)):
            rows = db.execute(select(model.academic_year, column).where(model.is_active)
                              .order_by(model.academic_year.desc(), column)).all()
            by_year = {}
            for year, code in rows:
                by_year.setdefault(year, []).append(code)
            plan.extend((kind, year, codes) for year, codes in by_year.items())
    failed = 0
    for kind, year, codes in plan:
        result = crawl(kind, codes, year, min_interval=3.0, max_withdrawals=0)
        logging.info('%s %s: %s', kind, year, result)
        failed += result['failed']
    with SessionLocal() as db:
        report = audit(db)
    logging.info('Audited %s owners, %s groups, %s elective pools, %s gaps',
                 report['owners'], report['groups'], len(report['elective_pools']),
                 len(report['gaps']))
    if failed or report['gaps']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
