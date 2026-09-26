"""Deciding whether a curated FAQ answers a question - and saying no.

The FAQ answer is drawn as *the* answer, above everything else, so a wrong one
costs more than none. The first version got this backwards. It matched a FAQ
when the question shared any word with the FAQ's question *or its answer*, then
sorted the matches by a hand-set priority before relevance. So:

* 学生签证续签 answered "How do I withdraw from a unit?", because that answer
  mentions a student visa and withdrawal had the higher priority;
* 学术诚信 answered "When do results come out?", because that answer mentions
  an academic integrity process;
* "scholarship" answered the GPA entry, whose answer mentions scholarships.

Sharing a word is not answering the question. This module asks two things
instead, both of the FAQ's own curated vocabulary rather than its prose:

1. **Is it triggered?** One of the FAQ's ``keywords`` appears in the question.
   Keywords are chosen to be specific to one entry - 退课, "withdraw" - and a
   generic topic word like 签证 lives in ``tags`` instead, where it can support
   a match but never start one. Where one entry's keyword sits inside another's
   (成绩 inside 成绩单), the longer one wins.
2. **Does it cover the question?** Once the FAQ's own words and the filler of a
   question (怎么, "how do I") are taken out, nothing of substance may be left.
   学生签证续签 leaves 续签 behind against the work-hours entry, and a FAQ
   about working on a visa does not answer a question about renewing one.

A triggered FAQ that fails the second test is not thrown away: it becomes a
"related question" the reader can open, which is honest about what it is.
Priority only breaks ties between entries that both passed.

Everything here is pure: no database, no network. The router loads the rows.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from app.search.chinese import CJK

# Words that carry no subject. A question is allowed to be made of these plus
# the FAQ's own vocabulary and still count as fully covered.
EN_FILLER = frozenset({
    "a", "about", "after", "again", "all", "also", "am", "an", "and", "any", "anyone",
    "are", "as", "ask", "at", "be", "been", "before", "being", "best", "but", "by",
    "can", "cannot", "could", "did", "do", "does", "doing", "done", "during", "each",
    "else", "for", "from", "get", "gets", "getting", "give", "go", "going", "got",
    "had", "has", "have", "having", "help", "hi", "hello", "her", "here", "his", "how",
    "i", "if", "im", "in", "into", "is", "it", "its", "just", "know", "let", "like",
    "may", "me", "might", "mine", "more", "most", "much", "must", "my", "need", "needs",
    "needed", "no", "not", "now", "of", "off", "ok", "okay", "on", "once", "one",
    "only", "or", "other", "our", "out", "over", "own", "please", "possible",
    "question", "questions", "really", "should", "so", "some", "someone", "something",
    "still", "such", "tell", "than", "thanks", "thank", "that", "the", "their", "them",
    "then", "there", "these", "they", "thing", "things", "this", "those", "through",
    "to", "too", "under", "until", "up", "us", "use", "used", "using", "very", "want",
    "wanted", "wants", "was", "way", "ways", "we", "were", "what", "whats", "when",
    "where", "whether", "which", "while", "who", "whom", "why", "will", "with", "would",
    "yes", "yet", "you", "your", "yours", "monash", "uni", "university", "student",
    "students",
})

# Single characters that are grammar rather than content in a question, and
# the common question frames. Multi-character entries are removed first.
ZH_FILLER_PHRASES = tuple(sorted({
    "请问", "怎么样", "怎么办", "怎么", "怎样", "如何", "什么时候", "什么", "哪里", "哪儿",
    "哪些", "哪个", "为什么", "是不是", "有没有", "能不能", "可不可以", "可以", "需要",
    "应该", "知道", "告诉", "一下", "我们", "我的", "你们", "自己", "现在", "这个",
    "那个", "还是", "或者", "关于", "相关", "问题", "申请", "办理", "多少", "多久",
    "几个", "一个", "一门", "一周", "要求", "流程", "步骤", "方法", "办法", "情况",
    "学生", "大学", "蒙纳士", "莫纳什", "莫纳士", "有关", "的话", "时间", "要不要",
    "吗", "呢", "吧", "啊", "呀", "了", "的", "得", "地", "我", "你", "他", "她", "它",
    "在", "是", "有", "要", "想", "能", "会", "去", "到", "给", "把", "被", "和", "与",
    "及", "或", "还", "就", "都", "也", "又", "才", "该", "么", "哪", "谁", "几", "个",
    "嘛", "哦", "喔", "嗯", "请", "帮", "问", "下", "上", "从", "对", "让", "用",
    "做", "办", "呐", "哈",
}, key=len, reverse=True))

# Latin tokens, keeping the "+" of C++ and the "." in abbreviations out of it.
WORD = re.compile(r"[a-z0-9]+")
PUNCT = re.compile(r"[\s\W_]+", re.UNICODE)


def normalise(text: str) -> str:
    """Full-width to half-width, lower case, one space between words."""
    text = unicodedata.normalize("NFKC", text or "").lower()
    return PUNCT.sub(" ", text).strip()


def stem(word: str) -> str:
    """Just enough English stemming to make "withdrawing" meet "withdraw".

    Applied to both sides, so a crude cut is still a consistent one.
    """
    for suffix, replacement in (("ies", "y"), ("ing", ""), ("ed", ""), ("es", ""),
                                ("s", ""), ("al", "")):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            word = word[: len(word) - len(suffix)] + replacement
            break
    if len(word) > 3 and word[-1] == word[-2] and word[-1] not in "aeiouls":
        word = word[:-1]
    return word


def _words(text: str) -> list[str]:
    return WORD.findall(normalise(text))


@dataclass(frozen=True)
class FaqCandidate:
    slug: str
    question: str
    keywords: tuple[str, ...]
    tags: tuple[str, ...] = ()
    priority: int = 0
    #: The question in the reader's languages - what they will read, and so
    #: vocabulary the question is allowed to use.
    translated_questions: tuple[str, ...] = ()


@dataclass
class FaqMatch:
    candidate: FaqCandidate
    #: Covers the question: safe to draw as the answer.
    confident: bool
    #: Length of the longest trigger, in a unit where one CJK character counts
    #: like three Latin ones - 退课 is as specific as "withdraw".
    strength: int
    triggers: list[str] = field(default_factory=list)
    residue: list[str] = field(default_factory=list)


def _weight(keyword: str) -> int:
    return sum(3 if CJK.match(ch) else 1 for ch in keyword)


def _find_trigger(query_norm: str, query_stems: list[str], keyword: str) -> tuple[int, int] | None:
    """Where ``keyword`` sits in the query, as a character span, or ``None``."""
    key = normalise(keyword)
    if not key:
        return None
    if CJK.search(key):
        start = query_norm.find(key)
        return (start, start + len(key)) if start >= 0 else None
    # Latin: whole words, compared stem to stem, so "sc" never fires inside
    # "science" and "withdrawing" still finds "withdraw".
    key_stems = [stem(w) for w in WORD.findall(key)]
    if not key_stems:
        return None
    n = len(key_stems)
    for i in range(len(query_stems) - n + 1):
        if query_stems[i:i + n] == key_stems:
            # A span in word positions, offset so it cannot collide with the
            # character spans CJK triggers use.
            return (10_000 + i, 10_000 + i + n)
    return None


def _vocabulary(candidate: FaqCandidate) -> tuple[set[str], list[str]]:
    """Latin stems and CJK strings this FAQ is allowed to be asked with."""
    latin: set[str] = set()
    cjk: list[str] = []
    for text in (candidate.question, *candidate.translated_questions,
                 *candidate.keywords, *candidate.tags):
        latin.update(stem(w) for w in _words(text))
        norm = normalise(text)
        if CJK.search(norm):
            cjk.append(norm)
    return latin, cjk


def _cjk_residue(query_norm: str, vocabulary: list[str]) -> list[str]:
    """CJK runs in the query that neither the FAQ's words nor filler explain."""
    text = re.sub(r"[a-z0-9 ]+", " ", query_norm)
    # Cover every substring of two or more characters that appears in the
    # FAQ's own vocabulary, longest first.
    covered = [False] * len(text)
    for i in range(len(text)):
        for j in range(len(text), i + 1, -1):
            piece = text[i:j]
            if " " in piece:
                continue
            if any(piece in v for v in vocabulary):
                for k in range(i, j):
                    covered[k] = True
                break
    left = "".join(ch if not covered[i] else " " for i, ch in enumerate(text))
    for phrase in ZH_FILLER_PHRASES:
        left = left.replace(phrase, " ")
    # A lone character left over is grammar the filler list missed (开 in
    # 怎么开成绩单, 留 once 学生 is taken out of 留学生) far more often than it
    # is a subject. Two or more is a word, and a word is a subject.
    return [run for run in left.split() if CJK.search(run) and len(run) >= 2]


def _residue(query_norm: str, query_words: list[str], candidate: FaqCandidate,
             ignore: set[str]) -> list[str]:
    latin, cjk = _vocabulary(candidate)
    leftover = [
        w for w in query_words
        if w not in EN_FILLER and stem(w) not in latin and w not in ignore
        and not w.isdigit()
    ]
    return leftover + _cjk_residue(query_norm, cjk)


def match(query: str, candidates: list[FaqCandidate], *,
          ignore: set[str] | None = None) -> list[FaqMatch]:
    """Every triggered FAQ, the ones that cover the question first.

    ``ignore`` holds Latin words already accounted for elsewhere - the unit
    code in "FIT2004 怎么退课" is the router's business, not residue.
    """
    ignore = {w.lower() for w in (ignore or set())}
    query_norm = normalise(query)
    if not query_norm:
        return []
    query_words = WORD.findall(query_norm)
    query_stems = [stem(w) for w in query_words]

    # Every trigger of every candidate, as spans, so a keyword sitting inside a
    # longer keyword of another entry can be discarded.
    hits: list[tuple[FaqCandidate, str, tuple[int, int]]] = []
    for candidate in candidates:
        for keyword in candidate.keywords:
            span = _find_trigger(query_norm, query_stems, keyword)
            if span is not None:
                hits.append((candidate, keyword, span))

    def shadowed(span: tuple[int, int], owner: str) -> bool:
        return any(
            other.slug != owner and s[0] <= span[0] and span[1] <= s[1] and s != span
            for other, _, s in hits
        )

    by_slug: dict[str, FaqMatch] = {}
    for candidate, keyword, span in hits:
        if shadowed(span, candidate.slug):
            continue
        found = by_slug.get(candidate.slug)
        if found is None:
            found = by_slug[candidate.slug] = FaqMatch(candidate, False, 0)
        found.triggers.append(keyword)
        found.strength = max(found.strength, _weight(keyword))

    # Asking the FAQ's own question - a suggestion chip being clicked - is
    # always a trigger, whatever the keywords say.
    for candidate in candidates:
        if candidate.slug in by_slug:
            continue
        if any(normalise(q) == query_norm
               for q in (candidate.question, *candidate.translated_questions)):
            by_slug[candidate.slug] = FaqMatch(candidate, False, 1_000, ["<question>"])

    for found in by_slug.values():
        found.residue = _residue(query_norm, query_words, found.candidate, ignore)
        found.confident = not found.residue

    return sorted(
        by_slug.values(),
        key=lambda m: (m.confident, m.strength, len(m.triggers), m.candidate.priority),
        reverse=True,
    )
