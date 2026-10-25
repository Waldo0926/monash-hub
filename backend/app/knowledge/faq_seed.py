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
    #: The Monash Malaysia pages for an answer that covers both campuses.
    #: Visas, health cover and study load follow each country's law, so such an
    #: answer says which part is Australia and which is Malaysia, and cites
    #: both: ``page_slug`` for Australia, these for Malaysia.
    malaysia_pages: tuple[str, ...] = ()


FAQ_SEEDS: tuple[FaqSeed, ...] = (
    FaqSeed(
        "how-to-apply-special-consideration",
        "How do I apply for special consideration?",
        "Special consideration covers short-term circumstances outside your control that "
        "affected an assessment. Apply online with the special consideration form; the same "
        "form is used for a short extension and for an extension through special "
        "consideration. You can't ask your chief examiner for an extension. Apply as soon as "
        "you can, no later than 11.55pm on the day the assessment is due or scheduled, and "
        "attach supporting documents. Deferring a final assessment is a separate application. "
        "Check the official page for the exact rules before you apply.",
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
        "It depends on your circumstance, and the official page lists the documents for each "
        "one. For a medical condition you need a medical certificate on the practitioner's "
        "letterhead, signed, stamped and dated; the page says what you can give instead if you "
        "could not get one. A statutory declaration alone is not accepted for a medical "
        "condition, and photographs and medical images are not accepted. At a campus outside "
        "Australia, such as Malaysia, the practitioner must be fully registered in the "
        "country you are enrolled in. Documents not in English need a translation by a "
        "NAATI-accredited translator. You also write an impact statement on the application "
        "form saying how you were affected, from when and for how long.",
        "assessment",
        ("special consideration", "sc", "特殊考虑", "need", "required", "evidence",
         "需要", "提交", "申请"),
        ("documents", "document", "supporting documents", "medical certificate",
         "health professional", "证明", "证明材料", "材料", "医生证明", "病假条"),
        "supporting-documents",
        priority=70,
    ),
    FaqSeed(
        "defer-a-final-assessment",
        "Can I defer my final exam?",
        "Deferring a final assessment has its own form, separate from the short extension and "
        "special consideration form. Apply by 11.55pm on the day the assessment is set and "
        "attach your supporting documents. If it is approved, you sit the assessment in the "
        "deferred assessment period, unless your faculty offers you an alternative assessment. "
        "The official page explains when a deferral applies and how rescheduling works; check "
        "it before you apply.",
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
        "what-is-a-hurdle",
        "What is a hurdle, and what happens if I fail one?",
        "A hurdle is an assessment requirement you have to meet to pass the unit, whatever "
        "your other marks add up to. If you complete and fail a competency hurdle, the chief "
        "examiner must give you at least one additional assessment on the same learning "
        "outcomes; you do not apply for it, and it is due by the end of the teaching period. "
        "Special consideration does not apply to it, and if the hurdle is weighted the most "
        "you can get for the task is 50%. If you still have not met the hurdle and your mark "
        "is 45 or more, your result is NH (Hurdle Fail) 45; below 45 it is N with your mark. "
        "A failed hurdle does not lead to a supplementary assessment. Your unit's hurdles and "
        "the number of attempts are listed in its Handbook entry and on Moodle.",
        "assessment",
        ("fail", "failed", "failing", "pass", "unit", "assessment", "task", "exam", "mark",
         "marks", "45", "what happens", "attempt", "挂", "挂了", "挂科", "没过", "不及格",
         "考核", "考试", "作业", "分数", "怎么办", "什么", "是什么", "意思", "补考", "supp",
         "supplementary", "additional assessment", "额外考核", "重考", "再考", "机会", "几次"),
        ("hurdle", "hurdles", "hurdle requirement", "hurdle requirements", "hurdle fail",
         "competency hurdle", "nh", "及格门槛", "门槛要求"),
        "hurdles",
        priority=95,
    ),
    # The 2026 Assessment Regime Procedure (teaching periods from 27 July 2026)
    # finishes removing threshold hurdles. Students ask what changed as often as
    # what a hurdle is, so the change has its own entry.
    FaqSeed(
        "hurdle-changes",
        "What has changed about hurdles?",
        "Monash is removing threshold hurdles, the rule that you needed a minimum mark (45%) "
        "on a task to pass the unit. No new unit has used one since 1 March 2025, units whose "
        "assessment was reviewed lost them from 1 January 2026, and by 31 December 2026 no "
        "unit will have one. What stays are competency hurdles: tasks that show a skill you "
        "must have, marked pass/fail or with a weighted mark. If you fail one you must be "
        "given at least one additional assessment, and it is double marked before a final "
        "fail. Failing a hurdle still means NH 45 if your mark is 45 or more, with no "
        "supplementary assessment. The current rules are in section 4 of the Assessment "
        "Regime Procedure, for teaching periods starting on or after 27 July 2026.",
        "assessment",
        ("门槛", "及格门槛", "rule", "rules", "policy", "procedure", "2025", "2026", "now",
         "现在", "以前", "之前", "还有", "还要", "unit", "units", "课", "什么", "哪些",
         "change", "changes", "changed", "changing", "new", "removed", "变化", "变了",
         "改了", "改成", "改变", "改动", "更新", "新规", "新规定", "新政策", "取消",
         "没有了", "不一样", "区别"),
        ("hurdle", "hurdles", "threshold hurdle", "threshold hurdles", "hurdle changes",
         "hurdle改", "hurdle变", "hurdle新", "hurdle取消", "hurdle 改", "hurdle 变",
         "hurdle 新",
         "分数门槛", "最低分要求"),
        "hurdles",
        priority=60,
    ),
    FaqSeed(
        "supplementary-assessment",
        "Can I get a supplementary assessment?",
        "If you finish a unit with a mark of 45 to 49, a grade of N or NH, and your results "
        "show NS, you have already been given a supplementary assessment - there is nothing "
        "to apply for. Not every unit offers one; its Handbook entry says. It is optional and "
        "it is your last chance to pass the unit: pass it and your result becomes 50 (P), "
        "which is the most you can get; fail it or skip it and you keep your original mark. "
        "It is held on a set date within 90 days of results release. You can't reschedule "
        "it; special arrangements only cover a time-zone clash. Retaking the unit instead "
        "can earn a higher mark for your WAM, but costs another enrolment.",
        "assessment",
        ("fail", "failed", "unit", "exam", "assessment", "45", "49", "ns", "can", "get",
         "eligible", "挂科", "挂了", "不及格", "考试", "能", "可以", "有没有", "资格"),
        ("supplementary", "supplementary assessment", "supplementary exam", "supp",
         "supp exam", "补考"),
        "supplementary-assessment",
        priority=90,
    ),
    FaqSeed(
        "unsatisfactory-progress",
        "I got an email about unsatisfactory academic progress - what does it mean?",
        "Monash reviews academic progress after each review period and assigns one of three "
        "risk levels. Level one (Advice) means you failed a unit but did not meet any "
        "unsatisfactory progress criterion. Level two (Monitoring) means you met a criterion "
        "for the first time: you must complete My Progress and Support, and your faculty may "
        "set conditions on your enrolment. Level three (Intervention) - for example meeting "
        "a criterion two periods in a row, or failing a compulsory unit twice - means you "
        "must complete My Academic Progress Response and may be called to an Academic "
        "Progress Committee hearing, which can exclude you from your course. Do what the "
        "email asks by its deadline: your engagement is taken into account later.",
        "academic-rules",
        ("email", "notice", "letter", "level", "risk", "mean", "means", "fail", "failed",
         "邮件", "通知", "收到", "什么意思", "怎么办", "挂科", "等级"),
        ("unsatisfactory progress", "unsatisfactory academic progress",
         "academic progress", "risk level", "apc", "academic progress committee",
         "学业预警", "学业进度", "学业警告", "学术预警"),
        "unsatisfactory-progress",
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
        "GPA is calculated on a 4.0 scale from your grades rather than your marks: High "
        "Distinction 4.0, Distinction 3.0, Credit 2.0, Pass 1.0, Near pass 0.7, Fail and "
        "Hurdle fail 0.3, Withdrawn fail 0.0. Some results, such as SFR and NE, are not "
        "counted. Your GPA is shown in WES and on your transcript. "
        "Malaysia also uses a Cumulative Grade Point Average (CGPA) with different values: "
        "High Distinction 4.0, Distinction 3.67, Credit 2.85, Pass 2.15, Near pass 1.7, Fail "
        "and Hurdle fail 1.15, Withdrawn fail 0.0. It is not on your academic record, so you "
        "request a CGPA letter.",
        "assessment",
        ("results", "calculate", "calculation", "scale", "怎么算", "计算", "算",
         "malaysia", "马来西亚", "马莫", "letter", "证明", "成绩单", "transcript"),
        ("gpa", "cgpa", "绩点", "平均绩点", "grade point average",
         "cumulative grade point average"),
        "gpa",
        priority=80,
    ),
    FaqSeed(
        "census-date-meaning",
        "What is a census date and why does it matter?",
        "The census date is the last day you can withdraw from a unit without paying for it and "
        "without it appearing on your record. After that date you are liable for the fees and a "
        "withdrawal is recorded. Census dates differ by teaching period, so check the date for "
        "your specific unit rather than assuming one date covers the semester. At the "
        "Malaysia campus, a unit withdrawn after the census date shows as WD-LATE or WD-FAIL, "
        "and the dates are in Monash Malaysia's Principal Dates.",
        "enrolment",
        ("withdraw", "fees", "deadline", "date", "dates", "important", "matter",
         "截止", "截止日", "日期", "学费", "重要", "为什么", "退课"),
        ("census", "census date", "census dates", "学籍统计日", "退课截止",
         "退课截止日", "退课截止日期", "退课的截止日期"),
        "census-dates-explained",
        priority=85,
        malaysia_pages=("malaysia-frequently-asked-questions-faq-unit-withdra",),
    ),
    FaqSeed(
        "how-to-withdraw-from-a-unit",
        "How do I withdraw from a unit?",
        "Australia: withdraw through WES while enrolment changes are open. Before the census "
        "date there is no fee and no record; after it, you keep the fee liability and the unit "
        "shows as a withdrawal. If you are on a student visa you have study load requirements "
        "to maintain: Monash's study load page says you can reduce your load only in "
        "compassionate or compelling circumstances, unless you are in your final year and "
        "will finish within the time on your CoE. "
        "Malaysia: after the census date a withdrawn unit shows as WD-LATE or WD-FAIL, and the "
        "date you withdraw can affect fee refunds and your academic record. The last day to "
        "withdraw without academic penalty is before the WD-LATE date ends; the dates are in "
        "Monash Malaysia's Principal Dates. With a Student Pass, a full-time load is 48 credit "
        "points a year (usually 24 a semester). You can go down to no less than 18 credit "
        "points a semester only in the cases the page lists, such as an academic progress "
        "condition, a medical reason or your final semester, and with supporting documents. "
        "Below 18 credit points you have to apply for intermission.",
        "enrolment",
        ("enrolment", "unit", "units", "subject", "course", "wes", "课", "一门课",
         "课程", "网上", "malaysia", "马来西亚", "马莫", "australia", "澳洲", "澳大利亚",
         "澳莫"),
        ("withdraw", "withdrawal", "drop", "discontinue a unit", "退课", "退选",
         "退掉"),
        "add-or-withdraw-units",
        priority=75,
        malaysia_pages=("malaysia-frequently-asked-questions-faq-unit-withdra",
                        "malaysia-international-students-during-your-studies"),
    ),
    FaqSeed(
        "student-visa-work-hours",
        "How many hours can I work on a student visa?",
        "The rules are each country's, not Monash's, and they are different. "
        "Australia: work rights for student visa holders are set by the Australian Government, "
        "and the cap has changed several times in recent years. Monash's page links to the "
        "current Department of Home Affairs conditions - always confirm the number there "
        "before relying on it. "
        "Malaysia: with a Student Pass you may work only during semester breaks or public "
        "holidays of more than seven days, and for no more than 20 hours a week, at "
        "restaurants, petrol kiosks, mini markets or hotels; the page lists jobs that are not "
        "allowed. Every job has to be approved by the Immigration Department: you apply "
        "through the International Student Pass office and must be there in person when the "
        "application is submitted.",
        "international",
        ("visa", "student visa", "签证", "学生签证", "hours", "hour", "week",
         "fortnight", "australia", "australian", "小时", "每周", "一周", "两周",
         "澳洲", "澳大利亚", "澳莫", "多少", "能", "可以", "limit", "cap", "job",
         "international", "国际学生", "留学生", "malaysia", "马来西亚", "马莫",
         "student pass", "学生准证", "holiday", "holidays", "break", "breaks", "假期",
         "放假"),
        ("work", "working", "work hours", "work rights", "part-time work",
         "打工", "兼职", "工作时长", "打工时长"),
        "working-on-a-student-visa",
        priority=70,
        malaysia_pages=("malaysia-international-students-student-pass2",),
    ),
    FaqSeed(
        "what-is-coe",
        "What is a CoE and when do I need a new one? (Australia)",
        "Australia: a Confirmation of Enrolment (CoE) is the enrolment document your student "
        "visa is based on. If your visa will expire "
        "before you finish your course, you need a new CoE, and you can apply two months "
        "before the visa expires. Monash approves a new one only for compassionate or "
        "compelling circumstances, an academic progress intervention, or an approved "
        "deferment or intermission. Changing your study load can also mean a new CoE with a "
        "new completion date. "
        "Malaysia: there is a Student Pass instead. You come in on an eVisa Approval Letter "
        "(eVAL), and you renew the pass through the International Student Pass office.",
        "international",
        ("visa", "签证", "new", "need", "when", "change", "新", "换", "需要",
         "什么时候", "australia", "澳洲"),
        ("coe", "confirmation of enrolment", "confirmation of enrollment", "入学确认",
         "入学确认书"),
        "confirmation-of-enrolment",
        priority=60,
        malaysia_pages=("malaysia-student-pass",
                        "malaysia-international-students-during-your-studies"),
    ),
    FaqSeed(
        "international-student-health-insurance",
        "Do international students need health insurance?",
        "Yes, at both campuses, but the cover is different. "
        "Australia: international students on a student visa must have Overseas Student "
        "Health Cover (OSHC) for the length of their visa while studying in Australia. The "
        "official page explains how to buy it and who is exempt. "
        "Malaysia: the Ministry of Higher Education requires every international student to "
        "have valid medical insurance for the whole period of study, and proof of it is a "
        "condition of the Student Pass. You buy it through Monash University Malaysia, from "
        "its appointed insurer, when you apply for your Student Pass, and the fee to renew "
        "the pass includes it. A personal policy can only be added on top of it.",
        "international",
        ("international", "国际学生", "留学生", "visa", "student visa", "签证", "学生签证",
         "student pass", "学生准证", "need", "required", "compulsory", "buy", "要", "买",
         "必须", "强制", "malaysia", "马来西亚", "马莫", "australia", "澳洲", "澳大利亚",
         "澳莫", "medical", "health", "看病", "医疗", "cover", "policy", "insurance",
         "保险", "医保"),
        # Not 医保 or 保险 alone: a bare topic word is a search for the pages.
        ("health insurance", "medical insurance", "health cover", "oshc",
         "overseas student health cover", "医疗保险", "健康保险", "买保险", "买医保"),
        "oshc",
        priority=50,
        malaysia_pages=("malaysia-international-students-medical-insurance",
                        "malaysia-international-students-during-your-studies"),
    ),
    FaqSeed(
        "apply-for-intermission",
        "Can I take a semester off?",
        "Yes - it is called intermission, and approval is not automatic. The rules for "
        "international students depend on the campus. "
        "Australia: you can take up to 12 months during your course, over one or two teaching "
        "periods. If you are on a student visa, study leave is approved only in compassionate "
        "or compelling circumstances. Before you return, you apply for a new Confirmation of "
        "Enrolment (CoE); the page explains when you also need a new student visa. "
        "Malaysia: you can take up to two semesters or 12 months, once your first census date "
        "has passed, and you should apply before the census date of the current semester. "
        "With a Student Pass, intermission for medical reasons lets you stay in Malaysia as "
        "long as your Student Pass stays valid, with medical evidence. For any other reason "
        "you must cancel your Student Pass and leave Malaysia, and to come back you apply for "
        "a new eVisa Approval Letter (eVAL) through the International Student Pass office, "
        "between 4 and 2 months before the semester starts. You must still finish within "
        "the full-time course duration plus at most 12 months of approved leave.",
        "enrolment",
        ("leave", "semester", "take", "off", "break", "study", "apply", "学期",
         "一个学期", "申请", "请假", "visa", "student visa", "签证", "学生签证",
         "student pass", "学生准证", "affect", "影响", "international", "国际学生",
         "留学生", "malaysia", "马来西亚", "马莫", "australia", "澳洲", "澳大利亚",
         "澳莫"),
        ("intermission", "休学", "停学", "gap year", "leave of absence",
         "semester off", "break from study", "break from studies", "study break"),
        "intermission",
        priority=55,
        malaysia_pages=("malaysia-changing-your-enrolment-intermission",
                        "malaysia-international-students-during-your-studies"),
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
        "Australia: exchange runs through Monash Abroad. Eligibility normally depends on your "
        "WAM, how much of your course you have completed, and having units that can be "
        "credited back. "
        "Applications open well before the semester you want to travel in, so check the round "
        "dates early. At the Malaysia campus, start from Monash Malaysia's outbound exchange "
        "page.",
        "exchange",
        ("go", "eligible", "eligibility", "requirement", "requirements", "apply",
         "条件", "要求", "申请", "去", "出国"),
        ("exchange", "study abroad", "abroad", "monash abroad", "交换", "海外交换",
         "出国交换", "交换生"),
        "semester-exchange",
        priority=50,
        malaysia_pages=("malaysia-outbound-exchange-program",),
    ),
    # Monash added the notice to the graduations page on 2026-10-16 and says the
    # full details come out in December 2026. Rewrite this entry then, and check
    # whether Monash Malaysia has moved over: its FAQ still says you must apply.
    # The delay rule (3 months in the system, up to 12 through Monash Connect)
    # is the one sentence no page backs yet: the graduations office confirmed
    # it in writing in October 2026, and the answer says so. Replace it with
    # the published wording in December.
    FaqSeed(
        "automatic-conferral",
        "Do I still need to apply to graduate?",
        "From December 2026, Monash confers awards automatically, so you will not need to "
        "apply to graduate. Once your faculty confirms you have completed your course, you "
        "are conferred in the next monthly cycle and receive your testamur shortly after. "
        "You are conferred first and then invited to an upcoming ceremony, so graduating in "
        "absentia will no longer apply. If you have already applied to graduate this year, "
        "the current process on the official page still applies to you. Full details of the "
        "new process will be published in December. "
        "Not on the website yet, but confirmed by Monash's graduations office in October "
        "2026: after you complete your course you can delay conferral yourself in the system "
        "by up to 3 months. For a longer delay, for example for a graduate recruitment "
        "program, ask Monash Connect; it can be up to 12 months after you complete. Your "
        "testamur shows the date the award was actually conferred. "
        "Monash Malaysia's own graduation pages "
        "still describe applying to graduate, so Malaysia campus students should check "
        "those as well until they are updated.",
        "graduation",
        ("graduation", "graduate", "graduating", "ceremony", "degree", "award", "awards",
         "automatic", "automatically", "december", "2026", "monthly", "faculty",
         "complete", "completed", "change", "changes", "new", "process", "still",
         "apply", "applied", "malaysia", "毕业", "毕业典礼", "典礼", "学位", "自动",
         "每月", "学院", "完成", "变化", "改变", "新", "还", "12月", "十二月",
         "马来西亚", "校区", "申请", "毕业证", "学位证", "证书", "delay", "defer",
         "postpone", "months", "3", "12", "recruitment", "program", "延迟", "推迟", "延期",
         "晚点", "个月", "三个月", "十二个月", "招聘", "工作", "日期", "connect"),
        ("apply to graduate", "applying to graduate", "apply for graduation",
         "graduation application", "conferral", "conferred", "confer", "testamur",
         "in absentia", "delay conferral", "defer conferral", "postpone conferral",
         "延迟授予", "推迟授予", "延期授予", "晚点授予", "授予延期", "延迟毕业", "推迟毕业",
         "申请毕业", "毕业申请", "授予学位", "学位授予", "自动毕业",
         "自动授予", "缺席毕业", "毕业要不要申请", "毕业还要申请", "毕业还需要申请",
         "毕业需要申请", "毕业要申请"),
        "graduations",
        priority=45,
    ),
    # Malaysia campus only. The unit list changes with the intake and differs for
    # Malaysian and international students, and students ask for their own row,
    # so every list on the page is spelled out here. Re-check it each semester.
    FaqSeed(
        "malaysia-general-studies",
        "Which MPU (General Studies) units do I need to graduate in Malaysia?",
        "At the Malaysia campus, the Ministry of Higher Education requires you to pass "
        "General Studies units, also called MPU units, before you graduate. Which ones depends "
        "on your intake and on whether you are a Malaysian or an international student, and "
        "the list got longer from Semester 2, 2026. "
        "International students: Semester 2, 2026 intake: MPU3143, MPU3172, MPU3222, "
        "MPU3312, MPU3322, MPU3412. Semester 1, 2025 intake: MPU3143, MPU3193, MPU3312, "
        "MPU3412. Semester 1, 2024 intake: MPU3143, MPU3193, MPU3312. "
        "Malaysian students: Semester 2, 2026 intake: MPU3182, MPU3192, MPU3222, MPU3312, "
        "MPU3322, MPU3412. Semester 1, 2025 intake: MPU3183, MPU3193, MPU3312, MPU3412. "
        "Semester 1, 2024 intake: MPU3183, MPU3193, MPU3312. Malaysian students without a "
        "Credit in SPM Bahasa Melayu, or without SPM, also take MPU3212. "
        "Diploma of Business: international students MPU2143, MPU2313, MPU2412; Malaysian "
        "students MPU2183, MPU2313, MPU2412, plus MPU2212 under the same SPM rule. "
        "The page names only these intakes, so if you started in another one, ask Monash "
        "Connect which list is yours. You can take them at any time, but Monash Malaysia "
        "suggests finishing them in your first three semesters.",
        "enrolment",
        ("malaysia", "马来西亚", "马莫", "graduate", "graduation", "毕业", "need", "required",
         "requirement", "要", "需要", "必须", "which", "哪些", "什么", "units", "unit", "课",
         "international", "国际生", "国际学生", "留学生", "malaysian", "本地生", "本地学生",
         "马来西亚学生", "intake", "入学", "入读", "开学", "take", "修", "上", "学", "几门",
         "多少门", "几个", "列表", "清单", "semester", "学期", "s1", "s2", "26s2", "25s1",
         "24s1", "2024", "2025", "2026", "diploma", "文凭", "预科", "spm", "课程", "每年",
         "每个学期", "每学期", "年份", "change",
         "changed", "different", "不一样", "不同", "变了", "增加", "新增", "多了"),
        ("mpu", "mpu units", "general studies", "general study", "通识课", "通识",
         "马来西亚必修课"),
        "malaysia-general-studies",
        priority=50,
    ),
    FaqSeed(
        "malaysia-getting-around",
        "How do I get to the Malaysia campus and around Sunway?",
        "The free Sunway Shuttle Bus stops at Monash and runs about every 45 minutes from 7 am "
        "to 10.15 pm. The BRT station SunU-Monash is in front of the campus: the line connects "
        "to the KTM train at Setia Jaya and to the Kelana Jaya LRT at USJ 7, both of which reach "
        "KL Sentral, where the express train goes to KLIA. A covered walkway links the campus "
        "to Sunway Pyramid, and a Grab there costs under RM10. The official page has the "
        "shuttle stops, the BRT stations and where to park.",
        "campus",
        ("malaysia", "马来西亚", "马莫", "sunway", "双威", "campus", "学校", "校园", "get",
         "go", "去", "到", "怎么", "how", "pyramid", "金字塔", "kl", "吉隆坡", "klia", "机场",
         "kl sentral", "around", "附近"),
        ("transport", "public transport", "shuttle", "shuttle bus", "brt", "lrt", "ktm",
         "get to campus", "get to the campus", "getting to campus", "交通", "校车", "班车",
         "公交", "公车", "轻轨", "地铁", "怎么去学校", "klia", "去机场", "到机场", "回机场",
         "机场怎么去", "机场到学校"),
        "malaysia-maps-and-transport",
        priority=40,
    ),
    FaqSeed(
        "malaysia-campus-map",
        "Where is my classroom? Is there a campus map for Monash Malaysia?",
        "Download the Monash Study app: you can look up and search where a classroom or "
        "building is on campus. The maps and transport page also has a campus map and a map "
        "of how to get to the campus.",
        "campus",
        ("malaysia", "马来西亚", "马莫", "where", "在哪", "在哪里", "哪里", "find", "找",
         "room", "building", "楼", "教学楼", "位置", "search", "查", "地图", "map"),
        ("campus map", "classroom", "lecture theatre", "monash study", "校园地图", "学校地图",
         "教室", "教室在哪", "找教室", "教室位置", "马莫地图", "校区地图"),
        "malaysia-maps-and-transport",
        priority=40,
    ),
)


#: FAQ slug -> its Malaysia pages, for the answers written for both campuses.
MALAYSIA_PAGES: dict[str, tuple[str, ...]] = {
    seed.slug: seed.malaysia_pages for seed in FAQ_SEEDS if seed.malaysia_pages
}
