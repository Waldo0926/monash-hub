"""Unit titles that name a topic and then modify it.

The same failure as a degree name, in a different place. English puts the
qualifier first - *Introduction to financial accounting* - and Chinese puts it
last: 财务会计导论. A general translator handles the words and not the order,
and measured over the 2026 catalogue it gets the order wrong about as often as
it gets it right:

    Introduction to  123 units   65 wrong   导论到解剖学, 导论与公共关系,
                                            导论改为学术研究
    Foundations of    49 units   17 wrong
    Principles of     47 units   12 wrong
    Fundamentals of   23 units   10 wrong

Those readings are not merely clumsy: 导论改为学术研究 says "the introduction
has been changed to academic research".

So the qualifier is taken off, the topic is translated by the ordinary pipeline
- which is good at topics, 财务会计 needs no help - and the two are put back in
Chinese order. Same reasoning as ``degrees.py``, and the same restraint: a title
whose shape is not this one is returned as ``None`` and left alone.
"""
from __future__ import annotations

import re

LOCALES = ("zh", "ja", "ko")

#: English qualifier -> what it becomes, written after the topic.
QUALIFIERS: dict[str, dict[str, str]] = {
    "Introduction to": {"zh": "导论", "ja": "入門", "ko": "개론"},
    "An introduction to": {"zh": "导论", "ja": "入門", "ko": "개론"},
    "Foundations of": {"zh": "基础", "ja": "の基礎", "ko": "기초"},
    "Fundamentals of": {"zh": "基础", "ja": "の基礎", "ko": "기초"},
    "Principles of": {"zh": "原理", "ja": "の原理", "ko": "원리"},
}

_ALTERNATION = "|".join(
    re.escape(q) for q in sorted(QUALIFIERS, key=lambda q: (-len(q), q))
)
_SHAPE = re.compile(rf"^(?P<qualifier>{_ALTERNATION})\s+(?P<topic>.+)$", re.IGNORECASE)

# A topic carrying its own punctuation is a title with a structure of its own -
# "Introduction to X: theory and practice" - and appending the qualifier to the
# end of all of it would attach it to the subtitle instead of the subject.
_HAS_STRUCTURE = re.compile(r"[:;,]|\band\b")


def compose(title: str, locale: str, translate) -> str | None:
    """The title in ``locale``, or ``None`` to leave it to the caller.

    ``translate`` renders the topic. Returning ``None``, or the English
    unchanged, means no translation was available and the whole title is left to
    the ordinary path rather than composed half in English.
    """
    if locale not in LOCALES:
        return None
    shape = _SHAPE.match(title.strip())
    if not shape:
        return None

    topic = shape.group("topic").strip()
    if not topic or _HAS_STRUCTURE.search(topic):
        return None

    rendered = translate(topic)
    if not rendered or rendered.strip() == topic:
        return None

    qualifier = QUALIFIERS[_canonical(shape.group("qualifier"))][locale]
    return f"{rendered.strip()}{qualifier}"


def _canonical(written: str) -> str:
    lowered = written.strip().lower()
    for key in QUALIFIERS:
        if key.lower() == lowered:
            return key
    raise KeyError(written)
