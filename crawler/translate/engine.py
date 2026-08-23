"""Offline machine translation, with the domain terms taken out of its hands.

The engine is Argos Translate (OPUS-MT models through CTranslate2). It runs on
the same box as everything else, needs no key, costs nothing per call and has no
rate limit, which is what makes translating five thousand units possible at all.

It is also, unaided, wrong in the places that matter - see
``app/knowledge/glossary.py`` for the measurements. So every string goes through
three stages:

    protect the terms  ->  translate what is left  ->  put the terms back

and a string that turns out to be nothing *but* terms never reaches the model,
because asked to translate the bare placeholder ``Zqa`` it answers 兹卡.

The cache is not an optimisation detail. The Handbook repeats the same
boilerplate paragraph across thousands of units; translating it once and reusing
it is the difference between an hour and a week.
"""
from __future__ import annotations

import logging
import re
import threading
from collections.abc import Iterable

from app.knowledge.glossary import (
    is_only_placeholders,
    placeholders_survived,
    protect,
    restore,
    whole_value,
)

log = logging.getLogger(__name__)

# Model packages published by the Argos index, per target language.
SUPPORTED = ("zh", "ja", "ko")

# Sentences the model reliably mangles, or that should not be translated at all.
_SKIP = re.compile(
    r"^\s*(?:[\W\d]+|Social Media Share Bar.*|Not Configured)\s*$",
    re.IGNORECASE,
)

# Argos emits ASCII punctuation into CJK text, which reads as a foreign body in
# a Chinese or Japanese sentence. Korean uses ASCII punctuation, so it is left
# alone.
_PUNCTUATION = {
    "zh": {",": "，", ";": "；", ":": "：", "?": "？", "!": "！", "(": "（", ")": "）"},
    "ja": {",": "、", ";": "；", ":": "：", "?": "？", "!": "！", "(": "（", ")": "）"},
}
_CJK = r"㐀-䶿一-鿿぀-ヿ가-힯"


class Translator:
    """One loaded model per language, translating with the glossary in front."""

    def __init__(self, locale: str) -> None:
        if locale not in SUPPORTED:
            raise ValueError(f"no model for {locale!r}")
        self.locale = locale
        self._cache: dict[str, str] = {}
        self._lock = threading.Lock()
        self._translate = _load_model(locale)

    @property
    def cached(self) -> int:
        return len(self._cache)

    def text(self, source: str | None) -> str | None:
        """Translate one string. Returns ``None`` for nothing worth translating."""
        if not source:
            return None
        source = source.strip()
        if not source or _SKIP.match(source):
            return None

        cached = self._cache.get(source)
        if cached is not None:
            return cached or None

        # A complete field value off one of the Handbook's closed lists - a
        # campus, a teaching period, an assessment type. Agreed wording, not a
        # translation problem.
        agreed = whole_value(source, self.locale)
        if agreed:
            self._cache[source] = agreed
            return agreed

        masked, terms = protect(source, self.locale)
        if is_only_placeholders(masked):
            # Entirely known terms - a unit title like "Programming paradigms",
            # a campus name, an assessment type. Nothing for the model to do.
            result = restore(masked, terms)
        else:
            try:
                translated = self._translate(masked)
            except Exception as exc:  # one bad string must not end a batch of 5,000
                log.warning("translation failed (%s): %s", exc, source[:60])
                self._cache[source] = ""
                return None
            if not placeholders_survived(translated, len(terms)):
                # The model rewrote one of the tokens instead of copying it -
                # "What is Zqa?" came back as 什么是兹卡?. Restoring cannot find
                # it, so the reader would get a transliterated nonsense word
                # where a term should be. English is the better answer.
                log.debug("placeholder lost, keeping English: %s", source[:60])
                self._cache[source] = ""
                return None
            # Tidy after restoring, not before: with the placeholders still in
            # place the punctuation rules see a Latin character where the
            # finished sentence has a Chinese one, and leave the comma alone.
            result = _tidy(restore(translated, terms), self.locale)

        result = result.strip()
        # A "translation" identical to the source is not one. Storing it would
        # mean the reader sees English behind a banner promising Chinese.
        if result == source:
            self._cache[source] = ""
            return None
        self._cache[source] = result
        return result

    def many(self, sources: Iterable[str | None]) -> dict[str, str]:
        """Translate a batch, skipping what is already known. Source -> target."""
        out: dict[str, str] = {}
        for source in sources:
            if not source:
                continue
            key = source.strip()
            if not key or key in out:
                continue
            translated = self.text(key)
            if translated:
                out[key] = translated
        return out


def quieten() -> None:
    """Silence the engine's own logging.

    Argos logs every sentence it tokenises, and Stanza logs the model it loads
    to do it. Setting the parent logger is not enough - they set a level on the
    child themselves - so every logger already registered under those names is
    turned down by name, after import.
    """
    logging.getLogger().setLevel(logging.WARNING)
    for name in list(logging.root.manager.loggerDict):
        if name.split(".")[0] in {"argostranslate", "stanza", "ctranslate2", "sentencepiece"}:
            logging.getLogger(name).setLevel(logging.ERROR)


def _load_model(locale: str):
    import argostranslate.package as package
    import argostranslate.translate as translate

    installed = {
        (lang.code, target.to_lang.code)
        for lang in translate.get_installed_languages()
        for target in lang.translations_from
    }
    if ("en", locale) not in installed:
        log.info("installing the en->%s model", locale)
        package.update_package_index()
        candidates = [
            p for p in package.get_available_packages()
            if p.from_code == "en" and p.to_code == locale
        ]
        if not candidates:
            raise RuntimeError(f"the Argos index has no en->{locale} package")
        package.install_from_path(candidates[0].download())

    quieten()

    def run(text: str) -> str:
        return translate.translate(text, "en", locale)

    return run


def _tidy(text: str, locale: str) -> str:
    """Make the output read like the language it is in.

    The glossary's own wording already uses full-width punctuation, so running
    this over the restored sentence leaves it untouched.
    """
    text = text.strip()
    mapping = _PUNCTUATION.get(locale)
    if mapping:
        # Only between CJK characters: "45%, up from" inside an English quote
        # should keep its comma, and "1,200" must not become "1，200".
        for ascii_mark, wide in mapping.items():
            text = re.sub(
                rf"(?<=[{_CJK}])\s*{re.escape(ascii_mark)}\s*(?=[{_CJK}])",
                wide,
                text,
            )
        # Sentence-final full stop, which the rule above cannot see.
        text = re.sub(rf"(?<=[{_CJK}])\s*\.\s*$", "。", text)
        text = re.sub(rf"(?<=[{_CJK}])\s*\.\s+(?=[{_CJK}])", "。", text)
    # Two CJK words with a space between them is an artefact of putting a
    # glossary term back where a placeholder was; Chinese and Japanese do not
    # space words. A space between Latin and CJK is correct and stays
    # ("Monash 大学"), and so is one before a digit ("第 2 级").
    text = re.sub(rf"(?<=[{_CJK}])[ \t]+(?=[{_CJK}])", "", text)
    # A space against CJK punctuation is not.
    text = re.sub(r"[ \t]+(?=[，。、；：？！）])", "", text)
    text = re.sub(r"(?<=（)[ \t]+", "", text)
    return re.sub(r"[ \t]{2,}", " ", text).strip()
