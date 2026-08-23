"""Machine-translate unit descriptions, in batches, by hand.

    python -m app.knowledge.translate_units --dry-run          # no API key needed
    python -m app.knowledge.translate_units --limit 50
    python -m app.knowledge.translate_units --units FIT1008,FIT2102
    python -m app.knowledge.translate_units --restale          # redo changed units

Deliberately not on a timer and not part of a deploy. It spends money, it writes
content that speaks for Monash, and both of those are things somebody should be
watching when they happen.

What it does per unit: takes the four descriptive fields, protects the glossary
terms, sends them to the configured translator, restores the terms, checks the
output, and writes one `content_translations` row with `method='machine'`
stamped with the unit's current content hash. A unit whose output fails the
glossary check is **skipped and counted**, not stored - it keeps its English.

Re-running is safe. A unit that already has a current translation is not sent
again, so the cost of a second run is the cost of the units that changed.
"""
from __future__ import annotations

import argparse
import logging
import time

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.knowledge.glossary import GlossaryViolation
from app.knowledge.machine_translation import (
    DeepLTranslator,
    EchoTranslator,
    TranslationFailed,
    Translator,
    translate_prose,
)
from app.models.handbook import Unit
from app.models.translation import MACHINE, PUBLISHED, UNIT, ContentTranslation

log = logging.getLogger("translate-units")

# Written as one row per unit holding a string map, matching how a hand-written
# page translation is stored: the serialiser already knows how to apply one.
FIELD = "prose"


def _passages(unit: Unit) -> dict[str, str]:
    """The English this unit has that is worth translating, keyed by itself."""
    passages: dict[str, str] = {}
    for field in ("overview", "teaching_approach", "workload_requirements"):
        value = (getattr(unit, field) or "").strip()
        if not value:
            continue
        # Paragraph at a time: the Handbook's boilerplate paragraphs already
        # have hand-written translations, and re-translating them by machine
        # would overwrite better text with worse.
        for paragraph in value.split("\n\n"):
            paragraph = paragraph.strip()
            if len(paragraph) >= 40:
                passages[paragraph] = paragraph
    for outcome in unit.learning_outcomes:
        text = (outcome.description or "").strip()
        if len(text) >= 40:
            passages[text] = text
    return passages


def _existing(db: Session, unit_code: str, locale: str) -> ContentTranslation | None:
    return db.scalar(
        select(ContentTranslation).where(
            ContentTranslation.locale == locale,
            ContentTranslation.target_type == UNIT,
            ContentTranslation.target_key == unit_code,
            ContentTranslation.field == FIELD,
        )
    )


def _units_to_do(
    db: Session, *, locale: str, codes: list[str] | None, limit: int, restale: bool
) -> list[Unit]:
    query = select(Unit).options(selectinload(Unit.learning_outcomes))
    if codes:
        query = query.where(Unit.unit_code.in_([c.upper() for c in codes]))
    query = query.order_by(Unit.unit_code)

    chosen: list[Unit] = []
    for unit in db.scalars(query):
        row = _existing(db, unit.unit_code, locale)
        # Already done, and still current unless the Handbook moved.
        if row is not None and (not restale or row.source_hash == unit.content_hash):
            continue
        if not _passages(unit):
            continue
        chosen.append(unit)
        if limit and len(chosen) >= limit:
            break
    return chosen


def run(
    translator: Translator,
    *,
    locale: str = "zh",
    codes: list[str] | None = None,
    limit: int = 0,
    restale: bool = False,
    min_interval: float = 0.0,
    commit: bool = True,
) -> dict[str, int]:
    if isinstance(translator, EchoTranslator) and commit:
        # Echo returns the source, and the pipeline then swaps the glossary
        # terms into Chinese - so its output passes every check while still
        # being English prose. Storing that would fill the table with rows that
        # claim to be translations and are not.
        raise ValueError("EchoTranslator is for dry runs; it must never be committed")

    summary = {"units": 0, "passages": 0, "rejected": 0, "failed": 0}

    with SessionLocal() as db:
        units = _units_to_do(db, locale=locale, codes=codes, limit=limit, restale=restale)
        log.info("%d units to translate", len(units))

        for unit in units:
            strings: dict[str, str] = {}
            for source in _passages(unit):
                if min_interval:
                    time.sleep(min_interval)
                try:
                    strings[source] = translate_prose(source, translator, target=locale)
                except GlossaryViolation as exc:
                    # The one failure worth being loud about: the protection
                    # did not hold, and storing this would be storing a term
                    # rendered the way this platform must not render it.
                    summary["rejected"] += 1
                    log.warning("%s: rejected a passage - %s", unit.unit_code, exc)
                except TranslationFailed as exc:
                    summary["failed"] += 1
                    log.error("%s: %s", unit.unit_code, exc)

            if not strings:
                continue

            row = _existing(db, unit.unit_code, locale)
            if row is None:
                row = ContentTranslation(
                    locale=locale, target_type=UNIT, target_key=unit.unit_code, field=FIELD
                )
                db.add(row)
            row.data = {"strings": strings}
            row.text = None
            row.status = PUBLISHED
            row.method = MACHINE
            row.translator = "deepl+glossary"
            row.note = "机器翻译，未经人工校对"
            row.source_hash = unit.content_hash
            summary["units"] += 1
            summary["passages"] += len(strings)
            log.info("%s: %d passages", unit.unit_code, len(strings))

        if commit:
            db.commit()
        else:
            db.rollback()
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", default="zh")
    parser.add_argument("--units", help="comma separated unit codes")
    parser.add_argument("--limit", type=int, default=0, help="0 means every unit that is due")
    parser.add_argument(
        "--restale", action="store_true",
        help="also redo units whose Handbook entry changed since they were translated",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="run the whole pipeline with a translator that returns the source, and "
             "write nothing. Needs no API key, and is how you check the selection.",
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
        log.warning("dry run: nothing will be translated and nothing will be written")
    else:
        translator = DeepLTranslator(settings)

    summary = run(
        translator,
        locale=args.locale,
        codes=[c.strip() for c in args.units.split(",")] if args.units else None,
        limit=args.limit,
        restale=args.restale,
        min_interval=0.0 if args.dry_run else settings.deepl_min_interval_seconds,
        commit=not args.dry_run,
    )
    log.info("summary: %s", summary)


if __name__ == "__main__":
    main()
