"""Re-apply the engine's small Chinese corrections to rows already stored.

For the corrections added after a long pass has run: rewriting the rows costs
nothing, re-translating them costs hours.

    python -m crawler.translate.polish --targets curriculum
"""
from __future__ import annotations

import argparse
import logging

from app.core.db import SessionLocal
from app.models.translation import (
    AREA_OF_STUDY,
    COURSE,
    MACHINE,
    OFFICIAL_PAGE,
    UNIT,
    ContentTranslation,
)
from sqlalchemy import select

from crawler.translate.engine import polish_zh

log = logging.getLogger("crawler.translate.polish")
TARGETS = {
    "curriculum": (COURSE, AREA_OF_STUDY),
    "units": (UNIT,),
    "official": (OFFICIAL_PAGE,),
    "all": (COURSE, AREA_OF_STUDY, UNIT, OFFICIAL_PAGE),
}


def polish_rows(rows) -> dict[str, int]:
    summary = {"rows": 0, "strings": 0}
    for row in rows:
        strings = dict((row.data or {}).get("strings") or {})
        changed = 0
        for english, chinese in strings.items():
            if not isinstance(chinese, str):
                continue
            polished = polish_zh(chinese)
            if polished != chinese:
                strings[english] = polished
                changed += 1
        if changed:
            row.data = {"strings": strings}
            summary["rows"] += 1
            summary["strings"] += changed
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--targets", required=True, choices=sorted(TARGETS))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    with SessionLocal() as db:
        rows = db.scalars(
            select(ContentTranslation).where(
                ContentTranslation.locale == "zh",
                ContentTranslation.provenance == MACHINE,
                ContentTranslation.target_type.in_(TARGETS[args.targets]),
            )
        ).all()
        summary = polish_rows(rows)
        db.commit()
    log.info("polished: %s", summary)


if __name__ == "__main__":
    main()
