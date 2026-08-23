"""Machine-translate official content, in batches, run by hand.

    python -m app.knowledge.translate_content --what guides --dry-run
    python -m app.knowledge.translate_content --what guides
    python -m app.knowledge.translate_content --what units --limit 200
    python -m app.knowledge.translate_content --what all --restale

Deliberately not on a timer and not part of a deploy. It spends quota and it
writes content that speaks for Monash, and both are things somebody should be
watching when they happen.

Two rules about what it will not do, and they are the ones to preserve:

* **It never overwrites a person's translation.** A target that already has a
  hand-written row for the same field is skipped entirely, so the GPA page keeps
  its reviewed Chinese and does not end up labelled as machine translated.
* **It never touches anything a student wrote.** Community posts and answers are
  somebody's own words in a forum.

Every passage it writes is stamped ``method='machine'``, which is what puts the
"machine translation, not yet checked" notice and the link to the English
original on the page.

Re-running is cheap: a target that already has a current translation is not sent
again, so a second run costs only what has changed. ``--restale`` also redoes the
targets whose source has moved since they were translated.
"""
from __future__ import annotations

import argparse
import logging
import time

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.knowledge import translations
from app.knowledge.machine_translation import (
    DeepLTranslator,
    EchoTranslator,
    TranslationFailed,
    Translator,
    translate_prose,
)
from app.models.handbook import Unit
from app.models.knowledge import OfficialPage
from app.models.translation import (
    HUMAN,
    MACHINE,
    OFFICIAL_PAGE,
    PUBLISHED,
    UNIT,
    ContentTranslation,
)

log = logging.getLogger("translate-content")

# Units store their machine translation under 'prose'; official pages under
# 'body', which is the same field a hand-written page translation uses - hence
# the skip when a human row already exists.
UNIT_FIELD = "prose"
PAGE_FIELD = "body"

# Below this a "passage" is a label or a stray number, and sending it wastes
# quota for a worse result than the term dictionary already gives at display
# time.
MIN_UNIT_PASSAGE = 25
MIN_PAGE_PASSAGE = 2


class Target:
    """One thing to translate: what it is, what English it has, where it goes."""

    __slots__ = ("field", "key", "kind", "passages", "source_hash")

    def __init__(
        self, kind: str, key: str, field: str, source_hash: str | None, passages: list[str]
    ) -> None:
        self.kind = kind
        self.key = key
        self.field = field
        self.source_hash = source_hash
        self.passages = passages


def _unit_passages(unit: Unit, already: set[str]) -> list[str]:
    out: list[str] = []
    for field in ("overview", "teaching_approach", "workload_requirements",
                  "assessment_summary"):
        value = (getattr(unit, field) or "").strip()
        if not value:
            continue
        # Paragraph at a time, and skip the Handbook boilerplate that already
        # has a hand-written translation - re-translating it by machine would
        # replace better text with worse and pay for the privilege.
        for paragraph in value.split("\n\n"):
            paragraph = paragraph.strip()
            if len(paragraph) >= MIN_UNIT_PASSAGE and paragraph not in already:
                out.append(paragraph)
    for outcome in unit.learning_outcomes:
        text = (outcome.description or "").strip()
        if len(text) >= MIN_UNIT_PASSAGE and text not in already:
            out.append(text)
    return list(dict.fromkeys(out))


def _page_passages(page: OfficialPage, already: set[str]) -> list[str]:
    """Every distinct string in the page's blocks - what the swap looks up."""
    out: list[str] = []

    def add(value: str | None) -> None:
        text = (value or "").strip()
        if len(text) >= MIN_PAGE_PASSAGE and text not in already:
            out.append(text)

    for block in page.blocks or []:
        kind = block.get("type")
        if kind == "heading":
            add(block.get("text"))
        elif kind == "paragraph":
            add("".join(s.get("text", "") for s in block.get("spans") or []))
        elif kind == "list":
            for item in block.get("items") or []:
                add("".join(s.get("text", "") for s in item))
        elif kind == "table":
            add(block.get("caption"))
            for cell in block.get("columns") or []:
                add(cell)
            for row in (block.get("rows") or []) + (block.get("foot") or []):
                for cell in row:
                    add(cell)
    # A grade name appears in every table on the page; send each string once.
    return list(dict.fromkeys(out))


def _row(db: Session, locale: str, kind: str, key: str, field: str) -> ContentTranslation | None:
    return db.scalar(
        select(ContentTranslation).where(
            ContentTranslation.locale == locale,
            ContentTranslation.target_type == kind,
            ContentTranslation.target_key == key,
            ContentTranslation.field == field,
        )
    )


def _collect(
    db: Session, *, what: str, locale: str, keys: list[str] | None, limit: int, restale: bool
) -> list[Target]:
    # The shared Handbook boilerplate, so a paragraph a person has already
    # translated is never sent to a machine.
    shared = set(translations.load(db, locale, "none", "none").strings)
    targets: list[Target] = []

    def due(existing: ContentTranslation | None, source_hash: str | None) -> bool:
        if existing is None:
            return True
        if existing.method == HUMAN:
            return False  # a person got there first
        return restale and existing.source_hash != source_hash

    if what in ("guides", "all"):
        query = select(OfficialPage).where(OfficialPage.status == "ok")
        if keys:
            query = query.where(OfficialPage.slug.in_(keys))
        for page in db.scalars(query.order_by(OfficialPage.slug)):
            if not due(_row(db, locale, OFFICIAL_PAGE, page.slug, PAGE_FIELD), page.content_hash):
                continue
            passages = _page_passages(page, shared)
            if passages:
                targets.append(
                    Target(OFFICIAL_PAGE, page.slug, PAGE_FIELD, page.content_hash, passages)
                )
            if limit and len(targets) >= limit:
                return targets

    if what in ("units", "all"):
        query = select(Unit).options(selectinload(Unit.learning_outcomes))
        if keys:
            query = query.where(Unit.unit_code.in_([k.upper() for k in keys]))
        for unit in db.scalars(query.order_by(Unit.unit_code)):
            if not due(_row(db, locale, UNIT, unit.unit_code, UNIT_FIELD), unit.content_hash):
                continue
            passages = _unit_passages(unit, shared)
            if passages:
                targets.append(
                    Target(UNIT, unit.unit_code, UNIT_FIELD, unit.content_hash, passages)
                )
            if limit and len(targets) >= limit:
                return targets

    return targets


def run(
    translator: Translator,
    *,
    what: str = "all",
    locale: str = "zh",
    keys: list[str] | None = None,
    limit: int = 0,
    restale: bool = False,
    min_interval: float = 0.0,
    commit: bool = True,
) -> dict[str, int]:
    if isinstance(translator, EchoTranslator) and commit:
        # Echo returns the source, and the pipeline then swaps the glossary
        # terms into Chinese - so its output looks plausible while still being
        # English prose. Storing that would fill the table with rows that claim
        # to be translations and are not.
        raise ValueError("EchoTranslator is for dry runs; it must never be committed")

    summary = {
        "targets": 0, "passages": 0, "characters": 0,
        "repaired": 0, "leaked": 0, "failed": 0,
    }

    with SessionLocal() as db:
        targets = _collect(db, what=what, locale=locale, keys=keys, limit=limit, restale=restale)
        log.info(
            "%d targets, %d passages, %d characters",
            len(targets),
            sum(len(t.passages) for t in targets),
            sum(len(p) for t in targets for p in t.passages),
        )

        for target in targets:
            strings: dict[str, str] = {}
            for source in target.passages:
                if min_interval:
                    time.sleep(min_interval)
                try:
                    result = translate_prose(source, translator, target=locale)
                except TranslationFailed as exc:
                    summary["failed"] += 1
                    log.error("%s %s: %s", target.kind, target.key, exc)
                    continue
                strings[source] = result.text
                summary["characters"] += len(source)
                if result.repaired_terms:
                    summary["repaired"] += 1
                    log.info(
                        "%s %s: repaired %s",
                        target.kind, target.key, ", ".join(result.repaired_terms),
                    )
                if result.leaked_terms:
                    summary["leaked"] += 1
                    log.warning("%s %s: %s", target.kind, target.key, result.leaked_terms[0])

            if not strings:
                continue

            row = _row(db, locale, target.kind, target.key, target.field)
            if row is None:
                row = ContentTranslation(
                    locale=locale,
                    target_type=target.kind,
                    target_key=target.key,
                    field=target.field,
                )
                db.add(row)
            row.data = {"strings": strings}
            row.text = None
            row.status = PUBLISHED
            row.method = MACHINE
            row.translator = "deepl+glossary"
            row.note = "机器翻译，未经人工校对"
            row.source_hash = target.source_hash
            summary["targets"] += 1
            summary["passages"] += len(strings)
            log.info("%s %s: %d passages", target.kind, target.key, len(strings))

        if commit:
            db.commit()
        else:
            db.rollback()
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--what", default="all", choices=["guides", "units", "all"])
    parser.add_argument("--locale", default="zh")
    parser.add_argument("--keys", help="comma separated unit codes or guide slugs")
    parser.add_argument("--limit", type=int, default=0, help="0 means everything due")
    parser.add_argument(
        "--restale", action="store_true",
        help="also redo targets whose source changed since they were translated",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="run the pipeline with a translator that returns the source and write "
             "nothing. Needs no API key. Reports the character count a real run "
             "would send, which is the unit the quota is measured in.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    settings = get_settings()
    translator: Translator
    if args.dry_run:
        translator = EchoTranslator()
        log.warning("dry run: nothing will be sent and nothing will be written")
    else:
        translator = DeepLTranslator(settings)

    summary = run(
        translator,
        what=args.what,
        locale=args.locale,
        keys=[k.strip() for k in args.keys.split(",")] if args.keys else None,
        limit=args.limit,
        restale=args.restale,
        min_interval=0.0 if args.dry_run else settings.deepl_min_interval_seconds,
        commit=not args.dry_run,
    )
    log.info("summary: %s", summary)
    if summary["leaked"]:
        log.warning(
            "%d passages still carry a reserved term in English - grep the log for "
            "them before trusting those pages",
            summary["leaked"],
        )


if __name__ == "__main__":
    main()
