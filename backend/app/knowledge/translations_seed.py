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
    "about-academic-progress": {
        "All communications will be sent to your Monash email address, "
        "so if you don’t have access to your Monash account, you need "
        "to let your managing faculty know.":
            "所有通知都会发到你的 Monash 邮箱。如果你无法登录 Monash 账号，需要告知负责你的学院。",
        "At each risk level, we’ll provide you with a different level "
        "of support to help you improve your academic performance.":
            "不同的风险等级，我们提供的支持力度也不同，以帮助你改善学业表现。",
        "At least half of the total number required for the course":
            "至少达到该学位课程所需总量的一半",
        "At least three-quarters of the total number of required the "
        "course":
            "至少达到该学位课程所需总量的四分之三",
        "At least two-thirds of the total number required for the "
        "course":
            "至少达到该学位课程所需总量的三分之二",
        "For this reason, we check in twice a year to make sure you’re "
        "on track to complete your course in the required time. If we "
        "have concerns about your progress, we’ll let you know what "
        "support is available and, if needed, meet with you to discuss "
        "your progress and options.":
            "正因如此，我们每年检查两次，确认你能在规定年限内完成学位课程。如果我们对你的进度有担心，会告诉你可以获得哪些支持；必要时还会约你面谈，一起讨论你的进度和可选的路径。",
        "If any of the following circumstances apply, your progress "
        "will be assessed as unsatisfactory:":
            "出现下列任一情形，你的学业进度会被判定为不达标：",
        "If you meet one of the criteria above, or your progress is at "
        "risk of being unsatisfactory, you’ll be assigned one of three "
        "academic progress risk levels:":
            "如果你符合上述任一标准，或你的学业进度有不达标的风险，你会被划入三个学业进度风险等级中的一个：",
        "If your academic progress is satisfactory, you won’t have an "
        "academic progress risk level.":
            "如果你的学业进度达标，就不会被划入任何学业进度风险等级。",
        "If you’re enrolled in a coursework award course at any "
        "location, your progress will be reviewed twice a year.":
            "只要你注册在册于任一地点的授课型学位课程，你的学业进度每年都会被审查两次。",
        "If you’re on intermission, or aren’t currently enrolled, your "
        "academic progress risk level won’t change until the next "
        "academic progress period you’re enrolled in.":
            "如果你正在休学（intermission）、或当前没有注册在册，你的学业进度风险等级会维持不变，直到下一个你有注册的学业进度审查期为止。",
        "If you’ve been assigned an academic progress risk level, "
        "you’ll be notified by email at your Monash account.":
            "如果你被划入了某个学业进度风险等级，我们会发邮件到你的 Monash 账号通知你。",
        "If you’ve previously been assigned an academic progress risk "
        "level, but achieve satisfactory progress in your next "
        "reviewed academic progress period, the academic progress risk "
        "level will be removed.":
            "如果你此前曾被划入某个学业进度风险等级，但在下一个受审查的学业进度审查期内进度达标，该风险等级就会被撤销。",
        "The dean may also review your academic progress at any time.":
            "院长也可以在任何时候审查你的学业进度。",
        "Time by which they must be successfully completed":
            "必须在此时间点之前修完",
        "To view the results release dates, see semester summary dates.":
            "成绩公布日期请查看「学期重要日期一览」。",
        "We review your progress and unit results released within the "
        "academic progress periods, excluding pathway diplomas and "
        "Withdrawn (WDN and WI) and interim (DEF, NS and WH) grades. "
        "However, your faculty may reassess your academic progress "
        "when your interim results are finalised.":
            "我们审查的是各学业进度审查期内你的进度和已公布的课程成绩，其中不含预科文凭课程，也不含 Withdrawn（WDN 和 "
            "WI，退课）以及临时性成绩（DEF、NS、WH）。不过，等你的临时成绩最终确定后，学院可能会重新评估你的学业进度。",
        "We want to make sure you succeed in your studies at Monash "
        "and fulfil all your academic requirements. However, we know "
        "that from time to time things come up that can affect your "
        "academic progress.":
            "我们希望你在 Monash 学有所成、满足所有学业要求。但我们也知道，生活中总会遇到一些事，影响到学业进度。",
        "When you’re halfway through the maximum course duration":
            "当你读到最长修业年限的一半时",
        "When you’re three-quarters of the way through the maximum "
        "course duration":
            "当你读到最长修业年限的四分之三时",
        "When you’re two-thirds of the way through the maximum course "
        "duration":
            "当你读到最长修业年限的三分之二时",
        "You fail the same unit two times or more.":
            "同一门课程不及格两次或更多次。",
        "You fail to successfully complete the required number of "
        "credit points within the required time (see table below). "
        "This means you can't complete your course within the maximum "
        "course duration.":
            "你未能在规定时间内修满所需的学分（见下表）。这意味着你无法在最长修业年限内完成学位课程。",
        "You have a fail grade for 50 per cent or more of the "
        "completed credit points (except if you fail only a single 6-, "
        "12- or 18-credit point unit in your first review period at "
        "Monash).":
            "你已修学分中有 50% 或以上为不及格（例外情况：在 Monash 的首个审查期内，只有一门 6 学分、12 学分或 18 "
            "学分的课程不及格）。",
        "You're at risk of unsatisfactory academic progress if, within "
        "the academic progress period:":
            "在一个学业进度审查期内出现下列情况，你就存在学业进度不达标的风险：",
        "Your academic progress is satisfactory if, within the "
        "academic progress period:":
            "在一个学业进度审查期内满足下列条件，你的学业进度即为达标：",
        "Your maximum course duration is recorded in the Handbook for "
        "the year you began your course.":
            "你的最长修业年限，记载在你入学那一年的 Handbook 里。",
        "You’ve exceeded the maximum course duration without "
        "completing your course.":
            "已超过最长修业年限，仍未完成学位课程。",
        "academic progress risk level one: advice":
            "学业进度风险一级：指导建议",
        "academic progress risk level three: intervention.":
            "学业进度风险三级：干预。",
        "academic progress risk level two: monitoring":
            "学业进度风险二级：监控",
        "none of the unsatisfactory academic progress criteria apply "
        "to your performance.":
            "你的表现不符合任何一条学业进度不达标的判定标准。",
        "period 1: from the day after semester two results are "
        "released until the end of the day on which semester one "
        "results are released":
            "审查期 1：自第二学期成绩公布次日起，至第一学期成绩公布当日结束为止",
        "period 2: from the day after semester one results are "
        "released until the end of the day on which semester two "
        "results are released.":
            "审查期 2：自第一学期成绩公布次日起，至第二学期成绩公布当日结束为止。",
        "you didn’t meet any of the unsatisfactory academic progress "
        "criteria.":
            "你没有触及任何一条学业进度不达标的判定标准。",
        "you failed one or more units, but":
            "你有一门或多门课程不及格，但",
        "you pass all your units, and":
            "你所有课程均及格；并且",
        "About academic progress":
            "关于学业进度审查",
        "Academic progress risk levels":
            "学业进度风险等级",
        "At risk of unsatisfactory progress":
            "存在学业进度不达标的风险",
        "Satisfactory academic progress":
            "学业进度达标",
        "The two review periods are:":
            "两个审查期分别是：",
        "Unsatisfactory academic progress criteria":
            "学业进度不达标的判定标准",
        "What is academic progress?":
            "什么是学业进度审查？",
        "Whose progress is reviewed":
            "哪些人的学业进度会被审查",
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
        "Find the teaching period for a unit":
            "查一门课属于哪个开课学期",
        "For units you’re already enrolled in, log into the Web "
        "Enrolment System and go to the Unit enrolment section. In the "
        "table displaying your units, check the Semester column.":
            "已经选上的课程：登录 WES（学生系统），进入 Unit enrolment（课程注册）一节，在列出你所选课程的表格里看 "
            "Semester（学期）那一列。",
        "If you haven’t completed your enrolment, once you select "
        "units, they will display the same as described above before "
        "submitting or confirming your enrolment.":
            "还没完成选课注册的：选定课程之后，在提交或确认注册之前，界面上显示的内容与上述相同。",
        "If you're a domestic student with government support, the "
        "census date is also:":
            "如果你是有政府资助的本地学生，census date（学籍统计日）同时还是：",
        "Some units have a different deadline for withdrawing – this "
        "is called Withdrawn Early – which acts the same as a census "
        "date (e.g. summer units). Check the main census dates page "
        "for where to find non-standard unit dates.":
            "有些课程的退选截止日不同，叫作 Withdrawn Early（提前退选），作用与 census "
            "date（学籍统计日）相同，暑期课程就是一例。非标准开课日期在哪里查，请看 census dates（学籍统计日）主页面。",
        "The census date is when the University finalises your "
        "enrolment. Once the census date has passed, you’re liable for "
        "fees and incur academic penalties.":
            "census date（学籍统计日）是学校确认你选课注册的时点。过了这一天，你就要承担学费，并且会有学业上的处罚。",
        "The census date is your last opportunity to withdraw from a "
        "unit without the unit appearing on your academic record "
        "(transcript).":
            "census date（学籍统计日）是你退选一门课而不留下记录的最后机会——过了这天再退，这门课就会出现在你的成绩单上。",
        "To check which teaching period a unit falls in, search for "
        "the unit in the Handbook and check the Offerings section.":
            "想知道一门课属于哪个开课学期，可在 Handbook 里搜索该课程，查看 Offerings（开课信息）一节。",
        "block mode – your faculty will advise the dates for each "
        "block mode unit.":
            "block mode（集中授课）——每门集中授课课程的日期由你所在学院另行通知。",
        "summer semester – see your faculty's summer unit dates":
            "夏季学期——请查看你所在学院公布的暑期课程日期",
        "when you become liable for HECS-HELP and FEE-HELP debts.":
            "你开始承担 HECS-HELP 贷款和 FEE-HELP 贷款债务的时点。",
        "your last opportunity to apply for HECS-HELP or FEE-HELP loans":
            "申请 HECS-HELP 贷款或 FEE-HELP 贷款的最后机会",
        "your last opportunity to make up-front fee payments":
            "选择先行付清学费的最后机会",
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
        "Any units already completed at Monash will remain on your "
        "academic record, but you'll need to reapply if you want to "
        "return to study.":
            "你在 Monash 已修完的课程会保留在成绩单上；但若日后想回来读书，需要重新申请。",
        "Discontinuing means you’ll lose your place in your course, so "
        "it’s a good idea to assess your options before making a "
        "decision.":
            "退课意味着你会失去这个学位课程的学籍，所以在做决定之前，先把各种选择都考虑清楚为好。",
        "Firstly, what kind of student are you?":
            "首先，你属于哪一类学生？",
        "If discontinuing your course is the right decision for you, "
        "the steps below will guide you through the process.":
            "如果退课确实是适合你的决定，按下面的步骤办理即可。",
        "If you're a coursework student at Monash University, "
        "Australia, you can submit the form below:":
            "如果你是 Monash 大学（澳大利亚）的授课型学生，可以提交下面的表格：",
        "If you're a domestic or international coursework student "
        "studying at Monash University, you're in the right place. If "
        "that's not you, you'll find the information you need below:":
            "如果你是在 Monash 大学就读的本地或国际授课型学生，这个页面就是给你看的。如果不是，请看下面对应的入口：",
        "If you're considering leaving your course, it's worth taking "
        "a moment to explore your options first.":
            "如果你正在考虑离开这个学位课程，不妨先花点时间，把别的可能性了解一遍。",
        "In the form, you’ll be asked to explain why you’re requesting "
        "a discontinuation. Understanding what has influenced your "
        "decision helps us identify support services for you, and "
        "improve our experience for all Monash students. You can also "
        "elect to be contacted by Monash Connect about our services "
        "and next steps.":
            "表格里会请你说明申请退课的原因。了解是什么影响了你的决定，有助于我们为你找到合适的支持服务，也有助于改善所有 Monash "
            "学生的就读体验。你也可以选择让 Monash Connect（学生服务中心）就相关服务和后续步骤与你联系。",
        "Monash College students\n \nCourse discontinuation steps and "
        "deadlines":
            "Monash College 学生\n \n退课步骤与截止日期",
        "Monash Online students\n \nApply in the Student Hub":
            "Monash Online 学生\n \n在 Student Hub 提交申请",
        "Monash University, Indonesia\n \nmi-admin@monash.edu":
            "Monash 大学印度尼西亚校区\n \nmi-admin@monash.edu",
        "Monash University, Malaysia\n \nCourse withdrawal process and "
        "requirements":
            "Monash 大学马来西亚校区\n \n退课流程与要求",
        "Once you’ve submitted the form, we’ll review your request and "
        "contact you within two University working days. You'll "
        "receive confirmation of your course discontinuation by email "
        "once it's been processed.":
            "提交表格后，我们会审核你的申请，并在两个学校工作日内与你联系。办理完成后，你会收到退课确认邮件。",
        "Students consider leaving their course for many different and "
        "valid reasons, but you may not need to discontinue your "
        "studies to find a solution that works for you. Many students "
        "find that the right support, a short-term adjustment or a "
        "study break is all they need to get them back on track.":
            "学生考虑离开学位课程的理由各不相同，也都有其道理；但要解决问题，未必非得退学。很多学生发现，只要找对支持、做一点短期调整，或者休学一段时间，就足以回到正轨。",
        "This could affect you if you decide to return to study later "
        "on, so make sure you check the penalties for withdrawing from "
        "units.":
            "如果你日后打算回来继续读书，这一点可能会影响到你，所以务必先了解退选课程的处罚规定。",
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
        "After you submit your form":
            "提交表格之后",
        "All documents need to:":
            "所有材料都必须：",
        "Census dates and teaching periods":
            "census dates（学籍统计日）与开课学期",
        "During your study leave":
            "休学期间",
        "Enrolment Procedure – section 6 (pdf)":
            "Enrolment Procedure（选课注册规程）第 6 节（pdf）",
        "Examples include:":
            "例如：",
        "Extending your leave":
            "延长休学",
        "Intermission (study leave)":
            "休学（intermission，即 study leave）",
        "Intermission Request form":
            "休学申请表",
        "International student":
            "国际学生",
        "Not on a student visa?":
            "不是持学生签证？",
        "Returning from study leave":
            "休学结束复学",
        "Step 1: Check your eligibility":
            "第 1 步：确认你是否符合条件",
        "Step 2: When to apply":
            "第 2 步：什么时候申请",
        "Step 3: Submit an application":
            "第 3 步：提交申请",
        "Step 4: Next steps":
            "第 4 步：后续步骤",
        "Still deciding?":
            "还在犹豫？",
        "Student visa conditions":
            "学生签证条件",
        "Supporting documents":
            "证明材料",
        "Supporting documents View":
            "证明材料 查看",
        "Thinking about taking a break?":
            "在考虑暂停学业？",
        "be recently dated":
            "日期是近期的",
        "how long they lasted":
            "持续了多久",
        "notification from defence services.":
            "国防部门出具的通知。",
        "police report":
            "报案记录",
        "their level of impact.":
            "影响的严重程度。",
        "when they occurred":
            "发生的时间",
        "your compassionate or compelling circumstances":
            "你所处的 compassionate or compelling circumstances（体恤或不可抗情形）",
        "Arts honours students may only take study leave in "
        "exceptional circumstances, for a maximum of one semester. You "
        "need to seek approval from your honours coordinator before "
        "applying.":
            "文学院荣誉学位学生只有在特殊情况下才可以申请 study "
            "leave（休学），且最长一个学期。申请前需要先取得荣誉学位课程协调人的批准。",
        "Before you decide to take intermission, it's a good idea to "
        "weigh your options and the support available.":
            "在决定休学（intermission）之前，先把可选的路径和能拿到的支持权衡一遍为好。",
        "Compassionate or compelling circumstances are personal "
        "circumstances that:":
            "compassionate or compelling "
            "circumstances（体恤或不可抗情形）指的是具备以下特征的个人处境：",
        "Depending on your circumstances, you may need to provide more "
        "than one of the documents listed above.":
            "视你的具体处境而定，上面列出的材料可能需要提交不止一种。",
        "Do not, under any circumstances, submit fraudulent "
        "documentation":
            "任何情况下都不要提交伪造材料",
        "Documents issued in a language other than English must be "
        "translated into English by the National Accreditation "
        "Authority for Translators and Interpreters (NAATI) or an "
        "overseas notary department with a common seal.":
            "非英文签发的材料，必须由 National Accreditation Authority for Translators "
            "and Interpreters（NAATI，澳大利亚翻译资格认可局）或持有公章的海外公证机构译成英文。",
        "Domestic coursework students are eligible to apply for study "
        "leave using the intermission form below, with some exceptions.":
            "本地授课型学生可以用下面的 intermission（休学）表格申请 study leave（休学），但有少数例外。",
        "Firstly, what kind of student are you?":
            "首先，你属于哪一类学生？",
        "For more details, see supporting documents for compassionate "
        "or compelling circumstances.":
            "更多细节，请查看compassionate or compelling "
            "circumstances（体恤或不可抗情形）所需的证明材料。",
        "If you can provide proof that the reason you applied for "
        "study leave after the census date was due to exceptional "
        "circumstances, you can apply for a fee reversal.":
            "如果你能提供证据，证明你在 census date（学籍统计日）之后才申请 study "
            "leave（休学）是出于特殊情况，就可以申请学费冲销。",
        "If you have been seeing a counsellor in an ongoing way about "
        "issues affecting your study, you can talk to your counsellor "
        "about completing a Health Professional Report (HPR) to "
        "support an application under compassionate and compelling "
        "circumstances.":
            "如果你一直在就影响学业的问题接受心理咨询，可以和咨询师商量，请他填写一份 Health Professional "
            "Report（HPR，健康专业人员报告），作为按compassionate or compelling "
            "circumstances（体恤或不可抗情形）提出申请的支持材料。",
        "If you need to take a longer period of study leave than you "
        "initially requested, submit a new intermission request. "
        "Intermission extensions beyond 12 months of total leave are "
        "only approved in exceptional circumstances, and at the "
        "discretion of the faculty. You may need to provide supporting "
        "documentation.":
            "如果你需要的 study leave（休学）比当初申请的更长，请重新提交一份 "
            "intermission（休学）申请。累计休学超过 12 "
            "个月的延长，只有在特殊情况下才会获批，且由学院自行裁量，你可能需要提交证明材料。",
        "If you want to return early, message Monash Connect.":
            "如果你想提前复学，请给 Monash Connect（学生服务中心）留言。",
        "If you're a domestic or international coursework student "
        "studying at Monash University, you're in the right place. If "
        "that's not you, you'll find the information you need below:":
            "如果你是在 Monash 大学就读的本地或国际授课型学生，这个页面就是给你看的。如果不是，请看下面对应的入口：",
        "If you're not on a student visa, you can go ahead and apply "
        "for intermission – you won't need to show compassionate or "
        "compelling circumstances.":
            "如果你不是持学生签证，可以直接申请休学（intermission）——不需要证明存在compassionate or "
            "compelling circumstances（体恤或不可抗情形）。",
        "If you're on a student visa, approval for study leave is "
        "given only in compassionate or compelling circumstances "
        "(unless intermission was recommended by an Academic Progress "
        "Committee panel).":
            "如果你持学生签证，只有在存在compassionate or compelling "
            "circumstances（体恤或不可抗情形）时，study "
            "leave（休学）才会获批（除非休学是学业进度审查委员会小组建议的）。",
        "If you're only taking leave for one semester or teaching "
        "period, don’t forget to re-enrol for the following semester "
        "or teaching period – see re-enrolment dates and details.":
            "如果你只休一个学期或一个开课学期的假，别忘了为下一个学期或开课学期重新注册选课——请查看重新注册的日期与说明。",
        "If you’re granted study leave for compassionate or compelling "
        "circumstances, there are a few things you’ll need to do:":
            "如果你因compassionate or compelling circumstances（体恤或不可抗情形）获批 "
            "study leave（休学），有几件事需要办：",
        "If you’re sure you want to apply for intermission, timing "
        "matters – applying at the right time means you’ll avoid "
        "financial and academic penalties:":
            "如果你确定要申请休学（intermission），时间点很关键——挑对时间才不会产生费用上和学业上的处罚：",
        "In the form, you’ll be asked to explain why you’re taking a "
        "study break. Understanding what has influenced your decision "
        "helps us identify support services for you, and improve the "
        "experience for other students. You can also elect to be "
        "contacted by Monash Connect about our services and next steps.":
            "表格里会请你说明休学的原因。了解是什么影响了你的决定，有助于我们为你找到合适的支持服务，也有助于改善其他学生的就读体验。你也可以选择让 "
            "Monash Connect（学生服务中心）就相关服务和后续步骤与你联系。",
        "Keep your contact details up-to-date and check your Monash "
        "email regularly so you don't miss University updates.":
            "保持联系方式为最新，并经常查看你的 Monash 邮箱，以免错过学校的通知。",
        "Monash College students\n \nIntermission request steps and "
        "conditions":
            "Monash College 学生\n \n休学申请的步骤与条件",
        "Monash Online students\n \nApply in the Student Hub":
            "Monash Online 学生\n \n在 Student Hub 提交申请",
        "Monash University, Malaysia students\n \nIntermission "
        "eligibility and application process":
            "Monash 大学马来西亚校区学生\n \n休学的资格条件与申请流程",
        "Once you’ve submitted an intermission request, we’ll usually "
        "get back to you within two University working days to discuss "
        "your request and take you through the process (although this "
        "may take longer during busy periods).":
            "提交休学（intermission）申请后，我们通常会在两个学校工作日内与你联系，讨论你的申请并带你走完流程（繁忙时段可能会久一些）。",
        "Penalties incurred after the census date":
            "在 census date（学籍统计日）之后产生的处罚",
        "Ready to move forward? Follow the steps to apply your "
        "intermission.":
            "准备好了？按下面的步骤提交你的休学（intermission）申请。",
        "Research students (Australian campuses)\n \nApply in the "
        "graduate research portal":
            "研究型学生（澳大利亚校区）\n \n在研究生研究门户中提交申请",
        "Science honours students must complete an honours "
        "supplementary form (pdf, 0.6 mb) and attach the signed form "
        "to their intermission application.":
            "理学院荣誉学位学生必须填写一份 honours supplementary form（荣誉学位补充表，pdf，0.6 "
            "mb），并把签好字的表格附在休学申请上。",
        "Tell us a bit about your situation and we can point you to "
        "the right support.":
            "说说你的情况，我们可以帮你找到合适的支持。",
        "There are many reasons you might need to pause your studies, "
        "from managing personal or health challenges to needing time "
        "to reset or focus on other responsibilities. Whatever brought "
        "you here, this page will help you find the right path forward.":
            "需要暂停学业的原因有很多——可能是要应对个人或健康上的难处，也可能是需要时间调整状态、或先顾及别的责任。无论是什么把你带到这一页，这里都会帮你找到合适的下一步。",
        "To apply for intermission, submit the request form.":
            "要申请休学（intermission），请提交申请表。",
        "To find out more about your responsibilities (and what you "
        "should do if you don’t have the required supporting "
        "documents), see our documentation integrity page.":
            "想进一步了解你的责任（以及在拿不到所需证明材料时该怎么办），请查看 documentation "
            "integrity（材料真实性）页面。",
        "To support your intermission request, you can provide a:":
            "为支持你的休学（intermission）申请，你可以提交：",
        "While you're on study leave, you:":
            "在 study leave（休学）期间，你：",
        "You can apply for a break of up to 12 months during your "
        "course, which you can take over two separate or consecutive "
        "teaching periods.":
            "在整个学位课程期间，你最多可以申请 12 个月的休学，可以分两段、也可以在连续的两个开课学期内使用。",
        "You must give us information that is true, accurate and "
        "complete – without intending to mislead or gain advantage. If "
        "you make a false statement or provide a falsified document:":
            "你提供的信息必须真实、准确、完整，不得有误导或谋取便利的意图。如果你作出虚假陈述，或提交伪造材料：",
        "You need to complete your course within a certain time frame "
        "(which includes study leave), so make sure you have enough "
        "time left before you apply for intermission. See study load "
        "for more information.":
            "你必须在规定的年限内完成学位课程（休学时间也计算在内），所以申请休学（intermission）前请确认自己还剩足够的时间。详见「学习负荷」页面。",
        "You'll need to provide supporting documents as evidence. Keep "
        "in mind, the Government may cancel your student visa if you "
        "provide fraudulent evidence/documents to Monash University "
        "when applying for study leave (check our documentation "
        "integrity page for examples and penalty information).":
            "你需要提交证明材料作为证据。请注意：如果你在申请 study leave（休学）时向 Monash "
            "大学提交伪造的证据或材料，政府可能会取消你的学生签证（示例和处罚信息见 documentation "
            "integrity（材料真实性）页面）。",
        "You'll receive a reminder to re-enrol ahead of the "
        "re-enrolment period for coursework students. To avoid a late "
        "fee and keep your place in your course, make sure you "
        "re-enrol during this period.":
            "在授课型学生的重新注册期开始前，你会收到重新注册的提醒。请务必在这段期间内完成重新注册，以免产生滞纳金、并保住你在学位课程中的学籍。",
        "Your eligibility depends on whether you’re a domestic "
        "student, or an international student on a student visa.":
            "你是否符合条件，取决于你是本地学生，还是持学生签证的国际学生。",
        "You’ll need to provide supporting documents that clearly show:":
            "你需要提交的证明材料必须清楚显示：",
        "You’re responsible for making sure the documents you supply "
        "to us are genuine, accurate and complete. Penalties for "
        "submitting a forged, altered or falsified document can "
        "include exclusion from the University, a fine of up to AUD "
        "$1,000 and a permanent record in Monash systems.":
            "你有责任确保提交给我们的材料真实、准确、完整。提交伪造、篡改或造假材料的处罚包括：被学校退学处理（exclusion）、最高 "
            "1000 澳元罚款，以及在 Monash 系统中留下永久记录。",
        "a serious illness or medical condition affecting your ability "
        "to study":
            "影响你学习能力的重病或健康问题",
        "apply for a new Confirmation of Enrolment (CoE) before you "
        "return from study leave (your current CoE will be cancelled "
        "when you go on study leave). You’ll receive your new CoE with "
        "a revised completion date when you return from leave":
            "在复学之前申请新的入学确认书（CoE）——你现有的 CoE 会在你开始 study "
            "leave（休学）时被注销。复学时你会拿到载有新完成日期的新 CoE",
        "apply for a new student visa with your new CoE":
            "凭新的 CoE 申请新的学生签证",
        "are involuntary and outside your control (such as medical, "
        "family, wellbeing, or enrolment circumstances), and":
            "并非你自愿、且不在你控制范围之内（例如医疗、家庭、身心状况或选课注册方面的情形），并且",
        "be from an independent source or authority":
            "来自独立的第三方机构或主管部门",
        "bereavement of a close family member where you need to "
        "provide assistance or support":
            "近亲过世，且你需要提供协助或照料",
        "check your visa status in VEVO before you resume your studies "
        "– if your student visa has been cancelled, you’ll need to get "
        "a new one to enter Australia.":
            "复学前先在 VEVO 中查看签证状态——如果你的学生签证已被取消，需要重新办一份才能入境澳大利亚。",
        "confirm that your circumstances are ongoing and relevant to "
        "the timeframe.":
            "确认你的处境仍在持续，且与所涉时间段相关。",
        "course progression restrictions or unit unavailability.":
            "课程修读次序限制，或某些课程未开课。",
        "death notice or certificate and evidence of relationship":
            "讣告或死亡证明，以及亲属关系证明",
        "detailed statement from a counsellor (like the University's "
        "Counselling and Psychological Services team) who has been "
        "involved in your assessment and/or treatment":
            "由参与你评估和／或治疗的心理咨询师（例如学校的 Counselling and Psychological "
            "Services（心理咨询与心理健康服务）团队）出具的详细说明",
        "if you already know you won't be studying in the following "
        "teaching period – apply during the timely re-enrolment "
        "period, before enrolling in units for the next academic year":
            "如果你已经确定下一个开课学期不会读书——请在正常的重新注册期内申请，赶在为下一学年选课之前",
        "letter from a social worker, lawyer, or psychologist":
            "由社会工作者、律师或心理学家出具的信函",
        "medical certificate or letter from a medical professional "
        "which specifically suggests taking a study break and how long "
        "the break should be (even if your doctor has filled in your "
        "intermission request form)":
            "由医疗专业人员出具的 medical "
            "certificate（医疗证明）或信函，其中明确建议你休学、并写明应休多长时间（即使你的医生已经帮你填了休学申请表，这份材料仍然需要）",
        "must check your Monash email account for important "
        "information.":
            "必须查看 Monash 邮箱，以免错过重要信息。",
        "must keep your contact details up to date to receive "
        "communication from the University":
            "必须保持联系方式为最新，以便接收学校的通知",
        "present you with limited or no choice but to take a break "
        "from your studies.":
            "使你除了暂停学业之外几乎没有别的选择。",
        "remain a current student of Monash University with access to "
        "University services, including the library, WES, Student "
        "Portal and the Monash intranet":
            "仍是 Monash 大学的在读学生，可以继续使用学校的各项服务，包括图书馆、WES（学生系统）、学生门户以及 Monash "
            "内网",
        "resume your studies once your intermission period has ended, "
        "otherwise the Government may cancel your student visa.":
            "必须在休学期结束后复学，否则政府可能会取消你的学生签证。",
        "social or political upheaval in your country that is "
        "affecting your family":
            "你所在国家发生的社会或政治动荡正在影响你的家人",
        "statutory declarations from you or relevant people":
            "由你本人或相关人士出具的 statutory declaration（法定声明）",
        "we'll refer the matter to Student Conduct and Complaints for "
        "an academic misconduct investigation.":
            "我们会将此事移交 Student Conduct and Complaints（学生行为与投诉办公室）按学术不端立案调查。",
        "your application will be rejected, and":
            "你的申请会被驳回；并且",
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
        "A few important tips...":
            "几点提醒……",
        "Assessment Regime Procedure (pdf)":
            "Assessment Regime Procedure（考核制度规程，pdf）",
        "Defer your final assessment":
            "申请期末考核延期",
        "Extensions and special consideration":
            "延期与特殊考虑（special consideration）",
        "Get a short extension":
            "申请短期延期",
        "If you give false information":
            "提供虚假信息的后果",
        "In-class assessments and mid-semester tests":
            "课堂考核与期中测验",
        "Long-term or ongoing circumstances":
            "长期或持续性的情况",
        "Marking and Feedback Procedure (pdf)":
            "Marking and Feedback Procedure（评分与反馈规程，pdf）",
        "Medical documentation clarifications":
            "医疗材料要求说明",
        "Need an extension?":
            "需要延期？",
        "Reschedule your deferred assessment":
            "为延期考核改期",
        "Short extension (two calendar days)":
            "短期延期（两个日历日）",
        "Special Consideration Procedure (pdf)":
            "Special Consideration Procedure（特殊考虑规程，pdf）",
        "Successful application":
            "申请获批",
        "When you’re not eligible":
            "不符合条件的情形",
        "a group assessment":
            "小组考核",
        "a mid-semester test":
            "期中测验",
        "a practical assessment (including laboratories)":
            "实践考核（含实验课）",
        "a scheduled final assessment.":
            "已排定的期末考核。",
        "disruption caused by international conflict":
            "国际冲突造成的影响",
        "family (relationship breakdown)":
            "家庭（关系破裂）",
        "financial/employment issues":
            "经济或就业问题",
        "gender-based violence":
            "性别暴力",
        "loss or bereavement":
            "亲人离世与哀伤",
        "medical condition (including COVID-19)":
            "健康问题（含新冠）",
        "mental health condition":
            "心理健康问题",
        "mistaking your assessment due date":
            "记错了考核截止日期",
        "other extreme circumstances.":
            "其他极端情况。",
        "religious or cultural obligations":
            "宗教或文化义务",
        "serious and debilitating medical condition":
            "严重且使人失能的健康问题",
        "severe mental health condition":
            "严重心理健康问题",
        "technical disruption":
            "技术故障",
        "If an extension isn’t appropriate, we may arrange an "
        "alternative and equivalent form of your assessment. If the "
        "outcome of your application is an alternative assessment, "
        "you’ll need to complete it (you can’t get an extension "
        "instead)":
            "如果延期并不合适，我们可能会为你安排一种替代的、难度相当的考核形式。如果你的申请结果是替代考核，你就必须完成它（不能改成延期）",
        "Applications received after the final results for the unit "
        "are released will not be taken into consideration under any "
        "circumstances.":
            "在该课程最终成绩公布之后收到的申请，任何情况下都不予受理。",
        "Apply for fee reversal and Withdrawn grade (special "
        "circumstances)\n \nIf special circumstances that were beyond "
        "your control made it impossible for you to complete unit "
        "requirements, you may be eligible for a fee reversal or "
        "Withdrawn grade.":
            "申请学费冲销与 Withdrawn（退课）成绩（特殊情形）\n "
            "\n如果确有你无法控制的特殊情形，使你不可能完成该课程的要求，你可能符合申请学费冲销或 Withdrawn（退课）成绩的条件。",
        "Assessment and Academic Integrity Policy (pdf)":
            "Assessment and Academic Integrity Policy（考核与学术诚信政策，pdf）",
        "Certain assessments aren’t available for special "
        "consideration (e.g. placements) – this is determined by the "
        "dean (or delegate) of the faculty. If you can’t complete the "
        "assessment and it’s not available for special consideration, "
        "check the Handbook to see the alternative arrangements.":
            "某些考核不适用特殊考虑（special "
            "consideration）（例如实习），这由学院院长（或其授权人）决定。如果你无法完成该考核、而它又不适用特殊考虑（special "
            "consideration），请查看 Handbook 了解替代安排。",
        "Extension through special consideration (generally longer)":
            "通过特殊考虑（special consideration）申请延期（时长通常更久）",
        "Get an extension through special consideration":
            "通过特殊考虑（special consideration）申请延期",
        "How to apply\nSubmit an application as soon as possible, but "
        "no later than 11.55pm on the day your assessment is due.\n\n "
        "Short extension form":
            "如何申请\n请尽快提交申请，最迟不得晚于考核截止当天 23:55。\n\n 短期延期申请表",
        "How to apply\nSubmit an application as soon as possible, but "
        "no later than 11.55pm on the day your assessment is due. Make "
        "sure you attach all required supporting documents as evidence "
        "of your exceptional circumstances.Applications can still be "
        "submitted without supporting documents (not having your "
        "supporting documents ready is not a sufficient reason to "
        "apply late). You'll need to submit your application on time "
        "without your documents and include a date for when you will "
        "provide them.\n\n Apply for an extension":
            "如何申请\n请尽快提交申请，最迟不得晚于考核截止当天 "
            "23:55，并务必附上全部所需的证明材料，作为你所处特殊情况的证据。没有证明材料也仍然可以先提交申请（材料没准备好不构成迟交申请的正当理由）——你需要按时提交申请，并在其中写明将于哪一天补交材料。\n\n "
            "申请延期",
        "If an extension isn’t appropriate, we may arrange an "
        "alternative and equivalent form of your assessment. If the "
        "outcome of your application is an alternative assessment, "
        "you’ll need to complete it (you can’t get an extension "
        "instead).":
            "如果延期并不合适，我们可能会为你安排一种替代的、难度相当的考核形式。如果你的申请结果是替代考核，你就必须完成它（不能改成延期）。",
        "If an extension or alternative assessment isn’t appropriate, "
        "you may be exempt from completing your assessment if the task "
        "makes up 10% or less of your assessments overall. Your "
        "teaching faculty will determine which assessments are "
        "eligible and will reweight your other assessments for your "
        "unit.":
            "如果延期和替代考核都不合适，而该项任务占你全部考核的 10% "
            "或以下，你可能会被免于完成这项考核。哪些考核符合条件由授课学院判定，学院也会相应调整你这门课其他考核的权重。",
        "If an extension or alternative assessment isn’t appropriate, "
        "you may be exempt from completing your assessment if the task "
        "makes up 10% or less of your assessments overall.Your "
        "teaching faculty will determine which assessments are "
        "eligible and will reweight your other assessments for your "
        "unit.":
            "如果延期和替代考核都不合适，而该项任务占你全部考核的 10% "
            "或以下，你可能会被免于完成这项考核。哪些考核符合条件由授课学院判定，学院也会相应调整你这门课其他考核的权重。",
        "If exceptional circumstances prevented you from attending "
        "your practical activity, it’s best to speak to your chief "
        "examiner to see if there’s another scheduled activity you can "
        "attend. If there isn’t, you may be eligible to apply for "
        "special consideration for the assessment task that’s "
        "associated with your practical/lab activity.":
            "如果确有特殊情况使你无法参加实践活动，最好先联系主考官（chief "
            "examiner），看看有没有另一场已排定的活动可以参加。如果没有，你可能符合为该实践或实验活动所对应的考核任务申请特殊考虑（special "
            "consideration）的条件。",
        "If we approve your application, in most cases your extension "
        "will align with the days recommended in your supporting "
        "documents.An extension starts on the original due date of "
        "your assessment and applies to the day or set of days "
        "specified in your supporting documents. For example, if your "
        "original due date is 1 October and your doctor states on your "
        "medical certificate that you’re unfit to study for five days "
        "(23 September through 27 September), the new due date will be "
        "6 October.If you apply late or provide your supporting "
        "documents late, you may receive a response after the new due "
        "date for your assessment. If you’re well enough, it’s "
        "important that you continue working on your assessment. We "
        "won't be able to grant you an extension longer than the "
        "timeframe in your supporting documentation.":
            "如果你的申请获批，多数情况下延期天数会与你证明材料中建议的天数一致。延期从考核原定截止日起算，按你证明材料中载明的那一天或那几天顺延。举例来说：原定截止日是 "
            "10 月 1 日，医生在 medical certificate（医疗证明）上写明你有五天（9 月 23 日至 27 "
            "日）不适宜学习，那么新的截止日就是 10 月 6 "
            "日。如果你申请得晚、或材料交得晚，回复可能会在新截止日之后才到。只要身体允许，请务必继续做你的考核。我们无法给出超过你证明材料所载时长的延期。",
        "If we don’t approve your application, you’ll still need to "
        "submit your assessment.":
            "如果申请未获批，你仍然需要提交考核。",
        "If you apply and get an extension, it doesn’t guarantee that "
        "the rest of your group will be granted one as well. Your "
        "chief examiner will decide which outcome best suits your "
        "circumstances and let you know.":
            "你申请并拿到延期，并不代表小组里其他人也会一并获批。主考官（chief "
            "examiner）会判断哪种处理最符合你的情况，并通知你。",
        "If you need an additional extension":
            "如果你需要再一次延期",
        "If you require prolonged extension across the teaching "
        "period, we may decline your application and instead recommend "
        "that you withdraw from your unit. You may be eligible to "
        "apply for special circumstances.":
            "如果你需要跨越整个开课学期的长期延期，我们可能会驳回你的申请，转而建议你退选这门课程。你可能符合按特殊情形（special "
            "circumstances）提出申请的条件。",
        "If you submitted an application without supporting documents "
        "and didn't provide them by the date stated in your "
        "application, we’ll cancel your application.":
            "如果你提交申请时没有附证明材料，又没有在申请中写明的日期之前补交，我们会撤销你的申请。",
        "If you're registered with DSS and were prevented from "
        "applying on time due to the nature or exacerbation of your "
        "DSS registered condition, you’ll just need to provide "
        "supporting documents that explain why you were prevented from "
        "applying on time.":
            "如果你已在 DSS "
            "登记，并且是因为登记状况本身或其加重而无法按时申请，你只需要提交证明材料，说明是什么使你无法按时申请即可。",
        "If your application is approved, we’ll give you a new date to "
        "complete your assessment. In some cases, a second (and final) "
        "reschedule may be considered – but only if extreme "
        "circumstances beyond your control directly impact your "
        "ability to attend the new date.":
            "如果申请获批，我们会给你一个新的完成日期。在某些情况下，可以考虑第二次（也是最后一次）改期——但前提是确有你无法控制的极端情况，直接影响了你按新日期参加的能力。",
        "If your application is approved, you may receive one of the "
        "following outcomes.":
            "如果申请获批，你可能会收到下列结果之一。",
        "If your application is not approved":
            "如果申请未获批",
        "If you’re affected by long-term or ongoing circumstances, "
        "such as a recurring medical condition or carer "
        "responsibilities (including for your children), we encourage "
        "you to register with Disability Support Services (DSS). If "
        "you’re registered with DSS and the circumstances for which "
        "you’re registered prevent you from completing your assessment "
        "on time, you may be eligible for an extension through special "
        "consideration (as long as DSS has approved you for flexible "
        "deadlines). DSS can also support you with other reasonable "
        "adjustments to support your learning.":
            "如果你受长期或持续性情况影响，例如反复发作的健康问题或照护责任（包括照顾子女），我们建议你到 Disability "
            "Support "
            "Services（DSS，无障碍支持服务）登记。登记之后，若你登记的这些情况使你无法按时完成考核，你可能符合通过特殊考虑（special "
            "consideration）申请延期的条件（前提是 DSS 已批准你使用 flexible "
            "deadlines（弹性截止日期））。DSS 还可以为你安排其他合理调整，以支持你的学习。",
        "If you’re unable to attend your in-class assessment (for "
        "example, a class test or presentation), mid-semester test or "
        "practical assessment, you’ll need to provide supporting "
        "documents showing the exceptional circumstances that "
        "prevented you from completing it on the scheduled day. If "
        "you’re providing a medical certificate, it needs to be from "
        "an in-person consultation from a fully registered "
        "practitioner in the country you’re enrolled in. Video/phone "
        "consultation will only be accepted if it was impractical for "
        "you to attend in person. Make sure you check our supporting "
        "documents page for more details on these requirements.":
            "如果你无法参加课堂考核（例如课堂测验或口头报告）、期中测验或实践考核，需要提交证明材料，说明是什么样的特殊情况使你不能在排定当天完成。如果提交的是 "
            "medical "
            "certificate（医疗证明），它必须来自你就读所在国家、经完全注册的执业人员的当面就诊；只有在当面就诊确实不可行时，视频或电话问诊才会被接受。更多要求请查看「证明材料」页面。",
        "If you’re waiting for an outcome to an application and "
        "realise you need more time than what you requested, you’ll "
        "need to submit a new application. When you submit a new "
        "application, your previous application will be withdrawn "
        "immediately – so make sure you include all the supporting "
        "documents needed in your new application.":
            "如果你还在等结果，却发现需要的时间比申请时更多，就需要重新提交一份申请。新申请一经提交，之前那份会立即作废——所以请务必把所需的全部证明材料都放进新申请里。",
        "If you’ve already attempted an assessment task (or if you’ve "
        "exhausted all your attempts for a task that allowed multiple "
        "attempts), you won’t be able to get a short extension.":
            "如果你已经作答过某项考核任务（或者对允许多次作答的任务已经用完全部次数），就无法再申请短期延期。",
        "If you’ve already attempted or submitted an assessment task, "
        "we can’t grant you a second attempt or the ability to "
        "resubmit. If you’ve exhausted all your attempts for a task "
        "that allowed multiple attempts (e.g. a quiz), you won’t be "
        "eligible for special consideration. This includes situations "
        "where you've started an assessment and it's automatically "
        "submitted when closed.":
            "如果你已经作答或提交过某项考核任务，我们无法再给你一次作答机会或重新提交的机会。对允许多次作答的任务（例如小测），一旦用完全部次数，就不再符合特殊考虑（special "
            "consideration）的条件。这也包括你已经开始作答、系统在关闭时自动提交的情形。",
        "If you’ve already been given a short extension and then find "
        "that changed circumstances prevent you from completing your "
        "assessment by the revised due date, you may be eligible for "
        "an extension through special consideration, with supporting "
        "documents.":
            "如果你已经拿到过短期延期，之后情况有变、使你无法在新截止日前完成考核，你可能符合凭证明材料通过特殊考虑（special "
            "consideration）申请延期的条件。",
        "If you’ve already been given an extension but you're unable "
        "to complete your assessment by the revised due date, you’ll "
        "need to submit a new application with new supporting "
        "documents. Your supporting documents must explain why you are "
        "unable to complete your assessment by the revised due date "
        "and how much longer you need.":
            "如果你已经拿到过延期，但仍无法在新截止日前完成考核，就需要提交一份新申请和新的证明材料。材料中必须说明你为何无法在新截止日前完成，以及还需要多久。",
        "Medical certificate from UHS\n \nYou can get a medical "
        "certificate from a Monash University Health Services (UHS) "
        "doctor to support your application for special consideration.":
            "UHS 开具的 medical certificate（医疗证明）\n \n你可以找 Monash University "
            "Health Services（UHS，校内医疗服务）的医生开具 medical "
            "certificate（医疗证明），用于支持你的特殊考虑（special consideration）申请。",
        "Missed lab: If you have a laboratory in week 1 that you’re "
        "unable to complete because of an illness, and the associated "
        "assessment is due in week 2, you’ll need to submit an "
        "application for the assessment task due in week 2. You'll "
        "need to apply by 11.55pm on the date of the lab/practical "
        "activity you missed (e.g. the date in week 1) – the "
        "application information and supporting documents need to show "
        "why you missed this activity.\n\nCompleted lab but unable to "
        "complete the assessment: If you’ve completed the "
        "practical/lab activity but exceptional circumstances prevent "
        "you from completing the associated assessment, you may be "
        "eligible to apply for special consideration for the "
        "assessment task. The deadline for the application is 11.55pm "
        "of the date of the assessment task.":
            "错过实验课：如果你在第 1 周有一节实验课，因病无法参加，而对应的考核在第 2 周截止，那么你需要为第 2 "
            "周截止的那项考核任务提交申请，并且必须在你错过的那节实验或实践活动当天（即第 1 周的那一天）23:55 "
            "之前提交——申请信息和证明材料需要说明你为何错过了这项活动。\n\n已完成实验课但无法完成考核：如果你已经完成了实践或实验活动，但确有特殊情况使你无法完成对应的考核，你可能符合为该考核任务申请特殊考虑（special "
            "consideration）的条件。申请截止时间是该考核任务当天的 23:55。",
        "Need help? Ask our virtual assistant. It can help you check "
        "your eligibility and figure out what documents and "
        "information you’ll need.":
            "需要帮忙？问问我们的虚拟助手。它可以帮你确认自己是否符合条件，以及需要准备哪些材料和信息。",
        "Not sure about your options? Ask our virtual assistant!\nWhen "
        "you’re faced with exceptional circumstances, our virtual "
        "assistant can help you check your eligibility and figure out "
        "what documents and information you’ll need to provide.":
            "不确定自己有哪些选择？问问我们的虚拟助手！\n遇到特殊情况时，虚拟助手可以帮你确认是否符合条件，以及需要提供哪些材料和信息。",
        "Once your situation improves, it’s best to keep working on "
        "your assessment and try to submit it as soon as you can. "
        "Otherwise, you may risk a late penalty if we don’t approve "
        "your application. Also, an extension may delay any feedback "
        "on your assessment.":
            "情况一好转，最好就继续做你的考核，并尽快提交。否则万一申请未获批，你可能会被扣迟交分。另外，延期也会推迟你拿到考核反馈的时间。",
        "Practical activities (including laboratories) and associated "
        "assessments":
            "实践活动（含实验课）及其对应的考核",
        "Some assessments will require complex arrangements to be put "
        "in place and additional time may be needed to assess your "
        "application and provide an outcome.":
            "有些考核需要安排的事项比较复杂，评估你的申请并给出结果可能需要更长时间。",
        "Support and advice\n \nIf you need assistance with an "
        "assessment, get support and advice that will help you meet "
        "your course commitments.":
            "支持与建议\n \n如果你在某项考核上需要帮助，这里有能帮你完成学业要求的支持与建议。",
        "Supporting documents\n \nMake sure you provide the correct "
        "supporting documents as evidence of your exceptional or "
        "extreme circumstances when you apply for special "
        "consideration.":
            "证明材料\n \n申请特殊考虑（special "
            "consideration）时，请务必提交正确的证明材料，用以证明你所处的特殊或极端情况。",
        "The application deadline is 11.55pm on the day your "
        "assessment is due or scheduled.":
            "申请截止时间是考核截止或排定当天的 23:55。",
        "The exceptional circumstances approved for your deferred "
        "assessment are still unresolved. You’ll need to provide "
        "updated supporting documents demonstrating the unresolved or "
        "ongoing circumstances that have impacted your original and "
        "deferred assessments.":
            "当初获批延期考核时的那些特殊情况至今仍未解决。你需要提交更新后的证明材料，说明这些尚未解决或仍在持续的情况如何影响了你原定的考核和延期后的考核。",
        "The special consideration process applies to students at all "
        "Monash University campuses and locations.":
            "特殊考虑（special consideration）流程适用于 Monash 大学所有校区和地点的学生。",
        "To be eligible for a second (and final) reschedule of your "
        "in-class, mid-semester or practical assessment, you’ll need "
        "to meet one of the following criteria:":
            "要符合课堂考核、期中测验或实践考核第二次（也是最后一次）改期的条件，你需要满足下列标准之一：",
        "We can’t accept late applications. You’ll need to apply, with "
        "supporting documents, for an extension through special "
        "consideration instead. Your supporting documents will need to "
        "show that you weren’t able to apply on time due to extreme "
        "circumstances beyond your control (e.g. hospitalisation).":
            "我们无法受理迟交的申请。你需要改为凭证明材料通过特殊考虑（special "
            "consideration）申请延期，材料中必须显示你是因为无法控制的极端情况（例如住院）才没能按时申请。",
        "We can’t give you an extension for things like:":
            "下列这类原因我们不会给予延期：",
        "We understand that unexpected circumstances beyond your "
        "control may prevent you from completing your assessment. If "
        "this happens, you may be eligible to apply for more time. "
        "Your options will depend on the type of assessment and "
        "circumstances.":
            "我们理解，你无法控制的突发情况可能使你无法完成考核。遇到这种情况，你可能符合申请更多时间的条件。具体有哪些选择，取决于考核类型和你的处境。",
        "We won’t normally accept an application for an extension "
        "after the deadline – 11.55pm on the day that your assessment "
        "is due – but we understand that extreme circumstances could "
        "prevent you from applying on time (e.g. you were hospitalised "
        "with a serious illness). If this is the case, you’ll need to "
        "provide evidence of these circumstances and how they "
        "prevented you from applying on time.":
            "延期申请一旦超过截止时间——即考核截止当天 "
            "23:55——通常不予受理。但我们也明白，极端情况可能使你无法按时申请（例如你因重病住院）。若是如此，你需要提交证据，说明这些情况本身、以及它们如何使你无法按时申请。",
        "We’ll email you the outcome of your application within one "
        "University working day, with one of the following outcomes.":
            "我们会在一个学校工作日内把申请结果邮件发给你，结果为下列之一。",
        "We’ll email you the outcome of your application within three "
        "University working days as long as you’ve submitted a "
        "complete application with all the required supporting "
        "documents.":
            "只要你提交的申请完整、所需证明材料齐备，我们会在三个学校工作日内把结果邮件发给你。",
        "We’ll email you the outcome within three University working "
        "days of when you submit your new application (complete and "
        "with all the required supporting documents).":
            "自你提交新申请（完整且所需证明材料齐备）起，我们会在三个学校工作日内把结果邮件发给你。",
        "We’ve clarified the requirements for medical documentation "
        "from online or overseas medical providers. To make sure your "
        "application gets processed as quickly as possible, review the "
        "requirements on our supporting documents for special "
        "consideration page before you submit your application.":
            "我们已经把来自线上或海外医疗机构的医疗材料要求写得更清楚了。为使申请尽快得到处理，请在提交前先查看「特殊考虑（special "
            "consideration）证明材料」页面上的要求。",
        "When you apply for a short extension, you don’t need to give "
        "a reason on your first application for an assessment in a "
        "particular unit. All other applications for assessments in "
        "that unit will require a reason. Make sure to apply as soon "
        "as possible, but no later than 11.55pm on the day your "
        "assessment is due.":
            "申请短期延期时，你为某门课程的第一次申请不需要说明理由；同一门课程的其他考核再申请时就需要写明理由。请尽快提交，最迟不得晚于考核截止当天 "
            "23:55。",
        "When you apply for an extension, you must give us information "
        "that’s true, accurate and complete, without intending to "
        "mislead or gain advantage. If you make a false statement or "
        "provide a falsified supporting document, we won't approve "
        "your application and we'll refer the matter to Student "
        "Conduct and Complaints to investigate for academic misconduct.":
            "申请延期时，你提供的信息必须真实、准确、完整，不得有误导或谋取便利的意图。如果你作出虚假陈述，或提交伪造的证明材料，我们不会批准你的申请，并会将此事移交 "
            "Student Conduct and Complaints（学生行为与投诉办公室）按学术不端立案调查。",
        "While you’re waiting for an outcome, and once your situation "
        "improves, it’s best to keep working on your assessment and "
        "try to submit it as soon as possible. Otherwise, you may risk "
        "a late penalty.":
            "在等待结果期间，一旦情况好转，最好就继续做你的考核并尽快提交，否则可能会被扣迟交分。",
        "You can apply for a short extension for most assessments (see "
        "exceptions below), for example, an assignment or quiz.":
            "多数考核都可以申请短期延期（例外见下文），例如作业或小测。",
        "You can apply for an extension (of generally more than two "
        "days) through special consideration for any type of "
        "assessment except a scheduled final assessment (exam) as long "
        "as you can provide documents to support your exceptional "
        "circumstances. These will include:":
            "除已排定的期末考核（考试）外，任何类型的考核都可以通过特殊考虑（special "
            "consideration）申请延期（通常超过两天），前提是你能提供材料证明所处的特殊情况。这些情况包括：",
        "You can apply for special consideration for a group "
        "assessment – the application process is the same. If your "
        "application is approved (for group assessments where other "
        "students are impacted):":
            "小组考核也可以申请特殊考虑（special "
            "consideration），申请流程相同。如果申请获批（且该小组考核涉及其他同学）：",
        "You can't apply to reschedule a supplementary assessment or "
        "an additional assessment on a competency hurdle task.":
            "补考、以及能力门槛任务的附加考核，都不能申请改期。",
        "You can't request an extension from your chief examiner – "
        "instead, use the form below to apply for a short extension, "
        "or an extension through special consideration.":
            "你不能直接向主考官（chief examiner）要延期——请用下面的表格申请短期延期，或通过特殊考虑（special "
            "consideration）申请延期。",
        "You can’t apply for a short extension for:":
            "下列情形不能申请短期延期：",
        "You have an ongoing disability registered with Disability "
        "Support Services (DSS) that prevented you from attending your "
        "deferred assessment. You’ll need to provide supporting "
        "documents showing that the exceptional circumstances were "
        "beyond your control and directly related to your registered "
        "condition.":
            "你有已在 Disability Support "
            "Services（DSS，无障碍支持服务）登记的持续性障碍，并因此无法参加延期考核。你需要提交证明材料，显示这些特殊情况是你无法控制的、且与你登记的状况直接相关。",
        "You may be eligible for a short extension of two calendar "
        "days if you can’t complete your assessment on time due to "
        "short-term difficult circumstances, such as a medical "
        "condition, carer responsibilities (including for your "
        "children) or a car accident.":
            "如果你因短期困难而无法按时完成考核——例如健康问题、照护责任（包括照顾子女）或遭遇车祸——你可能符合申请两个日历日短期延期的条件。",
        "Your application may also be declined if your exceptional "
        "circumstances mean that you require prolonged extensions "
        "during or beyond the teaching period. We may instead "
        "recommend that you withdraw from your unit. You may be "
        "eligible to apply for special circumstances.":
            "如果你的特殊情况意味着你在开课学期之内或之后需要长期延期，申请也可能被驳回。我们可能转而建议你退选这门课程。你可能符合按特殊情形（special "
            "circumstances）提出申请的条件。",
        "You’ll be asked to provide supporting documents at the time "
        "of application. Check our supporting documents page for "
        "information on what documents you need and what to do if "
        "you’re facing delays while trying to get them.":
            "申请时我们会请你提交证明材料。需要哪些材料、以及在取得材料受阻时该怎么办，请查看「证明材料」页面。",
        "You’ve experienced (and can provide evidence of) extreme "
        "circumstances beyond your control, such as:":
            "你确实经历了（并且能提供证据的）无法控制的极端情况，例如：",
        "all the members of your group might be granted an extension.":
            "小组全体成员可能一并获得延期。",
        "an in-class test/assessment (including presentations)":
            "课堂测验或课堂考核（含口头报告）",
        "losing your Moodle access because you didn’t complete a "
        "compulsory module":
            "因为没完成必修模块而被停用 Moodle",
        "loss or bereavement: death of a person with whom you had a "
        "significant relationship":
            "亲人离世与哀伤：与你有重要关系的人过世",
        "military, jury or emergency services obligations":
            "兵役、陪审团或紧急救援服务义务",
        "obligations as athlete, artist or performer registered with "
        "Elite Student Performer Scheme or as representative of "
        "University in other key events and programs":
            "作为已在 Elite Student Performer "
            "Scheme（ESPS，精英学生表现者计划）登记的运动员、艺术家或表演者所负的义务，或代表学校参加其他重要赛事和项目的义务",
        "other exceptional circumstances beyond your control.":
            "其他你无法控制的特殊情况。",
        "representing a club or society as a volunteer":
            "以志愿者身份代表某个社团或学会",
        "scheduled final assessment (exam) (apply for a deferred "
        "assessment instead).":
            "已排定的期末考核（考试）——请改为申请延期考核。",
        "technical issues you might have avoided by uploading the "
        "correct files, allowing enough time for uploading and having "
        "the right equipment":
            "本可以避免的技术问题，例如上传了正确的文件、留出足够的上传时间、或备好合适的设备就不会发生的那些",
        "the method for marking the work of your group members (who "
        "did not apply for special consideration) might change, or":
            "对小组中未申请特殊考虑（special consideration）的其他成员，其作业的评分方式可能会有所调整；或者",
        "victim of crime or concerns about safety":
            "遭受犯罪侵害，或对人身安全的担忧",
        "you could be given an alternative assessment task":
            "你可能会被安排一项替代的考核任务",
        "If we approve your application, you’ll get an extension of two calendar days from the original due date of the assessment task.":
            "如果申请获批，你将从考核任务的原定截止日起获得 2 个日历日的延期。",
        "If you’ve already been given a short extension for an assessment but you need more time, you’ll need to then apply for an extension through special consideration with supporting documents.":
            "如果你已经为某项考核拿到短期延期但仍需更多时间，接下来需要通过特殊考虑（special consideration）申请延期，并提交证明材料。",
        "When you apply for an extension through special consideration, you need to provide supporting documents to show why you can’t complete your assessment as scheduled due to immediate and exceptional circumstances beyond your control. Make sure to apply as soon as possible, but no later than 11.55pm on the day your assessment is due.":
            "通过特殊考虑（special consideration）申请延期时，你需要提交证明材料，说明自己为何因突发且无法控制的特殊情况而不能按时完成考核。请尽快提出申请，最迟不得晚于考核截止当天 23:55。",
    },
    "student-visa": {
        "Apply for a student visa":
            "申请学生签证",
        "Applying for your visa":
            "递交签证申请",
        "Attach any documents required.":
            "上传所需的各项材料。",
        "If your visa is cancelled":
            "签证被取消时",
        "Keeping your visa valid":
            "保持签证有效",
        "Receiving an outcome":
            "收到审理结果",
        "Visas for family members":
            "家庭成员的签证",
        "your partner":
            "你的伴侣",
        "As an international student, you can only apply to reduce "
        "your study load or take a study break (intermission) under "
        "compassionate or compelling circumstances.":
            "作为国际学生，只有在具备体恤或不可抗因素（compassionate or compelling "
            "circumstances）的情况下，你才可以申请减少学习负荷或休学（intermission）。",
        "As an international student, you need a student visa "
        "(subclass 500) to study at Monash. If you’re a new student, "
        "you’ll need to apply for a student visa. If you’re a "
        "returning student, you’ll need to make sure your visa remains "
        "valid for the duration of your course.":
            "作为国际学生，你需要持学生签证（subclass 500）才能在 Monash "
            "学习。如果你是新生，需要申请学生签证；如果你是在读学生，则要确保签证在整个学位课程期间保持有效。",
        "Changing your enrolment\n \nHow changes to your enrolment can "
        "affect your visa.":
            "变更选课注册\n \n选课注册的变动会怎样影响你的签证。",
        "Confirmation of Enrolment (CoE)\n \nYour CoE should reflect "
        "your course enrolment and duration. You’ll need to apply for "
        "a new CoE if you can’t complete your course in the set time "
        "and need a new student visa.":
            "入学确认书（CoE）\n \n你的 CoE "
            "应当如实反映你的学位课程注册情况和学习年限。如果你无法在规定时间内完成学位课程、需要办新的学生签证，就要申请一份新的 "
            "CoE。",
        "Create or log into your ImmiAccount – this is where you’ll "
        "apply.":
            "创建或登录你的 ImmiAccount 账户——申请就在这里提交。",
        "Extending your stay\n \nFind out what to do if you need to "
        "extend your stay in Australia.":
            "延长在澳停留时间\n \n如果你需要延长在澳大利亚停留的时间，看看该怎么办。",
        "Familiarise yourself with the application process – take a "
        "look at the Department of Home Affairs’ page on Student visa "
        "(Subclass 500) so you know what to expect.":
            "先熟悉申请流程——看一看 Department of Home Affairs（澳大利亚内政部） 关于 Student "
            "visa (Subclass 500) 的页面，对整个过程心里有数。",
        "For more information, check your visa details and conditions "
        "(Department of Home Affairs).":
            "更多信息，请查看你的签证详情与签证条件（Department of Home Affairs（澳大利亚内政部））。",
        "Get your documents ready – use the Department of Home "
        "Affairs’ Document Checklist Tool to see what you’ll need (do "
        "this early, as you’ll need to organise things like Overseas "
        "Student Health Cover).":
            "把材料准备好——用 Department of Home Affairs（澳大利亚内政部） 的 Document "
            "Checklist "
            "Tool（材料清单工具）查清自己需要哪些材料。这件事要早做，因为像留学生医疗保险（OSHC）这类事项需要时间安排。",
        "Home Affairs no longer issues visa labels – instead, they now "
        "hold your visa information electronically. You can confirm "
        "your visa conditions (including work restrictions) using the "
        "Visa Entitlement Verification Online (VEVO) system.":
            "内政部已不再签发签证贴纸，改为以电子方式保存你的签证信息。你可以通过 Visa Entitlement "
            "Verification Online（VEVO，签证权利在线核验系统）确认自己的签证条件，包括工作限制。",
        "If you're on a student visa, you must complete your course in "
        "the time stated on your CoE. The standard undergraduate study "
        "load per year is 48 credit points (24 credit points per "
        "semester).":
            "如果你持学生签证，必须在 CoE 上载明的时间内完成学位课程。本科阶段每年的标准学习负荷是 48 学分（每学期 24 "
            "学分）。",
        "If your current visa is due to expire before you finish your "
        "course, you’ll need to apply for a new one.":
            "如果你现有签证会在学业结束前到期，就需要申请一份新签证。",
        "If your visa is approved, make sure you read through this "
        "communication carefully and keep a copy of it. It will "
        "include important information like your visa grant number, "
        "expiry date and conditions.":
            "如果签证获批，请仔细阅读这份通知并留存副本。里面会有签证批准号、到期日和签证条件等重要信息。",
        "If you’re coming to study at Monash on an Australia Awards "
        "scholarship, see family members of AAS students for relevant "
        "visa details.":
            "如果你是持 Australia Awards 奖学金来 Monash 学习的，相关签证事项请查看「AAS "
            "学生的家庭成员」页面。",
        "If you’re experiencing delays and your course start date is "
        "approaching, reach out to Monash Connect for advice. While we "
        "can’t speed up your application, we can discuss some study "
        "options with you.":
            "如果你的申请出现延误、而开课日期又临近，可以联系 Monash "
            "Connect（学生服务中心）咨询。我们没办法加快你的签证审理，但可以和你一起讨论几种学业上的安排。",
        "If you’re in Australia or immigration clearance, the "
        "Department of Home Affairs will usually notify you if they're "
        "considering cancelling your visa and give you the opportunity "
        "to explain why your visa should not be cancelled.":
            "如果你人在澳大利亚境内或正在办理入境查验，Department of Home "
            "Affairs（澳大利亚内政部）在考虑取消你的签证时，通常会先通知你，并给你机会陈述不应取消的理由。",
        "If you’re on a student visa, you need to be in Australia to "
        "attend face-to-face classes during your course. You can only "
        "study up to one-third of your course by distance education or "
        "online. For example, if your course has 24 units to be "
        "completed over a three-year period, you can only complete "
        "eight units by distance education or online.":
            "如果你持学生签证，就需要人在澳大利亚参加面授课程。你最多只能有三分之一的学位课程通过远程或线上方式修读。举例来说，如果你的学位课程需要在三年内修完 "
            "24 门课，其中最多只能有 8 门通过远程或线上完成。",
        "If you’re planning to study in Australia on another type of "
        "visa, go to immigration and citizenship (Department of Home "
        "Affairs) to check your visa rights and restrictions.":
            "如果你打算持其他类型的签证在澳大利亚学习，请到 Department of Home "
            "Affairs（澳大利亚内政部）的移民与公民事务页面查看该签证的权利与限制。",
        "It’s a good idea to prepare a few things so you’re ready when "
        "it’s time to apply:":
            "提前准备好几样东西，到要申请的时候就不会手忙脚乱：",
        "Once your application has been processed, the Department of "
        "Home Affairs will send an outcome to you in writing.":
            "申请审理完成后，Department of Home Affairs（澳大利亚内政部）会以书面形式把结果发给你。",
        "Pay the application charge for you and any family members.":
            "为你本人及随行家庭成员缴纳申请费。",
        "Students coming with family\n \nFind out what you need to "
        "consider (such as living expenses and cultural adjustment) "
        "before deciding to bring your family to Australia.":
            "携家庭成员同行的学生\n \n在决定把家人带来澳大利亚之前，先了解需要考虑哪些事情（例如生活开销和文化适应）。",
        "The independent Administrative Appeals Tribunal (AAT) is "
        "responsible for reviewing Home Affairs decisions, including "
        "visa cancellation decisions.":
            "独立的 Administrative Appeals "
            "Tribunal（AAT，行政上诉裁判所）负责复核内政部的决定，包括取消签证的决定。",
        "This way family members can be assessed for visa entry at the "
        "same time as you. Among other things, they must take a "
        "medical examination and have health insurance. You’ll also "
        "need to provide evidence that you have enough money to "
        "support your dependents in Australia.":
            "这样家庭成员就可以和你同时接受签证入境审核。除其他事项外，他们必须接受体检并购买医疗保险。你还需要提供证明，说明自己有足够的资金在澳大利亚供养受抚养的家属。",
        "To keep things moving in the meantime, make sure you:":
            "在等待期间，为了不耽误进度，请务必：",
        "Visa conditions are set by the Australian Government. It's "
        "important to follow these conditions to avoid having your "
        "visa cancelled. Student visa conditions include:":
            "签证条件由澳大利亚政府设定。务必遵守这些条件，以免签证被取消。学生签证的条件包括：",
        "We understand that waiting for an outcome can be "
        "nerve-wracking. Most of the time, it takes the Department of "
        "Home Affairs up to eight weeks to process an application. "
        "However, it can take longer during peak periods. We recommend "
        "using the visa processing times guide to see how long your "
        "application should take.":
            "我们明白等结果的滋味不好受。多数情况下，Department of Home "
            "Affairs（澳大利亚内政部）审理一份申请最长需要八周，但在高峰期可能更久。建议用签证审理时长指南查看你的申请大概需要多长时间。",
        "When you apply for a student visa, you can include these "
        "family members:":
            "申请学生签证时，你可以把下列家庭成员一并列入：",
        "Working on a student visa\n \nAlthough you receive permission "
        "to work automatically with your student visa, make sure you "
        "understand the current rules for working on a student visa.":
            "持学生签证工作\n \n虽然学生签证会自动附带工作许可，但仍请你弄清目前持学生签证工作的具体规定。",
        "You can apply for a student visa online through the "
        "Department of Home Affairs. Here’s what you’ll need to do:":
            "你可以在 Department of Home Affairs（澳大利亚内政部）的网站上在线申请学生签证。具体要做的是：",
        "You can't enrol exclusively in distance education or online "
        "study (unless it's your final unit in your final semester).":
            "你不能只注册远程或线上课程（除非那是你最后一个学期的最后一门课）。",
        "You need to declare all family members on your application, "
        "even if they don’t plan to travel with you to Australia. This "
        "will allow them to apply to join you after you have started "
        "your course.":
            "申请时必须申报所有家庭成员，即便他们并不打算和你一起来澳大利亚。这样他们才能在你开学之后再申请来与你团聚。",
        "Your student visa will remain valid unless you’re no longer "
        "enrolled in a registered course. Your enrolment ends when you "
        "complete the course, even if this is earlier than the end "
        "date on your Confirmation of Enrolment (CoE).":
            "只要你仍注册在册于某个已登记的学位课程，学生签证就保持有效。学业在你完成学位课程时即告结束——即便这比入学确认书（CoE）上的结束日期更早。",
        "You’ll receive a confirmation email from the Department of "
        "Home Affairs, who’ll get to work assessing your application.":
            "你会收到 Department of Home Affairs（澳大利亚内政部）的确认邮件，之后他们就会开始审核你的申请。",
        "check your email regularly for updates and requests from the "
        "Department of Home Affairs":
            "经常查看邮箱，留意 Department of Home Affairs（澳大利亚内政部）的进展通知和补件要求",
        "log into your ImmiAccount and check if there are any new "
        "requirements (for example, you may be asked to have a health "
        "assessment)":
            "登录 ImmiAccount 账户，查看是否有新的要求（例如可能会要求你做健康检查）",
        "maintaining Overseas Student Health Cover (OSHC) for the "
        "duration of your visa":
            "在整个签证有效期内持续持有留学生医疗保险（OSHC）",
        "maintaining your enrolment, satisfactory attendance (if "
        "applicable) and course progress for each study period":
            "保持选课注册有效、出勤达标（如适用），并在每个学习期保持学业进度合格",
        "not working more than the allowable hours per two-week period.":
            "每两周的工作时长不超过允许的上限。",
        "update the Department of Home Affairs if your details or "
        "situation changes.":
            "个人信息或情况发生变化时，及时向 Department of Home Affairs（澳大利亚内政部）更新。",
        "your or your partner’s dependent child if they’re unmarried "
        "and under 18 (otherwise, they’ll need to apply for their own "
        "visa).":
            "你或你伴侣所抚养的、未婚且未满 18 周岁的子女（否则他们需要自行申请签证）。",
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
        "Carer responsibilities View":
            "照护责任 查看",
        "DSS-registered condition View":
            "已在 DSS 登记的状况 查看",
        "Deferred assessment documents":
            "申请延期考核所需的材料",
        "Extension or deferred assessment documents":
            "申请延期或延期考核所需的材料",
        "Family (relationship breakdown)":
            "家庭（关系破裂）",
        "Family (relationship breakdown) View":
            "家庭（关系破裂） 查看",
        "Financial/employment issues View":
            "经济或就业问题 查看",
        "Gender-based violence View":
            "性别暴力 查看",
        "How to provide your documents":
            "如何提交你的材料",
        "If you give false information":
            "提供虚假信息的后果",
        "Loss or bereavement View":
            "亲人离世与哀伤 查看",
        "Medical condition View":
            "健康问题 查看",
        "Mental health condition View":
            "心理健康问题 查看",
        "Other exceptional circumstances View":
            "其他特殊情况 查看",
        "Other extreme circumstances View":
            "其他极端情况 查看",
        "Religious or cultural obligations View":
            "宗教或文化义务 查看",
        "Rescheduled deferred assessment documents":
            "申请改期延期考核所需的材料",
        "Scheduled assessments":
            "已排定的考核",
        "Severe mental health condition View":
            "严重心理健康问题 查看",
        "Students enrolled at Australian campuses":
            "在澳大利亚校区注册的学生",
        "Students enrolled at international campuses":
            "在海外校区注册的学生",
        "Supporting documents for special consideration":
            "特殊考虑（special consideration）所需的证明材料",
        "Technical disruption View":
            "技术故障 查看",
        "This may include:":
            "这可能包括：",
        "Unacceptable statement":
            "不可接受的写法",
        "Unscheduled assessments":
            "非排定的考核",
        "Why it's unacceptable":
            "为什么不可接受",
        "Why it’s unacceptable":
            "为什么不可接受",
        "a deferred assessment":
            "延期考核",
        "a rescheduled deferred assessment.":
            "改期后的延期考核。",
        "any medical condition requiring hospitalisation":
            "任何需要住院的健康问题",
        "recent discharge from hospital.":
            "近期刚出院。",
        "scheduled medical procedures":
            "已排定的医疗操作或手术",
        "A medical letter of support from a doctor (or other "
        "appropriate health professional) stating how your "
        "circumstances have affected your studies and your ability to "
        "complete your assessment on its set date. They don’t need to "
        "give details about your circumstances, but they must say when "
        "you’ve been affected by this and for how long.The letter must "
        "be on the medical surgery/health professional’s letterhead, "
        "signed and dated.":
            "由医生（或其他合适的医疗专业人员）出具的 medical letter of "
            "support（医疗情况说明信），说明你的处境如何影响了你的学习、以及你在规定日期完成考核的能力。他们不需要写出你处境的具体细节，但必须写明你从何时起受到影响、持续了多久。信件必须使用医疗机构或该专业人员的信笺抬头，并有签名和日期。",
        "Additionally, you need to provide a record confirming the "
        "problem (e.g. a call log to the Service Desk), along with "
        "screenshots. If you don’t have this documentation, you can "
        "instead send us a statutory declaration (or equivalent).":
            "此外，你还需要提交能证实该故障的记录（例如向 Service "
            "Desk（服务台）致电的通话记录）以及截图。如果你没有这类材料，可以改为提交一份 statutory "
            "declaration（法定声明，或同等效力的文件）。",
        "After you submit your application, we’ll send you an email "
        "with instructions on how to provide your supporting documents "
        "once you have them.":
            "提交申请后，我们会发一封邮件给你，说明拿到材料后该如何补交。",
        "Disruption caused by international conflict View":
            "国际冲突造成的影响",
        "If the conflict has affected your wellbeing or your ability "
        "to study, a certificate or letter from a doctor or counsellor "
        "can help certify that you are currently unfit for study.The "
        "doctor provides the certificate right after a consultation. "
        "The certificate must be on the medical centre/practitioner’s "
        "letterhead, signed, stamped and dated. (If the certificate "
        "has been backdated, the doctor must explain why.)In "
        "Australia, some pharmacists may also provide a medical "
        "certificate.\n\nAcceptable medical documentation\n\n\nAcceptable "
        "documentation must be from an in-person consultation (or "
        "video/phone consultation if attending in-person was "
        "impractical) for the following special consideration "
        "applications:Medical documentation from online medical "
        "providers, without a video/phone consultation, is normally "
        "not accepted. It may be considered when all of the following "
        "apply:You’ll be asked to outline the exceptional "
        "circumstances that prevented you from having a video/phone "
        "consultation to obtain your documentation for your special "
        "consideration application.":
            "如果这场冲突影响了你的身心状态或学习能力，医生或心理咨询师出具的证明或信函可以证实你目前不适宜学习。证明由医生在就诊后随即开具，必须使用医疗机构或执业人员的信笺抬头，并有签名、盖章和日期。（若证明日期被倒填，医生必须解释原因。）在澳大利亚，部分药剂师也可以开具 "
            "medical certificate（医疗证明）。\n\n可接受的医疗材料\n\n以下几类特殊考虑（special "
            "consideration）申请，材料必须来自当面就诊（若当面就诊确实不可行，视频或电话问诊亦可）：来自线上医疗机构、且没有经过视频或电话问诊的医疗材料，通常不予接受；只有在下列条件全部满足时才可能被考虑：届时我们会请你说明，是什么样的特殊情况使你无法通过视频或电话问诊取得材料。",
        "If the conflict has caused forced relocation or travel "
        "disruptions, you can provide independent records such as "
        "cancelled flight itineraries, evacuation notices, or border "
        "crossing documentation.":
            "如果这场冲突导致你被迫迁移或行程受阻，你可以提交独立的记录，例如已取消的航班行程单、撤离通知，或过境证明文件。",
        "If you don’t have your supporting documents ready":
            "如果你的证明材料还没准备好",
        "If you were not able to attend the deferred assessment "
        "because of circumstances that are not directly related to "
        "your condition registered with DSS, you’ll need to apply "
        "under another relevant category and provide the required "
        "supporting documentation.":
            "如果你未能参加延期考核的原因与你在 DSS "
            "登记的状况没有直接关系，你需要按其他相应类别提出申请，并提交该类别要求的证明材料。",
        "If your application relates to the same circumstances for "
        "which you were given approval for a deferral, you’ll need to "
        "instead provide updated supporting documents showing that "
        "your circumstances are ongoing and unresolved.":
            "如果你这次申请依据的仍是当初获批延期时的同一情况，则需要改为提交更新后的证明材料，以显示该情况仍在持续、尚未解决。",
        "If you’re not engaged with SCU and we need more details, we "
        "may require you to provide a statutory declaration (or "
        "equivalent) in addition to one of the other documents.":
            "如果你并未与 SCU（校园安全支持中心）接触，而我们需要更多细节，可能会要求你在上述材料之外，再补交一份 "
            "statutory declaration（法定声明，或同等效力的文件）。",
        "If you’re unable to provide supporting documents by the "
        "application deadline due to circumstances beyond your control:":
            "如果你因无法控制的原因，不能在申请截止前提交证明材料：",
        "If you’ve been approved for a deferred scheduled final "
        "assessment, but now need to reschedule it due to new extreme "
        "circumstances, you’ll need to provide one or more of the "
        "supporting documents below as evidence.":
            "如果你已获批延期参加已排定的期末考核，但现在因为新出现的极端情况需要再次改期，需要提交下列证明材料中的一项或多项作为证据。",
        "If you’ve experienced exceptional circumstances not covered "
        "elsewhere, a natural disaster, or a serious accident, you "
        "need to provide sufficient evidence explaining them and how "
        "they’ve affected your studies and your ability to complete "
        "your assessment on or before its set date. The evidence must "
        "also state the duration of this impact. And it needs to "
        "include some form of independent, verifiable documentation. "
        "We may contact you to provide additional information.":
            "如果你遇到的是上述各类之外的特殊情况、自然灾害或严重事故，你需要提交充分的证据，说明这些情况本身、以及它们如何影响了你的学习和你在规定日期或之前完成考核的能力，并写明影响持续了多久。证据中还需要包含某种形式的、可独立核实的书面材料。我们可能会联系你补充更多信息。",
        "If you’ve experienced extreme circumstances not covered "
        "elsewhere, a natural disaster, or a serious accident, you "
        "need to provide sufficient evidence explaining them and how "
        "they’ve affected your studies and your ability to complete "
        "your assessment on its set date. The evidence must also state "
        "the duration of this impact. And it needs to include some "
        "form of independent, verifiable documentation. We may contact "
        "you to provide additional information.":
            "如果你遇到的是上述各类之外的极端情况、自然灾害或严重事故，你需要提交充分的证据，说明这些情况本身、以及它们如何影响了你的学习和你在规定日期完成考核的能力，并写明影响持续了多久。证据中还需要包含某种形式的、可独立核实的书面材料。我们可能会联系你补充更多信息。",
        "In the event of a major known University technical "
        "disruption, we’ll let you know what to do.":
            "如果发生学校层面已知的重大技术故障，我们会另行通知你该怎么做。",
        "Indicate the reason why your application is incomplete.":
            "说明你的申请为何不完整。",
        "Screenshots of your technical problem must include timestamps "
        "confirming that it took place during your assessment. For "
        "example, you might provide a time-stamped screenshot of an "
        "error message, a window not loading or an internet speed "
        "test. Or you might provide dated communication from an "
        "electricity provider about the outage or other problem you "
        "experienced.":
            "技术故障的截图必须带有时间戳，证明故障发生在你的考核期间。例如，你可以提交带时间戳的报错信息截图、页面加载不出来的截图，或网速测试截图；也可以提交电力公司就此次停电或其他故障发出的、带日期的通知。",
        "Serious and debilitating medical condition View":
            "严重且使人失能的健康问题",
        "State the date by which you will provide the supporting "
        "documentation.":
            "写明你将在哪一天之前补交证明材料。",
        "Submit your application without supporting documents by the "
        "deadline.":
            "先在截止日期前提交申请，暂不附证明材料。",
        "Take a look at the following resources to see if the "
        "information is relevant to your circumstances:":
            "看看下列资源里的信息是否适用于你的情况：",
        "The impact on your studies: How these circumstances prevented "
        "you from completing your assessment on time.":
            "对学习的影响：这些处境如何使你无法按时完成考核。",
        "The letter from the Monash Safer Community Unit must confirm "
        "that circumstances beyond your control occurred, the "
        "timeframe of the circumstances and the impact to your "
        "assessment due dates.":
            "Monash Safer Community "
            "Unit（校园安全支持中心）出具的信函必须确认：确实发生了你无法控制的处境、该处境的时间范围，以及它对你考核截止日期造成的影响。",
        "The letter must be on the medical surgery/health "
        "professional’s letterhead, signed and dated.":
            "信件必须使用医疗机构或该专业人员的信笺抬头，并有签名和日期。",
        "The nature of the conflict: Briefly describe the situation "
        "and how it relates to you personally.":
            "冲突的性质：简要描述当时的情况，以及它与你个人有何关联。",
        "The police will determine the content of this report. If it "
        "doesn’t give enough detail to indicate how your circumstances "
        "have prevented you from completing your assessment on the set "
        "date, we may require you to supplement it with other "
        "documents.":
            "报案记录的内容由警方决定。如果其中的细节不足以说明你的处境如何使你不能在规定日期完成考核，我们可能会要求你再补充其他材料。",
        "The timeline: The specific dates you were affected and how "
        "long you expect the disruption to last.":
            "时间线：你受影响的具体日期，以及你预计这一影响还会持续多久。",
        "This includes documentation from government bodies (such as "
        "the Department of Foreign Affairs), embassies, or recognised "
        "international aid organisations regarding the conflict's "
        "impact on your location or family.":
            "这包括政府部门（例如外交部）、使领馆或获认可的国际援助组织出具的材料，说明该冲突对你所在地区或你家人造成的影响。",
        "This includes serious and debilitating medical conditions "
        "such as neurodegenerative disorders, cardiovascular disease, "
        "organ dysfunction and certain types of cancer.":
            "这一类包括严重且使人失能的健康问题，例如神经退行性疾病、心血管疾病、器官功能障碍和某些类型的癌症。",
        "This includes severe mental health conditions such as bipolar "
        "disorder, major depressive disorder, schizophrenia and "
        "post-traumatic stress disorder (PTSD).":
            "这一类包括严重的心理健康问题，例如双相情感障碍、重性抑郁障碍、精神分裂症，以及创伤后应激障碍（PTSD）。",
        "This record must show that you contacted Exam Support or the "
        "Service Desk during your scheduled assessment to report a "
        "technical problem.":
            "这份记录必须能显示：你在已排定的考核进行期间联系过 Exam Support（考试支持）或 Service "
            "Desk（服务台）报告技术故障。",
        "This refers only to the death of a close family member or "
        "person with whom you had a significant relationship. Due to "
        "their death, you’re now experiencing extreme loss or "
        "bereavement. For example, your grief is so great that you "
        "find it difficult to carry out normal routines.":
            "这一类仅指与你关系密切的家人、或与你有重要关系的人过世，你因此正经历极度的失去与哀伤——例如悲痛之深，已使你难以维持日常生活。",
        "To keep your application valid, make sure you provide your "
        "documents by the date specified in your application. If we "
        "don't receive them or hear from you by then, your application "
        "may be withdrawn without any further notice.":
            "为使申请保持有效，请务必在你申请中写明的日期之前提交材料。如果到期我们既没收到材料、也没收到你的消息，你的申请可能会被直接撤销，不再另行通知。",
        "We can’t accept a statutory declaration in support of a "
        "medical condition. Nor can we accept a laboratory test "
        "result, hospital identification wristband, vaccination card, "
        "photograph or medical image (e.g. X-ray, CT and MRI).":
            "用于证明健康状况时，我们不能接受 statutory "
            "declaration（法定声明），也不能接受化验结果、住院手环、疫苗接种卡、照片或医学影像（如 X 光、CT、MRI）。",
        "We can’t accept a statutory declaration in support of a "
        "severe mental health condition. Nor can we accept a hospital "
        "identification wristband.":
            "用于证明严重心理健康问题时，我们不能接受 statutory declaration（法定声明），也不能接受住院手环。",
        "We understand that global conflicts, wars, and international "
        "disputes may impact members of our community in different "
        "ways and that the impacts of international conflict can be "
        "unpredictable and may fluctuate.":
            "我们理解，全球冲突、战争和国际争端会以不同方式影响我们社群中的成员，而国际冲突带来的影响往往难以预料，也可能时轻时重。",
        "We understand that global conflicts, wars, and international "
        "disputes may impact members of our community in different "
        "ways. If these events are affecting your wellbeing or your "
        "ability to study, we’re here to support you.":
            "我们理解，全球冲突、战争和国际争端会以不同方式影响我们社群中的成员。如果这些事件正在影响你的身心状态或学习能力，我们会为你提供支持。",
        "We understand that obtaining official documentation during a "
        "crisis can be challenging. If you have supporting "
        "documentation, please provide this with your application. "
        "Otherwise, we’ll assess your application based on the details "
        "in your impact statement.":
            "我们理解，在危机之中要取得官方材料并不容易。如果你手上有证明材料，请随申请一并提交；如果没有，我们会依据你影响说明（impact "
            "statement）中的内容来评估你的申请。",
        "We understand that obtaining official documentation during an "
        "international conflict can be challenging. If you have "
        "supporting documentation, please provide this with your "
        "application. If you don’t have any documentation available, "
        "please detail your circumstances as much as possible in the "
        "impact statement and the Special Consideration team will "
        "contact you if further documentation is needed.":
            "我们理解，在国际冲突之中要取得官方材料并不容易。如果你手上有证明材料，请随申请一并提交；如果一份材料也拿不到，请在影响说明（impact "
            "statement）里尽可能详细地写明你的处境，如需补充材料，特殊考虑（special "
            "consideration）团队会与你联系。",
        "You can provide the following supporting documentation to "
        "support your application (if available).":
            "如果手上有，你可以提交下列证明材料来支持你的申请。",
        "You may be eligible for a Rescheduled Deferred Assessment if "
        "the timing of the international conflict is around the same "
        "as your deferred assessment or if you continue to be impacted "
        "by an earlier conflict.":
            "如果国际冲突发生的时间与你的延期考核大致重合，或者你至今仍受早先某场冲突的影响，你可能符合申请改期延期考核（Rescheduled "
            "Deferred Assessment）的条件。",
        "You may be eligible for an extension or special consideration "
        "if a conflict has directly disrupted your studies. This may "
        "include direct impacts on you or your family’s safety and "
        "your wellness, accessibility to learning resources or your "
        "capacity to engage with your academic responsibilities. Your "
        "safety and wellbeing are our top priority. Our focus is to "
        "understand how these events personally affect you rather than "
        "your physical location or residency.":
            "如果某场冲突直接扰乱了你的学习，你可能符合申请延期或特殊考虑（special "
            "consideration）的条件。这可能包括：对你或你家人的人身安全和健康状况的直接影响、你获取学习资源的困难，或你投入学业的能力受到削弱。你的安全与身心健康是我们最优先考虑的事。我们关心的是这些事件对你个人造成了什么影响，而不是你身在何处、居住在哪里。",
        "You may provide a letter of support from a recognised leader "
        "who can verify your relationship to the situation and explain "
        "how it prevents you from completing your academic work.":
            "你可以提交一封由公认领袖出具的 letter of "
            "support（情况说明信），由其证实你与该处境的关联，并说明它如何使你无法完成学业任务。",
        "You may wish to supplement the medical letter of support with "
        "a record of hospital admission.":
            "你也可以在 medical letter of support（医疗情况说明信）之外，附上住院记录作为补充。",
        "You need to provide a medical letter of support from a doctor "
        "(or other appropriate health professional) explaining how "
        "your condition has affected your studies and your ability to "
        "complete your assessment on its set date. The letter must "
        "also state the duration of this impact. The person writing "
        "this letter must have knowledge of your medical history and "
        "condition.":
            "你需要提交一份由医生（或其他合适的医疗专业人员）出具的 medical letter of "
            "support（医疗情况说明信），说明你的病情如何影响了你的学习、以及你在规定日期完成考核的能力，信中还必须写明这一影响持续了多久。写这封信的人必须了解你的病史和病情。",
        "You’ll be asked to complete a brief impact statement as part "
        "of your application. This will help us understand your "
        "circumstances and how they have affected your ability to "
        "complete assessments. Your statement should explain:":
            "作为申请的一部分，我们会请你填写一份简短的影响说明（impact "
            "statement），帮助我们了解你的处境、以及它如何影响了你完成考核的能力。说明中应当写清：",
        "You’ll be asked to complete an impact statement as part of "
        "your application. This will help us understand your "
        "circumstances and how they have affected your ability to "
        "complete assessments. Your statement should explain:":
            "作为申请的一部分，我们会请你填写一份影响说明（impact "
            "statement），帮助我们了解你的处境、以及它如何影响了你完成考核的能力。说明中应当写清：",
        "major or continuous disruption to power and/or internet "
        "service provision":
            "电力和／或网络服务出现重大或持续中断",
        "major technical problem with computer hardware (e.g. screen "
        "or fan malfunction).":
            "电脑硬件出现重大技术故障（例如屏幕或风扇失灵）。",
        "the exceptional circumstances that prevented you from "
        "completing the deferred assessment were beyond your control "
        "and directly related to your condition registered with DSS, "
        "and":
            "使你无法完成延期考核的特殊情况是你无法控制的，且与你在 DSS 登记的状况直接相关；并且",
        "A letter of support from a community leader or organisation "
        "to verify the circumstances and impact on the ability of the "
        "student to complete the assessment as scheduled. The letter "
        "should outline the reasons student is concerned about their "
        "safety on campus and the impact of the circumstances on the "
        "student’s ability to complete their assessment.":
            "由社区领袖或社区组织出具的 letter of "
            "support（情况说明信），用于核实学生的处境、以及它对学生按时完成考核能力造成的影响。信中应当说明该学生为何对自己在校园中的安全有所担忧，以及这一处境如何影响了他完成考核的能力。",
        "Athlete, artist, performer or representative View":
            "运动员、艺术家、表演者或校队代表",
        "If a technical problem prevented you from completing your "
        "scheduled final assessment, you need to have reported it to "
        "Exam Support. If you experienced technical issues during an "
        "in-semester test, you need to have contacted your faculty "
        "support person.":
            "如果是技术故障使你无法完成已排定的期末考核，你必须当时就向 Exam "
            "Support（考试支持）报告过。如果是学期内测验期间出现技术问题，你必须当时就联系过所在学院的支持人员。",
        "If you’re a victim of crime or have concerns about your "
        "safety, you need to provide one of these supporting "
        "documents. (We can’t accept a Notice of Victim email.)":
            "如果你遭受了犯罪侵害，或对自身安全有所担忧，需要提交下列证明材料中的一种。（我们不能接受 Notice of Victim "
            "邮件。）",
        "If you’re not registered with the ESPS, you need to provide a "
        "letter from the faculty or other area of the University.":
            "如果你没有在 ESPS 登记，需要提交一封由学院或学校其他部门出具的信函。",
        "If you’re registered with the ESPS, there’s no need to "
        "provide a supporting document. We have access to a record of "
        "your registration and event details.":
            "如果你已在 ESPS 登记，不需要提交证明材料——我们可以直接查到你的登记记录和赛事信息。",
        "If you’ve suffered a sudden loss of income or employment, you "
        "need to provide one of these supporting documents.":
            "如果你的收入或工作突然中断，需要提交下列证明材料中的一种。",
        "In a letter, the Safer Community Unit (SCU) addresses a crime "
        "that has occurred. SCU can provide this letter if you’re a "
        "victim of a violent crime. They must state that circumstances "
        "beyond your control prevented you from completing your "
        "assessment on or before the set date. They don’t need to give "
        "details about the crime, but they must say when you’ve been "
        "affected by this and for how long.":
            "Safer Community "
            "Unit（SCU，校园安全支持中心）可以就已发生的犯罪事件出具信函。如果你是暴力犯罪的受害者，SCU "
            "可以为你出具这封信。信中必须写明：你无法控制的处境使你不能在规定日期或之前完成考核。他们不需要写出该犯罪事件的具体细节，但必须写明你从何时起受到影响、持续了多久。",
        "In a letter, your employer or former employer must provide "
        "enough detail to show how circumstances beyond your control "
        "have prevented you from completing your assessment on or "
        "before the set date.The letter should include employer "
        "contact details and ideally be on their letterhead. It should "
        "also be signed and dated.":
            "在这封信里，你的现任或前任雇主必须提供足够的细节，说明你无法控制的处境如何使你不能在规定日期或之前完成考核。信中应当载明雇主的联系方式，最好使用其信笺抬头，并有签名和日期。",
        "In a personal letter of support, a recognised cultural or "
        "faith leader briefly describes their relationship with you "
        "and explains how a religious or cultural obligation will "
        "prevent you from completing your assessment task.The letter "
        "should be on official letterhead, signed and dated.":
            "在这封个人 letter of "
            "support（情况说明信）里，由公认的文化或宗教领袖简要说明他与你的关系，并解释某项宗教或文化义务将如何使你无法完成考核任务。信函应当使用正式信笺抬头，并有签名和日期。",
        "In this certificate, a practitioner (e.g. financial adviser, "
        "lawyer or social worker) registered with a relevant "
        "professional body must state that circumstances beyond your "
        "control have prevented you from completing your assessment on "
        "or before the set date. They don’t need to give details about "
        "your financial issues, but they must say when you’ve been "
        "affected by this and for how long.The certificate should be "
        "on the practitioner’s letterhead, signed and dated.":
            "在这份证明里，由在相应专业机构注册的执业人员（例如财务顾问、律师或社会工作者）写明：你无法控制的处境使你不能在规定日期或之前完成考核。他们不需要写出你财务问题的具体细节，但必须写明你从何时起受到影响、持续了多久。证明应当使用执业人员的信笺抬头，并有签名和日期。",
        "Military, jury or emergency services obligations View":
            "兵役、陪审团或紧急救援服务义务",
        "Supporting documents should be on official letterhead, signed "
        "and dated.":
            "证明材料应当使用正式信笺抬头，并有签名和日期。",
        "The circumstances must be beyond your control and include a:":
            "这些情况必须是你无法控制的，包括：",
        "The police will determine the content of this report. (This "
        "is the preferred supporting document if you’ve been a victim "
        "of crime.) If it doesn’t give enough detail to indicate how "
        "your circumstances have prevented you from completing your "
        "assessment on or before the set date, you’ll need to provide "
        "this information in an impact statement (on your application "
        "form).In some cases, you may need to provide a statutory "
        "declaration (or equivalent) explaining in more detail the "
        "impact of the crime on your studies.":
            "报案记录的内容由警方决定。（如果你遭受了犯罪侵害，这是我们首选的证明材料。）如果其中的细节不足以说明你的处境如何使你不能在规定日期或之前完成考核，你需要在申请表的影响说明（impact "
            "statement）里补充这些信息。在某些情况下，你可能还需要提交一份 statutory "
            "declaration（法定声明，或同等效力的文件），更详细地说明该犯罪事件对你学习造成的影响。",
        "This includes athletes, artists and performers registered "
        "with the Elite Student Performer Scheme (ESPS). It also "
        "includes students representing the University in key events "
        "and programs, such as debating, who are not registered with "
        "the ESPS.":
            "这一类包括已在 Elite Student Performer "
            "Scheme（ESPS，精英学生表现者计划）登记的运动员、艺术家和表演者，也包括虽未在 ESPS "
            "登记、但代表学校参加辩论等重要赛事和项目的学生。",
        "This includes obligations to defence services, Juries "
        "Commissioner’s Office and emergency services such as the "
        "Country Fire Authority. It can also include other civic "
        "obligations required by law in other countries.":
            "这一类包括对国防部门、Juries Commissioner's Office（陪审团事务专员办公室）以及 Country "
            "Fire Authority（乡村消防局）等紧急救援机构所负的义务，也可以包括其他国家法律所要求的公民义务。",
        "This letter must state that you’re participating in a "
        "required event and include the dates and nature of your "
        "obligation. It should be on official letterhead, signed and "
        "dated.":
            "信中必须写明你正在参加规定的赛事或活动，并载明你所负义务的日期和性质。信函应当使用正式信笺抬头，并有签名和日期。",
        "This letter must state the dates and nature of your "
        "obligation and how this has affected your ability to complete "
        "your assessment on or before its set date. It should be on "
        "official letterhead, signed and dated.":
            "信中必须写明你所负义务的日期和性质，以及它如何影响了你在规定日期或之前完成考核的能力。信函应当使用正式信笺抬头，并有签名和日期。",
        "This letter must state the dates and nature of your "
        "obligation and how this has affected your studies and your "
        "ability to complete your assessment on its set date. It "
        "should be on official letterhead, signed and dated.":
            "信中必须写明你所负义务的日期和性质，以及它如何影响了你在规定日期或之前完成考核的能力。信函应当使用正式信笺抬头，并有签名和日期。",
        "Unscheduled assessments (such as assignments, quizzes, "
        "take-home assessments over a long duration of time, or "
        "asynchronous online tasks) can generally be completed anytime "
        "before the due date once they open, giving you flexibility to "
        "plan ahead. If the due date of one of these falls on a day of "
        "significant religious or cultural observance, we recommend "
        "you complete and submit your assessment before the due date "
        "so you can focus fully on the observance when the day "
        "arrives. Extensions for an unscheduled assessment due date "
        "may only be considered when exceptional circumstances, "
        "supported by evidence, have prevented you from completing "
        "your work by the due date as planned.":
            "非排定考核（例如作业、小测、时间跨度较长的带回家考核，或异步的线上任务）一般在开放之后、截止日期之前的任何时间都可以完成，你有余地提前安排。如果其中某项的截止日恰好落在重要的宗教或文化仪节当天，我们建议你提前完成并提交，好在那天专心履行仪节。非排定考核的截止日期延期，只有在你能提供证据、证明确有特殊情况使你无法按原计划在截止日前完成时，才可能被考虑。",
        "We recognise that religious and cultural observance is an "
        "important part of many students’ lives. In line with the "
        "University’s commitment to promoting an inclusive community, "
        "we want you to feel supported to honour your faith and "
        "cultural tradition while studying at Monash. This includes "
        "religious observance and ceremonial duties. If your religious "
        "or cultural obligation conflicts with your academic "
        "commitments, we’re here to support you.":
            "我们理解，宗教与文化上的仪节是许多学生生活中重要的一部分。秉持学校建设包容社群的承诺，我们希望你在 Monash "
            "学习期间，能够安心地遵行自己的信仰与文化传统，这也包括宗教礼拜和仪式职责。如果你的宗教或文化义务与学业安排发生冲突，我们会为你提供支持。",
        "You can use a statutory declaration (or equivalent) and "
        "provide information about the impact of your circumstances on "
        "your studies.":
            "你可以使用 statutory declaration（法定声明，或同等效力的文件），在其中说明你的处境对学习造成的影响。",
        "You may apply for special consideration where the date and "
        "time of a scheduled assessment conflicts with a significant "
        "religious or cultural obligation (e.g. timed in-class tests, "
        "mid‐semester tests, practical/lab assessments, or "
        "presentations). We understand that these assessment dates are "
        "normally fixed, and we want to ensure that you’re not "
        "disadvantaged because of your faith.":
            "如果已排定考核的日期和时间与重要的宗教或文化义务相冲突（例如限时的课堂测验、期中测验、实践或实验考核、口头报告等），你可以申请特殊考虑（special "
            "consideration）。我们明白这些考核日期通常是固定的，也希望你不会因为自己的信仰而处于不利地位。",
        "You need to provide a letter from the appropriate authority "
        "(e.g. Army Reserve, Juries Commissioner’s Office or Country "
        "Fire Authority).":
            "你需要提交一封由相应主管机构出具的信函（例如 Army Reserve（预备役部队）、Juries "
            "Commissioner's Office（陪审团事务专员办公室）或 Country Fire "
            "Authority（乡村消防局））。",
        "You need to provide a personal letter of support from a "
        "recognised cultural or faith leader.":
            "你需要提交一封由公认的文化或宗教领袖出具的个人 letter of support（情况说明信）。",
        "someone in your family (or someone you care for) has "
        "developed a serious illness.":
            "你的家人（或受你照护的人）罹患重病。",
        "you have concerns about your safety that are affecting your "
        "ability to complete an assessment":
            "你对自身安全的担忧正在影响你完成考核的能力",
        "you’re traumatised by a crime that occurred in the past":
            "你因过去发生的某起犯罪事件而留有心理创伤",
        "you’ve been the victim of a crime":
            "你遭受了犯罪侵害",
        "you’ve had sudden loss of income or employment":
            "你的收入或工作突然中断",
        "A death notice or certificate must state the full name of the "
        "deceased and their date of death.":
            "讣告或死亡证明必须写明逝者的完整姓名和去世日期。",
        "A letter of support from a current or former employer which "
        "verifies your circumstances and the impact on your ability to "
        "complete your assessment as scheduled.":
            "由现任或前任雇主出具的 letter of "
            "support（情况说明信），用于核实你的处境、以及它对你按时完成考核的能力造成的影响。",
        "A medical letter of support from a doctor (or other "
        "appropriate health professional) describes your emotional "
        "state and how it has affected your studies and your ability "
        "to complete your assessment on its set date. It must also "
        "state the duration of this impact.The letter must be on the "
        "medical surgery/health professional’s letterhead, signed and "
        "dated.":
            "由医生（或其他合适的医疗专业人员）出具的 medical letter of "
            "support（医疗情况说明信），用于说明你的情绪状态，以及它如何影响了你的学习和你在规定日期或之前完成考核的能力；信中还必须写明你从何时起受到影响、持续了多久。信件必须使用医疗机构或该专业人员的信笺抬头，并有签名和日期。",
        "A medical letter of support from a doctor (or other "
        "appropriate health professional) describes your emotional "
        "state and how it has affected your studies and your ability "
        "to complete your assessment on or before the set date. It "
        "must also say when you’ve been affected by it and for how "
        "long.The letter must be on the medical surgery/health "
        "professional’s letterhead, signed and dated.":
            "由医生（或其他合适的医疗专业人员）出具的 medical letter of "
            "support（医疗情况说明信），用于说明你的情绪状态，以及它如何影响了你的学习和你在规定日期或之前完成考核的能力；信中还必须写明你从何时起受到影响、持续了多久。信件必须使用医疗机构或该专业人员的信笺抬头，并有签名和日期。",
        "A medical letter of support from a doctor (or other "
        "appropriate health professional) describing how your studies "
        "and your ability to complete your assessment on or before the "
        "set date have been affected. It must also say when you’ve "
        "been affected and for how long.The letter must be on the "
        "medical surgery/health professional’s letterhead, signed and "
        "dated.":
            "由医生（或其他合适的医疗专业人员）出具的 medical letter of "
            "support（医疗情况说明信），说明你的学习、以及你在规定日期或之前完成考核的能力受到了怎样的影响；信中还必须写明你从何时起受到影响、持续了多久。信件必须使用医疗机构或该专业人员的信笺抬头，并有签名和日期。",
        "A practitioner certificate may supplement your other "
        "supporting documents. In this certificate, a practitioner "
        "(e.g. medical practitioner, psychologist, counsellor, social "
        "worker or lawyer) registered with a relevant professional "
        "body must state how the death has affected your studies and "
        "your ability to complete your assessments on its set date. It "
        "must also state the duration of this impact and explain the "
        "significance of your relationship to the deceased person.The "
        "certificate must be on the practitioner’s letterhead, signed "
        "and dated.":
            "practitioner "
            "certificate（执业人员证明）可以作为其他证明材料的补充。在这份证明里，由在相应专业机构注册的执业人员（例如医生、心理学家、心理咨询师、社会工作者或律师）写明：你无法控制的处境使你不能在规定日期或之前完成考核。他们不需要写出你失去亲人或哀伤的具体细节，但必须写明你从何时起受到影响、持续了多久，并说明你与逝者之间关系的紧密程度。证明必须使用执业人员的信笺抬头，并有签名和日期。",
        "A practitioner certificate may supplement your other "
        "supporting documents. In this certificate, a practitioner "
        "(e.g. medical practitioner, psychologist, counsellor, social "
        "worker or lawyer) registered with a relevant professional "
        "body must state that circumstances beyond your control have "
        "prevented you from completing your assessment on or before "
        "the set date. They don’t need to give details about your loss "
        "or bereavement, but they must say when you’ve been affected "
        "by it and for how long. They must also explain the "
        "significance of your relationship to the deceased person.The "
        "certificate must be on the practitioner’s letterhead, signed "
        "and dated.":
            "practitioner "
            "certificate（执业人员证明）可以作为其他证明材料的补充。在这份证明里，由在相应专业机构注册的执业人员（例如医生、心理学家、心理咨询师、社会工作者或律师）写明：你无法控制的处境使你不能在规定日期或之前完成考核。他们不需要写出你失去亲人或哀伤的具体细节，但必须写明你从何时起受到影响、持续了多久，并说明你与逝者之间关系的紧密程度。证明必须使用执业人员的信笺抬头，并有签名和日期。",
        "A statutory declaration is a written statement that you (the "
        "declarant) sign and declare to be true and correct in the "
        "presence of an authorised witness. In the statutory "
        "declaration, you should declare and explain your specific "
        "circumstances and how they have affected your studies and "
        "your ability to complete your assessment on or before its set "
        "date. You must also state when you’ve been affected, and for "
        "how long.A statutory declaration (or equivalent) must be "
        "signed and declared to be true and correct in the presence of "
        "an authorised witness. By signing it, you agree that the "
        "information in it is true. You can be charged with a criminal "
        "offence if the information is false.To find out more about "
        "statutory declaration, including step-by-step instructions "
        "for obtaining a statutory declaration and details about who "
        "is authorised to witness it, visit the Victoria State "
        "Government web page.":
            "statutory "
            "declaration（法定声明）是一份由你（声明人）在获授权的见证人面前签署、并声明其内容真实无误的书面陈述。在这份声明里，你应当陈述并说明自己具体的处境，以及这些处境如何影响了你的学习、和你在规定日期或之前完成考核的能力；你还必须写明自己从何时起受到影响、持续了多久。statutory "
            "declaration（法定声明，或同等效力的文件）必须在获授权的见证人面前签署，并声明内容真实无误。签署即表示你认可其中信息属实；若信息不实，你可能被追究刑事责任。想进一步了解 "
            "statutory "
            "declaration（法定声明）——包括办理的分步说明、以及哪些人有资格担任见证人——请访问维多利亚州政府网页。",
        "A statutory declaration is a written statement that you (the "
        "declarant) sign and declare to be true and correct in the "
        "presence of an authorised witness. In the statutory "
        "declaration, you should declare and explain your specific "
        "circumstances and how they have affected your studies and "
        "your ability to complete your assessment on or before its set "
        "date. You must also state when you’ve been affected, and for "
        "how long.A statutory declaration (or equivalent) must be "
        "signed and declared to be true and correct in the presence of "
        "an authorised witness. By signing it, you agree that the "
        "information in it is true. You can be charged with a criminal "
        "offence if the information is false.To find out more about "
        "statutory declarations, including step-by-step instructions "
        "for obtaining a statutory declaration and details about who "
        "is authorised to witness it, visit the Victoria State "
        "Government web page.":
            "statutory "
            "declaration（法定声明）是一份由你（声明人）在获授权的见证人面前签署、并声明其内容真实无误的书面陈述。在这份声明里，你应当陈述并说明自己具体的处境，以及这些处境如何影响了你的学习、和你在规定日期或之前完成考核的能力；你还必须写明自己从何时起受到影响、持续了多久。statutory "
            "declaration（法定声明，或同等效力的文件）必须在获授权的见证人面前签署，并声明内容真实无误。签署即表示你认可其中信息属实；若信息不实，你可能被追究刑事责任。想进一步了解 "
            "statutory "
            "declaration（法定声明）——包括办理的分步说明、以及哪些人有资格担任见证人——请访问维多利亚州政府网页。",
        "A statutory declaration is a written statement that you (the "
        "declarant) sign and declare to be true and correct in the "
        "presence of an authorised witness. In the statutory "
        "declaration, you should declare and explain your specific "
        "circumstances and how they have affected your studies and "
        "your ability to complete your assessment on or before its set "
        "date. You must state when you’ve been affected and for how "
        "long, and explain the significance of your relationship to "
        "the deceased person.A statutory declaration (or equivalent) "
        "must be signed and declared to be true and correct in the "
        "presence of an authorised witness. By signing it, you agree "
        "that the information in it is true. You can be charged with a "
        "criminal offence if the information is false.To find out more "
        "about statutory declaration, including step-by-step "
        "instructions for obtaining a statutory declaration and "
        "details about who is authorised to witness it, visit the "
        "Victoria State Government web page.":
            "statutory "
            "declaration（法定声明）是一份由你（声明人）在获授权的见证人面前签署、并声明其内容真实无误的书面陈述。在这份声明里，你应当陈述并说明自己具体的处境，以及这些处境如何影响了你的学习、和你在规定日期或之前完成考核的能力；你还必须写明自己从何时起受到影响、持续了多久。你还需要说明你与逝者之间关系的紧密程度。statutory "
            "declaration（法定声明，或同等效力的文件）必须在获授权的见证人面前签署，并声明内容真实无误。签署即表示你认可其中信息属实；若信息不实，你可能被追究刑事责任。想进一步了解 "
            "statutory "
            "declaration（法定声明）——包括办理的分步说明、以及哪些人有资格担任见证人——请访问维多利亚州政府网页。",
        "Hardship, trauma, victim of crime or concerns about safety":
            "生活困境、心理创伤、遭受犯罪侵害，或对人身安全的担忧",
        "Hardship, trauma, victim of crime or concerns about safety "
        "View":
            "生活困境、心理创伤、遭受犯罪侵害，或对人身安全的担忧",
        "In this certificate or letter, a practitioner (e.g. social "
        "worker or lawyer) registered with a relevant professional "
        "body must state that circumstances beyond your control have "
        "prevented you from completing your assessment on or before "
        "the set date. They don’t need to give details about your "
        "relationship breakdown, but they must say when you’ve been "
        "affected by this and for how long.":
            "在这份证明或信函里，由在相应专业机构注册的执业人员（例如社会工作者或律师）写明：你无法控制的处境使你不能在规定日期或之前完成考核。他们不需要写出你关系破裂的具体细节，但必须写明你从何时起受到影响、持续了多久。",
        "In this certificate, a practitioner (e.g. social worker, "
        "counsellor or lawyer) registered with a relevant professional "
        "body must state that circumstances beyond your control have "
        "prevented you from completing your assessment on or before "
        "the set date. They don’t need to give details about your "
        "circumstance, but they must say when you’ve been affected by "
        "this and for how long.The certificate must be on the "
        "practitioner’s letterhead, signed and dated.":
            "在这份证明里，由在相应专业机构注册的执业人员（例如社会工作者、心理咨询师或律师）写明：你无法控制的处境使你不能在规定日期或之前完成考核。他们不需要写出你处境的具体细节，但必须写明你从何时起受到影响、持续了多久。",
        "In this certificate, a practitioner (e.g. social worker, "
        "counsellor or lawyer) registered with a relevant professional "
        "body must state that circumstances beyond your control have "
        "prevented you from completing your assessment on or before "
        "the set date. They don’t need to give details about your "
        "circumstances, but they must say when you’ve been affected by "
        "this and for how long.":
            "在这份证明里，由在相应专业机构注册的执业人员（例如社会工作者、心理咨询师或律师）写明：你无法控制的处境使你不能在规定日期或之前完成考核。他们不需要写出你处境的具体细节，但必须写明你从何时起受到影响、持续了多久。",
        "In this certificate, a practitioner (e.g. social worker, "
        "counsellor or lawyer) registered with a relevant professional "
        "body must state that circumstances beyond your control have "
        "prevented you from completing your assessment on or before "
        "the set date. They don’t need to give details about your "
        "circumstances, but they must say when you’ve been affected by "
        "this and for how long.The certificate must be on the "
        "practitioner’s letterhead, signed and dated.":
            "在这份证明里，由在相应专业机构注册的执业人员（例如社会工作者、心理咨询师或律师）写明：你无法控制的处境使你不能在规定日期或之前完成考核。他们不需要写出你处境的具体细节，但必须写明你从何时起受到影响、持续了多久。",
        "In this certificate, a practitioner (e.g. social worker, "
        "counsellor or lawyer) registered with a relevant professional "
        "body must state that circumstances beyond your control have "
        "prevented you from completing your assessment on or before "
        "the set date. They don’t need to give details about your "
        "trauma, but they must say when you’ve been affected by this "
        "and for how long.":
            "在这份证明里，由在相应专业机构注册的执业人员（例如社会工作者、心理咨询师或律师）写明：你无法控制的处境使你不能在规定日期或之前完成考核。他们不需要写出你处境的具体细节，但必须写明你从何时起受到影响、持续了多久。",
        "In this letter, a district nurse or maternal and child health "
        "nurse must state that circumstances beyond your control (e.g. "
        "postnatal depression) have prevented you from completing your "
        "assessment on or before the set date. They don’t need to give "
        "details about your family situation, but they must say when "
        "you’ve been affected by this and for how long.":
            "在这份信函里，由社区护士或母婴健康护士写明：你无法控制的处境（例如产后抑郁）使你不能在规定日期或之前完成考核。他们不需要写出你家庭状况的具体细节，但必须写明你从何时起受到影响、持续了多久。",
        "In this letter, a family violence support service must state "
        "that circumstances beyond your control have prevented you "
        "from completing your assessment on or before the set date. "
        "They don’t need to give details about the family violence, "
        "but they must say when you’ve been affected by this and for "
        "how long.":
            "在这份信函里，由家庭暴力支持服务机构写明：你无法控制的处境使你不能在规定日期或之前完成考核。他们不需要写出家庭暴力的具体细节，但必须写明你从何时起受到影响、持续了多久。",
        "Make sure you provide the supporting document that best fits "
        "your circumstances. Supporting documents should be on "
        "official letterhead, signed and dated.":
            "请提交最贴合你自身处境的那一种证明材料。证明材料应当使用正式信笺抬头，并有签名和日期。",
        "The court will determine the content of the letter or "
        "document. If it doesn’t give enough detail to indicate how "
        "your circumstances have prevented you from completing your "
        "assessment on or before the set date, you’ll need to provide "
        "this information in an impact statement (on your application "
        "form).In some cases, you’ll need to also provide a statutory "
        "declaration (or equivalent) explaining in more detail the "
        "impact of your circumstances of family violence or a "
        "relationship breakdown on your studies.If you need help "
        "getting court documents, contact the court registrar in your "
        "jurisdiction.":
            "信函或文件的内容由法院决定。如果其中的细节不足以说明你的处境如何使你不能在规定日期或之前完成考核，你需要在申请表的影响说明（impact "
            "statement）里补充这些信息。在某些情况下，你还需要另外提交一份 statutory "
            "declaration（法定声明，或同等效力的文件），更详细地说明家庭暴力或关系破裂对你学习造成的影响。如果你在获取法院文件时需要帮助，请联系你所在司法辖区的法院登记处。",
        "The court will determine the content of this letter or "
        "document, but it must include the date or dates on which the "
        "crime took place. If it doesn’t give enough detail to "
        "indicate how your circumstances have prevented you from "
        "completing your assessment on or before the set date, you’ll "
        "need to provide this information in an impact statement (on "
        "your application form).In some cases, you’ll need to also "
        "provide a statutory declaration (or equivalent) explaining in "
        "more detail the impact of the crime on your studies.If you "
        "need help getting court documents, contact the court "
        "registrar in your jurisdiction.":
            "信函或文件的内容由法院决定。如果其中的细节不足以说明你的处境如何使你不能在规定日期或之前完成考核，你需要在申请表的影响说明（impact "
            "statement）里补充这些信息。如果你在获取法院文件时需要帮助，请联系你所在司法辖区的法院登记处。",
        "The court will determine the content of this letter or "
        "document. If it doesn’t give enough detail to indicate how "
        "your circumstances have prevented you from completing your "
        "assessment on or before the set date, you’ll need to provide "
        "this information in an impact statement (on your application "
        "form).If you need help getting court documents, contact the "
        "court registrar in your jurisdiction.":
            "信函或文件的内容由法院决定。如果其中的细节不足以说明你的处境如何使你不能在规定日期或之前完成考核，你需要在申请表的影响说明（impact "
            "statement）里补充这些信息。如果你在获取法院文件时需要帮助，请联系你所在司法辖区的法院登记处。",
        "The court will determine the content of this letter or "
        "document. If it doesn’t give enough detail to indicate how "
        "your circumstances have prevented you from completing your "
        "assessment on the set date, we may require you to supplement "
        "it with other documents.If you need help getting court "
        "documents, contact the court registrar in your jurisdiction.":
            "信函或文件的内容由法院决定。如果其中的细节不足以说明你的处境如何使你不能在规定日期或之前完成考核，你需要在申请表的影响说明（impact "
            "statement）里补充这些信息。如果你在获取法院文件时需要帮助，请联系你所在司法辖区的法院登记处。",
        "The doctor provides the certificate right after a "
        "consultation (including video/phone consultation if attending "
        "in-person was impractical). The certificate must be on the "
        "medical centre/practitioner’s letterhead, signed, stamped and "
        "dated. (If the certificate has been backdated, the doctor "
        "must explain why.)In Australia, some pharmacists may also "
        "provide a medical certificate.\n\nAcceptable medical "
        "documentation\n\n\nAcceptable documentation must be from an "
        "in-person consultation (or video/phone consultation if "
        "attending in-person was impractical) for the following "
        "special consideration applications:Medical documentation from "
        "online medical providers, without a video/phone consultation, "
        "is normally not accepted. It may be considered when all of "
        "the following apply:You’ll be asked to outline the "
        "exceptional circumstances that prevented you from having a "
        "video/phone consultation to obtain your documentation for "
        "your special consideration application.":
            "医生在就诊后随即开具证明（若当面就诊确实不可行，视频或电话问诊亦可）。证明必须使用医疗机构或执业人员的信笺抬头，并有签名、盖章和日期。（若证明日期被倒填，医生必须解释原因。）在澳大利亚，部分药剂师也可以开具 "
            "medical certificate（医疗证明）。\n\n可接受的医疗材料\n\n以下几类特殊考虑（special "
            "consideration）申请，材料必须来自当面就诊（若当面就诊确实不可行，视频或电话问诊亦可）：来自线上医疗机构、且没有经过视频或电话问诊的医疗材料，通常不予接受；只有在下列条件全部满足时才可能被考虑：届时我们会请你说明，是什么样的特殊情况使你无法通过视频或电话问诊取得材料。",
        "The letter from the Safer Community Unit must confirm that "
        "circumstances beyond your control occurred, the timeframe of "
        "the circumstances and the impact on your assessment due dates.":
            "Safer Community "
            "Unit（校园安全支持中心）出具的信函必须确认：确实发生了你无法控制的处境、该处境的时间范围，以及它对你考核截止日期造成的影响。",
        "The police will determine the content of this report. If it "
        "doesn’t give enough detail to indicate how your circumstances "
        "have prevented you from completing your assessment on or "
        "before the set date, you’ll need to provide this information "
        "in an impact statement (on your application form).":
            "报案记录的内容由警方决定。如果其中的细节不足以说明你的处境如何使你不能在规定日期或之前完成考核，你需要在申请表的影响说明（impact "
            "statement）里补充这些信息。",
        "The police will determine the content of this report. If it "
        "doesn’t give enough detail to indicate how your circumstances "
        "have prevented you from completing your assessment on or "
        "before the set date, you’ll need to provide this information "
        "in an impact statement (on your application form).You can "
        "also provide a statutory declaration (or equivalent) "
        "explaining in more detail the impact of of your circumstances "
        "of family violence on your studies.":
            "报案记录的内容由警方决定。如果其中的细节不足以说明你的处境如何使你不能在规定日期或之前完成考核，你需要在申请表的影响说明（impact "
            "statement）里补充这些信息。你也可以另外提交一份 statutory "
            "declaration（法定声明，或同等效力的文件），更详细地说明家庭暴力处境对你学习造成的影响。",
        "This includes family violence, sexual harm and other forms of "
        "gender-based violence.":
            "这一类包括家庭暴力、性侵害，以及其他形式的性别暴力。",
        "This includes severe disruption to your domestic arrangements.":
            "这也包括你的居家生活安排受到严重扰乱的情况。",
        "This includes, but is not limited to, if:":
            "这一类包括但不限于以下情形：",
        "We understand that you may not be in a position to provide "
        "evidence or documentation if you’ve been affected by "
        "gender-based violence. If this is the case, the Monash Safer "
        "Community Unit (SCU) can assist you with your application "
        "(they can even provide you a letter).":
            "我们理解，如果你受到性别暴力的影响，可能没有条件提供证据或材料。若是如此，Monash Safer Community "
            "Unit（校园安全支持中心）可以协助你提出申请，甚至可以为你出具一封信函。",
        "We understand that you may not be in a position to provide "
        "evidence or documentation if you’ve been affected by "
        "gender-based violence. If this is the case, the Monash Safer "
        "Community Unit can assist you with your application (they can "
        "even provide you a letter).":
            "我们理解，如果你受到性别暴力的影响，可能没有条件提供证据或材料。若是如此，Monash Safer Community "
            "Unit（校园安全支持中心）可以协助你提出申请，甚至可以为你出具一封信函。",
        "A medical certificate must state that the person you care for "
        "was unwell on or before the date you were meant to complete "
        "your assessment, and how long they required your care. The "
        "certificate must name you as the carer.The doctor provides "
        "the certificate right after a consultation (including "
        "video/phone consultation if attending in-person was "
        "impractical). The certificate must be on the medical "
        "centre/practitioner’s letterhead, signed, stamped and dated. "
        "(If the certificate has been backdated, the doctor must "
        "explain why, and give the reason they believe the person you "
        "care for was unwell at that time.)In Australia, some "
        "pharmacists may also provide a medical "
        "certificate.\n\nAcceptable medical documentation\n\n\nAcceptable "
        "documentation must be from an in-person consultation (or "
        "video/phone consultation if attending in-person was "
        "impractical) for the following special consideration "
        "applications:Medical documentation from online medical "
        "providers, without a video/phone consultation, is normally "
        "not accepted. It may be considered when all of the following "
        "apply:You’ll be asked to outline the exceptional "
        "circumstances that prevented you from having a video/phone "
        "consultation to obtain your documentation for your special "
        "consideration application.":
            "medical "
            "certificate（医疗证明）必须写明：受你照护的人在你应当完成考核的日期或之前确实身体不适，以及需要你照护多长时间；证明中必须写明你是照护者。医生在就诊后随即开具（若当面就诊确实不可行，视频或电话问诊亦可）。证明必须使用医疗机构或执业人员的信笺抬头，并有签名、盖章和日期。（若证明日期被倒填，医生必须解释原因，并说明他认为受你照护的人当时确实身体不适的依据。）在澳大利亚，部分药剂师也可以开具 "
            "medical certificate（医疗证明）。\n\n可接受的医疗材料\n\n以下几类特殊考虑（special "
            "consideration）申请，材料必须来自当面就诊（若当面就诊确实不可行，视频或电话问诊亦可）：来自线上医疗机构、且没有经过视频或电话问诊的医疗材料，通常不予接受；只有在下列条件全部满足时才可能被考虑：届时我们会请你说明，是什么样的特殊情况使你无法通过视频或电话问诊取得材料。",
        "If you’re a carer not registered with DSS, you need to "
        "provide a medical certificate. But if you couldn’t get this "
        "certificate when the person you care for was unwell, you can "
        "instead request a medical letter of support. Or you may "
        "provide a practitioner certificate.":
            "如果你是未在 DSS 登记的照护者，需要提交一份 medical "
            "certificate（医疗证明）。如果在受你照护的人患病期间没能开到，可以改为申请一份 medical letter "
            "of support（医疗情况说明信），或提交一份 practitioner certificate（执业人员证明）。",
        "If you’re a carer registered with Disability Support Services "
        "(DSS), you'll only need to provide supporting documents if "
        "you're applying for:":
            "如果你是已在 Disability Support "
            "Services（DSS，无障碍支持服务）登记的照护者，只有在下列情况下才需要提交证明材料：",
        "If you’re registered with Disability Support Services (DSS), "
        "you'll only need to provide supporting documents if you're "
        "applying for:":
            "如果你已在 Disability Support "
            "Services（DSS，无障碍支持服务）登记，只有在下列情况下才需要提交证明材料：",
        "If you’ve been hospitalised, or recently discharged, as an "
        "inpatient, you can provide evidence of a hospital discharge "
        "(e.g. letter).":
            "如果你曾作为住院病人入院、或近期刚出院，可以提交出院证明（例如 hospital discharge letter）。",
        "It doesn’t express the medical opinion of the psychiatrist or "
        "other medical doctor that the student was unwell. It merely "
        "reports what the student said.":
            "这份证明没有表达精神科医生或其他医生本人对该学生身体不适的医学判断，只是转述了学生自己的说法。",
        "It only certifies attendance. It doesn’t certify a mental "
        "health condition preventing the student from doing their "
        "assessment.":
            "这份证明只能证明就诊这件事，并没有证明存在使该学生无法完成考核的心理健康问题。",
        "This includes mental health conditions, such as severe "
        "anxiety and depression.":
            "这也包括心理健康问题，例如重度焦虑和抑郁。",
        "This is to certify that <student name> attended this centre "
        "on 10/01/2024 because of a medical condition. I conclude by "
        "way of the patient’s statement that he was unable to attend a "
        "university exam on 8 January 2024 .":
            "兹证明 <student name> 因健康问题于 2024 年 1 月 10 "
            "日到本中心就诊。据患者本人陈述，我判断他无法参加 2024 年 1 月 8 日的大学考试。",
        "This is to certify that <student name> attended this "
        "consulting suite on 10/01/2024 because of a mental health "
        "condition. I conclude by way of the patient’s statement that "
        "he was unable to attend a university assessment (exam) on 8 "
        "January 2024 .":
            "兹证明 <student name> 因心理健康问题于 2024 年 1 月 10 "
            "日到本诊所就诊。据患者本人陈述，我判断他无法参加 2024 年 1 月 8 日的大学考核（考试）。",
        "This is to certify that <student name> attended this "
        "consulting suite today due to a mental health condition.":
            "兹证明 <student name> 因心理健康问题于今日到本诊所就诊。",
        "This is to certify that <student name> attended this "
        "consulting suite today. She states that she has been unwell "
        "and was unable to attend her assessment (exam) today.":
            "兹证明 <student name> 于今日到本诊所就诊。她自述近来身体不适，无法参加今日的考核（考试）。",
        "This is to certify that <student name> is unfit for their "
        "usual occupation on 10 January 2024 due to a medical "
        "condition. He has been unwell since 8th Jan.":
            "兹证明 <student name> 因健康问题于 2024 年 1 月 10 日不适宜从事其日常工作。他自 1 月 8 "
            "日起身体不适。",
        "This is to certify that <student name> is unfit for their "
        "usual occupation on 10 January 2024 due to a mental health "
        "condition. He has been unwell since 8th Jan.":
            "兹证明 <student name> 因心理健康问题于 2024 年 1 月 10 日不适宜从事其日常工作。他自 1 月 "
            "8 日起状况不佳。",
        "This is unacceptable for an application to defer an "
        "assessment on 8 January. The doctor hasn’t certified that the "
        "illness was consistent with the student being unfit for the "
        "assessment on 8 January. They’ve only reported something the "
        "student has said.":
            "用于申请 1 月 8 日考核的延期时，这份证明不可接受。医生并没有证明该病情足以使该学生在 1 月 8 "
            "日不适合参加考核，只是转述了学生自己的说法。",
        "This is unacceptable for an application to defer an "
        "assessment on 8 January. The doctor or pharmacist hasn’t "
        "certified that the student is unfit for the assessment date. "
        "They’ve only reported something the student has said.":
            "用于申请 1 月 8 "
            "日考核的延期时，这份证明不可接受。医生或药剂师并没有证明该学生在考核当日状况不适合参加，只是转述了学生自己的说法。",
        "This is unacceptable for an application to defer an "
        "assessment on 8 January. The psychiatrist or other medical "
        "doctor hasn’t certified that the student is unfit for the "
        "assessment on 8 January. They’ve only reported something the "
        "student has said.":
            "用于申请 1 月 8 日考核的延期时，这份证明不可接受。精神科医生或其他医生并没有证明该学生在 1 月 8 "
            "日不适合参加考核，只是转述了学生自己的说法。",
        "This is unacceptable for an application to defer an "
        "assessment on 8 January. The psychiatrist, other medical "
        "doctor or pharmacist hasn’t certified that the student is "
        "unfit for the assessment date. They’ve only reported "
        "something the student has said.":
            "用于申请 1 月 8 "
            "日考核的延期时，这份证明不可接受。精神科医生、其他医生或药剂师并没有证明该学生在考核当日状况不适合参加，只是转述了学生自己的说法。",
        "This refers to the death of a close family member or person "
        "with whom you had a significant relationship. Due to their "
        "death, you’re now experiencing great loss or bereavement.":
            "这一类指的是：与你关系密切的家人、或与你有重要关系的人过世，你因此正经历巨大的失去与哀伤。",
        "This refers to when you can’t complete your assessment "
        "because you’re dealing with the illness of a family member "
        "(including your child) or other person you care for.":
            "这一类指的是：你因为要照顾生病的家人（包括子女）或其他受你照护的人，而无法完成考核。",
        "You can provide a certificate from a practitioner (e.g. "
        "psychologist or counsellor) registered with a relevant "
        "professional body. The certificate must state that you were "
        "unfit to complete your assessment on or before the date you "
        "were meant to complete it, and for how long.The practitioner "
        "provides the certificate right after a consultation. The "
        "certificate must be signed and dated. (If the certificate has "
        "been backdated, your practitioner must explain why, and give "
        "the reason they believe you were unfit at that time.)The "
        "certificate must be on the medical centre/practitioner’s "
        "letterhead.":
            "你可以提交一份由在相应专业机构注册的执业人员（例如心理学家或心理咨询师）开具的证明。证明必须写明：你在应当完成考核的日期或之前状况不适合完成考核，以及持续了多久。证明由执业人员在就诊后随即开具，须有签名和日期。（若证明日期被倒填，执业人员必须解释原因，并说明他认为你当时状况不适合的依据。）证明必须使用医疗机构或执业人员的信笺抬头。",
        "You can provide a certificate from a practitioner (e.g. "
        "social worker or physiotherapist) registered with a relevant "
        "professional body. The certificate must state that the person "
        "you care for was unwell on or before the date you were meant "
        "to complete your assessment, and for how long. The "
        "certificate must name you as the carer.The practitioner "
        "provides the certificate right after a consultation. The "
        "certificate must be signed and dated. (If the certificate has "
        "been backdated, the doctor must explain why, and give the "
        "reason they believe the person you care for was unwell at "
        "that time.)The certificate must be printed on the medical "
        "centre/practitioner’s letterhead.":
            "你可以提交一份由在相应专业机构注册的执业人员（例如社会工作者或物理治疗师）开具的证明。证明必须写明：受你照护的人在你应当完成考核的日期或之前确实身体不适，以及持续了多久；证明中必须写明你是照护者。证明由执业人员在就诊后随即开具，须有签名和日期。（若证明日期被倒填，医生必须解释原因，并说明他认为受你照护的人当时确实身体不适的依据。）证明必须打印在医疗机构或执业人员的信笺抬头上。",
        "You need to provide a document such as a death notice or "
        "certificate. If this isn’t available, you can provide a "
        "practitioner certificate or a statutory declaration (or "
        "equivalent). In the case of extreme and ongoing grief, your "
        "doctor or counsellor can also provide a medical letter of "
        "support.":
            "你需要提交讣告或死亡证明一类的材料。如果拿不到，可以提交 practitioner "
            "certificate（执业人员证明）或 statutory "
            "declaration（法定声明，或同等效力的文件）。如果哀伤程度严重且持续，你的医生或心理咨询师也可以出具一份 "
            "medical letter of support（医疗情况说明信）。",
        "You need to provide a document such as a death notice or "
        "certificate. You may wish to supplement this with a "
        "practitioner certificate or a statutory declaration (or "
        "equivalent). In the case of extreme and ongoing grief, your "
        "doctor or counsellor can provide a medical letter of support.":
            "你需要提交讣告或死亡证明一类的材料。如果拿不到，可以提交 practitioner "
            "certificate（执业人员证明）或 statutory "
            "declaration（法定声明，或同等效力的文件）。如果哀伤程度严重且持续，你的医生或心理咨询师也可以出具一份 "
            "medical letter of support（医疗情况说明信）。",
        "You need to provide a supporting document, such as a medical "
        "certificate or a practitioner certificate. But if you "
        "couldn't get this certificate when you were affected by your "
        "condition, you can instead:":
            "你需要提交一份证明材料，例如 medical certificate（医疗证明）或 practitioner "
            "certificate（执业人员证明）。如果在患病期间没能开到，可以改为：",
        "You should get a medical letter of support only if you "
        "couldn’t get a medical certificate when the person you care "
        "for was unwell.The letter must state that the person you care "
        "for was unwell on or before the date you were meant to "
        "complete your assessment, and how long they required your "
        "care. The doctor writing this letter must have knowledge of "
        "their medical history and/or condition. Additionally, they "
        "must explain how they concluded that the condition affected "
        "this person when they had no consultation with them at that "
        "time.The letter must be printed on the medical "
        "centre/doctor’s letterhead and name you as the carer. It must "
        "be signed and dated.":
            "只有在受你照护的人患病当时开不到 medical certificate（医疗证明）的情况下，才应改开 medical "
            "letter of "
            "support（医疗情况说明信）。信中必须写明：受你照护的人在你应当完成考核的日期或之前确实身体不适，以及需要你照护多长时间。写这封信的医生必须了解其病史或病情；此外，既然当时并未为其诊治，医生还必须说明他是根据什么判断该状况对这个人造成了影响。信件必须打印在医疗机构或医生的信笺抬头上，写明你是照护者，并有签名和日期。",
        "Your impact statement (on your application form) will need to "
        "show the significance of the relationship between you and the "
        "deceased person (e.g. evidence of kinship or family "
        "connection), and how long you’ve been affected by their "
        "death. If we need more details, we may require you to provide "
        "a statutory declaration (or equivalent) in addition to one of "
        "the other documents.":
            "你在申请表上写的影响说明（impact "
            "statement）需要说明你与逝者之间关系的紧密程度（例如亲属关系或家庭关系的证据），以及你受这件事影响了多久。如果我们需要更多细节，可能会要求你在上述材料之外，再补交一份 "
            "statutory declaration（法定声明，或同等效力的文件）。",
        "A hospital discharge form should state how long you were "
        "hospitalised and on what dates.":
            "hospital discharge form（出院证明）应写明你住院多长时间、具体是哪些日期。",
        "A medical certificate must state that you were unfit to "
        "complete your assessment on or before the date you were meant "
        "to complete it, and for how long.Your doctor can provide the "
        "certificate at the consultation. The certificate must be on "
        "the medical centre/practitioner's letterhead, signed, stamped "
        "and dated.In Australia, some pharmacists may also provide a "
        "medical certificate if the illness falls within the scope of "
        "the pharmacist's assessment ability.If you became unwell "
        "during your scheduled final assessment (exam), you must have "
        "reported this to the nurse or other medical professional at "
        "the assessments venue (or online equivalent). If you don’t do "
        "this, we won’t consider your application for a deferred "
        "assessment. Only in exceptional circumstances can you defer "
        "your assessment if you’ve seen and/or attempted to answer "
        "assessment questions.You may be able to make an appointment "
        "for a medical certificate at the University Health "
        "Services.\n\nAcceptable medical documentation\n\n\nAcceptable "
        "documentation must be from an in-person consultation (or "
        "video/phone consultation if attending in-person was "
        "impractical) for the following special consideration "
        "applications:Medical documentation from online medical "
        "providers, without a video/phone consultation, is normally "
        "not accepted. It may be considered when all of the following "
        "apply:You’ll be asked to outline the exceptional "
        "circumstances that prevented you from having a video/phone "
        "consultation to obtain your documentation for your special "
        "consideration application.\n\nUnacceptable certificate":
            "medical "
            "certificate（医疗证明）必须写明：你在应当完成考核的日期或之前身体状况不适合完成考核，以及这种状况持续多久。医生可以在就诊时当场开具。证明必须使用医疗机构或执业人员的信笺抬头，并有签名、盖章和日期。在澳大利亚，若病情在药剂师的评估能力范围内，部分药剂师也可以开具 "
            "medical "
            "certificate（医疗证明）。如果你是在已排定的期末考核（考试）进行当中感到不适，必须当场向考场（或线上等效渠道）的护士或其他医疗人员报告；没有报告的，我们不会受理你的延期考核申请。只有在特殊情况下，已经看过、或已经尝试作答考题的人，才可能获准延期。你也可以到 "
            "University Health Services（校内医疗服务）预约开具 medical "
            "certificate（医疗证明）。\n\n可接受的医疗材料\n\n以下几类特殊考虑（special "
            "consideration）申请，材料必须来自当面就诊（若当面就诊确实不可行，视频或电话问诊亦可）：来自线上医疗机构、且没有经过视频或电话问诊的医疗材料，通常不予接受；只有在下列条件全部满足时才可能被考虑：届时我们会请你说明，是什么样的特殊情况使你无法通过视频或电话问诊取得材料。\n\n不可接受的证明",
        "A medical certificate must state that you were unfit to "
        "complete your assessment on or before the date you were meant "
        "to complete it, and for how long.Your psychiatrist or other "
        "medical doctor can provide the medical certificate right "
        "after a consultation (including video/phone consultation if "
        "attending in-person was impractical). The certificate must be "
        "on the medical centre/practitioner’s letterhead, signed, "
        "stamped and dated. (If the certificate has been backdated, "
        "your psychiatrist or other medical doctor must explain why, "
        "and give the reason they believe you were unfit at that "
        "time.)In Australia, some pharmacists may also provide a "
        "medical certificate.If you became unwell during your "
        "scheduled final assessment (exam), you must have reported "
        "this to the nurse or other medical professional at the "
        "assessments venue (or online equivalent). If you don’t do "
        "this, we won’t consider your application for a deferred "
        "assessment. Only in exceptional circumstances can you defer "
        "your assessment if you’ve seen and/or attempted to answer "
        "assessment questions.You may be able to make an appointment "
        "for a medical certificate at the University Health "
        "Services.\n\nAcceptable medical documentation\n\n\nAcceptable "
        "documentation must be from an in-person consultation (or "
        "video/phone consultation if attending in-person was "
        "impractical) for the following special consideration "
        "applications:Medical documentation from online medical "
        "providers, without a video/phone consultation, is normally "
        "not accepted. It may be considered when all of the following "
        "apply:You’ll be asked to outline the exceptional "
        "circumstances that prevented you from having a video/phone "
        "consultation to obtain your documentation for your special "
        "consideration application.\n\nUnacceptable certificate":
            "medical "
            "certificate（医疗证明）必须写明：你在应当完成考核的日期或之前身体状况不适合完成考核，以及这种状况持续多久。医生可以在就诊时当场开具。证明必须使用医疗机构或执业人员的信笺抬头，并有签名、盖章和日期。在澳大利亚，若病情在药剂师的评估能力范围内，部分药剂师也可以开具 "
            "medical "
            "certificate（医疗证明）。如果你是在已排定的期末考核（考试）进行当中感到不适，必须当场向考场（或线上等效渠道）的护士或其他医疗人员报告；没有报告的，我们不会受理你的延期考核申请。只有在特殊情况下，已经看过、或已经尝试作答考题的人，才可能获准延期。你也可以到 "
            "University Health Services（校内医疗服务）预约开具 medical "
            "certificate（医疗证明）。\n\n可接受的医疗材料\n\n以下几类特殊考虑（special "
            "consideration）申请，材料必须来自当面就诊（若当面就诊确实不可行，视频或电话问诊亦可）：来自线上医疗机构、且没有经过视频或电话问诊的医疗材料，通常不予接受；只有在下列条件全部满足时才可能被考虑：届时我们会请你说明，是什么样的特殊情况使你无法通过视频或电话问诊取得材料。\n\n不可接受的证明",
        "Check below to find out which documents you need and the "
        "acceptable format. All non-English documents must be "
        "professionally translated into English by a NAATI-accredited "
        "translator. We cannot accept photographs or medical images.":
            "下面列出了各种情况需要哪些材料、以及可接受的格式。所有非英文材料都必须由 NAATI "
            "认证译员专业译成英文。我们不接受照片或医学影像。",
        "Do not, under any circumstances, submit fraudulent "
        "documentation":
            "任何情况下都不要提交伪造材料",
        "Don’t have your supporting documents ready?":
            "证明材料还没准备好？",
        "If you’re applying for an extension or a deferred scheduled "
        "final assessment, you’ll need to provide one or more of the "
        "documents below as evidence of your exceptional circumstances.":
            "如果你申请的是延期，或延期参加已排定的期末考核，需要提交下列材料中的一项或多项，作为你所处特殊情况的证明。",
        "If you’re granted an extension that is longer than 10 "
        "calendar days, it’ll start from the original due date of your "
        "assessment and align with the additional days mentioned in "
        "your medical documents.":
            "如果你获批的延期超过 10 个日历日，延期将从考核原定截止日起算，并与你医疗材料中载明的天数相衔接。",
        "If you’re registered with Disability Support Services (DSS), "
        "you’ll only need to provide supporting documents if you’re "
        "applying for:":
            "如果你已在 Disability Support "
            "Services（DSS，无障碍支持服务）登记，只有在下列情况下才需要提交证明材料：",
        "If you’ve been hospitalised as an inpatient, you can provide "
        "evidence of a hospital discharge (e.g. letter).":
            "如果你曾作为住院病人入院，可以提交出院证明（例如 hospital discharge letter）。",
        "It doesn’t certify that the student is unfit to sit the "
        "assessment on 21 January. A short interruption to study is "
        "not a valid circumstance for deferral of the assessment.":
            "这份证明并没有证明该学生在 1 月 21 日不适合参加考核。学习上的短暂中断，不足以构成延期考核的正当理由。",
        "It doesn’t express the medical opinion of the doctor that the "
        "student was ill. It merely reports what the student said.":
            "这份证明没有表达医生本人对该学生患病的医学判断，只是转述了学生自己的说法。",
        "It only certifies attendance. It doesn’t certify an illness "
        "preventing the student from doing their assessment.":
            "这份证明只能证明就诊这件事，并没有证明存在使该学生无法完成考核的疾病。",
        "Make sure you provide the correct supporting documents as "
        "evidence of your exceptional or extreme circumstances when "
        "you apply for special consideration (for an extension, a "
        "deferred scheduled final assessment or a rescheduled deferred "
        "assessment).":
            "申请特殊考虑（special "
            "consideration）时——无论是申请延期、延期参加已排定的期末考核，还是改期后的延期考核——请务必提交正确的证明材料，用以证明你所处的特殊或极端情况。",
        "This is to certify that <student name> attended this medical "
        "centre today due to a medical condition.":
            "兹证明 <student name> 因健康问题于今日到本医疗中心就诊。",
        "This is to certify that <student name> attended this medical "
        "centre today. She states that she has been ill and was unable "
        "to attend her assessment (exam) today.":
            "兹证明 <student name> 于今日到本医疗中心就诊。她自述近来身体不适，无法参加今日的考核（考试）。",
        "This is to certify that <student name> is unfit for study "
        "from 12–16 January 2024 and should be excused from his "
        "assessment (exam) on 21 January.":
            "兹证明 <student name> 自 2024 年 1 月 12 日至 16 日不适宜学习，应免于参加其 1 月 21 "
            "日的考核（考试）。",
        "To find out more about your responsibilities (and what you "
        "should do if you don’t have the required supporting "
        "documents), see our Documentation integrity page.":
            "想进一步了解你的责任（以及在拿不到所需证明材料时该怎么办），请查看 Documentation "
            "integrity（材料真实性）页面。",
        "Unacceptable statements on a medical certificate and the "
        "reasons why":
            "medical certificate（医疗证明）上不可接受的写法，以及为什么不可接受",
        "We can’t accept a statutory declaration alone in support of a "
        "mental health condition. Nor can we accept a hospital "
        "identification wristband or COVID-19 test.":
            "仅凭一份 statutory "
            "declaration（法定声明）不足以证明健康状况，我们不能接受。化验结果、新冠检测结果、住院手环、疫苗接种卡、照片或医学影像（如 "
            "X 光、CT、MRI）同样不能接受。",
        "We can’t accept a statutory declaration alone, in support of "
        "a medical condition. Nor can we accept a laboratory test "
        "result, COVID-19 test, hospital identification wristband, "
        "vaccination card, photograph or medical image (e.g. X-ray, CT "
        "and MRI).":
            "仅凭一份 statutory "
            "declaration（法定声明）不足以证明健康状况，我们不能接受。化验结果、新冠检测结果、住院手环、疫苗接种卡、照片或医学影像（如 "
            "X 光、CT、MRI）同样不能接受。",
        "You can get a medical letter of support if you couldn’t get a "
        "medical certificate when you were unwell.The letter must "
        "state that you were unwell on or before the date you were "
        "meant to complete your assessment, and for how long. The "
        "doctor writing this letter must have knowledge of your "
        "medical history and/or condition. Additionally, they must "
        "explain how they concluded that your condition has prevented "
        "you from completing your assessment when they had no "
        "consultation with you at that time.The letter must be on the "
        "medical surgery/doctor’s letterhead, signed and dated.":
            "如果你在患病当时开不到 medical certificate（医疗证明），可以改开一份 medical letter "
            "of "
            "support（医疗情况说明信）。信中必须写明：你在应当完成考核的日期或之前确实身体不适，以及持续了多久。写这封信的医生必须了解你的病史或病情；此外，既然当时并未为你诊治，医生还必须说明他是根据什么判断你的状况使你无法完成考核。信件必须使用医疗机构或医生的信笺抬头，并有签名和日期。",
        "You can get a medical letter of support if you couldn’t get a "
        "medical certificate when you were unwell.The letter must "
        "state that you were unwell on or before the date you were "
        "meant to complete your assessment, and for how long. The "
        "psychiatrist or other medical doctor writing this letter must "
        "have knowledge of your mental health history and/or "
        "condition. Additionally, they must explain how they concluded "
        "that your condition has prevented you from completing your "
        "assessment when they had no consultation with you at that "
        "time.The letter must be on the psychiatrist’s/other medical "
        "doctor’s letterhead, signed and dated.":
            "如果你在患病当时开不到 medical certificate（医疗证明），可以改开一份 medical letter "
            "of "
            "support（医疗情况说明信）。信中必须写明：你在应当完成考核的日期或之前确实身体不适，以及持续了多久。写这封信的医生必须了解你的病史或病情；此外，既然当时并未为你诊治，医生还必须说明他是根据什么判断你的状况使你无法完成考核。信件必须使用医疗机构或医生的信笺抬头，并有签名和日期。",
        "You can provide a certificate from an AHPRA-registered health "
        "practitioner (e.g. physiotherapist or rehabilitation "
        "specialist) registered with a relevant professional body. The "
        "certificate must state that you were unfit to complete your "
        "assessment on or before the date you were meant to complete "
        "it, and for how long.The practitioner provides the "
        "certificate right after a consultation. The certificate must "
        "be signed and dated. (If the certificate has been backdated, "
        "your practitioner must explain why, and give the reason they "
        "believe you were unfit at that time.)The certificate must be "
        "on the medical centre/practitioner’s letterhead.":
            "你可以提交一份由 AHPRA "
            "注册医疗执业人员（例如物理治疗师或康复专科医生）开具的证明，该执业人员须在相应的专业机构注册。证明必须写明：你在应当完成考核的日期或之前身体状况不适合完成考核，以及持续了多久。证明由执业人员在就诊后随即开具，须有签名和日期。（若证明日期被倒填，执业人员必须解释原因，并说明他认为你当时状况不适合的依据。）证明必须使用医疗机构或执业人员的信笺抬头。",
        "You must give us information that’s true, accurate and "
        "complete, without intending to mislead or gain advantage. If "
        "you make a false statement or provide a falsified supporting "
        "document, we won't approve your application and we'll refer "
        "the matter to Student Conduct and Complaints for an "
        "investigation into academic misconduct.":
            "你提供的信息必须真实、准确、完整，不得有误导或谋取便利的意图。如果你作出虚假陈述，或提交伪造的证明材料，我们不会批准你的申请，并会将此事移交 "
            "Student Conduct and Complaints（学生行为与投诉办公室）按学术不端立案调查。",
        "You need to provide a medical certificate. But if you "
        "couldn’t get this certificate when you were affected by your "
        "condition, you can instead:":
            "你需要提交一份 medical certificate（医疗证明）。如果在患病期间没能开到，可以改为：",
        "Your medical documentation must: be from a health "
        "practitioner fully registered with the relevant body for that "
        "practitioner's expertise in the country in which you are "
        "enrolled be provided by a health practitioner whose expertise "
        "relates to your diagnosis and treatment include the health "
        "practitioner’s contact details be in English or include a "
        "complete English translation by an accredited translator, "
        "such as NAATI.":
            "你的医疗材料必须：来自在你就读所在国家、经该专业相应主管机构完全注册的医疗执业人员；由专业领域与你的诊断和治疗相关的医疗执业人员出具；载明该医疗执业人员的联系方式；并且为英文，或附有由 "
            "NAATI 等认证译员出具的完整英文译文。",
        "Your medical documentation must: be from an AHPRA-registered "
        "health practitioner or a social worker accredited with the "
        "AASW be provided by a health practitioner whose expertise "
        "relates to your diagnosis and treatment include your provider "
        "details: name, practice address, contact details, and AHPRA "
        "registration number or social worker registration number.":
            "你的医疗材料必须：来自 AHPRA 注册的医疗执业人员，或在 AASW "
            "认证的社会工作者；由专业领域与你的诊断和治疗相关的医疗执业人员出具；并载明出具人的信息：姓名、执业地址、联系方式，以及 "
            "AHPRA 注册号或社会工作者注册号。",
        "You’ll need to make a detailed impact statement on your "
        "application form in addition to providing supporting "
        "documents. This statement should explain how circumstances "
        "beyond your control have affected your studies and your "
        "ability to complete your assessment on or before the set "
        "date. It must also say when you’ve been affected and for how "
        "long.":
            "除了提交证明材料，你还需要在申请表上写一份详细的影响说明（impact "
            "statement），说明你无法控制的情况如何影响了你的学习、以及你在规定日期或之前完成考核的能力，并写明你从何时开始受到影响、持续了多久。",
        "You’re responsible for making sure that the documents you "
        "supply to us are genuine, accurate and complete. Penalties "
        "for submitting a forged, altered or falsified document can "
        "include exclusion from the University, a fine of up to AUD "
        "$1,000 and a permanent record in Monash systems.":
            "你有责任确保提交给我们的材料真实、准确、完整。提交伪造、篡改或造假材料的处罚包括：被学校退学处理（exclusion）、最高 "
            "1000 澳元罚款，以及在 Monash 系统中留下永久记录。",
        "a scheduled assessment (e.g. mid-semester and in-class test)":
            "已排定的考核（例如期中测验、课堂测验）",
        "acute illness or serious injuries (including influenza or "
        "COVID-19, accidents causing physical injuries, dental issues "
        "requiring surgery or resulting in significant pain, or severe "
        "gastritis)":
            "急性疾病或严重外伤（包括流感或新冠、造成身体损伤的意外事故、需要手术或引起明显疼痛的牙科问题，或重度胃炎）",
        "an extension and you're not approved for flexible deadlines":
            "申请延期，且你未获批 flexible deadlines（弹性截止日期）",
        "an extension and you’re not approved for flexible deadlines":
            "申请延期，且你未获批 flexible deadlines（弹性截止日期）",
        "provide a certificate of attendance, along with a statutory "
        "declaration - only if you're unable to get a medical "
        "certificate.":
            "提交一份 certificate of attendance（就诊证明）连同一份 statutory "
            "declaration（法定声明）——仅限于你确实开不到 medical certificate（医疗证明）的情况。",
        "provide a certificate of attendance, along with a statutory "
        "declaration – only if you're unable to get a medical "
        "certificate.":
            "提交一份 certificate of attendance（就诊证明）连同一份 statutory "
            "declaration（法定声明）——仅限于你确实开不到 medical certificate（医疗证明）的情况。",
        "provide a practitioner certificate to support that your study "
        "has been affected, or":
            "提交一份 practitioner certificate（执业人员证明），说明你的学习确实受到了影响；或",
        "request a letter of support for the affected period from a "
        "medical practitioner or mental health professional, or":
            "请医生或心理健康专业人士为受影响的这段时间开一份 letter of support（情况说明信）；或",
        "request a letter of support for the affected period, from a "
        "medical practitioner or mental health professional, or":
            "请医生或心理健康专业人士为受影响的这段时间开一份 letter of support（情况说明信）；或",
        "serious chronic or episodic conditions (such as migraines, "
        "allergies with sudden flare ups, endometriosis, severe "
        "asthma, adenomyosis, or polycystic ovary syndrome (PCOS) and "
        "related complications)":
            "严重的慢性或发作性疾病（例如偏头痛、会突然发作的过敏、子宫内膜异位症、重度哮喘、子宫腺肌症，或多囊卵巢综合征（PCOS）及其相关并发症）",
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
        "Changes affecting your visa":
            "会影响签证的变动",
        "Compliance reporting":
            "合规上报",
        "Enrolment, assessments and results":
            "选课注册、考核与成绩",
        "Transferring to another Monash course":
            "转到 Monash 的其他学位课程",
        "Transferring to another university":
            "转学到其他大学",
        "deferred your course start date":
            "推迟了学位课程的开课日期",
        "failed one or more units":
            "有一门或多门课程不及格",
        "lost your place at Monash":
            "失去了在 Monash 的学籍",
        "reduced your study load":
            "减少了学习负荷",
        "took intermission (study leave)":
            "申请了休学（intermission，即 study leave）",
        "transferred to another Monash course":
            "转到了 Monash 的其他学位课程",
        "Changing your citizenship or visa type":
            "更改国籍或签证类型",
        "However, you do need a new student visa if:":
            "但在下列情况下，你确实需要办新的学生签证：",
        "If you change your citizenship or visa type, you need to let "
        "us know straight away. For details, see change of residency "
        "status.":
            "如果你更改了国籍或签证类型，请立即告知我们。详情见「居留身份变更」页面。",
        "If you don’t intend to complete further studies, you may wish "
        "to extend your time in Australia to work or travel. While you "
        "can’t get a student visa for this purpose, you can apply for "
        "a range of other visa types through the Department of Home "
        "Affairs.":
            "如果你不打算继续升学，可能会想延长在澳大利亚的时间以工作或旅行。这种情况下拿不到学生签证，但你可以通过 "
            "Department of Home Affairs（澳大利亚内政部）申请其他多种类型的签证。",
        "If your current visa is due to expire before you finish your "
        "course, you’ll need to apply for a new one. You may find "
        "yourself in this situation because you:":
            "如果你现有签证会在学业结束前到期，就需要申请一份新签证。出现这种情况，可能是因为你：",
        "There's a chance you may need to apply for a new visa if you "
        "change your course.":
            "如果你更换学位课程，有可能需要申请新签证。",
        "To stay in Australia, you need a valid visa. If your visa "
        "does not have a condition that prevents you from extending "
        "your stay, you may be able to apply for a new visa while your "
        "current visa is still valid. Find out what you can do to "
        "extend your stay.":
            "要留在澳大利亚，你需要持有有效签证。如果你的签证没有附带禁止延长停留的条件，就可能在现有签证仍然有效期间申请新签证。请了解可以怎样延长在澳停留时间。",
        "You don't need a new student visa if you:":
            "在下列情况下，你不需要办新的学生签证：",
        "You don't need to tell the Department of Home Affairs that "
        "you're changing your course, as they will have this "
        "information through your Confirmation of Enrolment (CoE).":
            "更换学位课程不需要另行告知 Department of Home "
            "Affairs（澳大利亚内政部）——他们会通过你的入学确认书（CoE）得知这一信息。",
        "You’ll need a release to transfer to another college or "
        "university, and you won’t be able to accept any offers until "
        "your release has been approved. But you won't need approval "
        "for release if you’re transferring to another course after "
        "having studied six calendar months of your course at Monash.":
            "转学到其他学院或大学需要取得 release（放行同意），在获批之前你不能接受任何录取。但如果你已在 Monash "
            "就读满六个自然月后再转到其他学位课程，则无需申请 release（放行同意）。",
        "are sitting deferred or supplementary assessments":
            "正在参加延期考核或补考",
        "expect to finish your studies before your current visa "
        "expires.":
            "预计会在现有签证到期之前完成学业。",
        "plan to remain in Australia while under examination after "
        "submitting your thesis.":
            "打算在提交论文后、评审期间继续留在澳大利亚。",
        "submitted your thesis later than expected":
            "提交论文比预期晚",
        "transfer to a course of the same type (e.g. bachelor degree "
        "to bachelor degree) and":
            "转到同一层次的学位课程（例如从学士学位转到学士学位），并且",
        "transferred to another college or university":
            "转学到了其他学院或大学",
        "you transfer to a course of a different type (e.g. diploma to "
        "bachelor degree) or":
            "你转到了不同层次的学位课程（例如从文凭课程转到学士学位），或者",
        "your new course will take longer and you won't finish before "
        "your current visa expires. In this case, make sure to apply "
        "for a new student visa just before your current one expires.":
            "你的新学位课程耗时更长，无法在现有签证到期前完成。这种情况下，请务必在现有签证到期前不久申请新的学生签证。",
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
