"""Batch machine translation of unit prose.

This is the one place in the product where a model is involved, and the shape of
its involvement is what keeps `AGENTS.md`'s "no LLM" rule intact rather than
breaking it:

* It runs **offline, as a batch**, writing rows into `content_translations` -
  the same table a person writes into, with `method='machine'` so the page can
  say which it is. Nothing calls a service during a request. Answering a
  question is still a database lookup.
* It never touches **anything a student wrote**, and it never overwrites a
  translation a person made. Handbook units and official Monash pages are in
  scope; the community is not, and a page with a hand-written translation is
  skipped rather than replaced.
* Every glossary term is protected before the request and restored after it, and
  the output is checked. A passage that fails the check is **repaired** - the
  bad rendering is substituted for the required one - and the repair is counted
  in the run summary rather than hidden.

The earlier draft discarded a failed passage instead of repairing it, which left
that paragraph in English. The instruction is full Chinese coverage, so the
trade was reversed: every page carries the machine-translation notice and a link
to the English, and the glossary keeps the terms that would actually mislead
from ever reaching the page.

DeepL is called over plain HTTP rather than through its SDK, for the same reason
`core/email.py` calls Resend that way: one dependency fewer, and the request is
three fields.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from app.core.config import Settings, get_settings
from app.knowledge import glossary

log = logging.getLogger(__name__)

USER_AGENT = "MonashHub/0.1 (+https://monashhub.secureview.tech)"

# The unit fields this module is allowed to translate. Anything not listed is
# somebody's own words.
TRANSLATABLE_UNIT_FIELDS = (
    "overview",
    "teaching_approach",
    "workload_requirements",
    "assessment_summary",
    "learning_outcomes",
)


class TranslationFailed(RuntimeError):
    """The text could not be translated, or came back failing the glossary check."""


class Translator(Protocol):
    """Sends text away and gets it back translated.

    The text it receives already has its glossary terms wrapped in
    ``<x>...</x>``, and an implementation must return them untouched. Protecting
    and restoring is `translate_prose`'s job, not an implementation's - putting
    it inside one implementation is how a second implementation silently ships
    without any protection at all.
    """

    def translate(self, text: str, target: str) -> str: ...


@dataclass(frozen=True, slots=True)
class EchoTranslator:
    """Returns the source unchanged. For dry runs and for tests.

    It exists so the whole pipeline - protection, restoration, the glossary
    check, the write - can be exercised without a network call or an API key.
    """

    def translate(self, text: str, target: str) -> str:
        return text


class DeepLTranslator:
    """DeepL, with glossary terms held out of its reach.

    `tag_handling=xml` plus `ignore_tags` is DeepL's documented mechanism for
    "leave this span alone". The terms go in wrapped, come back wrapped, and are
    swapped for our Chinese here rather than by the service.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        if not self.settings.deepl_api_key:
            raise TranslationFailed("DEEPL_API_KEY is not set")

    def translate(self, text: str, target: str) -> str:
        payload = urllib.parse.urlencode(
            {
                # Already protected by translate_prose; this just tells DeepL
                # which tag to leave alone.
                "text": text,
                "target_lang": target.upper(),
                "source_lang": "EN",
                "tag_handling": "xml",
                "ignore_tags": glossary.PROTECT_TAG,
                # Course descriptions are institutional prose, not chat.
                "formality": "prefer_more",
                "preserve_formatting": "1",
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            self.settings.deepl_api_url,
            data=payload,
            headers={
                "Authorization": f"DeepL-Auth-Key {self.settings.deepl_api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.settings.deepl_timeout_seconds
            ) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise TranslationFailed(f"DeepL returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise TranslationFailed(f"DeepL unreachable: {exc.reason}") from exc

        try:
            return body["translations"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise TranslationFailed("DeepL returned no translation") from exc


@dataclass(frozen=True, slots=True)
class Translated:
    """A translated passage, and what had to be corrected on the way out."""

    text: str
    repaired_terms: tuple[str, ...] = ()
    leaked_terms: tuple[str, ...] = ()

    @property
    def clean(self) -> bool:
        return not self.repaired_terms and not self.leaked_terms


def translate_prose(text: str, translator: Translator, *, target: str = "zh") -> Translated:
    """Translate one passage and make sure the reserved terms survived it.

    Paragraph breaks are preserved by translating the passage whole:
    `preserve_formatting` keeps them, and splitting first would lose the context
    that makes the second paragraph read as a continuation of the first.

    Never raises on a glossary problem. It repairs what it can and reports what
    it did; the caller decides what to do with a run full of repairs.
    """
    source = text.strip()
    if not source:
        raise TranslationFailed("nothing to translate")

    raw = translator.translate(glossary.protect(source), target)
    restored = glossary.restore(raw)

    repaired, fixed = glossary.repair(source, restored)
    leaked: tuple[str, ...] = ()
    try:
        glossary.check(source, repaired)
    except glossary.GlossaryViolation as exc:
        # A term still in English after protection and repair. Worth counting,
        # not worth throwing the paragraph away over.
        leaked = (str(exc),)

    return Translated(repaired.strip(), tuple(fixed), leaked)
