"""The Chinese translations, as reviewable data.

They live in the repository rather than only in the database for the same reason
the FAQ does: a translation of somebody else's words is a claim this platform is
making, and a claim belongs somewhere it can be read in a diff and argued with
in a pull request. ``python -m app.knowledge.seed`` loads them.

**What is in here and what is not.** Two kinds of English get translated:

* the Handbook's *boilerplate* — the stock paragraphs it repeats across
  thousands of units, where one careful translation covers the lot; and
* whole pages that were translated deliberately, sentence by sentence.

Everything else stays in English until somebody translates it. That is not a
gap to be filled by a tool later: it is the design. A page that is 60% Chinese
and 40% English is obviously partial and a reader treats it accordingly. A page
that is 100% Chinese because a machine filled the other 40% reads as finished
and is trusted as finished, and the terms it gets wrong — hurdle, census date,
intermission, WAM — are exactly the ones that cost a student money or a
semester.

Adding a translation
--------------------
Add an entry below and re-run the seeder. For a page body, key each entry on the
**exact** English string the crawler extracted; anything that does not match
character for character simply stays in English, which is the safe direction to
fail in. ``source_hash`` is filled in by the seeder from the page's current
content hash, so that a later Monash edit marks the translation stale on screen
instead of leaving it to speak for text that has changed underneath it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.models.translation import FAQ_ENTRY, GLOBAL, OFFICIAL_PAGE

ZH = "zh"


@dataclass(frozen=True)
class TranslationSeed:
    locale: str
    target_type: str
    target_key: str
    field: str
    text: str | None = None
    strings: dict[str, str] = field(default_factory=dict)
    translator: str = "monash-hub"
    note: str | None = None


# --- Handbook boilerplate -------------------------------------------------
#
# Measured across a 160-unit sample of the 2026 Handbook: one assessment notice
# on every unit that has one, six teaching-approach paragraphs covering most
# units that list an approach, and five workload paragraphs covering most that
# list a workload. Translating these thirteen strings is worth more than
# translating any thirteen individual units.

HANDBOOK_BOILERPLATE: dict[str, str] = {
    "Assessment details may change. Please refer to the assessment information in "
    "Moodle closer to the start of the teaching period.":
        "考核细节可能会有变动。请在教学期开始前，以 Moodle 上的考核信息为准。",

    "Active learning - This unit engages you in actively applying your knowledge, "
    "skills and attributes in interactive, collaborative and reflective activities.":
        "主动学习 —— 本课程通过互动、协作与反思性的活动，让你主动运用自己的知识、技能与素养。",

    "Active learning":
        "主动学习",

    "Active learning - You will be provided with the opportunity to engage with "
    "relevant literature and resources. Further, you will be encouraged to deepen "
    "your understanding of topic areas through collegial discussion and debate, and "
    "by participating in activities designed to extend your understanding.":
        "主动学习 —— 你将有机会阅读并使用相关文献与资源；同时，课程鼓励你通过同侪讨论与辩论，"
        "以及参与专门设计的拓展活动，来加深对各个主题的理解。",

    "Problem-based learning - This unit includes problem-based learning approaches, "
    "where you engage in research, integrate theory and practice and apply knowledge "
    "and skills to develop viable solutions in response to a problem or set of problems.":
        "问题导向学习 —— 本课程采用问题导向的教学方式：你需要开展研究、把理论与实践结合起来，"
        "并运用知识与技能，针对某个问题或一组问题提出可行的解决方案。",

    "Case-based teaching - This unit includes case-based teaching, where you apply "
    "your knowledge and engage in analytical and reflective thinking to solve complex "
    "contextual scenarios. Activities are often designed so that there is not one "
    "clear answer, but you need to work together to examine, analyse and make "
    "decisions to resolve the situation.":
        "案例教学 —— 本课程采用案例教学：你需要运用所学知识，通过分析与反思去处理复杂的情境。"
        "这类活动通常没有唯一的标准答案，需要你和同学一起考察、分析并做出决策来解决问题。",

    "Enquiry-based learning - This unit engages you in enquiry-based learning, where "
    "you will be encouraged to use your own knowledge to develop and engage in a "
    "process of enquiry, study and research to identify areas to be investigated and "
    "an approach to doing so.":
        "探究式学习 —— 本课程采用探究式学习：课程鼓励你运用自己已有的知识，展开探究、学习与研究，"
        "自行确定值得深入的方向以及研究的方法。",

    "Research activities - This unit allows you to develop your research skills by "
    "engaging in structured inquiry using a systematic approach and "
    "discipline-specific methodologies.":
        "研究活动 —— 本课程让你通过结构化的探究，运用系统性的方法与本学科特有的研究方法，"
        "来培养自己的研究能力。",

    "Online learning":
        "线上学习",

    "Field trips - This unit provides you with opportunities to participate in "
    "experiential learning by visiting cultural, geographical and/or industrial sites "
    "relevant to your studies.":
        "实地考察 —— 本课程提供体验式学习的机会，带你走访与所学内容相关的文化、地理或产业场所。",

    "Minimum total expected workload to achieve the learning outcomes for this unit "
    "is 144 hours per semester typically comprising a mixture of scheduled learning "
    "activities and independent study. Independent study may include associated "
    "readings, assessment and preparation for scheduled activities. You are expected "
    "to complete all pre-class activities prior to your scheduled class, and "
    "post-class activities should be completed after your scheduled class. Learning "
    "activities may include a combination of teacher directed, peer directed and "
    "online engagement activities.":
        "要达成本课程的学习成果，每学期预计最少需投入 144 小时，"
        "通常由安排好的教学活动和自主学习共同构成。"
        "自主学习可能包括相关阅读、完成考核，以及为教学活动做准备。你需要在上课前完成全部课前活动，"
        "课后活动则应在课后完成。学习活动可能包含教师引导、同侪引导和线上参与等多种形式。",

    "Minimum total expected workload to achieve the learning outcomes for this unit "
    "is 144 hours per semester typically comprising a mixture of scheduled learning "
    "activities and independent study. Scheduled activities may include a combination "
    "of teacher directed learning, peer directed learning and online engagement.":
        "要达成本课程的学习成果，每学期预计最少需投入 144 小时，"
        "通常由安排好的教学活动和自主学习共同构成。"
        "教学活动可能包含教师引导学习、同侪引导学习和线上参与等多种形式。",

    "The minimum total expected workload to achieve the learning outcomes for this "
    "unit is 144 hours per teaching period comprising a mixture of scheduled learning "
    "activities and independent study.":
        "要达成本课程的学习成果，每个教学期预计最少需投入 144 小时，"
        "由安排好的教学活动和自主学习共同构成。",

    "Scheduled learning activities may include a combination of teacher directed "
    "learning, peer directed learning and online engagement.":
        "安排好的学习活动可能包含教师引导学习、同侪引导学习和线上参与等多种形式。",

    "Usually, you can expect to engage with:":
        "通常你可以预期参与以下内容：",
}


# --- official guide titles ------------------------------------------------
#
# Titles only, for now. The summaries are the first paragraph the crawler
# extracted, and on a dozen of these pages that paragraph is currently the MoVA
# chat widget rather than the page - fixed in the extractor, but the corrected
# summaries do not exist until the next crawl runs, and translating text that is
# about to be replaced is work thrown away.

GUIDE_TITLES: dict[str, str] = {
    "enrolments": "选课与注册",
    "changing-your-enrolment": "更改你的选课",
    "add-or-withdraw-units": "加选或退选课程",
    "intermission": "休学（Intermission）",
    "discontinue-course": "退出所修课程",
    "re-enrol": "重新注册",
    "census-dates-explained": "什么是 census date（学籍统计日）",
    "course-advice": "课程规划咨询",
    "credit-and-enrolment": "学分减免与选课",
    "study-at-another-institution": "在其他院校修读课程",
    "special-consideration": "延期与特殊考虑（Special Consideration）",
    "defer-final-assessment": "申请延期或改期参加期末考核",
    "supporting-documents": "特殊考虑所需的证明材料",
    "results": "成绩",
    "wam": "加权平均分（WAM）",
    "gpa": "平均绩点（GPA）",
    "results-legend": "如何看懂你的分数与等级",
    "final-assessment-dates": "期末考核日期",
    "assessment-at-monash": "Monash 的考核方式",
    "allocate-timetable": "你的课表 · Allocate+",
    "academic-progress": "学业进度（Academic Progress）",
    "about-academic-progress": "关于学业进度审查",
    "academic-integrity": "学术诚信",
    "policies": "政策与流程",
    "student-conduct": "学生行为准则",
    "international-students": "国际学生",
    "student-visa": "你的学生签证",
    "working-on-a-student-visa": "持学生签证打工",
    "visa-changes": "影响签证的变动",
    "confirmation-of-enrolment": "入学确认书（CoE）",
    "oshc": "海外学生医疗保险（OSHC）",
    "important-dates": "重要日期",
    "principal-dates": "校历主要日期",
    "census-dates": "Census date（学籍统计日）",
    "fees": "学费",
    "fee-payment-dates": "缴费日期",
    "graduations": "毕业典礼",
    "academic-transcripts": "成绩单与学业记录",
    "study-abroad": "海外交换与留学",
    "malaysia-student-services": "学生服务（马来西亚校区）",
}


# --- the GPA page, in full ------------------------------------------------
#
# Translated sentence by sentence against the extraction of
# monash.edu/students/admin/assessments/results/gpa. Two decisions worth
# knowing about:
#
# * The tab labels stay "Australia" and "Malaysia" in translation as 澳大利亚 /
#   马来西亚, and the two sets of numbers are kept apart, because the Malaysian
#   CGPA scale is genuinely different and merging them would be the single most
#   expensive mistake this page could make.
# * Grade names keep the English in brackets - a transcript says "High
#   distinction", not 高分优秀, and a student comparing the two needs to see the
#   word they will actually be shown.

GPA_PAGE: dict[str, str] = {
    "Grade point average (GPA)": "平均绩点（GPA）",

    "The Grade Point Average (GPA) is an internationally recognised calculation used "
    "to find the average result of all grades achieved throughout your course.":
        "平均绩点（GPA）是一种国际通行的计算方式，用来得出你在整个课程期间所有成绩等级的平均结果。",

    "For example, your grades might be a pass, credit, high distinction, distinction "
    "and so on. All grades,including fail grades and grades from any repeated units, "
    "are given a numerical value and then those values are averaged which gives you "
    "your GPA.":
        "举例来说，你的成绩等级可能是 pass、credit、high distinction、distinction 等等。"
        "所有等级——包括不及格的等级，以及重修课程的等级——都会被赋予一个数值，再对这些数值取平均，"
        "得到的就是你的 GPA。",

    "The GPA helps:": "GPA 的作用是：",
    "tertiary providers compare your results with those of other students":
        "让高等院校把你的成绩与其他学生的成绩作比较",
    "prospective employers interpret your results.":
        "让潜在雇主看懂你的成绩。",

    "Your Monash GPA is calculated on a four point grading scale where 4.0 is the "
    "highest and 0.0 is the lowest achievement.":
        "Monash 的 GPA 采用四分制，4.0 为最高，0.0 为最低。",

    "How to find out your GPA": "怎样查到自己的 GPA",

    "We'll calculate your GPA for your award course if you started on or after "
    "semester one, 2008. We don't calculate the GPA for research master's and PhD "
    "courses.":
        "如果你的学位课程是在 2008 年第一学期或之后开始的，学校会为你计算 GPA。"
        "研究型硕士和博士课程不计算 GPA。",

    "We'll calculate your GPA for your award course if you started on or after "
    "semester one, 2008.":
        "如果你的学位课程是在 2008 年第一学期或之后开始的，学校会为你计算 GPA。",

    "You can use our online calculator below to estimate your GPA.":
        "你可以用下方的在线计算器估算自己的 GPA。",
    "You can view your latest GPA in your unofficial academic record in the Web "
    "Enrolment System (WES) at any time. It will be calculated using the results from "
    "all of your completed semesters.":
        "你随时可以在选课系统（WES）的非正式学业记录里查看最新的 GPA，"
        "它是用你已完成的所有学期的成绩算出来的。",
    "You can view your latest GPA in the Web Enrolment System (WES) at any time.":
        "你随时可以在选课系统（WES）里查看最新的 GPA。",
    "You can also see your GPA in the Student Portal (either in the course progress "
    "screen or through the GPA/WAM widget).":
        "你也可以在学生门户（Student Portal）里看到 GPA——在课程进度页面，或者 GPA/WAM 小组件里。",
    "Your GPA will also appear on your academic record (transcript). You’ll receive a "
    "free academic record when you graduate.":
        "GPA 也会出现在你的学业记录（成绩单）上。毕业时你会免费获得一份学业记录。",
    "If you believe your GPA is incorrect, message Monash Connect and we’ll "
    "investigate it for you.":
        "如果你认为自己的 GPA 有误，可以给 Monash Connect 发消息，学校会帮你核查。",

    "Converting your GPA": "换算你的 GPA",
    "Other institutions in Australia and abroad can have different GPAs. For example, "
    "a seven point grading scale.":
        "澳大利亚国内外的其他院校可能使用不同的 GPA 制度，例如七分制。",
    "If you have a GPA from another institution and you want to convert it to our four "
    "point scale, you can use our online calculator.":
        "如果你有其他院校的 GPA，想换算成 Monash 的四分制，可以使用在线计算器。",
    "If however you want to convert your Monash GPA to that of another institution, "
    "you’ll need to contact that institution for assistance. They may even have an "
    "online calculator on their website.":
        "但如果你想把 Monash 的 GPA 换算成其他院校的制度，需要联系那所院校寻求帮助，"
        "对方网站上可能也有在线计算器。",
    "If you want to convert your GPA to WAM, simply use our Weighted average mark "
    "(WAM) calculator.":
        "如果你想把 GPA 换算成 WAM，直接使用加权平均分（WAM）计算器即可。",

    "Australia": "澳大利亚",
    "Malaysia": "马来西亚",

    "GPA calculator": "GPA 计算器",
    "Use the online calculator to estimate your GPA.": "使用在线计算器估算你的 GPA。",
    "Estimate your GPA": "估算你的 GPA",
    "Methodology": "计算方法",
    "To calculate your GPA, we need to assign each grade a value. We use a 4.0 GPA "
    "scale.":
        "计算 GPA 时，需要先给每个成绩等级赋一个数值。Monash 使用 4.0 分制。",

    "Grades and their GPA grade value": "各成绩等级对应的 GPA 数值",
    "Grade": "成绩等级",
    "GPA grade value": "GPA 数值",
    "High distinction": "High distinction（最高优等）",
    "Distinction": "Distinction（优等）",
    "Credit": "Credit（良好）",
    "Pass": "Pass（及格）",
    "Near pass": "Near pass（接近及格）",
    "Fail": "Fail（不及格）",
    "Hurdle fail": "Hurdle fail（必过项未通过）",
    "Withdrawn fail": "Withdrawn fail（退课记为不及格）",

    "Grades not included in the calculation:": "不计入计算的成绩等级：",
    "SFR (satisfied faculty requirements)": "SFR（已满足学院要求）",
    "NE (not examinable)": "NE（不参加考核）",
    "NAS (not assessed)": "NAS（未评定）",
    "WI (withdrawn incomplete)": "WI（退课且未完成）",
    "PGO (pass grade only)": "PGO（仅记及格）",

    "GPA calculation formula": "GPA 计算公式",
    "GPA = Σ (grade value x unit credit points) ÷ Σ unit credit points":
        "GPA = Σ（成绩数值 × 课程学分）÷ Σ 课程学分",
    "Calculation steps": "计算步骤",
    "Multiply each grade value by the unit credit points": "把每个成绩数值乘以该课程的学分",
    "Sum the resulting values (weighted GPA unit score)": "把得到的数值相加（即加权 GPA 课程分）",
    "Sum the unit credit points": "把课程学分相加",
    "Divide the sum of the weighted GPA unit score by the sum of the unit credit points":
        "用加权 GPA 课程分之和除以课程学分之和",
    "Calculate to three decimal places.": "计算结果保留三位小数。",

    "Example": "示例",
    "An example of how a weighted GPA unit score is calculated for nine units with a "
    "range of grades and credit points.":
        "以九门成绩与学分各不相同的课程为例，说明加权 GPA 课程分的算法。",
    "An example of how a weighted GPA unit score is calculated.":
        "加权 GPA 课程分的计算示例。",
    "Unit": "课程",
    "Mark": "分数",
    "Grade value": "成绩数值",
    "Unit credit points": "课程学分",
    "Weighted GPA unit score": "加权 GPA 课程分",
    "Total": "合计",
    "Final calculation:": "最终计算：",

    # --- Malaysia tab -----------------------------------------------------
    "Cumulative Grade Point Average (CGPA)": "累计平均绩点（CGPA）",
    "The Cumulative Grade Point Average is a calculation used in Malaysia.":
        "累计平均绩点（CGPA）是马来西亚使用的一种计算方式。",
    "How to get your CGPA": "怎样拿到自己的 CGPA",
    "As your CGPA doesn't appear on your academic record, you need to request a CGPA "
    "letter.":
        "CGPA 不会出现在你的学业记录上，需要另外申请一份 CGPA 证明信。",
    "Delivery times are:": "寄送时间为：",
    "within Australia – up to five University working days":
        "澳大利亚境内 —— 最多五个学校工作日",
    "overseas – 10 to 15 University working days.":
        "寄往海外 —— 10 至 15 个学校工作日。",
    "The CGPA doesn't apply to any grade other than those listed in the table below. "
    "It's available to students who started a Monash University course on or after 1 "
    "January 2008.":
        "CGPA 只适用于下表所列的成绩等级。它面向 2008 年 1 月 1 日或之后开始 Monash 课程的学生。",
    "CGPA calculator": "CGPA 计算器",
    "Use the online calculator to estimate your CGPA.": "使用在线计算器估算你的 CGPA。",
    "Estimate your CGPA": "估算你的 CGPA",
    "To calculate your CGPA, we need to assign each grade a value. We use a 4.0 scale.":
        "计算 CGPA 时，需要先给每个成绩等级赋一个数值。使用的是 4.0 分制。",
    "Grades and their CGPA grade value": "各成绩等级对应的 CGPA 数值",
    "CGPA grade value": "CGPA 数值",
    "Sum the resulting values (weighted CGPA unit score)": "把得到的数值相加（即加权 CGPA 课程分）",
    "Divide the sum of the weighted CGPA unit score by the sum of the unit credit points":
        "用加权 CGPA 课程分之和除以课程学分之和",
    "An example of how a weighted CGPA unit score is calculated for nine units with a "
    "range of grades and credit points.":
        "以九门成绩与学分各不相同的课程为例，说明加权 CGPA 课程分的算法。",
    "Weighted CGPA unit score": "加权 CGPA 课程分",
}


# --- the curated FAQ ------------------------------------------------------
#
# Our own writing, so this is a straight translation with no source to be
# faithful to but ours.

FAQ_ZH: dict[str, tuple[str, str]] = {
    "how-to-apply-special-consideration": (
        "怎么申请特殊考虑（special consideration）？",
        "特殊考虑针对的是你无法控制、且影响了某次考核的短期状况。"
        "申请在学生门户的特殊考虑表单里提交，"
        "通常要在该次考核的截止日期或安排的考试时间之后两个学校工作日内提交，并附上证明材料。"
        "平时作业的短期延期由课程的教学团队另行处理。申请前请先看官方页面，"
        "确认当前的截止时限和所需的具体证明。",
    ),
    "what-documents-for-sc": (
        "申请特殊考虑需要哪些材料？",
        "你需要第三方出具的、覆盖受影响日期的证明——"
        "最常见的是医生证明或 Monash 的 Health Professional Report。"
        "截图、自己写的说明、没有日期的信函通常不被接受。官方页面列明了哪种情形对应哪种材料。",
    ),
    "what-is-wam": (
        "WAM 是什么，怎么算？",
        "WAM 是加权平均分：按每门课的学分加权求出你各门课分数的平均值，"
        "多数课程还会再按课程等级加权。"
        "它用的是分数而不是等级，所以比 GPA 更精确。"
        "Monash 在官方 WAM 页面上公布了确切公式和哪些课程不计入。",
    ),
    "what-is-gpa": (
        "Monash 的 GPA 是什么？",
        "GPA 是 0–4 分制，按成绩等级（而不是具体分数）计算，HD 记 4 分，N 记 0 分。"
        "Monash 有些奖学金和录取决定看 GPA，有些看 WAM，所以申请前要确认对方要的是哪一个。",
    ),
    "census-date-meaning": (
        "census date 是什么，为什么重要？",
        "census date 是你退选一门课而不用付这门课学费、也不留下记录的最后一天。"
        "过了这一天，学费就要照付，退课也会被记录在案。不同教学期的 census date 不一样，"
        "所以要查你那门课的具体日期，不要以为整个学期只有一个日子。",
    ),
    "how-to-withdraw-from-a-unit": (
        "怎么退选一门课？",
        "在选课变更开放期间，通过 WES 退选。census date 之前退，不收费也不留记录；"
        "之后退，学费照付，并且这门课会显示为退课。如果你持学生签证，"
        "课业量降到全日制以下可能影响签证，"
        "先找顾问确认再操作。",
    ),
    "student-visa-work-hours": (
        "持学生签证一周能打工多少小时？",
        "学生签证的工作权限由澳大利亚政府规定，不是 Monash 定的，近几年上限改过好几次。"
        "Monash 的页面会链到内政部（Department of Home Affairs）的现行规定——"
        "在按某个小时数行事之前，"
        "务必到那里确认当前数字。",
    ),
    "when-do-results-come-out": (
        "成绩什么时候出？",
        "成绩按教学期发布，日期见官方成绩日历，出分后可在 WES 查看。"
        "如果有未了结的事项，例如欠费或学术诚信调查，某门课的成绩可能会被暂扣。",
    ),
    "what-is-coe": (
        "CoE 是什么？什么时候需要换新的？",
        "CoE（入学确认书）是签发学生签证所依据的文件。一般来说，只要你的课程、"
        "校区或完成日期发生变化，"
        "就需要一份新的 CoE——包括申请休学或减少课业量的情况。请在现有 CoE 过期之前提出申请。",
    ),
    "apply-for-intermission": (
        "可以休学一个学期吗？",
        "可以，这叫 intermission（休学）。授课型课程的学生通常可以申请到规定的最长期限，"
        "但审批不是自动通过的。"
        "持学生签证的国际学生要在申请前先确认对签证的影响，因为休学会改变你的 CoE。",
    ),
    "exchange-eligibility": (
        "在 Monash 怎么去交换？",
        "交换项目由 Monash Abroad 负责。是否符合条件通常取决于你的 WAM、课程完成的进度，"
        "以及有没有可以转回学分的课程。申请轮次远早于你想出去的那个学期，所以要尽早查申请日期。",
    ),
    "how-to-get-a-transcript": (
        "怎么申请正式成绩单？",
        "通过官方文件服务（official documents）申请学业记录。"
        "在读学生可以在 WES 免费看到非正式的分数单；"
        "带认证的正式成绩单是另外的付费申请，有自己的处理时间。",
    ),
}


# --- results legend -------------------------------------------------------
#
# The codes themselves - P, N, NE, NGO, SFR, WDN - are never translated: they
# are what a student matches against their own transcript, and the engine
# leaves them alone. What is translated is the grade beside each code.
#
# Written in plain Chinese rather than the "Credit（良好）" shape used on the
# GPA page: there the grade name is being discussed in a sentence, here it is
# a cell in a lookup table that already carries the English code in the column
# to its left.

RESULTS_LEGEND: dict[str, str] = {
    "Code": "代码",
    "Grade": "成绩等级",
    "Mark": "分数",

    "High Distinction": "最高优等",
    "Distinction": "优等",
    "Credit": "良好",
    "Pass": "及格",
    "Fail": "不及格",
    "Deferred Assessment": "延期考核",
    "Not Assessed": "未评定",
    "Not Examinable": "不参加考核",
    "Hurdle Fail": "必过项未通过",
    "Supplementary Assessment": "补考",
    "Not Satisfied Requirements": "未满足要求",
    "Satisfied Faculty Requirements": "已满足学院要求",
    "Withdrawn": "退课",
    "Withheld": "成绩暂扣",
    "Withdrawn Incomplete": "退课且未完成",
    "Withdrawn Fail": "退课记为不及格",
    "Exempt": "免修",
    "Faculty Pass": "学院及格",
    "Merit": "优良",
    "Not Applicable": "不适用",
    "Pass Grade Only (no higher grade available)": "仅记及格（该课不设更高等级）",
    "NGO (Fail)": "NGO（不及格）",
    "PGO (Pass)": "PGO（及格）",

    "First Class Honours": "一等荣誉",
    "Second Class Honours Division A": "二等甲级荣誉",
    "Second Class Honours Division B": "二等乙级荣誉",
    "Third Class Honours Applies only to students who started before 2021":
        "三等荣誉　仅适用于 2021 年之前入学的学生",
    "Pass Applies only to students who started on or after 1 January 2021":
        "及格　仅适用于 2021 年 1 月 1 日及之后入学的学生",

    "The Monash grading system": "Monash 的成绩等级制度",
    "Honours course grades": "荣誉学位课程的成绩等级",
    "2020–2021 Temporary grading system in response to COVID-19":
        "2020–2021 年因应 COVID-19 的临时评分制度",
    "Masters awarded with distinction": "硕士优等毕业（awarded with distinction）",
    "Marks from previous years": "往年的成绩等级",
    "Related links": "相关链接",

    "Code, grade and mark range for academic transcript results. Links in this table "
    "open in a lightbox.":
        "成绩单上的代码、成绩等级与分数区间。表中的链接会在弹层中打开。",
    "Code, grade and mark range in academic transcript results for honours degrees and "
    "degrees with honours.":
        "荣誉学位及带荣誉学位的成绩单代码、成绩等级与分数区间。",
}


def all_seeds() -> tuple[TranslationSeed, ...]:
    seeds: list[TranslationSeed] = [
        TranslationSeed(
            ZH, GLOBAL, "handbook", "strings",
            strings=HANDBOOK_BOILERPLATE,
            note="Handbook 模板化段落，逐句人工翻译",
        ),
        TranslationSeed(
            ZH, OFFICIAL_PAGE, "gpa", "body",
            strings=GPA_PAGE,
            note="全文人工翻译，2026-08-23 对照官方页面",
        ),
        TranslationSeed(ZH, OFFICIAL_PAGE, "gpa", "title", text=GUIDE_TITLES["gpa"]),
        TranslationSeed(
            ZH, OFFICIAL_PAGE, "results-legend", "body",
            strings=RESULTS_LEGEND,
            note="成绩等级名称人工翻译，代码保留原文",
        ),
    ]
    seeds += [
        TranslationSeed(ZH, OFFICIAL_PAGE, slug, "title", text=title)
        for slug, title in GUIDE_TITLES.items()
        if slug != "gpa"
    ]
    for slug, (question, answer) in FAQ_ZH.items():
        seeds.append(TranslationSeed(ZH, FAQ_ENTRY, slug, "question", text=question))
        seeds.append(TranslationSeed(ZH, FAQ_ENTRY, slug, "answer", text=answer))
    return tuple(seeds)


TRANSLATION_SEEDS: tuple[TranslationSeed, ...] = all_seeds()
