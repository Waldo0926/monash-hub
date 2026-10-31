"""Apply a file of English -> Chinese renderings to the stored machine rows.

For when the translating is done somewhere the database is not, such as a
paid engine run from the machine that holds its key, with the result brought
back as one JSON object,

    {"<exact English string>": "<中文>", ...}

This replaces the rendering of each such string in every machine row that holds
it, and nothing else. A rendering is refused - and the row keeps what it had -
when it has lost a number, dropped a unit code, come back empty, or carries one
of the wrong words that ``structure_zh.py`` exists to get rid of. Strings that
have reviewed wording (``STRUCTURE_ZH``) are never touched: that wording beats
the machine on read anyway, and this keeps the machine row honest about it.

    python -m crawler.translate.apply_map --file map.json --targets curriculum
"""
from __future__ import annotations

import argparse
import json
import logging
import re

from app.core.db import SessionLocal
from app.knowledge.structure_zh import STRUCTURE_ZH
from app.models.translation import (
    AREA_OF_STUDY,
    COURSE,
    GLOBAL,
    MACHINE,
    PUBLISHED,
    UNIT,
    ContentTranslation,
)
from sqlalchemy import select

log = logging.getLogger("crawler.translate.apply_map")

TARGETS = {"curriculum": (COURSE, AREA_OF_STUDY), "units": (UNIT,)}
TRANSLATOR = "machine:google+glossary"

_WRONG = re.compile(
    "面包|中子|中医药|中杂技|中程器|惩罚|互联网档案馆|存檔|维基|兹卡|Zq[a-z]|#[a-z]#"
)
_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
_CODE = re.compile(r"\b[A-Z]{2,4}\d{3,4}\b")


def acceptable(english: str, chinese: str) -> bool:
    """Whether a rendering is fit to replace what is stored."""
    if not chinese or not chinese.strip() or chinese == english:
        return False
    if _WRONG.search(chinese):
        return False
    if any(code not in chinese for code in _CODE.findall(english)):
        return False
    squashed = chinese.replace(",", "").replace(" ", "")
    for number in _NUMBER.findall(english):
        if number not in chinese and number.replace(",", "") not in squashed:
            return False
    return True


def apply(rows, renderings: dict[str, str]) -> dict[str, int]:
    """Rewrite the strings of ``rows`` in place; returns what happened."""
    summary = {"rows": 0, "replaced": 0, "refused": 0}
    for row in rows:
        strings = dict((row.data or {}).get("strings") or {})
        changed = False
        for english in strings:
            if english in STRUCTURE_ZH or english not in renderings:
                continue
            chinese = renderings[english]
            if not acceptable(english, chinese):
                summary["refused"] += 1
                continue
            if strings[english] != chinese:
                strings[english] = chinese
                summary["replaced"] += 1
                changed = True
        if changed:
            row.data = {"strings": strings}
            row.translator = TRANSLATOR
            summary["rows"] += 1
    return summary


def add_global(db, renderings: dict[str, str], locale: str = "zh") -> int:
    """Put renderings in one machine row that every Handbook page reads.

    For strings that failed in a pass and so are in no row: there is no unit to
    attach them to without re-running the pass, and a string map is looked up by
    its exact English anyway. The row says what it is.
    """
    row = db.scalar(
        select(ContentTranslation).where(
            ContentTranslation.locale == locale,
            ContentTranslation.target_type == GLOBAL,
            ContentTranslation.target_key == "handbook",
            ContentTranslation.field == "retried",
            ContentTranslation.provenance == MACHINE,
        )
    )
    if row is None:
        row = ContentTranslation(
            locale=locale, target_type=GLOBAL, target_key="handbook", field="retried",
            provenance=MACHINE, status=PUBLISHED,
        )
        db.add(row)
    accepted = {k: v for k, v in renderings.items() if k not in STRUCTURE_ZH and acceptable(k, v)}
    strings = dict((row.data or {}).get("strings") or {})
    strings.update(accepted)
    row.data = {"strings": strings}
    row.translator = TRANSLATOR
    row.note = "strings that failed in a bulk pass, translated again with a stricter prompt"
    return len(accepted)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--file", required=True)
    parser.add_argument("--targets", choices=sorted(TARGETS))
    parser.add_argument(
        "--as-global", action="store_true",
        help="add the strings to one machine row every Handbook page reads, instead of "
             "replacing them in rows that already hold them",
    )
    parser.add_argument("--locale", default="zh")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    with open(args.file, encoding="utf-8") as handle:
        renderings = json.load(handle)
    log.info("%d renderings in %s", len(renderings), args.file)

    if not args.as_global and not args.targets:
        parser.error("--targets is required unless --as-global")
    if args.as_global:
        with SessionLocal() as db:
            added = add_global(db, renderings, args.locale)
            db.commit()
        log.info("added %d strings to the shared retried row", added)
        return

    with SessionLocal() as db:
        rows = db.scalars(
            select(ContentTranslation).where(
                ContentTranslation.locale == args.locale,
                ContentTranslation.provenance == MACHINE,
                ContentTranslation.target_type.in_(TARGETS[args.targets]),
            )
        ).all()
        summary = apply(rows, renderings)
        db.commit()
    log.info("applied: %s", summary)


if __name__ == "__main__":
    main()
