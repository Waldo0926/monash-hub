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
    """One curated answer.

    ``keywords`` and ``tags`` do different jobs - see app/search/faq_match.py.

    * ``keywords`` *trigger* the entry. Each one must be specific to this entry
      alone: 退课 is, 签证 is not. A generic word here is how a question about
      renewing a visa got answered with the work-hours entry.
    * ``tags`` are topic words the question may also use. They never start a
      match; they only stop a question that uses them from being treated as
      asking about something this entry does not cover.
    """
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
        ("assessment", "assignment", "apply", "deadline", "due date", "form", "申请",
         "作业", "截止", "考核", "medical", "illness", "missed", "miss", "online"),
        ("sc", "special consideration", "特殊考虑", "extension", "extensions",
         "申请延期", "作业延期", "延期交", "晚交", "sick", "病假", "生病"),
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
        ("special consideration", "sc", "特殊考虑", "need", "required", "evidence",
         "需要", "提交", "申请"),
        ("documents", "document", "supporting documents", "medical certificate",
         "health professional report", "证明", "证明材料", "材料", "医生证明", "病假条"),
        "supporting-documents",
        priority=70,
    ),
    FaqSeed(
        "defer-a-final-assessment",
        "Can I defer my final exam?",
        "You ask to defer a final assessment through special consideration - there is no "
        "separate form. If it is approved, you sit the assessment later, in the deferred "
        "assessment period. The official page explains when a deferral applies, how "
        "rescheduling works and when the deferred period runs; check it before you apply.",
        "assessment",
        ("special consideration", "sc", "特殊考虑", "final", "exam", "assessment", "期末",
         "考试", "申请", "can", "my", "miss", "missed", "sick", "ill", "illness",
         "病", "生病", "病假", "去", "参加"),
        ("deferred exam", "deferred exams", "deferred assessment", "defer exam",
         "defer my exam", "defer a final", "defer my final", "defer final",
         "deferral", "missed my exam", "missed the exam", "missed exam",
         "missed my final", "延期考试", "缓考", "推迟考试", "考试延期", "没去考试",
         "错过考试", "缺考"),
        "defer-final-assessment",
        priority=60,
    ),
    FaqSeed(
        "what-is-wam",
        "What is WAM and how is it calculated?",
        "WAM is your weighted average mark: the average of your unit marks weighted by each "
        "unit's credit points, and in most courses also by unit level. It uses marks, not "
        "grades, so it is more precise than GPA. Monash publishes the exact formula and which "
        "units are excluded on the official WAM page.",
        "assessment",
        ("results", "average", "calculate", "calculation", "formula", "mark", "marks",
         "怎么算", "计算", "算", "公式", "平均分"),
        ("wam", "weighted average mark", "weighted average", "均分", "加权平均",
         "加权平均分"),
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
        ("results", "calculate", "calculation", "scale", "怎么算", "计算", "算"),
        ("gpa", "绩点", "平均绩点", "grade point average"),
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
        ("withdraw", "fees", "deadline", "date", "dates", "important", "matter",
         "截止", "截止日", "日期", "学费", "重要", "为什么", "退课"),
        ("census", "census date", "census dates", "学籍统计日", "退课截止",
         "退课截止日", "退课截止日期", "退课的截止日期"),
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
        ("enrolment", "unit", "units", "subject", "course", "wes", "课", "一门课",
         "课程", "网上"),
        ("withdraw", "withdrawal", "drop", "discontinue a unit", "退课", "退选",
         "退掉"),
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
        ("visa", "student visa", "签证", "学生签证", "hours", "hour", "week",
         "fortnight", "australia", "australian", "小时", "每周", "一周", "两周",
         "澳洲", "澳大利亚", "多少", "能", "可以", "limit", "cap", "job",
         "international", "国际学生", "留学生"),
        ("work", "working", "work hours", "work rights", "part-time work",
         "打工", "兼职", "工作时长", "打工时长"),
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
        ("visa", "签证", "new", "need", "when", "change", "新", "换", "需要",
         "什么时候", "australia", "澳洲"),
        ("coe", "confirmation of enrolment", "confirmation of enrollment", "入学确认",
         "入学确认书"),
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
        ("leave", "semester", "take", "off", "break", "study", "apply", "学期",
         "一个学期", "申请", "请假"),
        ("intermission", "休学", "停学", "gap year", "leave of absence",
         "semester off", "break from study", "break from studies", "study break"),
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
        ("dates", "date", "when", "come out", "release", "released", "wes",
         "什么时候", "公布", "发布", "出来", "查", "日期"),
        ("results", "result", "grades", "成绩", "出分", "出成绩", "成绩发布",
         "什么时候出成绩"),
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
        ("records", "official", "get", "order", "request", "copy", "certified",
         "正式", "开", "申请", "打印", "办", "官方"),
        ("transcript", "transcripts", "成绩单", "academic record", "academic records",
         "academic transcript", "statement of marks"),
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
        ("go", "eligible", "eligibility", "requirement", "requirements", "apply",
         "条件", "要求", "申请", "去", "出国"),
        ("exchange", "study abroad", "abroad", "monash abroad", "交换", "海外交换",
         "出国交换", "交换生"),
        "study-abroad",
        priority=50,
    ),
)
