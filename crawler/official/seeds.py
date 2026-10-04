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

from crawler.official.seeds_coverage import COVERAGE


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
    #: For a page Monash shows only after sign-in: what it covers, in our words.
    #: Such a page is never fetched. It is listed with this description and its
    #: link, so a student can find it, and its text stays where Monash put it.
    sign_in: str | None = None


CATEGORIES = {
    "enrolment": "Enrolment & course planning",
    "assessment": "Assessment & results",
    "academic-rules": "Academic rules & policy",
    "international": "International students",
    "fees-dates": "Fees & key dates",
    "graduation": "Graduation",
    "support": "Student support & services",
    "exchange": "Exchange & study abroad",
    "malaysia": "Malaysia campus",
}

SEEDS: tuple[Seed, ...] = (
    # --- Enrolment / course planning -------------------------------------
    Seed("enrolments", "https://www.monash.edu/students/admin/enrolments",
         "Enrolments", "enrolment", ("enrolment", "wes", "选课"),
         applies_to="all"),
    Seed("changing-your-enrolment", "https://www.monash.edu/students/admin/enrolments/change",
         "Changing your enrolment", "enrolment", ("enrolment", "change", "改选"),
         applies_to="all"),
    Seed("add-or-withdraw-units",
         "https://www.monash.edu/students/admin/enrolments/change/add-or-discontinue-units",
         "Add or withdraw from units", "enrolment",
         ("add", "drop", "withdraw", "退课", "加课"),
         applies_to="all"),
    Seed("intermission", "https://www.monash.edu/students/admin/enrolments/change/intermission",
         "Intermission (study leave)", "enrolment", ("intermission", "leave", "休学"),
         applies_to="all"),
    Seed("discontinue-course",
         "https://www.monash.edu/students/admin/enrolments/change/discontinue-course",
         "Discontinue your course", "enrolment", ("discontinue", "withdraw", "退学"),
         applies_to="all"),
    Seed("re-enrol", "https://www.monash.edu/students/admin/enrolments/re-enrol",
         "Re-enrol", "enrolment", ("re-enrol", "reenrolment", "重新注册"),
         applies_to="all"),
    Seed("census-dates-explained",
         "https://www.monash.edu/students/admin/enrolments/dates/census-definition",
         "What are census dates?", "enrolment", ("census", "deadline", "截止日"),
         applies_to="all"),
    Seed("course-advice", "https://www.monash.edu/students/study-success/course-advice",
         "Course advice", "enrolment", ("course advice", "planning", "课程规划"),
         applies_to="all"),
    # "Enrolment and credit" was here. Monash turned it into an interactive
    # "choose a topic" picker whose answers are loaded by script, so it has no
    # text to extract and has failed every crawl since 30 Aug 2026. The static
    # pages below cover what it used to: credit, study load and failed units.
    Seed("apply-for-credit", "https://www.monash.edu/admissions/credit",
         "Apply for credit", "enrolment",
         ("credit", "credit transfer", "exemption", "advanced standing", "学分减免", "学分转换"),
         applies_to="all"),
    Seed("study-load", "https://www.monash.edu/students/admin/enrolments/study-load",
         "Study load (overload and underload)", "enrolment",
         ("study load", "full-time", "part-time", "overload", "underload", "全日制", "学习负荷"),
         applies_to="all"),
    Seed("failed-units",
         "https://www.monash.edu/students/admin/enrolments/change/failed-withheld-invalid-units",
         "Failed, withheld and invalid units", "enrolment",
         ("fail", "failed", "withheld", "挂科", "不及格"),
         applies_to="all"),
    Seed("double-degrees", "https://www.monash.edu/students/admin/enrolments/double-degrees",
         "Double degrees", "enrolment", ("double degree", "双学位"),
         applies_to="all"),
    Seed("study-at-another-institution",
         "https://www.monash.edu/students/admin/enrolments/change/complementary-study",
         "Study at another institution", "enrolment", ("cross-institutional", "credit"),
         applies_to="all"),

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
         ("deferred", "defer", "补考"),
         applies_to="all"),
    Seed("supporting-documents",
         "https://www.monash.edu/students/admin/assessments/extensions-special-consideration/documents",
         "Supporting documents for special consideration", "assessment",
         ("documents", "medical certificate", "证明"),
         applies_to="all"),
    Seed("results", "https://www.monash.edu/students/admin/assessments/results",
         "Results", "assessment", ("results", "grades", "成绩"),
         applies_to="all"),
    Seed("wam", "https://www.monash.edu/students/admin/assessments/results/wam",
         "Weighted average mark (WAM)", "assessment", ("wam", "average", "均分"),
         applies_to="all"),
    Seed("gpa", "https://www.monash.edu/students/admin/assessments/results/gpa",
         "Grade point average (GPA)", "assessment", ("gpa", "绩点"),
         applies_to="all"),
    Seed("results-legend",
         "https://www.monash.edu/students/admin/assessments/results/results-legend",
         "Reading your marks and grades", "assessment", ("grades", "hd", "p", "n", "成绩等级"),
         applies_to="all"),
    Seed("final-assessment-dates",
         "https://www.monash.edu/students/admin/assessments/dates-timetables/finals",
         "Final assessment dates", "assessment", ("exam", "timetable", "考试时间"), tier="dynamic",
         applies_to="all"),
    Seed("assessment-at-monash", "https://www.monash.edu/students/admin/assessments/about",
         "Assessment at Monash", "assessment", ("assessment", "hurdle", "考核"),
         applies_to="all"),
    Seed("allocate-timetable", "https://www.monash.edu/students/admin/timetables/allocate",
         "Your timetable - Allocate+", "assessment", ("timetable", "allocate", "课表"),
         applies_to="all"),
    Seed("assessments-and-results", "https://www.monash.edu/students/admin/assessments",
         "Assessments and results", "assessment", ("assessment", "results", "考核", "成绩"),
         applies_to="all"),
    Seed("assessment-policies", "https://www.monash.edu/students/admin/assessments/about/procedures",
         "Assessment policy and processes", "assessment",
         ("policy", "procedure", "assessment regime", "grading schema", "考核政策"),
         tier="stable", applies_to="all"),
    # Hurdles decide whether a unit is passed at all, whatever the other marks
    # add up to, and Monash is changing them: threshold hurdles are being
    # removed from every unit by the end of 2026. The procedure itself is a PDF,
    # which this project does not ingest (AGENTS.md), so the page indexed is
    # Monash's own HTML guidance on applying it. It is written for teaching
    # staff, and it is the one public page that states the NH 45 rule and the
    # additional-assessment rule in full.
    Seed("hurdles", "https://www.monash.edu/learning-teaching/teachhq/Assessment"
         "/designing-assessment-regimes/how-to/use-hurdles-in-assessment",
         "Hurdles in assessment (competency and threshold hurdles)", "assessment",
         ("hurdle", "hurdles", "hurdle requirement", "competency hurdle", "threshold hurdle",
          "nh", "hurdle fail", "及格门槛", "门槛"),
         tier="stable", applies_to="all"),
    Seed("supplementary-assessment",
         "https://www.monash.edu/students/admin/assessments/supplementary",
         "Supplementary assessments", "assessment",
         ("supplementary", "supp", "ns", "补考"),
         applies_to="all"),
    Seed("results-release", "https://www.monash.edu/students/admin/assessments/results/dates",
         "Your results - when and how", "assessment",
         ("results", "release", "成绩发布", "出分"),
         applies_to="all"),
    Seed("assessment-feedback",
         "https://www.monash.edu/students/admin/assessments/results/feedback",
         "Feedback on your assessments", "assessment", ("feedback", "反馈"),
         applies_to="all"),
    Seed("eexam-rules", "https://www.monash.edu/students/admin/assessments/exams/rules",
         "eExam rules", "assessment",
         ("exam rules", "eexam", "cheating", "考试规则", "作弊"),
         tier="stable", applies_to="all"),
    Seed("how-eexams-work", "https://www.monash.edu/students/admin/assessments/exams/about",
         "How eExams work", "assessment", ("eexam", "exam", "电子考试"),
         applies_to="all"),
    Seed("on-campus-eexams", "https://www.monash.edu/students/admin/assessments/exams/on-campus",
         "On-campus eExams (Australia)", "assessment",
         ("eexam", "exam", "on campus", "考试", "线下考试")),
    Seed("exam-special-arrangements",
         "https://www.monash.edu/students/admin/assessments/exams/special-arrangements",
         "Special arrangements for exams", "assessment",
         ("special arrangements", "exam clash", "time zone", "考试冲突", "时差"),
         applies_to="all"),

    # --- Behind Monash sign-in ---------------------------------------------
    #
    # Both redirect to Monash's Okta login; they are listed, not copied.
    Seed("arts-course-transfer", "https://www.monash.edu/arts/current-students/course-transfer",
         "Course transfer - Faculty of Arts", "enrolment",
         ("course transfer", "transfer", "arts", "转专业", "转课程"),
         tier="stable",
         sign_in="The Faculty of Arts' guidance for current students who want to transfer "
                 "into or out of an Arts course. Monash shows it only after you sign in with "
                 "your Monash account. The University-wide rules - who can apply, how many "
                 "preferences, and when - are on the public Course or campus transfer page."),
    Seed("malaysia-apply-to-graduate",
         "https://www.monash.edu.my/student-services/student-admin/graduations/apply-to-graduate",
         "Apply to graduate (Monash Malaysia)", "graduation",
         ("malaysia", "apply to graduate", "graduation", "申请毕业", "毕业", "马来西亚"),
         tier="stable", applies_to="malaysia",
         sign_in="Monash Malaysia's step-by-step page on applying to graduate. Monash shows "
                 "it only after you sign in with your Monash account. Most of the same "
                 "questions - when to apply, ceremonies, graduating in absentia - are "
                 "answered on the public FAQs for graduations (Monash Malaysia)."),

    # --- Course maps ------------------------------------------------------
    #
    # Each faculty publishes, per commencement year, the order to take a
    # degree's units in. They are PDFs, so what is indexed is the faculty's page
    # listing them, never the files: the page names every degree and links the
    # official map. Next year's maps appear months before next year's Handbook
    # (see crawler/handbook/next_year.py), so these are how a student finds them.
    Seed("it-course-maps", "https://www.monash.edu/it/current-students/courses/maps",
         "Course maps - Information Technology", "enrolment",
         ("course map", "course maps", "course progression", "information technology",
          "computer science", "课程地图", "修读顺序")),
    # The faculty's own table of closing, renamed and changed units and the
    # approved replacement for each (backend/app/knowledge/teach_out.py reads it).
    # Marked for the site it is on, not "all": the page speaks for the Faculty of
    # IT but does not say which campuses, and the notice tells the reader to
    # confirm that with their faculty. Dynamic tier because it is updated as
    # teach-out plans are confirmed ("To be confirmed" rows become units).
    Seed("it-undergraduate-re-enrolment",
         "https://www.monash.edu/it/current-students/courses/re-enrolment/undergraduate",
         "Re-enrolment and unit changes - Information Technology (undergraduate)",
         "enrolment",
         ("re-enrolment", "teach out", "teach-out", "replacement units", "unit changes",
          "2027 course version", "information technology", "computer science",
          "停开", "替代课程", "课程变更"),
         tier="dynamic"),
    Seed("engineering-course-maps",
         "https://www.monash.edu/engineering/current-students/enrolment-and-re-enrolment"
         "/course-information/course-maps",
         "Course maps - Engineering", "enrolment",
         ("course map", "course maps", "course progression", "engineering",
          "课程地图", "修读顺序"),
         applies_to="all"),
    Seed("business-course-maps",
         "https://www.monash.edu/business/current-students/course-advice-and-planning"
         "/helpful-links/course-maps",
         "Course maps - Business and Economics", "enrolment",
         ("course map", "course maps", "course progression", "commerce", "business",
          "课程地图", "修读顺序"),
         applies_to="all"),
    Seed("arts-course-maps",
         "https://www.monash.edu/arts/current-students/course-and-unit-information/course-maps",
         "Course maps - Arts", "enrolment",
         ("course map", "course maps", "course progression", "arts", "课程地图", "修读顺序"),
         applies_to="all"),
    Seed("education-course-maps", "https://www.monash.edu/education/students/courses/maps",
         "Course maps - Education", "enrolment",
         ("course map", "course maps", "course progression", "education", "课程地图", "修读顺序")),
    Seed("mada-course-maps",
         "https://www.monash.edu/mada/current-students/planning-your-course/course-maps",
         "Course maps - Art, Design and Architecture", "enrolment",
         ("course map", "course maps", "course progression", "design", "architecture",
          "课程地图", "修读顺序")),
    Seed("law-course-maps",
         "https://www.monash.edu/law/current-students/resources/course-unit-information"
         "/course-information",
         "Course maps - Law", "enrolment",
         ("course map", "course maps", "course progression", "law", "课程地图", "修读顺序")),

    # --- Academic rules ---------------------------------------------------
    Seed("academic-progress", "https://www.monash.edu/students/study-success/academic-progress",
         "Student academic progress", "academic-rules",
         ("academic progress", "exclusion", "学业进度"),
         applies_to="all"),
    Seed("about-academic-progress",
         "https://www.monash.edu/students/study-success/academic-progress/about",
         "About academic progress", "academic-rules", ("academic progress", "unsatisfactory"),
         applies_to="all"),
    Seed("academic-integrity", "https://www.monash.edu/students/study-success/academic-integrity",
         "Academic integrity", "academic-rules",
         ("plagiarism", "integrity", "collusion", "学术诚信"),
         applies_to="all"),
    Seed("policies", "https://www.monash.edu/students/admin/policies",
         "Policies and procedures", "academic-rules", ("policy", "procedure", "政策"),
         tier="stable",
         applies_to="all"),
    Seed("student-conduct", "https://www.monash.edu/students/admin/policies/student-conduct",
         "Student Code of Conduct", "academic-rules", ("conduct", "behaviour"), tier="stable",
         applies_to="all"),
    Seed("unsatisfactory-progress",
         "https://www.monash.edu/students/unsatisfactory-progress/replying-notice-referral-hearing",
         "Receiving an email about unsatisfactory progress", "academic-rules",
         ("unsatisfactory progress", "risk level", "academic progress", "学业预警",
          "学业进度"),
         applies_to="all"),
    Seed("apc-hearing", "https://www.monash.edu/students/study-success/academic-progress/hearings",
         "Attending an Academic Progress Committee (APC) hearing", "academic-rules",
         ("apc", "hearing", "academic progress", "听证"),
         applies_to="all"),
    Seed("apc-decisions",
         "https://www.monash.edu/students/study-success/academic-progress/hearings/decisions",
         "Academic progress hearing decisions", "academic-rules",
         ("apc", "exclusion", "enrolment conditions", "退学", "附条件注册"),
         applies_to="all"),
    Seed("exclusion-appeal",
         "https://www.monash.edu/students/study-success/academic-progress/hearings"
         "/appeals-and-reviews/appeals",
         "Appealing a decision to exclude", "academic-rules",
         ("exclusion", "appeal", "eap", "退学申诉", "申诉"),
         applies_to="all"),
    Seed("academic-misconduct", "https://www.monash.edu/students/support/misconduct/academic",
         "Reported for academic misconduct", "academic-rules",
         ("academic misconduct", "cheating", "plagiarism", "学术不端", "作弊"),
         applies_to="all"),
    Seed("academic-misconduct-penalties",
         "https://www.monash.edu/students/support/misconduct/academic/panel-hearing/outcome",
         "Academic misconduct hearing outcomes and penalties", "academic-rules",
         ("academic misconduct", "penalty", "处罚", "学术不端"),
         applies_to="all"),
    Seed("academic-misconduct-appeal",
         "https://www.monash.edu/students/support/misconduct/academic/appeal",
         "Appealing an academic misconduct decision", "academic-rules",
         ("academic misconduct", "appeal", "申诉"),
         applies_to="all"),
    Seed("student-complaints", "https://www.monash.edu/students/support/complaints/how-to",
         "How to submit and resolve a complaint", "academic-rules",
         ("complaint", "grievance", "review", "ombudsman", "投诉", "申诉"),
         applies_to="all"),
    Seed("handbook-glossary", "https://www.monash.edu/students/handbooks/help/handbook-glossary",
         "Handbook glossary", "academic-rules",
         ("glossary", "handbook", "术语"),
         tier="stable", applies_to="all"),

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
         "Important dates", "fees-dates", ("dates", "calendar", "重要日期"), tier="dynamic",
         applies_to="all"),
    Seed("principal-dates", "https://www.monash.edu/students/admin/dates/principal-dates",
         "Principal dates", "fees-dates", ("dates", "semester", "学期时间"), tier="dynamic",
         applies_to="all"),
    Seed("census-dates", "https://www.monash.edu/students/admin/dates/census-dates",
         "Census dates", "fees-dates", ("census", "deadline", "截止日"), tier="dynamic",
         applies_to="all"),
    Seed("fees", "https://www.monash.edu/students/admin/fees",
         "Fees", "fees-dates", ("fees", "tuition", "学费"),
         # Australian fees and dates; Monash Malaysia publishes its own.
         applies_to="australia"),
    Seed("fee-payment-dates", "https://www.monash.edu/students/admin/fees/payment/dates",
         "Fee payment dates", "fees-dates", ("fees", "payment", "缴费"), tier="dynamic",
         applies_to="australia"),
    Seed("graduations", "https://www.monash.edu/students/admin/graduations",
         "Graduations", "fees-dates", ("graduation", "毕业"),
         applies_to="all"),
    Seed("graduation-eligibility",
         "https://www.monash.edu/students/admin/graduations/before/eligibility",
         "Eligibility to graduate", "fees-dates",
         ("graduation", "eligibility", "encumbrance", "毕业条件", "毕业"),
         applies_to="all"),
    Seed("course-completion",
         "https://www.monash.edu/students/admin/graduations/eligibility/course-completion",
         "Course completion", "fees-dates",
         ("course completion", "graduation", "完成学业", "毕业"),
         applies_to="all"),
    Seed("academic-transcripts",
         "https://www.monash.edu/students/support/connect/official-documents/academic-transcripts",
         "Academic records (transcripts)", "fees-dates",
         ("transcript", "records", "成绩单"),
         applies_to="all"),

    # --- Exchange ----------------------------------------------------------
    # Was https://www.monash.edu/study-abroad, which became a 330-character
    # landing page. The exchange programme itself is described here.
    Seed("semester-exchange", "https://www.monash.edu/study-abroad/outbound/exchange",
         "Semester exchange", "exchange",
         ("exchange", "study abroad", "abroad", "semester exchange", "交换", "海外交换")),

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
         "Student Pass (Monash Malaysia)", "malaysia",
         ("malaysia", "student pass", "emgs", "签证", "学生签证", "学生准证"),
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
    Seed("malaysia-science-course-maps",
         "https://www.monash.edu.my/science/current/undergraduate/course-and-unit-information"
         "/course-maps",
         "Course structure and course maps (Monash Malaysia Science)", "malaysia",
         ("malaysia", "course map", "course maps", "science", "课程地图", "修读顺序"),
         applies_to="malaysia"),
    Seed("malaysia-business-course-maps",
         "https://www.monash.edu.my/business/current/course-map-tool",
         "Course map tool (Monash Malaysia Business)", "malaysia",
         ("malaysia", "course map", "course maps", "business", "commerce", "课程地图", "修读顺序"),
         applies_to="malaysia"),
    Seed("malaysia-exam-rules",
         "https://www.monash.edu.my/student-services/student-admin/examinations-results"
         "/exam-rules",
         "Exam rules (Monash Malaysia)", "malaysia",
         ("malaysia", "exam", "考试规则"), applies_to="malaysia"),
)

# The long tail: every other content page on the student sites, Malaysia first.
SEEDS = SEEDS + tuple(
    Seed(slug, url, title, category, tags, tier=tier, applies_to=applies_to)
    for slug, url, title, category, tags, tier, applies_to in COVERAGE
)

SEEDS_BY_SLUG = {seed.slug: seed for seed in SEEDS}
