"""Applying stored translations to official content.

Loading is one query per response: everything for one target in one language,
plus the global string set. Applying is exact string replacement — a string that
has a translation is swapped, a string that does not stays exactly as Monash
wrote it.

Nothing in here translates. It looks things up. If the lookup misses, the reader
gets English, and that is the intended outcome rather than a degraded one.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.translation import GLOBAL, HUMAN, MACHINE, PUBLISHED, ContentTranslation

# The string set applied to every Handbook unit, for the boilerplate the
# Handbook repeats verbatim across thousands of them.
HANDBOOK_GLOBAL = "handbook"


class Translation:
    """Everything stored for one target in one language, ready to apply."""

    __slots__ = ("fields", "locale", "machine", "reviewed", "source_hash", "stale", "strings")

    def __init__(self, locale: str) -> None:
        self.locale = locale
        self.fields: dict[str, str] = {}
        self.strings: dict[str, str] = {}
        self.source_hash: str | None = None
        # True when the source has changed since the translation was written.
        self.stale = False
        # Where the words came from. Both can be true: a page can have a
        # machine body with a few paragraphs corrected by hand.
        self.machine = False
        self.reviewed = False

    def __bool__(self) -> bool:
        return bool(self.fields or self.strings)

    def field(self, name: str, source: str | None) -> str | None:
        """The translation of a whole field, or the source unchanged.

        A field with no whole-field translation is tried paragraph by
        paragraph. That is what makes the Handbook's boilerplate tractable: a
        unit's teaching approach is two or three stock paragraphs plus, at most,
        one written for that unit, and translating the stock ones once covers
        thousands of units without anybody claiming to have translated the rest.
        """
        if source is None:
            return None
        whole = self.fields.get(name) or self.strings.get(source.strip())
        if whole:
            return whole
        if not self.strings or "\n\n" not in source:
            return source

        paragraphs = source.split("\n\n")
        translated = [self.strings.get(part.strip(), part) for part in paragraphs]
        return "\n\n".join(translated)

    def string(self, source: str | None) -> str | None:
        if source is None:
            return None
        return self.strings.get(source.strip()) or source

    def meta(self) -> dict[str, Any] | None:
        """What the UI needs to label this as a translation rather than a source."""
        if not self:
            return None
        return {
            "locale": self.locale,
            "stale": self.stale,
            "unofficial": True,
            "machine": self.machine,
            "reviewed": self.reviewed,
        }


def load(
    db: Session,
    locale: str | None,
    target_type: str,
    target_key: str,
    *,
    source_hash: str | None = None,
    global_key: str | None = HANDBOOK_GLOBAL,
) -> Translation:
    """Every published translation for one target, merged with the global set."""
    return load_many(
        db, locale, target_type, [target_key],
        source_hashes={target_key: source_hash} if source_hash else None,
        global_key=global_key,
    )[target_key]


def load_many(
    db: Session,
    locale: str | None,
    target_type: str,
    target_keys: list[str],
    *,
    source_hashes: dict[str, str | None] | None = None,
    global_key: str | None = HANDBOOK_GLOBAL,
) -> dict[str, Translation]:
    """Translations for several targets in one query.

    The guides index renders fifty pages, and fifty round trips to fetch fifty
    titles is how a list page becomes the slowest thing on the site.

    ``source_hashes`` carries the current hash of each English source. When a
    stored row was written against a different one, the translation is still
    returned - a slightly out of date Chinese paragraph beside a "this may be
    out of date" warning is more use than nothing - but it is flagged.
    """
    result = {key: Translation(locale or "") for key in target_keys}
    if not locale or locale == "en" or not target_keys:
        return result

    conditions = [
        (ContentTranslation.target_type == target_type)
        & ContentTranslation.target_key.in_(target_keys)
    ]
    if global_key:
        conditions.append(
            (ContentTranslation.target_type == GLOBAL)
            & (ContentTranslation.target_key == global_key)
        )

    rows = db.scalars(
        select(ContentTranslation).where(
            ContentTranslation.locale == locale,
            ContentTranslation.status == PUBLISHED,
            or_(*conditions),
        )
    ).all()

    # Machine before human, everywhere: whatever is applied last wins, and a
    # sentence somebody checked must not be replaced by one nobody did.
    def order(row: ContentTranslation) -> int:
        return 0 if row.provenance == MACHINE else 1

    own = sorted((r for r in rows if r.target_type != GLOBAL), key=order)
    shared = sorted((r for r in rows if r.target_type == GLOBAL), key=order)

    for key, translation in result.items():
        # Global first, so a page's own strings overwrite the shared boilerplate
        # rather than the other way round.
        for row in shared:
            _apply(translation, row)
        for row in (r for r in own if r.target_key == key):
            _apply(translation, row)
            translation.source_hash = translation.source_hash or row.source_hash
            current = (source_hashes or {}).get(key)
            # Only a whole-field translation can go quietly out of date: it
            # replaces the field wholesale, so if the English moved the reader
            # is looking at a paragraph that no longer exists. A string map is
            # keyed by the exact English sentence - when that sentence changes
            # the key simply stops matching and the reader gets the new English,
            # which is the honest outcome and not worth a warning banner on
            # every page the extractor has ever touched.
            if (
                row.text is not None
                and current
                and row.source_hash
                and row.source_hash != current
            ):
                translation.stale = True

    return result


def _apply(translation: Translation, row: ContentTranslation) -> None:
    if row.provenance == MACHINE:
        translation.machine = True
    elif row.provenance == HUMAN:
        translation.reviewed = True
    if row.text is not None:
        translation.fields[row.field] = row.text
    for source, translated in ((row.data or {}).get("strings") or {}).items():
        if isinstance(source, str) and isinstance(translated, str):
            translation.strings[source.strip()] = translated


# --- applying to blocks ---------------------------------------------------

def translate_blocks(blocks: list[dict[str, Any]], tr: Translation) -> list[dict[str, Any]]:
    """A copy of the block list with every known string swapped.

    Spans are joined before lookup and the translation replaces the whole run,
    because a sentence is the unit a person can translate correctly and "all
    grades," on its own is not. Emphasis inside a translated paragraph is
    therefore dropped; the link on a span is kept when the run had exactly one.
    """
    if not tr.strings:
        return blocks

    out = []
    for block in blocks:
        kind = block.get("type")
        if kind == "heading":
            out.append({**block, "text": tr.string(block.get("text")) or block.get("text")})
        elif kind == "paragraph":
            out.append({**block, "spans": _translate_spans(block.get("spans") or [], tr)})
        elif kind == "list":
            out.append({
                **block,
                "items": [_translate_spans(item, tr) for item in block.get("items") or []],
            })
        elif kind == "table":
            out.append({
                **block,
                "caption": tr.string(block.get("caption")) if block.get("caption") else None,
                "columns": [tr.string(c) or c for c in block.get("columns") or []],
                "rows": [[tr.string(c) or c for c in row] for row in block.get("rows") or []],
                **(
                    {"foot": [[tr.string(c) or c for c in row] for row in block["foot"]]}
                    if block.get("foot")
                    else {}
                ),
            })
        else:
            out.append(block)
    return out


def _translate_spans(spans: list[dict[str, Any]], tr: Translation) -> list[dict[str, Any]]:
    joined = "".join(s.get("text", "") for s in spans).strip()
    translated = tr.strings.get(joined)
    if translated is None:
        # No translation for the run as a whole: try each span, so a list item
        # that is one linked phrase still comes through.
        return [{**s, "text": tr.strings.get(s.get("text", "").strip(), s.get("text", ""))}
                for s in spans]

    links = [s for s in spans if s.get("url")]
    span: dict[str, Any] = {"text": translated}
    if len(links) == 1:
        span["url"] = links[0]["url"]
    return [span]


def translated_headings(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rebuild the outline from already-translated blocks, so the two agree."""
    return [
        {"level": b["level"], "text": b["text"], "id": b["id"]}
        for b in blocks
        if b.get("type") == "heading"
    ]
