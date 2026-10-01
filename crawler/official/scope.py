"""Which campus an official page is for, decided from what the page says.

Monash Australia and Monash Malaysia publish separate student sites, and on the
things that cost a student most they disagree: a Malaysian student pass is not
an Australian subclass 500 visa, health cover there is not OSHC, the loans and
fee rules are not HECS and FEE-HELP. Telling a Malaysia student that an
Australian rule is theirs is the worst mistake this label can make - and
telling them that a University-wide rule (academic integrity, special
consideration, academic progress) is "Australia" only is the second worst,
because they then ignore a rule that binds them.

So for a page on www.monash.edu, in order:

1. Its address is about Malaysia (the Malaysian graduation ceremonies live on
   monash.edu) -> ``malaysia``.
2. Its title names Australia, or its text carries something only Australia has
   (HECS, Commonwealth supported places, OSHC, the subclass 500 visa, Home
   Affairs, Centrelink, a TFN or USI, Australia Awards) -> ``australia``.
3. Its text says it covers every campus, or speaks to Malaysia as well -> ``all``.
   Unless that mention is the page sending Malaysia students elsewhere ("students
   at Monash Malaysia should refer to ..."), which makes it ``australia``.
4. It is a University-wide rule - assessment, academic integrity and
   misconduct, academic progress, complaints, the Handbook - with nothing
   Australian in it -> ``all``. Monash's policies and procedures bind every
   campus; that is what a University policy is.
5. Otherwise ``australia``: the site it is on.

A monash.edu.my page is always ``malaysia``.

``scope`` returns the reason with the answer, so a reviewer can read why each
page was labelled the way it was (``python -m crawler.official.coverage``
prints them).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

ALL, AUSTRALIA, MALAYSIA = "all", "australia", "malaysia"

# Things that exist only in Australia. One is enough: a page that explains HECS
# is an Australian page even if it also mentions Malaysia once.
AUSTRALIA_ONLY = re.compile(
    r"\bHECS\b|FEE-HELP|SA-HELP|OS-HELP|Commonwealth supported|\bCSP\b|"
    r"Overseas Student Health Cover|\bOSHC\b|subclass 500|Home Affairs|Centrelink|"
    r"tax file number|\bTFN\b|Unique Student Identifier|\bUSI\b|Australia Awards|"
    r"Australian (?:citizen|permanent resident)s? only|Australian campuses only|"
    r"Victorian? Government",
    re.IGNORECASE,
)
# The page says it covers every campus, or speaks to Malaysia alongside.
EVERY_CAMPUS = re.compile(
    r"all (?:Monash(?: University)? )?campuses|every (?:Monash )?campus|"
    r"all (?:Monash(?: University)? )?(?:campuses and )?locations|"
    r"\b(?:Monash )?Malaysia\b|Suzhou|Monash Indonesia",
    re.IGNORECASE,
)
# ... unless it mentions Malaysia only to send those students elsewhere.
ELSEWHERE = re.compile(
    r"(?:Malaysia[^.]{0,80}(?:refer to|see|visit|go to|check)[^.]{0,60}monash\.edu\.my)|"
    r"(?:does not|doesn't|do not|don't) apply to[^.]{0,60}Malaysia|"
    r"(?:not available|isn't available|is not available)[^.]{0,60}Malaysia",
    re.IGNORECASE,
)
# Paths of University-wide rules. Policy binds every campus.
UNIVERSITY_RULES = re.compile(
    r"/academic-integrity|/misconduct|/complaints|/academic-progress|"
    r"/unsatisfactory-progress|/admin/policies|/assessments/about|"
    r"/extensions-special-consideration|/handbooks/|/learning-teaching/",
    re.IGNORECASE,
)


def scope(url: str, title: str | None, text: str | None) -> tuple[str, str]:
    """``(applies_to, reason)`` for one page."""
    host = urlparse(url).netloc
    path = urlparse(url).path
    if host.endswith("monash.edu.my"):
        return MALAYSIA, "on monash.edu.my"
    if "malaysia" in path.lower():
        return MALAYSIA, "address is about Malaysia"
    title = title or ""
    text = text or ""
    if re.search(r"\bAustralia\b", title) and "Malaysia" not in title:
        return AUSTRALIA, "title names Australia"
    if found := AUSTRALIA_ONLY.search(text):
        return AUSTRALIA, f"Australia only: {found.group(0)!r}"
    if found := ELSEWHERE.search(text):
        return AUSTRALIA, f"sends Malaysia elsewhere: {found.group(0)[:60]!r}"
    if found := EVERY_CAMPUS.search(text):
        return ALL, f"every campus: {found.group(0)!r}"
    if UNIVERSITY_RULES.search(path):
        return ALL, "University-wide rule"
    return AUSTRALIA, "monash.edu, nothing says otherwise"
