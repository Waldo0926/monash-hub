"""Fill the translation table by machine.

    python -m crawler.translate.run --locale zh --targets official
    python -m crawler.translate.run --locale zh --targets units --fields short
    python -m crawler.translate.run --locale zh --targets units --fields all
    python -m crawler.translate.run --locale zh --targets units --fields all --units FIT1008
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
import hashlib
import logging
import time

from app.core.db import SessionLocal
from app.knowledge.glossary import GENERAL, HANDBOOK, LOCALES, STRUCTURE
from app.models.curriculum import AreaOfStudy, Course, CurriculumContainer
from app.models.handbook import Unit
from app.models.knowledge import FaqEntry, OfficialPage
from app.models.translation import (
    AREA_OF_STUDY,
    COURSE,
    FAQ_ENTRY,
    MACHINE,
    OFFICIAL_PAGE,
    PUBLISHED,
    UNIT,
    ContentTranslation,
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from crawler.official.seeds import SEEDS
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


def course_strings(course: Course, containers: list[CurriculumContainer]) -> list[str]:
    """A degree's own prose, plus the name of every requirement group under it.

    The group titles are the reason this exists. A course page is mostly an
    outline, and an outline of "Part A. Foundation studies" under a Chinese
    heading is the exact failure this whole translation layer was built to
    avoid. They are short and highly repeated across degrees, so the engine's
    cache makes 503 courses cost far less than 503 pages of prose.

    What it deliberately leaves alone is the long structural prose, for the
    reason given inline below.
    """
    strings: list[str | None] = [
        course.title, course.aqf_level, course.course_type, course.faculty, course.school
    ]
    strings += course.campuses or []
    strings += _paragraphs(course.overview)
    # Not structure_text or requirements_text. They are the longest prose on a
    # course page - five thousand characters against the overview's fifteen
    # hundred - and nothing renders them yet. Translating what is not shown is
    # four fifths of this job for none of its value; when a page displays them,
    # this is one line.
    for container in containers:
        strings.append(container.title)
        strings += _paragraphs(container.description)
        strings += _paragraphs(container.footnote)
    return [s.strip() for s in strings if s and s.strip()]


def aos_strings(aos: AreaOfStudy, containers: list[CurriculumContainer]) -> list[str]:
    strings: list[str | None] = [aos.title, aos.aos_type, aos.study_level, aos.faculty, aos.school]
    strings += _paragraphs(aos.overview)
    for container in containers:
        strings.append(container.title)
        strings += _paragraphs(container.description)
        strings += _paragraphs(container.footnote)
    return [s.strip() for s in strings if s and s.strip()]


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
    # Merged, not replaced. A pass that covers fewer strings than the last one
    # is not evidence that the others are wrong: running `--fields short` after
    # `--fields all` used to overwrite every overview, outcome and workload
    # paragraph with a map that did not contain them, and the pages silently
    # went back to English.
    #
    # A key whose English has since changed is left behind rather than deleted.
    # It costs a little room and can never be read: the lookup is by the exact
    # sentence, so a sentence that no longer exists is never asked for.
    existing = ((row.data or {}).get("strings") or {}) if row.data else {}
    row.data = {"strings": {**existing, **strings}}
    # The widest pass this row has seen, so that a later `short` does not make
    # an `all` row look as though the long prose still needs doing.
    widest = scope
    if (row.note or "") == "fields=all" or scope == "fields=all":
        widest = "fields=all"
    # The source hash is what the caller passed: a unit's own hash, or for a
    # unit in several Handbook years the digest from `years_marker`. `load_many`
    # only warns "may be out of date" for whole-field translations (`text`), so
    # a string-map row like this one is never flagged by it.
    row.source_hash = source_hash
    row.status = PUBLISHED
    row.translator = TRANSLATOR_NAME
    row.note = widest or None


def _stored_strings(db, locale: str, target_type: str, target_key: str) -> dict[str, str]:
    """The machine string map already stored for one target, to prime the translator."""
    data = db.scalar(
        select(ContentTranslation.data).where(
            ContentTranslation.locale == locale,
            ContentTranslation.target_type == target_type,
            ContentTranslation.target_key == target_key,
            ContentTranslation.field == "content",
            ContentTranslation.provenance == MACHINE,
        )
    )
    return dict((data or {}).get("strings") or {})


def years_marker(hashes: list[str | None]) -> str:
    """What a unit's translation is stamped with: its English in every Handbook year.

    One year: that year's content hash, as before. Several: a digest of all of
    them, newest first. Stamping only the newest year meant a code already done
    for 2026 and 2027 was skipped when the 2025 Handbook was loaded, and every
    sentence 2025 worded differently stayed English. A string-map row is never
    flagged stale on read (only a whole-field translation is), so a digest here
    changes nothing a reader sees.
    """
    present = [h or "" for h in hashes]
    if len(present) == 1:
        return present[0]
    return hashlib.sha256("|".join(present).encode()).hexdigest()


def _stored_strings(db, locale: str, target_type: str, target_key: str) -> dict[str, str]:
    """The machine row's string map for one target, or nothing."""
    data = db.scalar(
        select(ContentTranslation.data).where(
            ContentTranslation.locale == locale,
            ContentTranslation.target_type == target_type,
            ContentTranslation.target_key == target_key,
            ContentTranslation.field == "content",
            ContentTranslation.provenance == MACHINE,
        )
    )
    return (data or {}).get("strings") or {}


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

def _select_codes(all_codes: list[str], units: list[str] | None, limit: int) -> list[str]:
    """Which unit codes a pass should touch.

    ``units`` scopes to specific codes - for the day a Handbook page like
    FIT1008 is republished mid-year and the rest of the catalogue does not
    need re-translating with it. It is checked against what actually exists
    so a typo fails loudly instead of silently translating nothing. ``limit``
    only makes sense against the full catalogue, so it is ignored once
    ``units`` has already scoped the list down to what was asked for.
    """
    if not units:
        return all_codes[:limit] if limit else all_codes
    existing = set(all_codes)
    wanted = [code.strip().upper() for code in units if code.strip()]
    missing = [code for code in wanted if code not in existing]
    if missing:
        raise ValueError(f"unit code(s) not found: {', '.join(missing)}")
    return wanted


def translate_units(
    translator: Translator, *, long_prose: bool, limit: int, refresh: bool,
    units: list[str] | None = None,
) -> dict:
    locale = translator.locale
    summary = {"translated": 0, "skipped": 0, "strings": 0}
    started = time.monotonic()
    # Unit prose is Handbook prose, not guide prose: see HANDBOOK_TERMS.
    translator.use_scope(HANDBOOK)

    with SessionLocal() as db:
        # One code exists once per Handbook year. Translations are stored by code,
        # so every year's English has to be translated into the same row: a
        # sentence Monash rewrote for 2027 would otherwise stay English. The newest
        # year is the one whose hash the row is stamped with.
        all_codes = list(db.scalars(select(Unit.unit_code).distinct().order_by(Unit.unit_code)))
        codes = _select_codes(all_codes, units, limit)

        for index, code in enumerate(codes, start=1):
            rows = db.scalars(
                select(Unit).where(Unit.unit_code == code)
                .order_by(Unit.academic_year.desc())
                .options(
                    selectinload(Unit.offerings),
                    selectinload(Unit.assessments),
                    selectinload(Unit.activities),
                    selectinload(Unit.learning_outcomes),
                    selectinload(Unit.requisite_groups),
                )
            ).all()
            if not rows:
                continue
            marker = years_marker([row.content_hash for row in rows])
            scope = "fields=all" if long_prose else "fields=short"
            if not refresh and _up_to_date(db, locale, UNIT, code, marker, scope):
                summary["skipped"] += 1
                continue

            translator.prime(_stored_strings(db, locale, UNIT, code))
            strings = translator.many(
                text for row in rows for text in unit_strings(row, long_prose=long_prose)
            )
            store(db, locale=locale, target_type=UNIT, target_key=code,
                  strings=strings, source_hash=marker, scope=scope)
            db.commit()
            summary["translated"] += 1
            summary["strings"] += len(strings)

            if index % PROGRESS_EVERY == 0 or index == len(codes):
                _progress(index, len(codes), started, summary, translator)
    translator.use_scope(GENERAL)
    return summary


def translate_official(translator: Translator, *, refresh: bool) -> dict:
    locale = translator.locale
    summary = {"translated": 0, "skipped": 0, "strings": 0}
    with SessionLocal() as db:
        pages = list(db.scalars(select(OfficialPage).where(OfficialPage.status == "ok")))
        # In seed-list order, which puts the pages most students need first: a
        # long pass over a few hundred pages is useful long before it finishes.
        order = {seed.slug: index for index, seed in enumerate(SEEDS)}
        pages.sort(key=lambda page: order.get(page.slug, len(order)))
        for page in pages:
            marker = page.content_hash or ""
            wanted = page_strings(page)
            if not refresh and marker and _up_to_date(
                db, locale, OFFICIAL_PAGE, page.slug, marker
            ):
                # Up to date except for strings it has never seen - a title the
                # seed list renamed - which are translated on their own rather
                # than sending the whole unchanged page to the model again. A
                # title whose campus the model translated itself counts as unseen.
                have = _stored_strings(db, locale, OFFICIAL_PAGE, page.slug)
                wanted = [s for s in wanted if s not in have
                          or (s == page.title and not _campus_title_ok(s, have[s], locale))]
                if not wanted:
                    summary["skipped"] += 1
                    continue
            title = page.title if page.title in wanted else None
            strings = translator.many([s for s in wanted if s != title])
            if title and (done := translate_title(translator, title, locale)):
                strings[title] = done
            store(db, locale=locale, target_type=OFFICIAL_PAGE, target_key=page.slug,
                  strings=strings, source_hash=marker)
            db.commit()
            summary["translated"] += 1
            summary["strings"] += len(strings)
            log.info("%s: %d strings", page.slug, len(strings))
    return summary


#: The campus a coverage title ends with, and how each language says it. It is
#: put back by hand, never sent to the model: asked to translate "FAQs for new
#: international students (Monash Malaysia)", it returned
#: 常见问题解答（新国际学生（Monash Malaysia（马来西亚校区））学生）.
CAMPUS_SUFFIX = " (Monash Malaysia)"
CAMPUS_SUFFIX_ZH = {"zh": "（马来西亚校区）", "ja": "（マレーシア校）", "ko": "(말레이시아 캠퍼스)"}


def translate_title(translator: Translator, title: str, locale: str) -> str | None:
    """A page title, with any campus suffix kept out of the model's hands."""
    if title.endswith(CAMPUS_SUFFIX) and locale in CAMPUS_SUFFIX_ZH:
        base = title[: -len(CAMPUS_SUFFIX)]
        done = translator.many([base]).get(base)
        return f"{done}{CAMPUS_SUFFIX_ZH[locale]}" if done else None
    return translator.many([title]).get(title)


def _campus_title_ok(title: str, translated: str, locale: str) -> bool:
    if not title.endswith(CAMPUS_SUFFIX) or locale not in CAMPUS_SUFFIX_ZH:
        return True
    suffix = CAMPUS_SUFFIX_ZH[locale]
    return translated.endswith(suffix) and translated.count("Monash Malaysia") == 0 \
        and translated.count(suffix) == 1


def translate_curriculum(translator: Translator, *, refresh: bool) -> dict:
    """Courses and areas of study, in that order.

    This is the one target translated in the structure scope: a few words mean
    something specific in the prose describing how a degree is assembled and
    something else in a unit's overview. "major" is the one that matters -
    an academic major here, and the ordinary adjective almost everywhere else.
    """
    translator.use_scope(STRUCTURE)
    locale = translator.locale
    summary = {"translated": 0, "skipped": 0, "strings": 0}
    with SessionLocal() as db:
        for model, code_attr, target_type, collect in (
            (Course, "course_code", COURSE, course_strings),
            (AreaOfStudy, "aos_code", AREA_OF_STUDY, aos_strings),
        ):
            owner = (
                CurriculumContainer.course_id
                if model is Course
                else CurriculumContainer.area_of_study_id
            )
            for row in db.scalars(select(model).where(model.is_active)):
                key = getattr(row, code_attr)
                marker = row.content_hash or ""
                if not refresh and marker and _up_to_date(db, locale, target_type, key, marker):
                    summary["skipped"] += 1
                    continue
                containers = list(
                    db.scalars(
                        select(CurriculumContainer)
                        .where(owner == row.id)
                        .order_by(CurriculumContainer.id)
                    )
                )
                # Each Handbook year is its own row here and they share one stored
                # map, so the years take turns looking out of date. Priming keeps
                # that from costing a model call per sentence every run.
                translator.prime(_stored_strings(db, locale, target_type, key))
                strings = translator.many(collect(row, containers))
                store(db, locale=locale, target_type=target_type, target_key=key,
                      strings=strings, source_hash=marker)
                db.commit()
                summary["translated"] += 1
                summary["strings"] += len(strings)
                log.info("%s: %d strings", key, len(strings))
    translator.use_scope(GENERAL)
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
        "--targets", default="all", choices=["all", "units", "official", "faq", "curriculum"]
    )
    parser.add_argument(
        "--fields",
        default="short",
        choices=["short", "all"],
        help="short: titles and enumerable values. all: adds overviews and outcomes",
    )
    parser.add_argument(
        "--engine", default="argos", choices=["argos", "google", "google-cloud", "llm"],
        help="argos: offline model (default). google: the web endpoint, paced and "
             "stopped on repeated failure. google-cloud: the paid Cloud Translation API, "
             "key in GOOGLE_TRANSLATE_API_KEY. llm: any OpenAI-compatible chat model "
             "(default Zhipu glm-4-flash, free) - see crawler/translate/llm.py",
    )
    parser.add_argument(
        "--workers", type=int, default=1,
        help="strings translated at once (remote engines only; the offline one ignores it)",
    )
    parser.add_argument("--limit", type=int, default=0, help="stop after this many units")
    parser.add_argument(
        "--units", nargs="+", default=None, metavar="CODE",
        help="only these unit codes, e.g. --units FIT1008 FIT1055 "
             "(units target only; a code not in the catalogue is an error)",
    )
    parser.add_argument(
        "--refresh", action="store_true", help="re-translate even when the source is unchanged"
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    if args.units and args.targets != "units":
        parser.error("--units requires --targets units")

    # Argos and Stanza log every sentence they see at INFO on the root logger,
    # which at five thousand units is the whole log. Root stays quiet and this
    # module talks.
    logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")
    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    for noisy in ("stanza", "argostranslate", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.ERROR)

    global TRANSLATOR_NAME
    translator = Translator(args.locale, engine=args.engine, workers=args.workers)
    if args.engine in ("google", "google-cloud"):
        TRANSLATOR_NAME = f"machine:{args.engine}+glossary"
    elif args.engine == "llm":
        TRANSLATOR_NAME = f"machine:llm:{translator._translate.model}+glossary"
    # Again after the model is loaded: importing it registers more loggers, and
    # they arrive with a level of their own already set.
    quieten()
    log.info("translating into %s", args.locale)

    if args.targets in ("all", "curriculum"):
        log.info("courses: %s", translate_curriculum(translator, refresh=args.refresh))
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
                refresh=args.refresh,
                units=args.units,
            ),
        )
    log.info("distinct strings translated this run: %d", translator.cached)


if __name__ == "__main__":
    main()
