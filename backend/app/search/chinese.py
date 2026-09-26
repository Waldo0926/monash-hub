"""Making a Chinese query find something.

The interface has been Chinese for a while and the content mostly is too, but
search was still English-only: a student who reads the whole site in Chinese had
to type English into the box. Typing 休学 returned nothing, on a site with a page
about intermission.

Two things stand in the way, and they need different answers.

**PostgreSQL cannot tokenise Chinese.** `to_tsvector('english', '选课与注册')`
produces one meaningless token, because the English parser looks for spaces and
Chinese has none. The real fix is `zhparser` or `pg_jieba`, which are server-side
extensions we cannot install on a shared box. What we do have is `pg_trgm`,
already installed and already indexed for typo tolerance on titles - and trigrams
work on Chinese. Better than work: for a language without word boundaries,
substring *is* the natural query, because a student typing 学籍统计 is typing a
contiguous run and means it.

**A translated page is not a translated index.** The Chinese lives in
`content_translations`, which search never joined to. `search_zh` on the row is
that text flattened out where an index can reach it; `app/search/reindex_zh.py`
fills it.

On top of both, the glossary earns its keep a second time. It already knows that
census date is 学籍统计日, so a query containing 学籍统计日 can be expanded to
also search for "census date" in the English tsvector - which finds the page even
where nobody has translated its body yet. That expansion is the difference
between "Chinese search works on the pages we translated" and "Chinese search
works".
"""
from __future__ import annotations

import re
from functools import lru_cache

from app.knowledge import glossary
from app.search import synonyms

# CJK ideographs, plus the kana and Hangul the other two locales need. A query
# with any of these cannot be served by the English text search config.
CJK = re.compile(
    r"[぀-ヿ"      # hiragana, katakana
    r"㐀-䶿"       # CJK extension A
    r"一-鿿"       # CJK unified ideographs
    r"가-힯]"      # Hangul syllables
)

# Runs of CJK inside a translation, so "census date（学籍统计日）" yields the
# Chinese half without the English that is already searchable on its own.
CJK_RUN = re.compile(
    r"[぀-ヿ㐀-䶿一-鿿가-힯]{2,}"
)

# Below this a "run" is a single character doing duty as a particle, and it
# matches half the corpus. 课 alone is not a search term; 选课 is.
MIN_RUN = 2

# More than this and the expansion is noise rather than recall - a long query
# containing many terms should be answered by the trigram match on the text.
MAX_EXPANSIONS = 6


def has_cjk(text: str | None) -> bool:
    return bool(text and CJK.search(text))


@lru_cache(maxsize=1)
def _reverse_index() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """CJK run -> the English it means, longest run first.

    Two sources, in order of authority:

    1. ``app/search/synonyms.py`` - the words students type (续签, 挂科, 转专业)
       mapped to the words Monash writes. Nobody translating a policy page ever
       needed these, so the glossary cannot know them.
    2. The glossary, read backwards - so a term added for the translator is
       searchable the same day without anyone remembering to add it here too.
       Japanese and Korean come from here as well: the glossary carries all
       three locales and the reverse lookup does not care which one it is.

    Longest first because 学籍统计日 must win over 学籍.
    """
    pairs: dict[str, list[str]] = {}

    def add(run: str, english: str) -> None:
        alternatives = pairs.setdefault(run, [])
        if english not in alternatives:
            alternatives.append(english)

    for run, alternatives in synonyms.ZH_TERMS.items():
        for english in alternatives:
            add(run, english)

    glossary_pairs: dict[str, str] = {}
    for source, translations in ((*glossary.TERMS.items(), *glossary.ENUMS.items())):
        for locale in ("zh", "ja", "ko"):
            written = translations.get(locale)
            if not written:
                continue
            for run in CJK_RUN.findall(written):
                if len(run) < MIN_RUN:
                    continue
                # First writer wins: TERMS is iterated before ENUMS, and a term
                # is the more specific of the two.
                glossary_pairs.setdefault(run, source)
    for run, english in glossary_pairs.items():
        # A curated search synonym is the better authority for a word it
        # covers. The glossary maps 退课 to "discontinue" because that is how
        # one Handbook sentence used it; a student typing 退课 means withdraw.
        if run not in synonyms.ZH_TERMS:
            add(run, english)

    return tuple(
        (run, tuple(alternatives))
        for run, alternatives in sorted(pairs.items(), key=lambda kv: -len(kv[0]))
    )


def concept_runs(term: str) -> list[tuple[str, tuple[str, ...]]]:
    """Each CJK run the query uses, with the English alternatives it means.

    Runs never overlap, and the longest wins: 学籍统计日 is one concept, not
    学籍统计日 plus a shorter fragment that drags in every page about enrolment.
    """
    if not has_cjk(term):
        return []
    found: list[tuple[str, tuple[str, ...]]] = []
    taken = [False] * len(term)
    for run, alternatives in _reverse_index():
        start = term.find(run)
        while start >= 0 and any(taken[start:start + len(run)]):
            start = term.find(run, start + 1)
        if start < 0:
            continue
        for index in range(start, start + len(run)):
            taken[index] = True
        if all(alternatives != seen for _, seen in found):
            found.append((run, alternatives))
        if len(found) >= MAX_EXPANSIONS:
            break
    return found


def concepts(term: str) -> list[tuple[str, ...]]:
    """The distinct things a CJK query asks about, each as its English alternatives.

    学生签证续签 is two concepts - student visa, and renewing one - and a page
    has to be about both to answer it. Returning them separately is what lets
    the search AND the concepts and OR the alternatives inside each: before,
    every expansion was ORed together, so 签证 alone matched and the question
    about renewing a visa was answered with a sentence that mentioned visas.
    """
    return [alternatives for _, alternatives in concept_runs(term)]


def chinese_for(term: str) -> list[str]:
    """Chinese words an English query means, from the search synonym table.

    The other direction from :func:`expand`, and deliberately narrower: only a
    whole English alternative matching the whole query counts. It exists for
    the one kind of content that is written in Chinese to begin with - student
    posts - so that "withdraw" also finds a post titled 退课.
    """
    wanted = " ".join((term or "").lower().split())
    if not wanted or has_cjk(wanted):
        return []
    return [run for run, alternatives in synonyms.ZH_TERMS.items() if wanted in alternatives]


def expand(term: str) -> list[str]:
    """Every English term implied by the CJK in ``term``, flattened."""
    flat: list[str] = []
    for alternatives in concepts(term):
        for english in alternatives:
            if english not in flat:
                flat.append(english)
    return flat


LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z0-9+#.-]*")


def latin_part(term: str) -> str:
    """The Latin-script words in a mixed query - "SC" in 怎么申请 SC."""
    return " ".join(LATIN_WORD.findall(term or ""))


def expanded_query(term: str) -> str:
    """The query as one ``websearch_to_tsquery`` string, every expansion ORed.

    This is the loose form: it finds a page that mentions any one concept.
    ``app/search/service.py`` builds the strict form - every concept present -
    out of :func:`concepts` and falls back to this one only when the strict
    form finds nothing.

    The Chinese is left in rather than stripped: a query that is only Chinese
    would otherwise become empty, and an empty tsquery matches everything.
    An English query expands to nothing and comes back untouched, so English
    search keeps its AND semantics exactly as before.
    """
    extra = expand(term)
    if not extra:
        return term
    return " or ".join([term, *extra])
