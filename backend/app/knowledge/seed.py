"""Load curated FAQ rows and, optionally, the first moderator account.

    python -m app.knowledge.seed
    ADMIN_EMAIL=... ADMIN_PASSWORD=... ADMIN_NICKNAME=... python -m app.knowledge.seed

Idempotent: running it twice updates the same rows rather than duplicating them.
The admin account is only created when both env vars are set, so a default
password never ends up on a public server.
"""
from __future__ import annotations

import logging
import os

from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.knowledge.faq_seed import FAQ_SEEDS
from app.models.knowledge import FaqEntry, OfficialPage
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
    seed_admin()


if __name__ == "__main__":
    main()
