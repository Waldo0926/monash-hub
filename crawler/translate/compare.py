"""Put two chat models side by side on the site's own text before switching.

    python -m crawler.translate.compare --models glm-4.5-flash,glm-4-flash \
        --locale zh --sample 20 --out /out/compare-zh.md

Takes paragraphs from stored official pages (Monash Malaysia first, since
that is who reads the site), runs each through the full pipeline - glossary,
masking, the reply checks - once per model, and writes a Markdown table with
the time each took. Nothing is written to the database: the point is for a
person to read the two columns and decide, not for a score to decide.
"""
from __future__ import annotations

import argparse
import random
import time

from app.core.db import SessionLocal
from app.models.knowledge import OfficialPage
from sqlalchemy import select

from crawler.translate import llm
from crawler.translate.engine import Translator, quieten


def paragraphs(sample: int, seed: int) -> list[str]:
    """Paragraphs of 80 to 600 characters, Malaysia's pages first."""
    with SessionLocal() as db:
        pages = db.execute(
            select(OfficialPage.applies_to, OfficialPage.clean_text)
            .where(OfficialPage.status == "ok", OfficialPage.clean_text.is_not(None))
        ).all()
    pages.sort(key=lambda row: row[0] != "malaysia")
    found = [p.strip() for _, text in pages for p in text.split("\n\n")
             if 80 <= len(p.strip()) <= 600]
    rng = random.Random(seed)
    head = found[: max(sample * 5, 50)]
    return rng.sample(head, min(sample, len(head)))


def run(model: str, locale: str, texts: list[str]) -> list[tuple[str, float]]:
    translator = Translator(locale, engine="llm", workers=1)
    base = translator._translate
    translator._translate = llm.LLMModel(locale, url=base.url.removesuffix("/chat/completions"),
                                         key=base._key, model=model)
    results = []
    for text in texts:
        started = time.monotonic()
        try:
            result = translator.text(text) or "(kept in English)"
        except Exception as exc:
            result = f"(failed: {exc})"
        results.append((result, time.monotonic() - started))
    return results


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "<br>")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--models", required=True, help="comma separated model names")
    parser.add_argument("--locale", default="zh")
    parser.add_argument("--sample", type=int, default=20)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    quieten()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    texts = paragraphs(args.sample, args.seed)
    columns = {model: run(model, args.locale, texts) for model in models}

    lines = [f"# {args.locale}: {' vs '.join(models)}", ""]
    for model, rows in columns.items():
        seconds = sum(t for _, t in rows)
        failed = sum(1 for r, _ in rows if r.startswith("(failed"))
        lines.append(f"- {model}: {seconds:.0f}s for {len(rows)} paragraphs, {failed} failed")
    lines += ["", "| English | " + " | ".join(models) + " |",
              "|---|" + "---|" * len(models)]
    for index, text in enumerate(texts):
        cells = [_cell(columns[m][index][0]) for m in models]
        lines.append(f"| {_cell(text)} | " + " | ".join(cells) + " |")
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print("\n".join(lines[:len(models) + 2]))


if __name__ == "__main__":
    main()
