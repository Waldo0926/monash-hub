"""Curated FAQ entries.

Every answer here is written by a person, kept short, and tied to an official
page by slug. Nothing is generated, and nothing states a rule the linked page
does not - the FAQ is a shortcut to the official source, not a replacement for
reading it.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FaqSeed:
    slug: str
    question: str
    answer: str
    category: str
    tags: tuple[str, ...]
    keywords: tuple[str, ...]
    page_slug: str
    priority: int = 0


FAQ_SEEDS: tuple[FaqSeed, ...] = (
    FaqSeed(
        "how-to-apply-special-consideration",
        "How do I apply for special consideration?",
        "Special consideration covers short-term circumstances outside your control that "
        "affected an assessment. Apply through the special consideration form in your student "
        "portal, normally within two university working days of the assessment due date or "
        "scheduled sitting, and attach supporting documentation. Short extensions for "
        "coursework are handled separately by your unit's teaching team. Check the official "
        "page for the current deadline and the exact evidence required before you apply.",
        "assessment",
        ("special consideration", "sc", "extension"),
        ("sc", "special consideration", "特殊考虑", "延期", "extension"),
        "special-consideration",
        priority=100,
    ),
    FaqSeed(
        "what-documents-for-sc",
        "What documents do I need for special consideration?",
        "You need third-party evidence covering the dates you were affected - most commonly a "
        "medical certificate or a Monash Health Professional Report. Screenshots, self-written "
        "statements and undated letters are generally not accepted. The official page lists "
        "which document type applies to which circumstance.",
        "assessment",
        ("special consideration", "documents"),
        ("documents", "medical certificate", "证明", "医生证明"),
        "supporting-documents",
        priority=70,
    ),
    FaqSeed(
        "what-is-wam",
        "What is WAM and how is it calculated?",
        "WAM is your weighted average mark: the average of your unit marks weighted by each "
        "unit's credit points, and in most courses also by unit level. It uses marks, not "
        "grades, so it is more precise than GPA. Monash publishes the exact formula and which "
        "units are excluded on the official WAM page.",
        "assessment",
        ("wam", "results"),
        ("wam", "average", "均分", "加权"),
        "wam",
        priority=90,
    ),
    FaqSeed(
        "what-is-gpa",
        "What is GPA at Monash?",
        "GPA is a 0-4 scale calculated from your grades rather than your marks, where HD is 4 "
        "and N is 0. Monash uses GPA for some scholarship and admission decisions and WAM for "
        "others, so check which one a specific application asks for.",
        "assessment",
        ("gpa", "results"),
        ("gpa", "绩点", "grade point average"),
        "gpa",
        priority=80,
    ),
    FaqSeed(
        "census-date-meaning",
        "What is a census date and why does it matter?",
        "The census date is the last day you can withdraw from a unit without paying for it and "
        "without it appearing on your record. After that date you are liable for the fees and a "
        "withdrawal is recorded. Census dates differ by teaching period, so check the date for "
        "your specific unit rather than assuming one date covers the semester.",
        "enrolment",
        ("census", "withdraw", "fees"),
        ("census", "census date", "退课截止", "截止日"),
        "census-dates-explained",
        priority=85,
    ),
    FaqSeed(
        "how-to-withdraw-from-a-unit",
        "How do I withdraw from a unit?",
        "Withdraw through WES while enrolment changes are open. Before the census date there is "
        "no fee and no record; after it, you keep the fee liability and the unit shows as a "
        "withdrawal. If you are on a student visa, dropping below full-time load can affect "
        "your visa, so check with an adviser first.",
        "enrolment",
        ("withdraw", "enrolment", "units"),
        ("withdraw", "drop", "退课", "退选"),
        "add-or-withdraw-units",
        priority=75,
    ),
    FaqSeed(
        "student-visa-work-hours",
        "How many hours can I work on a student visa? (Australia)",
        "This is about the Australian campuses. In Malaysia the right to stay is a student "
        "pass issued by the Immigration Department through EMGS, and its conditions are not "
        "the ones below - check monash.edu.my. "
        "Work rights for student visa holders are set by the Australian Government, not by "
        "Monash, and the cap has changed several times in recent years. Monash's page links to "
        "the current Department of Home Affairs conditions - always confirm the number there "
        "before relying on it.",
        "international",
        ("visa", "work"),
        ("visa", "work", "打工", "工作时长", "签证"),
        "working-on-a-student-visa",
        priority=70,
    ),
    FaqSeed(
        "what-is-coe",
        "What is a CoE and when do I need a new one? (Australia)",
        "This is about the Australian campuses; Malaysia issues a student pass through EMGS "
        "instead. "
        "A Confirmation of Enrolment (CoE) is the document your student visa is granted against. "
        "You generally need a new one if your course, campus or completion date changes - "
        "including if you take intermission or reduce your load. Request it before your current "
        "CoE expires.",
        "international",
        ("coe", "visa"),
        ("coe", "confirmation of enrolment", "入学确认"),
        "confirmation-of-enrolment",
        priority=60,
    ),
    FaqSeed(
        "apply-for-intermission",
        "Can I take a semester off?",
        "Yes - it is called intermission. Coursework students can usually apply for up to a "
        "defined maximum period, and approval is not automatic. International students on a "
        "student visa need to check the visa consequences before applying, because intermission "
        "changes your CoE.",
        "enrolment",
        ("intermission", "leave"),
        ("intermission", "休学", "gap", "leave of absence"),
        "intermission",
        priority=55,
    ),
    FaqSeed(
        "when-do-results-come-out",
        "When do results come out?",
        "Results are released per teaching period on the dates published in the official results "
        "calendar, and appear in WES. A grade can be withheld if there is an outstanding matter "
        "such as unpaid fees or an academic integrity process.",
        "assessment",
        ("results", "dates"),
        ("results", "成绩", "出分", "什么时候出成绩"),
        "results",
        priority=65,
    ),
    FaqSeed(
        "how-to-get-a-transcript",
        "How do I get an official transcript?",
        "Order academic records through the official documents service. Current students can see "
        "an unofficial statement of marks in WES for free; a certified transcript is a separate "
        "paid request with its own processing time.",
        "enrolment",
        ("transcript", "records"),
        ("transcript", "成绩单", "academic record"),
        "academic-transcripts",
        priority=40,
    ),
    FaqSeed(
        "exchange-eligibility",
        "How do I go on exchange at Monash?",
        "Exchange runs through Monash Abroad. Eligibility normally depends on your WAM, how much "
        "of your course you have completed, and having units that can be credited back. "
        "Applications open well before the semester you want to travel in, so check the round "
        "dates early.",
        "exchange",
        ("exchange", "abroad"),
        ("exchange", "交换", "abroad", "海外交换"),
        "study-abroad",
        priority=50,
    ),
)
