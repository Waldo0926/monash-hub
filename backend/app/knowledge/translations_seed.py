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

    # On nine units, and the sentence the machine kept leaving in English while
    # translating the two after it. *Hurdle* and *competency-based* are both
    # terms a student's result turns on, so this one is written out rather than
    # retried.
    "Assessments in this unit are competency-based. Competency is assessed "
    "against a criterion-referenced rubric. Failure to pass any hurdle "
    "assessment tasks may result in failure of the unit.":
        "本课程的考核采用能力本位（competency-based）方式，"
        "依据既定评分标准（criterion-referenced rubric）评定是否达到要求。"
        "任何一项及格门槛（hurdle）考核未通过，都可能导致本课程不及格。",
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

    "You’ve been granted a deferred assessment, resulting from your special consideration application.":
        "你的特殊考虑（special consideration）申请获批，因此获得了延期考核。",
}


# --- guide bodies, sentence by sentence ------------------------------------
#
# What the machine would not translate. Every string here was held back by a
# reserved term the model rendered a third way - deferred assessment came back
# as 递延摊款, a loan repayment - so the engine kept the English rather than
# guess at a word a student acts on. These are the pages where guessing is
# worst: census dates, visas, and what happens to a grade when you withdraw.
#
# Keyed on the exact English the crawler extracted. Anything that does not
# match character for character stays in English, which is the safe direction.

GUIDE_BODIES: dict[str, dict[str, str]] = {
    "academic-integrity": {
        "A pop-up blocker will prevent you from accessing the "
        "module.Make sure your browser allows pop-ups in the "
        "Compulsory Unit Portal (CUP).":
            "弹窗拦截会导致模块打不开。请把浏览器设置为允许 Compulsory Units "
            "Portal（CUP，必修模块门户）弹出窗口。",
        "Academic integrity and what plagiarism, collusion and "
        "cheating mean":
            "学术诚信，以及抄袭、合谋作弊和作弊分别指什么",
        "All students and staff can access the Academic Integrity "
        "module in the Compulsory Units Portal (CUP) at any time.":
            "所有学生和教职员工都可以随时在 Compulsory Units Portal（CUP，必修模块门户）中打开学术诚信模块。",
        "As a Monash student, you’ve joined a community that upholds "
        "integrity in all of its academic endeavours, and you’ve made "
        "a personal commitment to studying with academic integrity. "
        "This means that, whenever you work on an assignment or submit "
        "an assessment, you do so honestly, fairly, respectfully and "
        "responsibly.":
            "作为 Monash "
            "的学生，你加入的是一个在所有学术活动中恪守诚信的群体，也就等于亲自作出承诺：以符合学术诚信的方式完成学业。这意味着，你在做作业或提交考核时，都要做到诚实、公平、尊重他人、对自己负责。",
        "Compulsory modules are not graded, so your grade will remain "
        "0% even after completion. But, once you’ve completed the "
        "module, your progress will show as 100% on the CUP dashboard.":
            "必修模块不计分，所以即使你已经完成，成绩仍会显示为 0%——这是正常的。判断是否完成要看 CUP 首页的进度：完成后会显示 "
            "100%。",
        "Find out what a report of academic misconduct means for you, "
        "and what steps you need to take.":
            "了解被举报学术不端对你意味着什么，以及你需要采取哪些步骤。",
        "If the module freezes, and you can't select an option or move "
        "on to the next page, you need to email servicedesk@monash.edu:":
            "如果模块卡住，选不了选项、也翻不到下一页，请发邮件到 servicedesk@monash.edu：",
        "If you don’t complete compulsory modules by the deadline, "
        "you'll lose access to Moodle until the modules are completed. "
        "So make sure you complete them on time.":
            "如果到截止日期还没完成必修模块，你会被停用 Moodle，直到补完为止。请务必按时完成。",
        "If you have trouble accessing the module, see our "
        "troubleshooting section below.":
            "如果打不开模块，请看下面的「问题排查」一节。",
        "If you're having trouble accessing the module:":
            "如果你打不开模块：",
        "If you’re still having trouble accessing or completing the "
        "module, contact Monash Connect. Make sure to give us:":
            "如果仍然打不开或做不完模块，请联系 Monash Connect（学生服务中心）。联系时请提供：",
        "If you’re unsure whether you need to complete the Academic "
        "Integrity module, check in the Web Enrolment System (WES) "
        "under Enrolment/Re-Enrolment. Your compulsory modules will be "
        "listed in the Status column of the Enrolment Summary screen.":
            "如果你不确定自己是否需要完成学术诚信模块，可以到 WES（学生系统）里的 "
            "Enrolment/Re-enrolment（选课注册／重新注册）查看。你的必修模块会列在 Enrolment "
            "Summary（选课注册摘要）页面的 Status（状态）一栏。",
        "Learning how to apply and maintain academic integrity in your "
        "assessments is essential to your success at Monash. Learn HQ "
        "resources will help you with:":
            "学会在考核中践行并保持学术诚信，是你在 Monash 顺利完成学业的关键。Learn HQ（学习支持平台）上的资源可以帮你：",
        "Monash University is strongly committed to honesty and "
        "academic integrity.":
            "Monash 大学高度重视诚实与学术诚信。",
        "Once you've completed the module, the Compulsory Units Portal "
        "(CUP) dashboard should show the unit as 100% complete.If you "
        "signed into CUP with your Monash student account, your "
        "progress will be recorded in the Web Enrolment System (WES) - "
        "it takes about 15 minutes.If you signed into CUP using a "
        "personal email account (or you’re a Monash University "
        "Accommodation student), your student record won’t be "
        "automatically updated. We’ll need to do a data merge so "
        "completion of the module is recorded in WES. Please submit an "
        "email to servicedesk@monash.edu with the subject line, CUP "
        "merge required, and we'll fix this for you.You can check "
        "which email address is linked to your account in CUP under "
        "the profile icon in the top left corner.":
            "完成模块后，Compulsory Units Portal（CUP，必修模块门户）首页应显示该模块 100% "
            "完成。如果你是用 Monash 学生账号登录 CUP 的，进度大约 15 分钟后会记录到 "
            "WES（学生系统）。如果你用的是个人邮箱（或者你是 Monash "
            "学生宿舍的住宿生），学生记录不会自动更新：我们需要做一次数据合并，才能把完成记录写进 WES（学生系统）。请发邮件到 "
            "servicedesk@monash.edu，主题写 CUP merge "
            "required，我们会帮你处理。想确认账号绑定的是哪个邮箱，点开 CUP 左上角的头像图标即可查看。",
        "To help you maintain academic integrity throughout your "
        "studies, we’ve created a short compulsory module. It gives "
        "you a basic understanding of academic integrity and points "
        "you to important resources that build on this. You’ll learn:":
            "为帮助你在整个学习期间守住学术诚信，我们准备了一个简短的必修模块。它会带你建立对学术诚信的基本认识，并指引你找到进一步的重要资源。你将学到：",
        "Understand that plagiarism, collusion and cheating bring "
        "serious consequences. Not only while you’re at Monash, but "
        "well beyond. Such misconduct could harm you personally and "
        "professionally for the rest of your life.":
            "要清楚：抄袭、合谋作弊和作弊都会带来严重后果，而且不止于你在 Monash "
            "的这几年。这类学术不端可能在你此后的人生里，长期影响你的个人声誉与职业发展。",
        "Use this information if you have trouble accessing or "
        "completing a module.":
            "打不开模块、或者做不完时，请参考下面的说明。",
        "Using your personal email account: If you log into CUP with "
        "your personal email account (or a Monash University "
        "Accommodation account), your record of completion won’t "
        "automatically appear in WES. You’ll need to request that we "
        "merge your personal CUP account with your Monash student "
        "account by emailing servicedesk@monash.edu with the subject "
        "line CUP merge required.":
            "用个人邮箱登录：如果你用个人邮箱（或 Monash 学生宿舍账号）登录 CUP，完成记录不会自动同步到 "
            "WES（学生系统）。你需要发邮件到 servicedesk@monash.edu，主题写 CUP merge "
            "required，请我们把你的个人 CUP 账号与 Monash 学生账号合并。",
        "Using your student email account: Best to log into CUP with "
        "your Monash student email account. That way your record of "
        "completion will also appear in WES (after about 15 minutes).":
            "用学生邮箱登录：建议用你的 Monash 学生邮箱登录 CUP。这样你的完成记录大约 15 分钟后也会同步到 "
            "WES（学生系统）。",
        "What happens if I don’t complete the module?":
            "不完成这个模块会怎样？",
        "When do I need to complete this module?":
            "这个模块要在什么时候完成？",
        "You can check which email address is linked to your account "
        "by looking under the profile icon in the top left corner of "
        "CUP.":
            "想确认账号绑定的是哪个邮箱，点开 CUP 左上角的头像图标即可查看。",
        "You should complete the compulsory modules before classes "
        "start, but we’ll send you a reminder (with a deadline) if you "
        "haven’t completed them. If you don’t complete them by the "
        "deadline, you’ll lose access to Moodle until they are "
        "completed.":
            "必修模块应当在开课前完成。如果你还没完成，我们会发提醒给你，并告知截止日期。若到期仍未完成，你会被停用 "
            "Moodle，直到补完为止。",
        "dos and don’ts of academic integrity":
            "弄清学术诚信上哪些能做、哪些不能做",
        "how plagiarism, collusion and cheating differ, and how to "
        "avoid them":
            "抄袭、合谋作弊和作弊有什么区别，以及如何避免",
        "how to deal with common scenarios involving academic integrity":
            "遇到与学术诚信有关的常见情况该怎么处理",
        "maintaining your study and research ethically, with honesty "
        "and integrity.":
            "在学习和研究中恪守伦理规范，做到诚实、正直。",
        "understanding terms that refer to different aspects of "
        "academic integrity":
            "理解学术诚信各个方面所使用的术语",
        "understanding what happens if you breach academic integrity":
            "了解违反学术诚信之后会发生什么",
        "where to find resources to grow your knowledge and skills for "
        "greater academic integrity.":
            "到哪里去找资源，进一步提升自己在学术诚信方面的认识与能力。",
        "why academic integrity is important to you, Monash and the "
        "University community":
            "学术诚信为什么对你、对 Monash、对整个大学群体都重要",
    },
    "academic-transcripts": {
        "If you’re a past student, you can buy digital letters for up to 12 months after you’ve been course completed.":
            "如果你已经毕业，在学位课程完成后的 12 个月内都可以购买电子版证明信。",
        "Your academic record has the following information about you:If a unit is marked as Incomplete on your academic transcript, it simply means the result isn't available yet.Masters awarded with distinctionFrom 6 October 2021, a student graduating with a master’s degree by coursework with a WAM of 80 or above will see ‘awarded with distinction’ on their transcript.Credit points not showing for some unit exemptionsSometimes exempted units listed in your academic record don’t have credit points attached. This is because you’ve been exempted from studying a particular unit (based on prior study), but you’re required to complete another unit in its place.":
            "你的学业记录包含以下关于你的信息：如果成绩单上某门课程标注为 Incomplete（未完成），只是表示成绩尚未公布。硕士优等毕业（awarded with distinction）：自 2021 年 10 月 6 日起，以授课型硕士学位毕业且 WAM（加权平均分）达到 80 分及以上的学生，成绩单上会显示「awarded with distinction」。部分免修课程不显示学分：成绩单上列出的免修课程有时没有对应学分，这是因为你（基于此前的学习）获准免修某门课程，但需要另修一门课程来替代。",
    },
    "add-or-withdraw-units": {
        "ADD UNITS":
            "添加课程",
        "After 11.59pm (Melbourne time) on the census date":
            "在 census date（学籍统计日）当天 23:59（墨尔本时间）之后",
        "Before 11.59pm (Melbourne time) on the census date":
            "在 census date（学籍统计日）当天 23:59（墨尔本时间）之前",
        "Check units you’re currently enrolled in – title and code, campus, faculty, credit points and teaching period of each – with our virtual assistant – it only takes a moment, and you’ll need to log in with your Monash student account.":
            "用我们的虚拟助手查看你当前已选的课程——每门课的名称与代码、校区、学院、学分和开课学期。只需片刻，需要用 Monash 学生账号登录。",
        "Financial penalties apply Academic penalties may apply to some teaching periods The teaching weeks' end date is the last day to withdraw from units":
            "会产生费用方面的处罚；部分开课学期还可能有学业方面的处罚；教学周结束日即为退选课程的最后一天",
        "If you have to withdraw after the census date because of circumstances out of your control, you may be eligible for a WDN grade, a fee reversal, or both.":
            "如果你因无法控制的原因不得不在 census date（学籍统计日）之后退选，你可能符合条件获得 WDN（退课）成绩等级、学费冲销，或两者兼有。",
        "If you’re a full-fee paying student and you withdraw from a unit after the census date, you still need to pay the fees.":
            "如果你是全额自费学生，在 census date（学籍统计日）之后退选课程，仍然需要缴纳该课程的学费。",
        "The following penalties apply to all units withdrawn after 11.59pm (Melbourne time) on the census date for your teaching period":
            "在你所在开课学期的 census date（学籍统计日）当天 23:59（墨尔本时间）之后退选的所有课程，适用下列处罚",
        "The following penalties apply to withdrawn units in most teaching periods after 11.59pm (Melbourne time) on the unit’s census date. To see what applies to your units, check your teaching period's census date.":
            "在课程的 census date（学籍统计日）当天 23:59（墨尔本时间）之后退选的课程，在多数开课学期适用下列处罚。想知道自己的课程适用哪一种，请查看你所在开课学期的 census date（学籍统计日）。",
    },
    "assessment-at-monash": {
        "Assessment is an integral part of your studies. It’s much more than a critical step in passing your units. Completing assessments and receiving feedback allows you to track the progress of your academic performance, and find ways of improving it.":
            "考核是学习中不可分割的一部分，远不只是通过课程的一道关口。完成考核并获得反馈，可以让你了解自己学业表现的变化，并找到改进的方法。",
        "Assessments for learning are designed to help you build and consolidate your knowledge, understanding and skills, and provide you with feedback on your progress. They’re usually set during the teaching weeks, and sometimes contribute to your overall unit results (but not always).":
            "促学型考核的目的，是帮助你建立并巩固知识、理解和技能，并就你的进展给出反馈。这类考核通常安排在教学周内，有时会计入课程的总成绩（但并非总是如此）。",
        "For teaching periods that started on or after 22 July 2024, you’ll receive a 5% penalty on the available marks if you submit your assessment after the due date (unless you have an extension or you’ve been granted special consideration).":
            "对于 2024 年 7 月 22 日及之后开始的开课学期，逾期提交考核会按可得分数扣罚 5%（除非你已获得延期，或获批特殊考虑（special consideration））。",
        "You might be eligible for a generally longer extension through special consideration if you can’t complete an assessment due to exceptional circumstances beyond your control. You can apply for an extension through special consideration for any type of assessment except a scheduled final assessment. Supporting documents are required.":
            "如果你因无法控制的特殊情况而无法完成考核，可能符合条件通过特殊考虑（special consideration）获得通常更长的延期。除原定的期末考核外，任何类型的考核都可以通过特殊考虑申请延期。申请需要提交证明材料。",
    },
    "census-dates": {
        "Check the details at add or withdraw from units.":
            "详情请见「添加或退选课程」页面。",
        "If you withdraw from a unit after a certain date, your academic record may show Withdrawn or Withdrawn Fail. You should understand how census and withdrawal dates can affect your fees and academic record. For more information, see:":
            "在某个日期之后退选课程，你的学业记录上可能会显示 Withdrawn（退课）或 Withdrawn Fail（退课记为不及格）。你应当了解 census date（学籍统计日）和退选日期会如何影响你的学费与学业记录。更多信息请见：",
        "You have until 11.59pm (Melbourne time) on the census date to withdraw from units without financial or academic penalty.":
            "你可以在 census date（学籍统计日）当天 23:59（墨尔本时间）之前退选课程，不会受到费用或学业方面的处罚。",
    },
    "census-dates-explained": {
        "Check the census dates for your units to avoid academic and financial penalties.":
            "查看你所选课程的 census dates（学籍统计日），以免受到学业和费用方面的处罚。",
        "If you discontinue before 11.59pm (Melbourne time) on the census date, you pay fees for the time you were enrolled. See chapters one and three of the Handbook of Doctoral and MPhil Degrees.":
            "如果你在 census date（学籍统计日）当天 23:59（墨尔本时间）之前退课，只需按已注册的时间缴纳相应费用。详见《Handbook of Doctoral and MPhil Degrees》第一章和第三章。",
        "If you withdraw from a unit after 11.59pm (Melbourne time) on the census date, you’ll have to pay for the unit up front, or if you’re a HELP-loan student, the fees will be added to your loan.":
            "如果你在 census date（学籍统计日）当天 23:59（墨尔本时间）之后退选课程，就必须自行缴清该课程的学费；如果你使用 HELP 贷款，这笔费用会计入你的贷款。",
        "If you withdraw from a unit after the census date (but before the Withdrawn Fail date) your record will show the unit result as Withdrawn. If you withdraw after the Withdrawn Fail date, your record will show the unit result as Withdrawn Fail. This will affect your grade point average (GPA).":
            "如果你在 census date（学籍统计日）之后、但在 Withdrawn Fail 日期之前退选课程，记录上这门课程会显示为 Withdrawn（退课）。如果在 Withdrawn Fail 日期之后退选，则会显示为 Withdrawn Fail（退课记为不及格），并会影响你的 GPA（平均绩点）。",
        "The last date to withdraw from a unit may differ if you are studying a unit taught in:":
            "如果你所修课程的授课地点属于以下情况，退选课程的最后日期可能有所不同：",
    },
    "confirmation-of-enrolment": {
        "A CoE is an official form that we provide to international students who need to apply for a student visa. It confirms you’re enrolled in a registered course and you’ve paid your enrolment fees, and displays the registration code and the start and end dates for your course.":
            "CoE（入学确认书）是学校出具给需要申请学生签证的国际学生的正式文件。它确认你已注册在册的学位课程、已缴纳注册费用，并载明课程注册代码以及学位课程的起止日期。",
        "If you can’t complete your course before your visa expires, you’ll need to apply for a new CoE to submit with your student visa application.":
            "如果你无法在签证到期前完成学位课程，需要申请新的 CoE（入学确认书），随学生签证申请一并提交。",
        "If your visa is going to expire before you’ve finished your course, you’ll need to apply for a new CoE.":
            "如果你的签证会在完成学位课程之前到期，你需要申请一份新的 CoE（入学确认书）。",
        "You’ll receive a CoE once you accept your course offer (unless you’re an Australia Awards Scholarship student). This includes if you’re transferring from one Monash course to another.":
            "接受录取通知后，你会收到 CoE（入学确认书）（澳大利亚奖学金 Australia Awards Scholarship 学生除外）。在 Monash 内部转读另一个学位课程时也同样会收到。",
    },
    "course-advice": {
        "If you apply to take a break or discontinue your course, we’ll automatically get in contact with you to discuss your options.":
            "如果你申请休息一段时间或退出学位课程，我们会主动联系你，一起讨论可选的方案。",
    },
    "defer-final-assessment": {
        "If there isn’t another suitable session on the same day, you’ll have to sit your deferred assessment at the time it is scheduled.":
            "如果当天没有其他合适的场次，你就必须按原定时间参加延期考核。",
        "If there isn’t another suitable session on the same day, you’ll have to sit your rescheduled deferred assessment at the time it is scheduled.":
            "如果当天没有其他合适的场次，你就必须按原定时间参加改期的延期考核。",
        "If we approve your application to reschedule your deferred assessment, your assessment will be held during the rescheduled deferred assessment period unless your faculty decides to offer you an alternative assessment – in that case it’ll be due at an alternative time. You’ll get an email with this information once it’s available.":
            "如果改期申请获批，考核将安排在改期延期考核期内进行，除非学院决定给你另一种考核形式——那样的话截止时间会另行安排。相关信息确定后，你会收到邮件通知。",
        "If we don’t approve your application and/or you didn’t sit your scheduled final assessment on the original date, your final grade will be based on your marks for other assessments you’ve completed for that unit.":
            "如果申请未获批准、和/或你没有在原定日期参加期末考核，你的最终成绩等级将依据你在这门课程已完成的其他考核的分数来评定。",
        "If you can’t complete your rescheduled deferred assessment on the rescheduled date, you won’t be able to reschedule it again. However, if you let us know ahead of time that you’re not able to complete your rescheduled deferred assessment, we’ll consider you for a WDN grade (provided you’re eligible). Otherwise we’ll finalise your grade by converting your interim DEF result to a final grade based on your marks for other assessments you’ve completed for that unit.":
            "如果你无法在改期后的日期完成延期考核，就不能再次改期。不过，若你提前告知我们无法完成这次改期考核，我们会考虑给你 WDN 成绩等级（前提是你符合条件）。否则，我们会依据你在这门课程已完成的其他考核的分数，把临时的 DEF 成绩转为最终成绩等级，以此定出最终成绩。",
        "If you’re eligible for a rescheduled deferred assessment, but can’t pass your unit even if you successfully complete your assessment, we recommend that you instead apply for a Withdrawn (WDN) grade if you meet the criteria.":
            "如果你符合改期延期考核的资格，但即使顺利完成考核也无法通过这门课程，我们建议你改为申请 Withdrawn（WDN，退课）成绩等级——前提是你满足相应条件。",
        "If you’re sitting a deferred assessment for a unit that is a prerequisite for another unit you’re enrolled in, you’ll need to pass your deferred assessment to stay enrolled in that unit. If you fail the unit, your enrolment in the subsequent unit will be invalid and cancelled by the faculty (this is because you won’t have met the academic requirements to remain enrolled).":
            "如果你参加延期考核的这门课程，是你已选的另一门课程的先修课程，那么你必须通过这次延期考核才能保留后一门课程的选课。如果这门课程不及格，你在后续课程的选课将失效并被学院取消（因为你没有满足继续选课所需的学术要求）。",
        "If you’re sitting a rescheduled deferred assessment for a unit that is a prerequisite for another unit you’re enrolled in, you’ll need to pass your rescheduled assessment to stay enrolled in that unit. If you fail the unit, your enrolment in the subsequent unit will be invalid and cancelled by the faculty (this is because you won’t have met the academic requirements to remain enrolled).":
            "如果你参加改期延期考核的这门课程，是你已选的另一门课程的先修课程，那么你必须通过这次改期考核才能保留后一门课程的选课。如果这门课程不及格，你在后续课程的选课将失效并被学院取消（因为你没有满足继续选课所需的学术要求）。",
        "If you’ve already deferred your assessment (exam) but still need more time due to unresolved circumstances or new extreme circumstances, you can apply for a rescheduled deferred assessment if you meet the stricter eligibility requirements.":
            "如果你已经获批延期考核（考试），但因情况仍未解决、或出现新的极端情况而需要更多时间，在满足更严格的资格要求的前提下，可以申请改期的延期考核。",
        "Keep in mind, you can’t take a supplementary assessment if you complete a deferred or rescheduled assessment.":
            "请注意：如果你完成了延期考核或改期考核，就不能再参加补考。",
        "Once you’ve notified exam support, a Monash medical support person will discuss your situation over the phone. If you’re unable to continue with your assessment, they will advise you on what you need to do if you intend to apply for special consideration.":
            "在你通知考试支持团队后，Monash 的医疗支持人员会通过电话了解你的情况。如果你无法继续参加考核，他们会告诉你：若打算申请特殊考虑（special consideration），接下来需要做什么。",
        "Some faculties won’t allow you to enrol in a unit if you have a deferred (DEF) grade for a prerequisite, so having an interim result (DEF grade) while you wait to see if you passed might affect your enrolment. This won’t be a problem if your deferred assessment results are released before re-enrolment closes (and you passed), but for some teaching periods, you may receive your final grade after the cut-off for enrolment.":
            "如果先修课程的成绩等级是 DEF（延期考核），部分学院不允许你选修相应课程。因此在等待结果期间持有临时成绩（DEF）可能影响你的选课。如果延期考核成绩在重新注册截止前公布（且你通过了），就不成问题；但在某些开课学期，你可能要到选课截止之后才拿到最终成绩等级。",
        "Some faculties won’t allow you to enrol in a unit if you have a deferred (DEF) or Withheld (WH) grade for a prerequisite, so having an interim result while you wait to see if you passed might affect your enrolment. This won’t be a problem if your rescheduled deferred assessment results are released before re-enrolment closes (and you passed), but for some teaching periods, you may receive your final grade after the cut-off for enrolment.":
            "如果先修课程的成绩等级是 DEF（延期考核）或 WH（成绩暂扣），部分学院不允许你选修相应课程。因此在等待结果期间持有临时成绩可能影响你的选课。如果改期延期考核的成绩在重新注册截止前公布（且你通过了），就不成问题；但在某些开课学期，你可能要到选课截止之后才拿到最终成绩等级。",
        "You can apply to reschedule your deferred assessment no later than 11.55pm on its set date.":
            "申请延期考核改期，最迟不得晚于原定考核日当天 23:55。",
        "You generally won’t be eligible to defer your assessment if you’ve seen and/or attempted to answer questions on your scheduled final assessment (exam).":
            "如果你已经看过、或尝试作答原定期末考核（考试）的题目，通常就不再符合申请延期考核的资格。",
        "You generally won’t be eligible to reschedule your deferred assessment if you’ve seen and/or attempted to answer questions on your scheduled final assessment (exam).":
            "如果你已经看过、或尝试作答原定期末考核（考试）的题目，通常就不再符合改期延期考核的资格。",
        "You should apply as soon as you’re aware that you can’t sit your scheduled final assessment (after timetable release) but no later than 11.55pm on the set date for your assessment. Make sure you attach all required supporting documents as evidence of your exceptional circumstances.":
            "一旦（在考试时间表公布后）确认自己无法参加原定的期末考核，就应尽快申请，最迟不得晚于考核当天 23:55。申请时务必附上全部所需的证明材料，作为你处于特殊情况的证据。",
        "You’ll need to make sure you’re available to sit your assessment. Your assessment will be held during the deferred assessment period unless your faculty decides to offer you an alternative assessment – in that case it’ll be due at an alternative time. You’ll get an email with information about your assessment date, time and location once it’s available.":
            "你需要确保自己能够参加考核。考核将安排在延期考核期内进行，除非学院决定给你另一种考核形式——那样的话截止时间会另行安排。考核的日期、时间和地点确定后，你会收到邮件通知。",
        "convert your interim DEF result to a final grade based on your marks for other assessments you’ve completed for that unit, if you’re not eligible for a WDN grade.":
            "如果你不符合 WDN 成绩等级的条件，则依据你在这门课程已完成的其他考核的分数，把临时的 DEF 成绩转为最终成绩等级。",
    },
    "discontinue-course": {
        "It’s okay to be unsure about continuing your course – we’re here to help you make the decision that’s right for you. This page will help you understand your options, what discontinuation actually means, and how to take the next step, whatever that ends up being.":
            "对是否继续读下去感到犹豫是很正常的——我们会帮你做出适合自己的决定。本页会说明你有哪些选择、退出学位课程究竟意味着什么，以及无论你最终怎么决定，下一步该怎么走。",
        "You should submit the Course Discontinuation request form before 11.59pm on the census date. If you submit it later, you'll be charged for the units you're enrolled in, and you may receive a fail grade after a certain date.":
            "你应在 census date（学籍统计日）当天 23:59 之前提交退出学位课程申请表。逾期提交的话，已选课程会照常收费；超过某个日期之后，还可能被记为不及格成绩等级。",
    },
    "enrolments": {
        "Continuing students must re-enrol for the entire following year – or apply for intermission – during the specified re-enrolment period.":
            "在读学生必须在规定的重新注册期内，完成次年整年的重新注册，或者申请休学（intermission）。",
    },
    "final-assessment-dates": {
        "For all other teaching periods, you’ll be given notice of at least five University working-days of the date of your deferred or supplementary assessment.":
            "在其他所有开课学期，学校会在你的延期考核或补考日期之前，至少提前 5 个大学工作日通知你。",
        "Not every teaching period has a defined set of dates to run deferred and supplementary assessments and the dates may vary from unit to unit. Check with your faculty if you’re unsure when to sit your deferred or supplementary assessment.":
            "并非每个开课学期都有固定的延期考核和补考日期，具体日期也可能因课程而异。如果不确定自己的延期考核或补考在什么时候，请向所在学院确认。",
    },
    "intermission": {
        "Here's what you need to know while you’re on intermission, and what to do before you return.":
            "以下是休学（intermission）期间你需要了解的事项，以及复学前需要办理的手续。",
        "If you apply for study leave after the census date, you’ll be charged for all enrolled units and receive a Withdrawn or Withdrawn Fail grade. For penalty dates, see census dates and teaching periods.":
            "如果你在 census date（学籍统计日）之后申请 study leave，所有已选课程都会照常收费，并会得到 Withdrawn（退课）或 Withdrawn Fail（退课记为不及格）成绩等级。各项处罚的日期见 census date（学籍统计日）与开课学期页面。",
        "If you've paid your fees up front and apply for study leave before 11.59pm (Melbourne time) on the census date, you can apply for a refund. Fees will not be refunded if you apply for study leave after the census date. If you fail to re-enrol for the following year on time, and then apply for study leave, you'll be charged a late enrolment fee.":
            "如果你已经预先缴清学费，并在 census date（学籍统计日）当天 23:59（墨尔本时间）之前申请 study leave，可以申请退费。在 census date 之后申请则不予退费。如果你没有按时完成次年的重新注册，之后才申请 study leave，将被收取逾期注册费。",
        "If you’re not sure whether to take a break, you should re-enrol in your units for now. This keeps your place in the course active while you consider your options. You have until the census date of the teaching period to apply for intermission without any financial or academic penalties.":
            "如果还没想好要不要休息一段时间，建议你先照常重新注册课程，这样在你考虑期间学位课程的学籍会保持有效。你可以在所在开课学期的 census date（学籍统计日）之前申请休学（intermission），不会产生任何费用或学业方面的处罚。",
        "Once you've started your course and your first census date has passed, you may be able to apply for intermission (study leave). If you haven’t started your course yet (or you’ve enrolled but the first census date hasn’t passed), you’ll need to defer your offer instead – see the deferral page for details.":
            "在你的学位课程已经开始、并且第一个 census date（学籍统计日）已过之后，你才可能申请休学（intermission，即 study leave）。如果学位课程尚未开始（或者已经注册但第一个 census date 还没到），你需要办理的是推迟入学，详见推迟入学页面。",
        "We’ll notify the Department of Home Affairs that you’re on study leave. You’re still considered a current student when you’re on study leave (intermission), with access to University support services and academic services, including the library, WES, Student Portal and the Monash intranets.":
            "我们会将你处于 study leave 的情况通知澳大利亚内政部（Department of Home Affairs）。在 study leave（休学，intermission）期间你仍被视为在读学生，可以继续使用学校的支持服务和学术服务，包括图书馆、WES（学生系统）、学生门户以及 Monash 内网。",
        "Your student visa and CoE":
            "你的学生签证与 CoE（入学确认书）",
        "if you decide to take a break after you’ve enrolled and the semester has started – apply before 11.59pm (Melbourne time) on the census date.":
            "如果你在注册且学期已经开始之后决定休息一段时间——请在 census date（学籍统计日）当天 23:59（墨尔本时间）之前提出申请。",
    },
    "oshc": {
        # *Quote* is 报价 here and 引用 on the academic integrity page, so it
        # cannot go in the glossary - this sentence is written out instead.
        "Get an online quote with Allianz Care Australia OSHC (by purchasing OSHC with Allianz Care through this link, Allianz Care will provide Monash with your policy information for administrative and billing purposes). Or speak to an OSHC representative. If you're with another provider, please contact them directly to do this.":
            "在线获取 Allianz Care Australia 的 OSHC（留学生医疗保险）报价（通过此链接向 Allianz Care "
            "投保 OSHC，Allianz Care 会将你的保单信息提供给 Monash，用于行政管理与账单处理）。"
            "你也可以直接联系 OSHC 客服代表。如果你投保的是其他保险公司，请直接联系该公司办理。",
        "These three exceptions apply as long as you’re not a Study Abroad student with OSHC included in your package.":
            "这三项例外适用于所有人，但套餐中已包含 OSHC（海外学生医疗保险）的 Study Abroad 交流学生除外。",
    },
    "principal-dates": {
        "Census date: Full-year (FY-01). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：全学年（FY-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Monash Online 1 (MO-TP1-01). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：Monash Online 1（MO-TP1-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Monash Online 2 (MO-TP2-01). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：Monash Online 2（MO-TP2-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Monash Online 3 (MO-TP3-01). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：Monash Online 3（MO-TP3-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Monash Online 4 (MO-TP4-01). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：Monash Online 4（MO-TP4-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Monash Online 5 (MO-TP5-01). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：Monash Online 5（MO-TP5-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Monash Online 6 (MO-TP6-01). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：Monash Online 6（MO-TP6-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Semester 1 (extended) (S1-32). Last day to withdraw from units in this teaching period without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：第一学期（延长）（S1-32）。退选本开课学期课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Semester one (S1-01). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：第一学期（S1-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Semester two (S2-01). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：第二学期（S2-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Term 1 (T1-57). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：第 1 学季（T1-57）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Term 2 (T2-57). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：第 2 学季（T2-57）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Term 3 (T3-57). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record.":
            "census date（学籍统计日）：第 3 学季（T3-57）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）。",
        "Census date: Trimester 1 (T1-58). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：第 1 学段（T1-58）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Trimester 2 (T2-58). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：第 2 学段（T2-58）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Winter semester (WS-01). Last day to withdraw from units without incurring fees. Units withdrawn after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：冬季学期（WS-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census dates – unit withdrawal dates for all teaching periods":
            "census date（学籍统计日）——各开课学期的课程退选日期",
        "Last day to withdraw from Monash Online 1 (MO-TP1-01) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 Monash Online 1（MO-TP1-01） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from Monash Online 2 (MO-TP2-01) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 Monash Online 2（MO-TP2-01） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from Monash Online 3 (MO-TP3-01) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 Monash Online 3（MO-TP3-01） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from Monash Online 4 (MO-TP4-01) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 Monash Online 4（MO-TP4-01） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from Monash Online 5 (MO-TP5-01) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 Monash Online 5（MO-TP5-01） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from Monash Online 6 (MO-TP6-01) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 Monash Online 6（MO-TP6-01） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from Summer A - semester 1 (SS-S1-01) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 夏季学期 A—第一学期（SS-S1-01） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from Term 4 (T4-57) and semester 2 - summer A (S2-SS-02) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 第 4 学季（T4-57）和第二学期—夏季学期 A（S2-SS-02） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from full-year (FY-01) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 全学年（FY-01） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from full-year (extended) (FY-32) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 全学年（延长）（FY-32） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from semester 1 (northern) (S1-60) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 第一学期（北半球）（S1-60） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from semester one (S1-01) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 第一学期（S1-01） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from summer semester B (SSB-01) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 夏季学期 B（SSB-01） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from trimester 1 (T1-58) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 第 1 学段（T1-58） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from trimester 3 (T3-58) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 第 3 学段（T3-58） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
        "Last day to withdraw from winter semester (WS-01) and trimester 2 (T2-58) units with Withdrawn showing on your academic record. Units withdrawn after this date will show as Withdrawn Fail":
            "退选 冬季学期（WS-01）和第 2 学段（T2-58） 课程、并在成绩单上记为 Withdrawn（退课）的最后一天。此日期之后退选的课程会记为 Withdrawn Fail（退课记为不及格）",
    },
    "special-consideration": {
        "If we approve your application, you’ll get an extension of two calendar days from the original due date of the assessment task.":
            "如果申请获批，你将从考核任务的原定截止日起获得 2 个日历日的延期。",
        "If you’ve already been given a short extension for an assessment but you need more time, you’ll need to then apply for an extension through special consideration with supporting documents.":
            "如果你已经为某项考核拿到短期延期但仍需更多时间，接下来需要通过特殊考虑（special consideration）申请延期，并提交证明材料。",
        "When you apply for an extension through special consideration, you need to provide supporting documents to show why you can’t complete your assessment as scheduled due to immediate and exceptional circumstances beyond your control. Make sure to apply as soon as possible, but no later than 11.55pm on the day your assessment is due.":
            "通过特殊考虑（special consideration）申请延期时，你需要提交证明材料，说明自己为何因突发且无法控制的特殊情况而不能按时完成考核。请尽快提出申请，最迟不得晚于考核截止当天 23:55。",
    },
    "student-visa": {
        "Check visa processing times (Department of Home Affairs). If you’re outside Australia, you’ll need enough time to get your visa before your course starts. If you’re already in Australia, make sure you apply in time before your current visa expires.":
            "查看签证审理时长（澳大利亚内政部 Department of Home Affairs）。如果你人在澳大利亚境外，需要留出足够时间在学位课程开始前拿到签证；如果你已在澳大利亚境内，请务必在现有签证到期前及时提交申请。",
        "If you’re starting your studies with us, you’ll need to apply for a student visa once you’ve accepted your offer and received your Confirmation of Enrolment (CoE).":
            "如果你即将来 Monash 开始学习，在接受录取并收到入学确认书（CoE）之后，需要申请学生签证。",
        "completing your course within the time frame on your CoE":
            "在 CoE（入学确认书）载明的期限内完成学位课程",
    },
    "study-at-another-institution": {
        "Your result will appear on your academic record (transcript) as either SFR (satisfied faculty requirements) or Fail. If you don't provide a record from the host institution you will have a Fail recorded against the units on your Monash academic record.":
            "你的成绩会以 SFR（已满足学院要求）或 Fail（不及格）的形式出现在成绩单上。如果你不提交接收院校出具的成绩记录，这些课程在 Monash 成绩单上会被记为 Fail（不及格）。",
    },
    "supporting-documents": {
        "If you’re registered with Disability Support Services (DSS) and couldn’t sit your deferred assessment due to circumstances not directly related to your DSS condition, you'll still need to provide the supporting documentation noted above.":
            "如果你已在无障碍支持服务（Disability Support Services，DSS）登记，但未能参加延期考核的原因与你在 DSS 登记的状况没有直接关系，你仍然需要提交上述证明材料。",
        "If you’re registered with Disability Support Services (DSS) and couldn’t sit your deferred assessment, you’ll need to provide supporting documents to prove that:":
            "如果你已在无障碍支持服务（Disability Support Services，DSS）登记且未能参加延期考核，你需要提交证明材料来说明：",
        "If you’re registered with Disability Support Services (DSS), and couldn’t sit your deferred assessment due to circumstances not directly related to your DSS condition, you’ll still need to provide the supporting documents noted above.":
            "如果你已在无障碍支持服务（Disability Support Services，DSS）登记，但未能参加延期考核的原因与你在 DSS 登记的状况没有直接关系，你仍然需要提交上述证明材料。",
        "an extension of more than 10 calendar days from the original due date of the assessment":
            "自考核原定截止日起、超过 10 个日历日的延期",
        "you'll be well enough to take the rescheduled deferred assessment within 90 days of the result release date of the teaching period in which the original assessment was scheduled, if your application is approved.":
            "如果申请获批，你的身体状况能够在原定考核所属开课学期成绩公布日起 90 天内参加改期后的延期考核。",
    },
    "visa-changes": {
        "Keep in mind that Monash is required to inform the Department of Home Affairs when you make changes to your enrolment. This includes taking intermission (study leave), changing course, extending the duration of your studies or having your enrolment terminated or suspended.":
            "请注意：当你的选课注册发生变动时，Monash 必须通知澳大利亚内政部（Department of Home Affairs）。这包括申请休学（intermission，即 study leave）、更换学位课程、延长学习年限，以及学籍被终止或暂停。",
    },
    "wam": {
        "DEF (deferred assessment)":
            "DEF（延期考核）",
        "NS (supplementary assessment)":
            "NS（补考）",
        "Weighted credit points":
            "加权学分",
    },
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
    seeds += [
        TranslationSeed(
            ZH, OFFICIAL_PAGE, slug, "body",
            strings=strings,
            note="人工翻译：机器因保留术语无法处理的句子",
        )
        for slug, strings in GUIDE_BODIES.items()
    ]
    for slug, (question, answer) in FAQ_ZH.items():
        seeds.append(TranslationSeed(ZH, FAQ_ENTRY, slug, "question", text=question))
        seeds.append(TranslationSeed(ZH, FAQ_ENTRY, slug, "answer", text=answer))
    return tuple(seeds)


TRANSLATION_SEEDS: tuple[TranslationSeed, ...] = all_seeds()
