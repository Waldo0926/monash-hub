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

# Exact title translations reviewed against the official English source.
#
# A catalogue title is a claim, not interface chrome.  The machine rendered
# "Accounting in business" as 商业中的会计, "assurance" as 保证, and
# "curating" as 惩罚/破解/诅咒 depending on the sentence.  Keep corrections
# keyed by the English title so every campus/code variant gets the same wording
# and a later Handbook rename naturally stops matching instead of retaining a
# stale Chinese title.
ZH_TITLE_OVERRIDES: dict[str, str] = {
    # Accounting — includes the eight cards surfaced on the home page.
    "Accounting in business": "商业会计",
    "Financial accounting 1": "财务会计 1",
    "Financial accounting 2": "财务会计 2",
    "Financial accounting 3": "财务会计 3",
    "Management accounting 1": "管理会计 1",
    "Management accounting 2": "管理会计 2",
    "Accounting information systems": "会计信息系统",
    "Assurance and audit services": "鉴证与审计服务",
    "Auditing and assurance": "审计与鉴证",
    "Accounting for business": "商业会计",
    "Business communication for accounting professionals": "会计专业人员商务沟通",
    "Forensic accounting and fraud examination": "法务会计与舞弊调查",
    "Foundations of accounting research": "会计研究基础",
    "Current issues in accounting research": "会计研究前沿问题",
    "Accounting for sustainability": "可持续发展会计",
    "Accounting for climate change": "气候变化会计",
    "Global issues in accounting": "会计全球议题",
    "Issues in financial accounting and auditing": "财务会计与审计专题",
    "Issues in management accounting and systems": "管理会计与系统专题",

    # Art history and curating — the machine repeatedly confused curating with
    # punishment, cracking, calibration and cursing.
    "Modernism and the avant-garde": "现代主义与先锋派",
    "Curating: Introduction": "策展导论",
    "Curating: Histories and theories": "策展：历史与理论",
    "Curating: Making exhibitions": "策展：展览实践",
    "Curating: Project studies": "策展项目研究",
    "Curating internship": "策展实习",
    "World wide: Art beyond the Western canon": "世界艺术：超越西方经典",
    "History of art in public space": "公共空间艺术史",

    # Communication and academic skills — literal machine readings changed
    # the discipline or produced non-existent terms such as 学术诉讼.
    "Academic literacies": "学术素养",
    "Communications research project": "传播学研究项目",
    "Communications research thesis": "传播学研究论文",
    "Communications industry internship": "传播行业实习",
    "Data analytics in communication": "传播数据分析",
    "Film, television and screen studies: Forms": "电影、电视与银幕研究：形式",
    "AI-powered public relations: Social media, digital PR and emerging technologies":
        "AI 驱动的公共关系：社交媒体、数字公关与新兴技术",
    "Climate change communication in Malaysia": "马来西亚气候变化传播",
    "Research methods in the arts and social sciences": "艺术与社会科学研究方法",
    "Public Relations: Cases and approaches": "公共关系：案例与方法",
    "Writing portfolio": "写作作品集",
    "Arts honours dissertation 1": "艺术荣誉学位论文 1",
    "Arts honours dissertation 2": "艺术荣誉学位论文 2",
}

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

# A colon introduces a subtitle - "Introduction to X: theory and practice" -
# where the subject is only the part before it; appending the qualifier to the
# end of the whole thing would attach it to the subtitle instead.
#
# A conjunction or a comma is *not* that. "Introduction to the history and
# theory of art" has one subject that happens to be a list, and 艺术的历史和理论导论
# is right. Excluding those too was over-cautious and left ten titles reading
# 导论对艺术的历史和理论 and 基础 of 解剖学和生理学.
_HAS_STRUCTURE = re.compile(r"[:;]")

#: See degrees.py - a translated fragment can come back with a full stop on it.
_TRAILING_STOP = re.compile(r"[。．.，,、；;：:\s]+$")


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

    # The translator sometimes ends a fragment as though it were a sentence, and
    # the qualifier would then land after the full stop - 建筑研究。学士 is how
    # this showed up on the degree names.
    subject = _TRAILING_STOP.sub("", rendered.strip())
    if not subject:
        return None

    qualifier = QUALIFIERS[_canonical(shape.group("qualifier"))][locale]
    return f"{subject}{qualifier}"


def _canonical(written: str) -> str:
    lowered = written.strip().lower()
    for key in QUALIFIERS:
        if key.lower() == lowered:
            return key
    raise KeyError(written)
