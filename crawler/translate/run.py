"""Fill the translation table by machine.

    python -m crawler.translate.run --locale zh --targets official
    python -m crawler.translate.run --locale zh --targets units --fields short
    python -m crawler.translate.run --locale zh --targets units --fields all
    python -m crawler.translate.run --locale zh --targets all

Everything it writes is marked ``provenance='machine'``. A human row for the
same target wins on read, so re-running this can never overwrite somebody's
work, and translating a page by hand later simply takes precedence.

``--fields short`` is titles and the enumerable values - campus, teaching
period, assessment type. That is what a reader sees on the home page, in search
results and in a unit header, and it finishes in minutes. ``all`` adds the long
prose (overviews, learning outcomes, workload) and takes about an hour for a
full year of units on eight cores.

The work is idempotent and hash-keyed: a unit whose English has not changed
since it was last translated is skipped.
"""
from __future__ import annotations

import argparse
import logging
import time

from app.core.db import SessionLocal
from app.knowledge.glossary import LOCALES
from app.models.handbook import Unit
from app.models.knowledge import FaqEntry, OfficialPage
from app.models.translation import (
    FAQ_ENTRY,
    MACHINE,
    OFFICIAL_PAGE,
    PUBLISHED,
    UNIT,
    ContentTranslation,
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawler.translate.engine import Translator, quieten

log = logging.getLogger("crawler.translate")

TRANSLATOR_NAME = "machine:argos+glossary"
PROGRESS_EVERY = 100


# --- collecting the English ------------------------------------------------

def unit_strings(unit: Unit, *, long_prose: bool) -> list[str]:
    """Every string on a unit page worth translating, longest job last."""
    strings: list[str | None] = [unit.title, unit.level, unit.faculty, unit.school]

    for offering in unit.offerings:
        strings += [offering.campus, offering.teaching_period, offering.attendance_mode]
    for assessment in unit.assessments:
        strings += [assessment.name, assessment.assessment_type, assessment.hurdle]
    for activity in unit.activities:
        strings += [activity.activity_type, activity.name]
    for group in unit.requisite_groups:
        strings.append(group.description)
        # The names the Handbook gives the units it points at. Historical
        # titles, sometimes: worth translating, not worth replacing.
        strings += [item.item_name for item in group.items]

    if long_prose:
        for field in (
            unit.overview,
            unit.workload_requirements,
            unit.assessment_summary,
            unit.teaching_approach,
            unit.areas_of_study,
        ):
            strings += _paragraphs(field)
        for outcome in unit.learning_outcomes:
            strings += _paragraphs(outcome.description)
        for assessment in unit.assessments:
            strings += _paragraphs(assessment.description)

    return [s for s in strings if s and s.strip()]


def _paragraphs(text: str | None) -> list[str]:
    """The whole field and, when it has several, each paragraph.

    Both, because ``Translation.field`` tries the whole string first and falls
    back to paragraphs - and because paragraphs are what repeats across units.
    """
    if not text or not text.strip():
        return []
    whole = text.strip()
    parts = [p.strip() for p in whole.split("\n\n") if p.strip()]
    return [whole, *parts] if len(parts) > 1 else [whole]


def page_strings(page: OfficialPage) -> list[str]:
    """Every string a guide page renders: title, summary, and the blocks."""
    strings: list[str | None] = [page.title, page.summary]
    for block in page.blocks or []:
        kind = block.get("type")
        if kind == "heading":
            strings.append(block.get("text"))
        elif kind == "paragraph":
            strings.append(_join(block.get("spans")))
        elif kind == "list":
            strings += [_join(item) for item in block.get("items") or []]
        elif kind == "table":
            strings.append(block.get("caption"))
            strings += list(block.get("columns") or [])
            for row in (block.get("rows") or []) + (block.get("foot") or []):
                strings += list(row)
    return [s for s in strings if s and s.strip()]


def _join(spans: list[dict] | None) -> str:
    return "".join(s.get("text", "") for s in spans or []).strip()


# --- writing ---------------------------------------------------------------

def store(db, *, locale: str, target_type: str, target_key: str,
          strings: dict[str, str], source_hash: str | None, scope: str = "") -> None:
    """Upsert the machine row for one target."""
    if not strings:
        return
    row = db.scalar(
        select(ContentTranslation).where(
            ContentTranslation.locale == locale,
            ContentTranslation.target_type == target_type,
            ContentTranslation.target_key == target_key,
            ContentTranslation.field == "content",
            ContentTranslation.provenance == MACHINE,
        )
    )
    if row is None:
        row = ContentTranslation(
            locale=locale,
            target_type=target_type,
            target_key=target_key,
            field="content",
            provenance=MACHINE,
        )
        db.add(row)
    row.data = {"strings": strings}
    # The source hash is the unit's own, unchanged: `load_many` compares it
    # against the current one to decide whether to warn that the English has
    # moved on. Anything appended here would make every translation look stale.
    row.source_hash = source_hash
    row.status = PUBLISHED
    row.translator = TRANSLATOR_NAME
    row.note = scope or None


def _up_to_date(
    db, locale: str, target_type: str, target_key: str, source_hash: str, scope: str = ""
) -> bool:
    """Whether this target already has a machine translation of this English.

    ``scope`` is part of the answer: a unit translated with ``--fields short``
    is up to date for short and not for ``all``, even though the English behind
    it has not moved.
    """
    stored = db.execute(
        select(ContentTranslation.source_hash, ContentTranslation.note).where(
            ContentTranslation.locale == locale,
            ContentTranslation.target_type == target_type,
            ContentTranslation.target_key == target_key,
            ContentTranslation.field == "content",
            ContentTranslation.provenance == MACHINE,
        )
    ).one_or_none()
    return bool(stored) and stored[0] == source_hash and (stored[1] or "") == scope


# --- the passes ------------------------------------------------------------

def _shard(value: str) -> tuple[int, int]:
    """Parse ``K/N``. Rejects the off-by-one that would silently skip units."""
    try:
        index, count = (int(part) for part in value.split("/", 1))
    except ValueError:
        raise argparse.ArgumentTypeError(f"--shard wants K/N, got {value!r}") from None
    if count < 1 or not 0 <= index < count:
        raise argparse.ArgumentTypeError(f"--shard {value} is not a shard of a whole")
    return index, count


def translate_units(translator: Translator, *, long_prose: bool, limit: int, refresh: bool,
                    shard: tuple[int, int] = (0, 1)) -> dict:
    locale = translator.locale
    summary = {"translated": 0, "skipped": 0, "strings": 0}
    started = time.monotonic()

    with SessionLocal() as db:
        codes = list(db.scalars(select(Unit.unit_code).order_by(Unit.unit_code)))
        # One process translating five thousand units with the long prose takes
        # most of a day, and the model is capped at a core and a half. Splitting
        # the list lets several run at once on different units; they share
        # nothing but the database, and each row is written by exactly one of
        # them. Interleaved rather than blocked, so every shard sees the same
        # mixture of long and short units and they finish together.
        index, count = shard
        if count > 1:
            codes = codes[index::count]
        if limit:
            codes = codes[:limit]

        for index, code in enumerate(codes, start=1):
            unit = db.scalar(
                select(Unit).where(Unit.unit_code == code).options(
                    selectinload(Unit.offerings),
                    selectinload(Unit.assessments),
                    selectinload(Unit.activities),
                    selectinload(Unit.learning_outcomes),
                    selectinload(Unit.requisite_groups),
                )
            )
            if unit is None:
                continue
            scope = "fields=all" if long_prose else "fields=short"
            if not refresh and _up_to_date(db, locale, UNIT, code, unit.content_hash, scope):
                summary["skipped"] += 1
                continue

            strings = translator.many(unit_strings(unit, long_prose=long_prose))
            store(db, locale=locale, target_type=UNIT, target_key=code,
                  strings=strings, source_hash=unit.content_hash, scope=scope)
            db.commit()
            summary["translated"] += 1
            summary["strings"] += len(strings)

            if index % PROGRESS_EVERY == 0 or index == len(codes):
                _progress(index, len(codes), started, summary, translator)
    return summary


def translate_official(translator: Translator, *, refresh: bool) -> dict:
    locale = translator.locale
    summary = {"translated": 0, "skipped": 0, "strings": 0}
    with SessionLocal() as db:
        pages = list(db.scalars(select(OfficialPage).where(OfficialPage.status == "ok")))
        for page in pages:
            marker = page.content_hash or ""
            if not refresh and marker and _up_to_date(
                db, locale, OFFICIAL_PAGE, page.slug, marker
            ):
                summary["skipped"] += 1
                continue
            strings = translator.many(page_strings(page))
            store(db, locale=locale, target_type=OFFICIAL_PAGE, target_key=page.slug,
                  strings=strings, source_hash=marker)
            db.commit()
            summary["translated"] += 1
            summary["strings"] += len(strings)
            log.info("%s: %d strings", page.slug, len(strings))
    return summary


def translate_faq(translator: Translator, *, refresh: bool) -> dict:
    locale = translator.locale
    summary = {"translated": 0, "skipped": 0, "strings": 0}
    with SessionLocal() as db:
        for entry in db.scalars(select(FaqEntry)):
            strings = translator.many([entry.question, *_paragraphs(entry.answer)])
            store(db, locale=locale, target_type=FAQ_ENTRY, target_key=entry.slug,
                  strings=strings, source_hash=None)
            db.commit()
            summary["translated"] += 1
            summary["strings"] += len(strings)
    return summary


def _progress(done: int, total: int, started: float, summary: dict, translator: Translator) -> None:
    elapsed = time.monotonic() - started
    rate = done / elapsed if elapsed else 0
    log.info(
        "%d/%d units (%.0f%%) - %d translated, %d unchanged, %d strings, "
        "%d cached - about %d min left",
        done, total, 100 * done / total, summary["translated"], summary["skipped"],
        summary["strings"], translator.cached, ((total - done) / rate / 60) if rate else 0,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Machine-translate stored content")
    parser.add_argument("--locale", required=True, choices=list(LOCALES))
    parser.add_argument(
        "--targets", default="all", choices=["all", "units", "official", "faq"]
    )
    parser.add_argument(
        "--fields",
        default="short",
        choices=["short", "all"],
        help="short: titles and enumerable values. all: adds overviews and outcomes",
    )
    parser.add_argument("--limit", type=int, default=0, help="stop after this many units")
    parser.add_argument(
        "--shard",
        default="0/1",
        metavar="K/N",
        help="translate only shard K of N, so N of these can run at once",
    )
    parser.add_argument(
        "--refresh", action="store_true", help="re-translate even when the source is unchanged"
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    # Argos and Stanza log every sentence they see at INFO on the root logger,
    # which at five thousand units is the whole log. Root stays quiet and this
    # module talks.
    logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")
    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    for noisy in ("stanza", "argostranslate", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.ERROR)

    translator = Translator(args.locale)
    # Again after the model is loaded: importing it registers more loggers, and
    # they arrive with a level of their own already set.
    quieten()
    log.info("translating into %s", args.locale)

    if args.targets in ("all", "official"):
        log.info("official pages: %s", translate_official(translator, refresh=args.refresh))
    if args.targets in ("all", "faq"):
        log.info("faq: %s", translate_faq(translator, refresh=args.refresh))
    if args.targets in ("all", "units"):
        log.info(
            "units: %s",
            translate_units(
                translator,
                long_prose=args.fields == "all",
                limit=args.limit,
                shard=_shard(args.shard),
                refresh=args.refresh,
            ),
        )
    log.info("distinct strings translated this run: %d", translator.cached)


if __name__ == "__main__":
    main()
