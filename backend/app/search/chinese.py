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
def _reverse_index() -> tuple[tuple[str, str], ...]:
    """Chinese run -> the English term it translates, longest run first.

    Built from the glossary rather than maintained separately, so a term added
    for the translator is searchable the same day without anyone remembering to
    add it here too. Longest first because 学籍统计日 must win over 学籍.
    """
    pairs: dict[str, str] = {}
    for source, translations in ((*glossary.TERMS.items(), *glossary.ENUMS.items())):
        chinese = translations.get("zh")
        if not chinese:
            continue
        for run in CJK_RUN.findall(chinese):
            if len(run) < MIN_RUN:
                continue
            # First writer wins: TERMS is iterated before ENUMS, and a term is
            # the more specific of the two.
            pairs.setdefault(run, source)
    return tuple(sorted(pairs.items(), key=lambda kv: -len(kv[0])))


def expand(term: str) -> list[str]:
    """English terms implied by the Chinese in ``term``.

    Only whole glossary runs count, and a run already covered by a longer match
    is skipped - otherwise 学籍统计日 expands to both "census date" and whatever
    shorter fragment sits inside it, and the shorter one drags in every page
    that mentions enrolment.
    """
    if not has_cjk(term):
        return []
    found: list[str] = []
    consumed: list[tuple[int, int]] = []
    for run, english in _reverse_index():
        start = term.find(run)
        if start < 0:
            continue
        end = start + len(run)
        if any(s <= start and end <= e for s, e in consumed):
            continue
        consumed.append((start, end))
        if english not in found:
            found.append(english)
        if len(found) >= MAX_EXPANSIONS:
            break
    return found


def expanded_query(term: str) -> str:
    """The query as the English text search should see it.

    Joined with ``or``, which is the whole trick. ``websearch_to_tsquery`` ANDs
    bare words, so "休学 intermission" asks for a document containing both - and
    no English page contains 休学, so the expansion made the query match *less*
    rather than more. Searching 休学 returned nothing for exactly that reason.

    The Chinese is left in rather than stripped: a query that is only Chinese
    would otherwise become empty, and an empty tsquery matches everything.

    An English query expands to nothing and comes back untouched, so English
    search keeps its AND semantics exactly as before.
    """
    extra = expand(term)
    if not extra:
        return term
    return " or ".join([term, *extra])
