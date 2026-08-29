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

from app.knowledge import degrees, titles
from app.knowledge.glossary import (
    GENERAL,
    MASKS,
    has_verbatim,
    is_critical,
    is_only_placeholders,
    placeholders_survived,
    protect,
    restore,
    terms_in,
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

# A short all-capitals token standing on its own is a code, not a word. The
# results legend is a whole table of them - P, N, NE, NGO, SFR, WDN - and the
# model reads every one as English: P came back as 页, NGO as 非政府组织, SFR
# as 南锥体. The code is what a student matches against their own transcript,
# so it has to survive verbatim. The column beside it is the part to translate.
_CODE = re.compile(r"^[A-Z][A-Z0-9]{0,4}$")

# A stored string that runs over several lines is usually two things stuck
# together - a link's own title and the sentence beneath it - and handing the
# model both at once makes it hallucinate instead of translate. "Policy
# bank\n \nTake a look at our policy bank ..." came back with a wiki's
# citation error message spliced into the middle. Each line is its own
# translation problem, so each is translated alone and put back with the
# separator it arrived with.
_LINES = re.compile(r"(\s*\n\s*)")

# A label is not a sentence, and the dates pages are made of labels: "Trimester
# 1 (T1-58) (Except Faculty of Law units)", "Summer semester A (SSA-02)". Handed
# over whole, the model reads one as prose and takes the period code apart -
# Semester 2 came back as 学士2 and Trimester 1 as 三月一日. Each bracket is its
# own small problem, and the head of the label is usually a closed-list value
# the glossary already has agreed wording for, so nothing is left to guess at.
_BRACKETED = re.compile(r"\s*[（(]\s*([^()（）]*?)\s*[）)]")
# Only for labels. A sentence has brackets too - "after the census date (but
# before the Withdrawn Fail date) your record will show ..." - and splitting one
# at its brackets leaves the head of the sentence to stand on its own, which is
# how that page came back with its first clause still in English. A label has no
# sentence-ending punctuation and a short head; prose has one or the other.
_LABEL_HEAD = 40

# When a whole string cannot be managed, the sentences it is made of usually
# can. "Census date: Term 4 (T4-57). Last day to withdraw from units without
# incurring fees. Units withdrawn after this date will show as WN." lost its
# period code and so lost all three sentences, when only the first one was
# ever in question. Split on a full stop that ends a sentence, not on the one
# inside 11.55pm - the space after it is what tells them apart.
#
# Two more boundaries, both found by looking at what was still English after
# every other repair:
#
# * A full stop or a colon with no space after it. The transcripts page arrives
#   from the crawler as "... information about you:If a unit is marked as
#   Incomplete ... available yet.Masters awarded with ..." - four sentences with
#   the spaces lost between them, and far too long to translate as one. Both
#   rules want a lowercase letter in front of the mark, so that "U.S." and
#   "11.55pm" are left alone.
# * A dash standing in for a clause break: "unsure about continuing your course
#   – we're here to help". Lowercase on both sides, so that "1 Jul – 30 Sep
#   2026" is left whole - a span split at its dash is how a start date was
#   published as a single day in September.
_SENTENCES = re.compile(
    r"((?<=[.!?])\s+"
    r"|(?<=[a-z][.!?:])(?=[A-Z])"
    r"|(?<=[a-z])\s+[–—]\s+(?=[a-z]))"
)

# Asked to translate a short heading the model sometimes signs its work with
# the name of a language: "Discontinue your course" came back as
# 退课你的学位课程（英语）. and "1 Apr 2026" as 2026年4月1日（中文（简体)）. It is
# never part of the sentence, and it is only ever the last thing in it.
_TRAILING_BRACKET = re.compile(
    r"[（(]([^（(]*(?:[（(][^）)]*[）)])?[^（(]*)[）)]{1,2}\s*[.。]?\s*$"
)
_LANGUAGE_NAMES = frozenset({
    "英语", "英文", "英語", "中文", "中文简体", "简体中文", "繁体中文",
    "日语", "日本語", "韩语", "한국어",
})
_LANGUAGE_WORDS = re.compile(r"English|Chinese|Mandarin|Japanese|Korean|language", re.I)


def _mask_debris(restored: str, source: str, mask: tuple[str, str]) -> bool:
    """Whether the restored text still carries pieces of the mask.

    Surviving is not the same as being copied once. The model sometimes repeats
    an invented token - the more so when it is punctuation, and "#a#" is - so
    every placeholder is present, restore puts the terms back, and the spare
    delimiters stay behind where the reader can see them.

    The English is the yardstick: a page may legitimately contain a "#", but it
    cannot contain more of them after translation than it did before.
    """
    for edge in {piece for piece in mask if piece}:
        if restored.count(edge) > source.count(edge):
            return True
    return False


def _is_label(source: str) -> bool:
    """Whether this is a bracketed label rather than a sentence with brackets."""
    match = _BRACKETED.search(source)
    if not match or re.search(r"[.!?。！？]", source):
        return False
    return match.start() <= _LABEL_HEAD


def _unsigned(text: str, source: str) -> str:
    """Drop a trailing bracket that names a language rather than saying anything.

    Unless the English was about a language itself, in which case the brackets
    are the translation doing its job.
    """
    if _LANGUAGE_WORDS.search(source):
        return text
    match = _TRAILING_BRACKET.search(text)
    if match and re.sub(r"[（()）\s]", "", match.group(1)) in _LANGUAGE_NAMES:
        return text[: match.start()].strip()
    return text


# Argos emits ASCII punctuation into CJK text, which reads as a foreign body in
# a Chinese or Japanese sentence. Korean uses ASCII punctuation, so it is left
# alone.
_PUNCTUATION = {
    "zh": {",": "，", ";": "；", ":": "：", "?": "？", "!": "！", "(": "（", ")": "）"},
    "ja": {",": "、", ";": "；", ":": "：", "?": "？", "!": "！", "(": "（", ")": "）"},
}
_CJK = r"㐀-䶿一-鿿぀-ヿ가-힯"

# Monash writes the curly apostrophe and the model was trained on the straight
# one. Measured over the sentences that were failing on the live guides,
# straightening it alone recovers eight of them - three of which then survive
# the very first mask. What cost those sentences their Chinese was the shape of
# the apostrophe in "you're", not the token standing beside it.
_CURLY = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})

# What the model produces when it has given up on a string and started
# inventing. 兹卡 is its transliteration of the Zqa mask token and no Monash
# page is about Zika; a run of one repeated letter is not a word in any of the
# four languages. M6024's "SPECIALISATIONS AVAILABLE" came back as
# 专业方向 AVALALLILL（兹卡 AVALLLLL）.
_INVENTED = re.compile(r"兹卡|\b\w*([A-Za-z])\1{3,}\w*\b")


def _invented(result: str, source: str) -> bool:
    """Whether the model made something up rather than translating.

    Checked against the source, because a string that genuinely repeats a
    letter should survive - and because the honest outcome for a string the
    model cannot manage is the English, not an approximation of it.
    """
    return bool(_INVENTED.search(result)) and not _INVENTED.search(source)


class Translator:
    """One loaded model per language, translating with the glossary in front."""

    #: Which glossary scope the strings being translated belong to. A class
    #: attribute so an instance built without ``__init__`` - the tests do that
    #: to avoid loading a model - still has one.
    scope: str = GENERAL

    def __init__(self, locale: str, scope: str = GENERAL) -> None:
        if locale not in SUPPORTED:
            raise ValueError(f"no model for {locale!r}")
        self.locale = locale
        # One cache per scope. The same English sentence is allowed to have two
        # renderings - "complete the major" means one thing in a degree's
        # structure and another in a unit's overview - so they must not share
        # an entry.
        self._caches: dict[str, dict[str, str]] = {}
        self._renderings: dict[str, str] = {}
        self._lock = threading.Lock()
        self.use_scope(scope)
        self._translate = _load_model(locale)

    def use_scope(self, scope: str) -> None:
        """Translate the strings that follow as ``scope`` (see the glossary)."""
        self.scope = scope
        self._cache: dict[str, str] = self._caches.setdefault(scope, {})

    @property
    def cached(self) -> int:
        return sum(len(cache) for cache in self._caches.values())

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

        if "\n" in source:
            return self._by_line(source)

        # A complete field value off one of the Handbook's closed lists - a
        # campus, a teaching period, an assessment type. Agreed wording, not a
        # translation problem.
        agreed = whole_value(source, self.locale)
        if agreed:
            self._cache[source] = agreed
            return agreed

        # A degree's name is built, not translated - English names it
        # front-to-back and Chinese back-to-front, and a model asked for the
        # whole string drops the discipline or renders "Master" as 大师. The
        # discipline itself goes through this same method, so it still gets the
        # glossary. See app/knowledge/degrees.py.
        composed = degrees.compose(source, self.locale, self.text)
        if composed:
            self._cache[source] = composed
            return composed

        # The same reordering problem in unit titles: "Introduction to X" is
        # X导论, not 导论到X. See app/knowledge/titles.py.
        composed = titles.compose(source, self.locale, self.text)
        if composed:
            self._cache[source] = composed
            return composed

        masked, terms = protect(source, self.locale, scope=self.scope)
        if is_only_placeholders(masked):
            # Entirely known terms - a unit title like "Programming paradigms",
            # a campus name, an assessment type. Nothing for the model to do,
            # but still something to tidy: the space that separated the English
            # words is left sitting between two Chinese ones, and "Accounting
            # fundamentals" came out as 会计 基础.
            result = _tidy(restore(masked, terms), self.locale)
        elif _CODE.match(source):
            # A grade code on its own. Checked after the glossary, so a term
            # that happens to look like one - WAM - still gets its agreed
            # wording rather than being left in English.
            self._cache[source] = ""
            return None
        else:
            try:
                attempt = self._masked(source)
            except Exception as exc:  # one bad string must not end a batch of 5,000
                log.warning("translation failed (%s): %s", exc, source[:60])
                self._cache[source] = ""
                return None
            if attempt is None:
                # Every token was rewritten rather than copied - see ``_masked``.
                if _is_label(source):
                    by_bracket = self._by_bracket(source)
                    if by_bracket:
                        return by_bracket
                if has_verbatim(source):
                    # What went missing was a date, a time or a code. The repair
                    # below re-translates with nothing masked, and unmasked is
                    # exactly how "1 Aug 2024" came back as 2024年8月1日纽约.
                    # There is nothing to look for and nothing to guess at, so
                    # this attempt is over - but the other sentences in the
                    # string were never in question.
                    log.debug("a date or a code was rewritten: %s", source[:60])
                    return self._by_sentence(source)
                if _SENTENCES.search(source):
                    # Several sentences are each a smaller problem: a
                    # placeholder in a short sentence usually survives, and the
                    # repair below is a heuristic - it reads 课程 in 课程框架 (a
                    # curriculum framework) as proof that *unit* was rendered
                    # right, and let 单位 through on the paragraph it could not
                    # manage.
                    by_sentence = self._by_sentence(source)
                    if by_sentence:
                        return by_sentence
                repaired = self._agreed_wording(source)
                if repaired is None:
                    log.debug("placeholder lost: %s", source[:60])
                    return self._by_sentence(source)
                result = repaired
            else:
                translated, terms, mask = attempt
                # Tidy after restoring, not before: with the placeholders still
                # in place the punctuation rules see a Latin character where
                # the finished sentence has a Chinese one, and leave the comma
                # alone.
                result = _tidy(restore(translated, terms, mask), self.locale)

        result = _unsigned(result.strip(), source)
        if _invented(result, source):
            # Better the English than a sentence nobody wrote. An untranslated
            # string stays in English; it is never approximated.
            log.debug("invented output discarded: %s", source[:60])
            self._cache[source] = ""
            return None
        # A "translation" identical to the source is not one. Storing it would
        # mean the reader sees English behind a banner promising Chinese.
        if result == source:
            self._cache[source] = ""
            return None
        self._cache[source] = result
        return result

    def _ask(self, text: str) -> str:
        """Hand a string to the model in the punctuation it was trained on."""
        return self._translate(text.translate(_CURLY))

    def _masked(self, source: str) -> tuple[str, list[str], tuple[str, str]] | None:
        """Translate with the terms masked, until a mask comes back intact.

        The model usually copies an invented token and occasionally
        transliterates one: "What is Zqa?" came back from a live page as
        什么是兹卡?, and restoring cannot find a token that is no longer there.
        Whether it does that is a property of the token in the sentence, not of
        invented tokens in general - the same sentence masked as Xya comes back
        with Xya still in it - and it is not predictable from reading either.

        Measured over the sentences that were actually failing on the live
        guides, no single token carries them all and the ones each token loses
        are largely different sentences, so the masks are tried in turn. Only a
        sentence that has already failed pays for the extra calls, and the
        alternative it is being compared against is the reader seeing English.

        Returns the translation, the replacements and the mask that survived.
        """
        for mask in MASKS:
            masked, terms = protect(source, self.locale, mask, scope=self.scope)
            translated = self._ask(masked)
            if not placeholders_survived(translated, len(terms), mask):
                log.debug("mask %s was rewritten: %s", mask[0], source[:60])
                continue
            if _mask_debris(restore(translated, terms, mask), source, mask):
                # Every token is present and there is still mask left over. The
                # model repeated the token instead of copying it once - "#a#"
                # came back as "#B#A#(SSA-02) #B#A#(SSA-02)" - and restoring
                # leaves the spare punctuation on the page: 在总的课程g#中达到50%.
                log.debug("mask %s was repeated: %s", mask[0], source[:60])
                continue
            return translated, terms, mask
        return None

    def _agreed_wording(self, source: str) -> str | None:
        """Translate with nothing masked, then put the agreed terms back.

        Masking exists because the model renders *census date* as 人口普查日期.
        When the mask does not survive, the answer is not to accept that
        rendering but to go and find it: the model translates a term the same
        way on its own as it does inside a sentence, so translating the bare
        term says what to look for. A term whose rendering cannot be found
        leaves the sentence in English - the same place it was already headed.
        """
        try:
            plain = self._ask(source)
        except Exception as exc:  # one bad string must not end a batch of 5,000
            log.warning("translation failed (%s): %s", exc, source[:60])
            return None
        # Longest agreed wording first, and each one claimed off a working copy
        # as it is found: *course* is 学位课程 and *unit* is 课程, so checking
        # the short one against the whole sentence reads the rendering of
        # "course" as proof that "unit" came out right. That is how 单位 - the
        # one word this glossary exists to keep out - reached a live page.
        unclaimed = plain
        for written, agreed in sorted(
            terms_in(source, self.locale, scope=self.scope), key=lambda pair: -len(pair[1])
        ):
            if agreed in unclaimed:
                # Every occurrence, not the first: "course" is written three
                # times in one Handbook sentence, and the two copies of
                # 学位课程 left behind were enough to answer for *unit* as well.
                unclaimed = unclaimed.replace(agreed, "")
                continue  # the model happened to land on the agreed wording
            rendered = self._bare(written)
            if rendered and rendered in plain:
                plain = plain.replace(rendered, agreed)
                unclaimed = unclaimed.replace(rendered, "")
                continue
            if written in plain:
                # An acronym the model copied rather than translated - WAM,
                # NSR, SFR come back untouched. That is the term still in
                # English, not a wrong rendering of it, so it can be replaced.
                plain = plain.replace(written, agreed)
                unclaimed = unclaimed.replace(written, "")
                continue
            if is_critical(written):
                # Rendered some third way in context, and this is a term a
                # student acts on with their money or their visa. English, and
                # no guessing at it.
                return None
            # Anything else: the model's own wording stands rather than the
            # whole sentence going back to English over a word like "results".
            log.debug("kept the model's wording for %r in: %s", written, source[:50])
        return _tidy(plain, self.locale)

    def _bare(self, term: str) -> str:
        """What the model makes of a term on its own. Cached - terms repeat."""
        with self._lock:
            known = self._renderings.get(term)
        if known is None:
            try:
                known = self._ask(term).strip().strip("。.")
            except Exception:
                known = ""
            with self._lock:
                self._renderings[term] = known
        return known

    def _by_line(self, source: str) -> str | None:
        """Translate a multi-line string a line at a time.

        The separators are kept, so a heading and the sentence beneath it come
        back arranged the way they arrived. A line the model cannot manage
        keeps its English instead of taking the rest of the string down with
        it, which is what happened while the whole blob was one call.
        """
        parts = _LINES.split(source)
        rendered: list[str] = []
        translated_any = False
        for index, part in enumerate(parts):
            if index % 2 or not part.strip():
                rendered.append(part)  # a separator, or the blank line itself
                continue
            done = self.text(part)
            rendered.append(done or part)
            translated_any = translated_any or bool(done)
        if not translated_any:
            self._cache[source] = ""
            return None
        result = "".join(rendered).strip()
        self._cache[source] = result
        return result

    def _by_bracket(self, source: str) -> str | None:
        """Translate a bracketed label a part at a time.

        "Summer semester A (SSA-02)" is a teaching period the glossary knows and
        a code that must not be touched, stuck together with a bracket. As one
        string it is neither, and the model treats it as prose: the code goes in
        and something else comes out. Split, the head matches a closed list and
        each bracket is either a code or a short qualifier.

        A bracket holding Chinese is closed full-width and a bracket holding a
        code is not: the code is what a student matches against their own
        enrolment, and it is written in ASCII on every Monash page.
        """
        parts: list[str] = []
        position = 0
        for match in _BRACKETED.finditer(source):
            parts.append(source[position : match.start()])
            parts.append(match.group(1))
            position = match.end()
        parts.append(source[position:])

        rendered: list[str] = []
        translated_any = False
        for index, part in enumerate(parts):
            stripped = part.strip()
            if not stripped:
                continue
            done = self.text(stripped)
            translated_any = translated_any or bool(done)
            text = done or stripped
            if not index % 2:
                rendered.append(text)
            elif re.search(rf"[{_CJK}]", text):
                rendered.append(f"（{text}）")
            else:
                rendered.append(f" ({text})")
        if not translated_any:
            self._cache[source] = ""
            return None
        result = _tidy("".join(rendered), self.locale)
        self._cache[source] = result
        return result

    def _by_sentence(self, source: str) -> str | None:
        """Translate a string one sentence at a time, after the whole failed.

        The same bargain as ``_by_line``: a sentence the engine will not vouch
        for keeps its English rather than taking the paragraph with it. Called
        only after the string as a whole has been given up on, so the extra
        model calls are paid for by the strings that would otherwise be shown
        to a Chinese reader in English.
        """
        parts = _SENTENCES.split(source)
        if len(parts) < 3:  # one sentence: there is nothing left to try
            self._cache[source] = ""
            return None
        rendered: list[str] = []
        translated_any = False
        for index, part in enumerate(parts):
            if index % 2 or not part.strip():
                rendered.append(part)
                continue
            done = self.text(part)
            rendered.append(done or part)
            translated_any = translated_any or bool(done)
        if not translated_any:
            self._cache[source] = ""
            return None
        result = _tidy("".join(rendered), self.locale)
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
        #
        # Spaces and tabs, never `\s`: a blank line between two paragraphs is
        # whitespace too, and the version that used `\s*` closed the gap -
        # "（每周5小时)\n\n参加研讨会" came out as one run-on paragraph.
        for ascii_mark, wide in mapping.items():
            text = re.sub(
                rf"(?<=[{_CJK}])[ \t]*{re.escape(ascii_mark)}[ \t]*(?=[{_CJK}])",
                wide,
                text,
            )
        # A bracket around Chinese is a Chinese bracket. The rule below only
        # sees a bracket with Chinese on both sides, so "第 1 学段 (T1-58)
        # (法学院课程除外)" kept the ASCII pair around a wholly Chinese
        # qualifier - which is the same call `_by_bracket` makes when it
        # assembles a label itself.
        text = re.sub(
            rf"\s*\(([^()]*[{_CJK}][^()]*)\)", r"（\1）", text
        )
        # A bracket opened full-width is closed full-width, wherever the
        # closing one happens to sit. The rule above only sees a bracket with
        # Chinese on both sides, so "（每周5小时)" at the end of a line kept
        # its half-width half and looked broken.
        text = re.sub(r"（([^（）]*)\)", r"（\1）", text)
        # Sentence-final full stop, which the rule above cannot see.
        text = re.sub(rf"(?<=[{_CJK}])[ \t]*\.[ \t]*$", "。", text)
        text = re.sub(rf"(?<=[{_CJK}])[ \t]*\.[ \t]+(?=[{_CJK}])", "。", text)
    # "grade point average (GPA)" is two reserved terms, and each one's agreed
    # wording carries the other: restoring both writes 平均绩点（GPA）（GPA（平均
    # 绩点））. The gloss is already there, so the bracket the English wrote is
    # the one to drop.
    text = re.sub(
        r"(?P<a>[^（）\s]+)（(?P<b>[^（）]+)）\s*[（(](?P=b)[（(](?P=a)[）)][）)]",
        r"\g<a>（\g<b>）",
        text,
    )
    # Two CJK words with a space between them is an artefact of putting a
    # glossary term back where a placeholder was; Chinese and Japanese do not
    # space words. A space between Latin and CJK is correct and stays
    # ("Monash 大学"), and so is one before a digit ("第 2 级").
    text = re.sub(rf"(?<=[{_CJK}])[ \t]+(?=[{_CJK}])", "", text)
    # A space against CJK punctuation is not - on either side of it. The
    # closing bracket of an agreed term ("WAM（加权平均分）") is the common
    # case: the term goes back in where a Latin word was, and the space that
    # followed the Latin word stays behind.
    text = re.sub(r"[ \t]+(?=[，。、；：？！）])", "", text)
    text = re.sub(rf"(?<=[，。、；：？！）])[ \t]+(?=[{_CJK}])", "", text)
    text = re.sub(r"(?<=（)[ \t]+", "", text)
    text = re.sub(r"[ \t]{2,}", " ", text).strip()
    for transliterated, name in _HOUSE.get(locale, {}).items():
        text = text.replace(transliterated, name)
    return text


# The model sometimes writes the university's name out in Chinese even when it
# was never given it to translate - 莫纳什 arrived in sentences where "Monash"
# had been masked out. No reviewed translation on this site has ever used it,
# and a student cannot match it against the address on their own email.
_HOUSE = {"zh": {"莫纳什大学": "Monash 大学", "莫纳什": "Monash", "蒙纳士": "Monash"}}
