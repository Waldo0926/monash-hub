"""Load curated FAQ rows, Chinese translations and, optionally, the first
moderator account.

    python -m app.knowledge.seed
    ADMIN_EMAIL=... ADMIN_PASSWORD=... ADMIN_NICKNAME=... python -m app.knowledge.seed

Idempotent: running it twice updates the same rows rather than duplicating them.
The admin account is only created when both env vars are set, so a default
password never ends up on a public server.

Run it after a crawl, not before. A translation is stored against the hash of
the English it was made from, and that hash only exists once the page has been
fetched - seeding first leaves the translations unable to tell whether they are
still current.
"""
from __future__ import annotations

import logging
import os

from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.knowledge.degrees import ZH_TITLE_OVERRIDES as ZH_DEGREE_TITLE_OVERRIDES
from app.knowledge.faq_seed import FAQ_SEEDS
from app.knowledge.titles import ZH_TITLE_OVERRIDES as ZH_UNIT_TITLE_OVERRIDES
from app.knowledge.translations_seed import TRANSLATION_SEEDS
from app.knowledge.unit_title_baseline import ZH_TITLE_BASELINE
from app.models.curriculum import Course
from app.models.handbook import Unit
from app.models.knowledge import FaqEntry, OfficialPage
from app.models.translation import (
    COURSE,
    HUMAN,
    MACHINE,
    OFFICIAL_PAGE,
    PUBLISHED,
    UNIT,
    ContentTranslation,
)
from app.models.user import User

log = logging.getLogger("seed")


def seed_faq() -> int:
    with SessionLocal() as db:
        for item in FAQ_SEEDS:
            page = db.scalar(select(OfficialPage).where(OfficialPage.slug == item.page_slug))
            entry = db.scalar(select(FaqEntry).where(FaqEntry.slug == item.slug))
            if entry is None:
                entry = FaqEntry(slug=item.slug)
                db.add(entry)
            entry.question = item.question
            entry.answer = item.answer
            entry.category = item.category
            entry.tags = list(item.tags)
            entry.keywords = list(item.keywords)
            entry.priority = item.priority
            entry.official_page_id = page.id if page else None
            entry.official_url = page.canonical_url if page else None
        db.commit()
    log.info("seeded %d FAQ entries", len(FAQ_SEEDS))
    return len(FAQ_SEEDS)


def seed_translations() -> int:
    """Write the Chinese, stamped with the hash of the English it was made from."""
    written = 0
    with SessionLocal() as db:
        hashes = dict(
            db.execute(select(OfficialPage.slug, OfficialPage.content_hash)).all()
        )
        for item in TRANSLATION_SEEDS:
            row = db.scalar(
                select(ContentTranslation).where(
                    ContentTranslation.locale == item.locale,
                    ContentTranslation.target_type == item.target_type,
                    ContentTranslation.target_key == item.target_key,
                    ContentTranslation.field == item.field,
                    ContentTranslation.provenance == HUMAN,
                )
            )
            if row is None:
                row = ContentTranslation(
                    locale=item.locale,
                    target_type=item.target_type,
                    target_key=item.target_key,
                    field=item.field,
                    provenance=HUMAN,
                )
                db.add(row)
            row.text = item.text
            row.data = {"strings": item.strings} if item.strings else None
            row.status = PUBLISHED
            row.translator = item.translator
            row.note = item.note
            # Only page translations can go stale; the global boilerplate and
            # our own FAQ have no upstream to drift from.
            row.source_hash = (
                hashes.get(item.target_key) if item.target_type == OFFICIAL_PAGE else None
            )
            if item.target_type == OFFICIAL_PAGE and item.target_key not in hashes:
                log.warning(
                    "%s has a translation but is not crawled yet - it will show as stale",
                    item.target_key,
                )
            written += 1

        # Exact reviewed degree titles are selected by their official English
        # source rather than by code.  The same award can have several campus
        # codes, and a later Handbook can assign it another one; matching the
        # source keeps the correction attached to the words that were reviewed.
        courses = db.scalars(
            select(Course).where(Course.title.in_(ZH_DEGREE_TITLE_OVERRIDES))
        ).all()
        for course in courses:
            row = db.scalar(
                select(ContentTranslation).where(
                    ContentTranslation.locale == "zh",
                    ContentTranslation.target_type == COURSE,
                    ContentTranslation.target_key == course.course_code,
                    ContentTranslation.field == "content",
                    ContentTranslation.provenance == HUMAN,
                )
            )
            if row is None:
                row = ContentTranslation(
                    locale="zh",
                    target_type=COURSE,
                    target_key=course.course_code,
                    field="content",
                    provenance=HUMAN,
                )
                db.add(row)
            strings = dict((row.data or {}).get("strings") or {})
            strings[course.title] = ZH_DEGREE_TITLE_OVERRIDES[course.title]
            row.data = {"strings": strings}
            row.status = PUBLISHED
            row.translator = "monash-hub"
            row.note = "学位名称人工校对：2026 Handbook 全目录审计"
            # An exact string map naturally expires when the English changes:
            # the old key stops matching, so no hash warning is needed.
            row.source_hash = None
            written += 1

        # Load a complete, deterministic Chinese title baseline.  It remains
        # machine provenance so the UI can label it honestly, and the reviewed
        # exact strings written immediately afterwards win on read.
        baseline_units = db.scalars(
            select(Unit).where(Unit.title.in_(ZH_TITLE_BASELINE))
        ).all()
        baseline_codes = {unit.unit_code for unit in baseline_units}
        machine_rows = {
            row.target_key: row
            for row in db.scalars(
                select(ContentTranslation).where(
                    ContentTranslation.locale == "zh",
                    ContentTranslation.target_type == UNIT,
                    ContentTranslation.target_key.in_(baseline_codes),
                    ContentTranslation.field == "content",
                    ContentTranslation.provenance == MACHINE,
                )
            ).all()
        }
        for unit in baseline_units:
            row = machine_rows.get(unit.unit_code)
            if row is None:
                row = ContentTranslation(
                    locale="zh",
                    target_type=UNIT,
                    target_key=unit.unit_code,
                    field="content",
                    provenance=MACHINE,
                )
                db.add(row)
                machine_rows[unit.unit_code] = row
            strings = dict((row.data or {}).get("strings") or {})
            strings[unit.title] = ZH_TITLE_BASELINE[unit.title]
            row.data = {"strings": strings}
            row.status = PUBLISHED
            row.translator = "google-translate-baseline"
            row.note = "课程名称完整中文基线：2026 Handbook 4,212 个唯一标题"
            row.source_hash = None
            written += 1

        # The same unit title can exist under several codes/campuses.  Attach
        # reviewed wording to the exact official English title so one fix covers
        # all variants while a future Handbook rename safely falls back to
        # English until the new wording is reviewed.
        units = db.scalars(
            select(Unit).where(Unit.title.in_(ZH_UNIT_TITLE_OVERRIDES))
        ).all()
        for unit in units:
            row = db.scalar(
                select(ContentTranslation).where(
                    ContentTranslation.locale == "zh",
                    ContentTranslation.target_type == UNIT,
                    ContentTranslation.target_key == unit.unit_code,
                    ContentTranslation.field == "content",
                    ContentTranslation.provenance == HUMAN,
                )
            )
            if row is None:
                row = ContentTranslation(
                    locale="zh",
                    target_type=UNIT,
                    target_key=unit.unit_code,
                    field="content",
                    provenance=HUMAN,
                )
                db.add(row)
            strings = dict((row.data or {}).get("strings") or {})
            strings[unit.title] = ZH_UNIT_TITLE_OVERRIDES[unit.title]
            row.data = {"strings": strings}
            row.status = PUBLISHED
            row.translator = "monash-hub"
            row.note = "课程名称人工校对：2026 Handbook 全目录翻译审计"
            row.source_hash = None
            written += 1
        db.commit()
    log.info("seeded %d translations", written)
    return written


def seed_admin() -> bool:
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    if not email or not password:
        log.info("ADMIN_EMAIL/ADMIN_PASSWORD not set - skipping admin account")
        return False
    nickname = os.getenv("ADMIN_NICKNAME", "moderator")
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(email=email, nickname=nickname, password_hash=hash_password(password))
            db.add(user)
        user.is_admin = True
        user.is_active = True
        db.commit()
    log.info("moderator account ready: %s", email)
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    seed_faq()
    seed_translations()
    seed_admin()


if __name__ == "__main__":
    main()
