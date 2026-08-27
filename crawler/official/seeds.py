"""The Official Knowledge Seed: hand-picked Monash pages.

Chosen, not discovered. The list covers the things students actually have to
look up - special consideration, WAM and GPA, census dates, visas, enrolment
changes, fees, graduation - and stops there. Blanket-crawling monash.edu would
cost more, index worse and give us thousands of pages nobody searches for.

Every URL here returned HTTP 200 when the list was compiled. Growing it is
driven by real search queries after public beta, per Stage 5 of the roadmap.

``tier`` controls how often we re-check the page (see crawler/sync/refresh.py):
dates move constantly, policy text barely moves at all.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Seed:
    slug: str
    url: str
    title: str
    category: str
    tags: tuple[str, ...]
    tier: str = "medium"
    #: Which campus the page is written for - see OfficialPage.applies_to. The
    #: default is the site the URL is on, and all but a handful of these are on
    #: monash.edu. Only a page that says so itself is marked ``all``.
    applies_to: str = "australia"


CATEGORIES = {
    "enrolment": "Enrolment & course planning",
    "assessment": "Assessment & results",
    "academic-rules": "Academic rules & policy",
    "international": "International students",
    "fees-dates": "Fees & key dates",
    "exchange": "Exchange & study abroad",
    "malaysia": "Malaysia campus",
}

SEEDS: tuple[Seed, ...] = (
    # --- Enrolment / course planning -------------------------------------
    Seed("enrolments", "https://www.monash.edu/students/admin/enrolments",
         "Enrolments", "enrolment", ("enrolment", "wes", "选课")),
    Seed("changing-your-enrolment", "https://www.monash.edu/students/admin/enrolments/change",
         "Changing your enrolment", "enrolment", ("enrolment", "change", "改选")),
    Seed("add-or-withdraw-units",
         "https://www.monash.edu/students/admin/enrolments/change/add-or-discontinue-units",
         "Add or withdraw from units", "enrolment",
         ("add", "drop", "withdraw", "退课", "加课")),
    Seed("intermission", "https://www.monash.edu/students/admin/enrolments/change/intermission",
         "Intermission (study leave)", "enrolment", ("intermission", "leave", "休学")),
    Seed("discontinue-course",
         "https://www.monash.edu/students/admin/enrolments/change/discontinue-course",
         "Discontinue your course", "enrolment", ("discontinue", "withdraw", "退学")),
    Seed("re-enrol", "https://www.monash.edu/students/admin/enrolments/re-enrol",
         "Re-enrol", "enrolment", ("re-enrol", "reenrolment", "重新注册")),
    Seed("census-dates-explained",
         "https://www.monash.edu/students/admin/enrolments/dates/census-definition",
         "What are census dates?", "enrolment", ("census", "deadline", "截止日")),
    Seed("course-advice", "https://www.monash.edu/students/study-success/course-advice",
         "Course advice", "enrolment", ("course advice", "planning", "课程规划")),
    Seed("credit-and-enrolment",
         "https://www.monash.edu/students/study-success/course-advice/enrolment-and-credit",
         "Enrolment and credit", "enrolment", ("credit", "exemption", "学分减免")),
    Seed("study-at-another-institution",
         "https://www.monash.edu/students/admin/enrolments/change/complementary-study",
         "Study at another institution", "enrolment", ("cross-institutional", "credit")),

    # --- Assessment / results --------------------------------------------
    Seed("special-consideration",
         "https://www.monash.edu/students/admin/assessments/extensions-special-consideration",
         "Extensions and special consideration", "assessment",
         ("special consideration", "sc", "extension", "特殊考虑"),
         # This page says so itself: "The special consideration process applies
         # to students at all Monash University campuses and locations."
         applies_to="all"),
    Seed("defer-final-assessment",
         "https://www.monash.edu/students/admin/assessments/extensions-special-consideration/defer",
         "Defer or reschedule your final assessment", "assessment",
         ("deferred", "defer", "补考")),
    Seed("supporting-documents",
         "https://www.monash.edu/students/admin/assessments/extensions-special-consideration/documents",
         "Supporting documents for special consideration", "assessment",
         ("documents", "medical certificate", "证明")),
    Seed("results", "https://www.monash.edu/students/admin/assessments/results",
         "Results", "assessment", ("results", "grades", "成绩")),
    Seed("wam", "https://www.monash.edu/students/admin/assessments/results/wam",
         "Weighted average mark (WAM)", "assessment", ("wam", "average", "均分")),
    Seed("gpa", "https://www.monash.edu/students/admin/assessments/results/gpa",
         "Grade point average (GPA)", "assessment", ("gpa", "绩点")),
    Seed("results-legend",
         "https://www.monash.edu/students/admin/assessments/results/results-legend",
         "Reading your marks and grades", "assessment", ("grades", "hd", "p", "n", "成绩等级")),
    Seed("final-assessment-dates",
         "https://www.monash.edu/students/admin/assessments/dates-timetables/finals",
         "Final assessment dates", "assessment", ("exam", "timetable", "考试时间"), tier="dynamic"),
    Seed("assessment-at-monash", "https://www.monash.edu/students/admin/assessments/about",
         "Assessment at Monash", "assessment", ("assessment", "hurdle", "考核")),
    Seed("allocate-timetable", "https://www.monash.edu/students/admin/timetables/allocate",
         "Your timetable - Allocate+", "assessment", ("timetable", "allocate", "课表")),

    # --- Academic rules ---------------------------------------------------
    Seed("academic-progress", "https://www.monash.edu/students/study-success/academic-progress",
         "Student academic progress", "academic-rules",
         ("academic progress", "exclusion", "学业进度")),
    Seed("about-academic-progress",
         "https://www.monash.edu/students/study-success/academic-progress/about",
         "About academic progress", "academic-rules", ("academic progress", "unsatisfactory")),
    Seed("academic-integrity", "https://www.monash.edu/students/study-success/academic-integrity",
         "Academic integrity", "academic-rules",
         ("plagiarism", "integrity", "collusion", "学术诚信")),
    Seed("policies", "https://www.monash.edu/students/admin/policies",
         "Policies and procedures", "academic-rules", ("policy", "procedure", "政策"),
         tier="stable"),
    Seed("student-conduct", "https://www.monash.edu/students/admin/policies/student-conduct",
         "Student Code of Conduct", "academic-rules", ("conduct", "behaviour"), tier="stable"),

    # --- International students -------------------------------------------
    Seed("international-students", "https://www.monash.edu/students/support/international",
         "International students", "international", ("international", "留学生")),
    Seed("student-visa", "https://www.monash.edu/students/support/international/visa",
         "Your student visa", "international", ("visa", "student visa", "签证")),
    Seed("working-on-a-student-visa",
         "https://www.monash.edu/students/support/international/visa/working",
         "Working on a student visa", "international", ("visa", "work", "打工")),
    Seed("visa-changes", "https://www.monash.edu/students/support/international/visa/changes",
         "Changes affecting your visa", "international", ("visa", "change", "签证变更")),
    Seed("confirmation-of-enrolment",
         "https://www.monash.edu/students/support/international/visa/confirmation-of-enrolment",
         "Confirmation of Enrolment (CoE)", "international", ("coe", "visa", "入学确认")),
    Seed("oshc", "https://www.monash.edu/students/admin/fees/other-costs/overseas-health-cover",
         "Overseas Student Health Cover (OSHC)", "international",
         ("oshc", "insurance", "保险")),

    # --- Fees and key dates ------------------------------------------------
    Seed("important-dates", "https://www.monash.edu/students/admin/dates",
         "Important dates", "fees-dates", ("dates", "calendar", "重要日期"), tier="dynamic"),
    Seed("principal-dates", "https://www.monash.edu/students/admin/dates/principal-dates",
         "Principal dates", "fees-dates", ("dates", "semester", "学期时间"), tier="dynamic"),
    Seed("census-dates", "https://www.monash.edu/students/admin/dates/census-dates",
         "Census dates", "fees-dates", ("census", "deadline", "截止日"), tier="dynamic"),
    Seed("fees", "https://www.monash.edu/students/admin/fees",
         "Fees", "fees-dates", ("fees", "tuition", "学费")),
    Seed("fee-payment-dates", "https://www.monash.edu/students/admin/fees/payment/dates",
         "Fee payment dates", "fees-dates", ("fees", "payment", "缴费"), tier="dynamic"),
    Seed("graduations", "https://www.monash.edu/students/admin/graduations",
         "Graduations", "fees-dates", ("graduation", "毕业")),
    Seed("academic-transcripts",
         "https://www.monash.edu/students/support/connect/official-documents/academic-transcripts",
         "Academic records (transcripts)", "fees-dates",
         ("transcript", "records", "成绩单")),

    # --- Exchange ----------------------------------------------------------
    Seed("study-abroad", "https://www.monash.edu/study-abroad",
         "Study abroad and exchange", "exchange", ("exchange", "abroad", "交换")),

    # --- Malaysia campus ----------------------------------------------------
    # --- Monash Malaysia ---------------------------------------------------
    #
    # Malaysia runs its own student site, and on the things that matter most it
    # does not agree with monash.edu: a student pass is issued by the
    # Immigration Department through EMGS and is not the Australian subclass 500
    # visa, and health cover is not OSHC. A reader in Malaysia needs these
    # pages, not their Australian equivalents.
    Seed("malaysia-student-services", "https://www.monash.edu.my/student-services",
         "Student services (Monash Malaysia)", "malaysia",
         ("malaysia", "student services", "马来西亚"), applies_to="malaysia"),
    Seed("malaysia-student-pass",
         "https://www.monash.edu.my/student-services/international-students/student-pass",
         "Student pass (Monash Malaysia)", "malaysia",
         ("malaysia", "student pass", "emgs", "签证", "学生准证"),
         applies_to="malaysia"),
    Seed("malaysia-insurance",
         "https://www.monash.edu.my/student-services/support-services/insurance",
         "Insurance (Monash Malaysia)", "malaysia",
         ("malaysia", "insurance", "保险"), applies_to="malaysia"),
    Seed("malaysia-student-admin",
         "https://www.monash.edu.my/student-services/student-admin",
         "Student administration (Monash Malaysia)", "malaysia",
         ("malaysia", "enrolment", "选课注册"), applies_to="malaysia"),
    Seed("malaysia-special-consideration",
         "https://www.monash.edu.my/student-services/student-admin/examinations-results"
         "/assessments-and-results/special-consideration2",
         "Special consideration (Monash Malaysia)", "malaysia",
         ("malaysia", "special consideration", "特殊考虑"), applies_to="malaysia"),
    Seed("malaysia-exam-rules",
         "https://www.monash.edu.my/student-services/student-admin/examinations-results"
         "/exam-rules",
         "Exam rules (Monash Malaysia)", "malaysia",
         ("malaysia", "exam", "考试规则"), applies_to="malaysia"),
)

SEEDS_BY_SLUG = {seed.slug: seed for seed in SEEDS}
