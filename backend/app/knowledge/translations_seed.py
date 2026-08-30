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

from app.models.translation import FAQ_ENTRY, GLOBAL, OFFICIAL_PAGE, UNIT

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

    # --- hurdles and grading schemes ---------------------------------------
    #
    # These sentences decide whether a student passes, and they are repeated
    # across hundreds of units, so the machine's readings of them were being
    # repeated hundreds of times too. "Failure of any hurdle assessment task"
    # came back with 失败 - defeat - where the word means "did not pass"; the
    # threshold paragraph produced 课程人, which is not a word; and "NGO", a
    # grade code, was read as 非政府组织, a non-governmental organisation.

    "Assessment in this unit includes hurdle assessment tasks. Failure of any "
    "hurdle assessment task may result in failure of the unit.":
        "本课程的考核中包含及格门槛考核项。任一及格门槛考核项未通过，可能导致本课程不及格。",

    "Assessment in this unit includes hurdle assessment tasks. Failure of any "
    "hurdle assessment task may result in failure of the unit":
        "本课程的考核中包含及格门槛考核项。任一及格门槛考核项未通过，可能导致本课程不及格。",

    "This unit contains hurdle requirements that you must achieve to be able to pass "
    "the unit. You are required to achieve at least 45% in the total continuous "
    "assessment component and at least 45% in the final assessment component. The "
    "consequence of not achieving a hurdle requirement is a fail grade (NH) and a "
    "maximum mark of 45 for the unit.":
        "本课程设有及格门槛要求，必须全部达到才能通过本课程。你需要在平时考核部分总分中至少达到 "
        "45%，并在期末考核部分中至少达到 45%。未达到及格门槛要求的后果是：本课程记为不及格"
        "（NH），且最终成绩最高只计 45 分。",

    "This unit contains threshold hurdle requirement that you must achieve to be able "
    "to pass the unit. You are required to achieve at least 45% in the total "
    "continuous assessment component and at least 45% in the final assessment "
    "component. The consequence of not achieving a hurdle requirement is a fail grade "
    "(NH) and a maximum mark of 45 for the unit.":
        "本课程设有及格门槛分数要求，必须达到才能通过本课程。你需要在平时考核部分总分中至少达到 "
        "45%，并在期末考核部分中至少达到 45%。未达到及格门槛要求的后果是：本课程记为不及格"
        "（NH），且最终成绩最高只计 45 分。",

    "This unit contains one or more hurdle requirements that you must successfully "
    "complete to be able to pass the unit. The consequence of not successfully "
    "completing a hurdle requirement is failure of the unit, regardless of the total "
    "marks you achieve.":
        "本课程设有一项或多项及格门槛要求，必须全部完成才能通过本课程。未能完成任一及格门槛要求"
        "的后果是本课程不及格，无论总分多少。",

    "Assessment in this unit includes a competency hurdle assessment task. The "
    "consequence of not achieving a competency hurdle is a fail grade (NH) and a "
    "maximum mark of 45 for the unit.":
        "本课程的考核中包含一项能力达标门槛考核项。未达到该能力门槛的后果是：本课程记为不及格"
        "（NH），且最终成绩最高只计 45 分。",

    "Final grades: PGO (pass grade only) or NGO (fail)":
        "最终成绩：PGO（仅评定为通过）或 NGO（不通过）",

    "This unit is graded pass grade only (PGO).":
        "本课程只评定通过与否（PGO），不给出等级分。",

    "This unit is a pass grade only (PGO) unit. Assessment will comprise of 100% in "
    "semester assessments. All learning outcomes will be assessed.":
        "本课程只评定通过与否（PGO）。考核全部为学期内考核，占 100%，并覆盖所有学习成果。",

    "This unit has competency-based assessments, with the final grade awarded as "
    "either Pass (PGO) or Fail (NGO).":
        "本课程采用能力达标式考核，最终成绩只有通过（PGO）或不通过（NGO）两种。",

    "The unit will be marked on an ungraded competency basis "
    "(satisfactory/unsatisfactory)":
        "本课程按能力达标评定，不给等级分（合格／不合格）。",

    "100% in-semester assessment":
        "学期内考核占 100%",

    "Continuous assessment: 100%":
        "平时考核：100%",

    "Continuous assessment: 60%":
        "平时考核：60%",

    "Continuous assessment: 50%":
        "平时考核：50%",

    "Continuous assessment: 40%":
        "平时考核：40%",

    "Continuous assessment: 50%\nFinal assessment: 50%":
        "平时考核：50%\n期末考核：50%",

    "Thesis assessed by two external examiners.":
        "学位论文由两位校外考官评阅。",

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


# --- unit titles ------------------------------------------------------------
#
# The complete machine baseline lives in ``unit_titles_zh.json``. A title is a
# noun phrase with little context, so exact human-reviewed strings here and in
# ``titles.py`` correct the cases where a general translator chose the wrong
# academic sense. Human rows load after machine rows and always win.
#
# These are the ones a reader meets first - the unit tree puts eleven titles on
# one screen - so they are written out.

UNIT_TITLES: dict[str, tuple[str, str]] = {
    # code: (English source, Chinese)
    "FIT1008": ("Fundamentals of algorithms", "算法基础"),
    "FIT1054": ("Fundamentals of algorithms (Advanced)", "算法基础（进阶）"),
    "FIT2085": ("Fundamentals of algorithms for engineers", "工程师算法基础"),
    "FIT1045": ("Introduction to programming", "编程导论"),
    "FIT1053": ("Introduction to programming (Advanced)", "编程导论（进阶）"),
    # 数值 not 数字: numerical analysis, not digital analysis.
    "ENG1014": ("Engineering numerical analysis", "工程数值分析"),
    # 离散 not 偏微: discrete mathematics, not partial differential.
    "MAT1830": ("Discrete mathematics for computer science", "计算机科学离散数学"),
    "ATS4367": (
        "Placement research project for honours in international studies",
        "国际研究荣誉学位实习研究项目",
    ),
    "BMA1012": (
        "Foundations of anatomy and physiology for health practice 2",
        "健康实践解剖学与生理学基础 2",
    ),
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
    # Monash Malaysia. The crawled English titles are the page banners -
    # "Before You Arrive" for the student pass page - so the Chinese says
    # what the page is instead of translating what the banner says.
    "malaysia-student-services": "学生服务",
    "malaysia-student-pass": "学生准证（Student Pass）",
    "malaysia-insurance": "保险",
    "malaysia-student-admin": "学生事务",
    "malaysia-special-consideration": "延期与特殊考虑（special consideration）",
    "malaysia-exam-rules": "eExam（线上考试）规则",
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
        "（澳大利亚校区）持学生签证一周能打工多少小时？",
        "这一条讲的是澳大利亚各校区。在马来西亚，居留身份是移民局通过 EMGS 签发的学生准证（Student Pass），适用条件与下面写的不是一回事，请以 monash.edu.my 为准。"
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
        "（澳大利亚校区）CoE 是什么？什么时候需要换新的？",
        "这一条讲的是澳大利亚各校区；马来西亚签发的是通过 EMGS 办理的学生准证（Student Pass）。"
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
        "Academic Integrity: a compulsory module":
            "学术诚信：一个必修模块",
        "Apply and maintain academic integrity":
            "践行并保持学术诚信",
        "Record of completion":
            "完成记录",
        "Start the Academic Integrity module":
            "开始学习学术诚信模块",
        "avoiding unintentional breaches":
            "避免无意间违规",
        "what academic integrity means":
            "学术诚信指的是什么",
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
    "policies": {
        "Academic integrity, plagiarism and collusion\nAs a Monash "
        "student, you’re required to maintain academic integrity – so "
        "it’s essential you understand what that means, what your "
        "obligations are and what happens if you don’t follow the "
        "rules.\n\n Learn more about academic integrity":
            "学术诚信、抄袭与合谋作弊\n作为 Monash "
            "的学生，你必须守住学术诚信——所以务必弄清它指的是什么、你有哪些义务，以及不守规矩会有什么后果。\n\n 了解学术诚信",
        "It's important for you to be aware of the University’s "
        "policies and procedures while you study at Monash.":
            "在 Monash 学习期间，了解学校的政策与流程很重要。",
        "Policies and procedures":
            "政策与流程",
        "Policy bank\n \nTake a look at our policy bank for a full list "
        "of our policies and procedures. They address a range of "
        "topics, from your academic studies to human resources and "
        "occupational health and safety.":
            "Policy bank（政策库）\n \n完整的政策与流程清单请查看 Policy "
            "bank（政策库），内容涵盖从学业到人力资源、职业健康与安全等各个方面。",
        "Student Code of Conduct\n \nThe Code of Conduct outlines your "
        "rights and responsibilities as a student, Monash University’s "
        "commitment to you, how to report concerning behaviour and "
        "more.":
            "Student Code of Conduct（学生行为守则）\n \n这份守则写明了你作为学生的权利与责任、Monash "
            "大学对你的承诺、以及如何举报可疑行为等内容。",
    },
    "changing-your-enrolment": {
        "Changing your enrolment":
            "变更选课注册",
        "If you're an honours student, before making changes, you need "
        "to discuss changes to your enrolment with your supervisor or "
        "honours coordinator. Contact your faculty "
        "supervisor/coordinator.":
            "如果你是荣誉学位学生，在改动之前需要先与导师或荣誉学位课程协调人商量，请联系你所在学院的导师或协调人。",
        "Take a break or transfer out":
            "暂停学业或转出",
        "Transfer course or campus":
            "转学位课程或转校区",
        "Update your personal information":
            "更新个人信息",
    },
    "study-abroad": {
        "Experience the world as part of your Monash degree.":
            "把看世界，变成你 Monash 学位的一部分。",
        "If you have any questions, we're here to help.":
            "有任何问题，我们都在。",
        "Live and learn in Australia at Monash.":
            "来 Monash，在澳大利亚生活与学习。",
        "Monash Abroad\nYour overseas study adventure starts here":
            "Monash Abroad（海外学习与交换）\n你的海外求学旅程从这里开始",
        "Monash Abroad\nYour overseas study adventure starts "
        "here\n\nMonash Abroad\n\nStudy Abroad and Exchange at "
        "Monash\n\nLive and learn in Australia at Monash.\n\nStudy "
        "Overseas\n\nExperience the world as part of your Monash "
        "degree.\n\nContact Us\n\nIf you have any questions, we're here to "
        "help.":
            "Monash Abroad（海外学习与交换）\n你的海外求学旅程从这里开始\n\nMonash "
            "Abroad（海外学习与交换）\n\nMonash 的海外学习与交换\n\n来 "
            "Monash，在澳大利亚生活与学习。\n\n出国学习\n\n把看世界，变成你 Monash "
            "学位的一部分。\n\n联系我们\n\n有任何问题，我们都在。",
        "Monash Abroad - Study Abroad":
            "Monash Abroad（海外学习与交换）——出国学习",
        "Study Abroad and Exchange at Monash":
            "Monash 的海外学习与交换",
    },
    "credit-and-enrolment": {
        "Changing my enrolment":
            "变更我的选课注册",
        "Changing my study load":
            "改变我的学习负荷",
        "Choose a topicChanging my study loadCourse or campus "
        "transferCredit for prior learningEnrolling in units and areas "
        "of studyChanging my enrolment":
            "选择一个主题：改变我的学习负荷／转学位课程或转校区／既往学习学分减免／选课与专业方向注册／变更我的选课注册",
        "Course or campus transfer":
            "转学位课程或转校区",
        "Credit for prior learning":
            "既往学习的学分减免",
        "Enrolling in units and areas of study":
            "选课与专业方向注册",
        "Enrolment and credit":
            "选课注册与学分减免",
        "What would you like help with?":
            "你想了解哪方面？",
    },
    "graduations": {
        "1. Before you apply\n\nLearn about course completion, if you're "
        "eligible, and when you should apply.\n\n\n\n\n\n\nStart preparing to "
        "graduate":
            "1. 申请之前\n\n了解学位课程完成情况、自己是否符合条件，以及该在什么时候申请。\n\n\n\n\n\n开始准备毕业",
        "2. Apply to graduate\n\nChoose a graduation round, apply, and "
        "start preparing for your graduation.\n\n\n\n\n\n\nApply to graduate "
        "now":
            "2. 申请毕业\n\n选定一个毕业批次，提交申请，并开始为毕业典礼做准备。\n\n\n\n\n\n现在就申请毕业",
        "3. Your graduation day\n\nFind out everything you need about "
        "graduation day using our ceremony guides.\n\n\n\n\n\n\nTake a look "
        "at our guides":
            "3. 毕业典礼当天\n\n用我们的典礼指南，了解毕业当天你需要知道的一切。\n\n\n\n\n\n查看指南",
        "4. After the day\n\nCheck how to receive your documents and how "
        "to stay in touch with the Monash community.\n\n\n\n\n\n\nSee what to "
        "do after the day":
            "4. 典礼之后\n\n了解如何领取你的证书文件，以及如何与 Monash 校友社群保持联系。\n\n\n\n\n\n看看典礼后要做什么",
        "All graduation dates":
            "全部毕业典礼日期",
        "Find out everything you need to know about graduating at "
        "Monash.":
            "在 Monash 毕业需要知道的一切，都在这里。",
        "Graduations\n\nMonash is proud to celebrate your academic "
        "achievements.\n\nYour graduation journey\n\nFind out everything "
        "you need to know about graduating at Monash.\n\n• 1. Before you "
        "apply\n\nLearn about course completion, if you're eligible, and "
        "when you should apply.\n\nStart preparing to graduate\n• 2. "
        "Apply to graduate\n\nChoose a graduation round, apply, and "
        "start preparing for your graduation.\n\nApply to":
            "毕业典礼\n\nMonash 很荣幸能一同庆祝你的学业成就。\n\n你的毕业之路\n\n在 Monash "
            "毕业需要知道的一切，都在这里。\n\n• 1. "
            "申请之前\n\n了解学位课程完成情况、自己是否符合条件，以及该在什么时候申请。\n\n开始准备毕业\n• 2. "
            "申请毕业\n\n选定一个毕业批次，提交申请，并开始为毕业典礼做准备。\n\n申请",
        "Monash is proud to celebrate your academic achievements.":
            "Monash 很荣幸能一同庆祝你的学业成就。",
        "Your graduation journey":
            "你的毕业之路",
    },
    "results": {
        "Academic records (transcripts)":
            "学业记录（成绩单）",
        "Check your results in WES":
            "在 WES（学生系统）里查成绩",
        "Feedback on your assessments":
            "考核反馈",
        "Getting your results":
            "查成绩",
        "Getting your results\n\n• Your results – when and how\n• Check "
        "your results in WES\n\nUnderstanding your results\n\n• Reading "
        "your marks\n• Academic records (transcripts)\n• Grade Point "
        "Average (GPA)\n• Weighted Average Mark (WAM)\n• Help with your "
        "results\n• Feedback on your assessments":
            "查成绩\n\n• 成绩什么时候出、怎么查\n• 在 WES（学生系统）里查成绩\n\n读懂你的成绩\n\n• 看懂分数\n• "
            "学业记录（成绩单）\n• GPA（平均绩点）\n• WAM（加权平均分）\n• 成绩方面需要帮助\n• 考核反馈",
        "Grade Point Average (GPA)":
            "GPA（平均绩点）",
        "Help with your results":
            "成绩方面需要帮助",
        "Understanding your results":
            "读懂你的成绩",
        "Weighted Average Mark (WAM)":
            "WAM（加权平均分）",
        "Your results – when and how":
            "成绩什么时候出、怎么查",
    },
    "re-enrol": {
        "Access dates for WES":
            "WES（学生系统）的开放日期",
        "Coursework re-enrolment":
            "授课型学生重新注册",
        "Graduate research\nre-enrolment":
            "研究生研究\n重新注册",
        "Late or failure to re-enrol":
            "逾期或未完成重新注册",
        "Re-enrol – continuing students":
            "重新注册——在读学生",
        "Re-enrolment dates and details":
            "重新注册的日期与说明",
        "Re-enrolment dates and details\n\n• Coursework re-enrolment\n• "
        "Graduate research\nre-enrolment\n• Late or failure to "
        "re-enrol\n• Returning after study leave (intermission)\n\nWeb "
        "Enrolment System (WES)\n\n• Overview of WES\n• Access dates for "
        "WES\n• WES login\n• Troubleshooting in WES":
            "重新注册的日期与说明\n\n• 授课型学生重新注册\n• 研究生研究\n重新注册\n• 逾期或未完成重新注册\n• "
            "休学（intermission）结束后复学\n\nWES（学生系统）\n\n• WES 概览\n• WES 的开放日期\n• WES "
            "登录\n• WES 问题排查",
        "Returning after study leave (intermission)":
            "休学（intermission）结束后复学",
        "Troubleshooting in WES":
            "WES（学生系统）问题排查",
        "Web Enrolment System (WES)":
            "WES（学生系统）",
    },
    "allocate-timetable": {
        "Adjusting your timetable\n \nFind out how to request a swap, "
        "remove yourself from an activity, and adjust your timetable "
        "on Allocate+.":
            "调整课表\n \n了解如何在 Allocate+ 里申请换班、退出某项活动，以及调整课表。",
        "Allocate+ dates\n \nSee when Allocate+ opens for preference "
        "entry and allocation adjustment.":
            "Allocate+ 日期\n \n查看 Allocate+ 什么时候开放填志愿、什么时候可以调整分配结果。",
        "Allocate+ glossary\n \nUnderstand the codes and abbreviations "
        "used across Allocate+.":
            "Allocate+ 术语表\n \n看懂 Allocate+ 里用到的各种代码和缩写。",
        "Allocate+ login\n \nLog into Allocate+ to view and manage your "
        "University timetable.":
            "Allocate+ 登录\n \n登录 Allocate+ 查看和管理你的课表。",
        "Entering your preferences\n \nLearn how to enter your "
        "preferences with Allocate+ so you can build your personal "
        "university timetable.":
            "填写志愿\n \n了解如何在 Allocate+ 里填志愿，从而排出属于你自己的课表。",
        "Fix timetable problems\n \nCheck out our page on self-help. If "
        "you can't solve it yourself, you can submit a help request.":
            "解决课表问题\n \n先看看我们的自助页面。自己解决不了的，可以提交帮助请求。",
        "How to use Allocate+":
            "怎么用 Allocate+",
        "Learn how timetabling works and the steps in creating your "
        "timetable for the semester. You’ll first enter your "
        "preferences, and then adjust your timetable.":
            "了解排课是怎么运作的，以及排出本学期课表的步骤：先填志愿，再调整课表。",
        "Review your final assessment timetable\n \nAccess and review "
        "your exam timetable. Find out what to check for and get help "
        "with any issues.":
            "查看期末考核课表\n \n打开并核对你的考试课表，了解要重点检查什么，以及遇到问题去哪里求助。",
        "When to use Allocate+\n \nUnderstand the three different stages "
        "of creating your timetable with Allocate+.":
            "什么时候用 Allocate+\n \n了解用 Allocate+ 排课表的三个阶段。",
        "Your timetable – Allocate+":
            "你的课表——Allocate+",
    },
    "student-conduct": {
        "Actions and behaviour by a student that breach the Student "
        "Code of Conduct may result in the student being subject to "
        "formal disciplinary action.":
            "学生若有违反 Student Code of Conduct（学生行为守则）的行为，可能会被正式处分。",
        "How the University manages reports of student misconduct.":
            "学校如何处理关于学生不端行为的举报。",
        "Monash University’s commitment to students":
            "Monash 大学对学生的承诺",
        "Pathways for reporting unacceptable or concerning conduct, "
        "and breaches of academic integrity or research standards by a "
        "student":
            "举报不当或可疑行为、以及学生违反学术诚信或研究规范的途径",
        "Student Code of Conduct":
            "Student Code of Conduct（学生行为守则）",
        "Student rights and responsibilities":
            "学生的权利与责任",
        "Student support resources":
            "学生支持资源",
        "Students are at the heart of Monash University, and help "
        "shape the vibrant, cohesive community we’re proud to be part "
        "of. As a student, you play a vital role in upholding our "
        "values which reflect not only who we are as a University, but "
        "also how we connect with those around us.":
            "学生是 Monash "
            "大学的核心，也是这个充满活力、彼此相连的社群得以成形的原因。作为学生，你在守护我们共同价值观这件事上举足轻重——这些价值观既体现了我们是怎样一所大学，也体现了我们如何与身边的人相处。",
        "The Student Code of Conduct reflects a shared commitment "
        "between students and the University to ensure the values of "
        "fairness, integrity, honesty and mutual respect, along with "
        "ethical conduct, which are at the core of everything we do. "
        "The Student Code of Conduct sets out both the University’s "
        "expectations of students, and how the University helps "
        "students to meet those expectations to foster a supportive, "
        "respectful, and thriving learning and research environment.":
            "Student Code of "
            "Conduct（学生行为守则）体现的是学生与学校之间的共同承诺：守住公平、诚信、诚实与相互尊重，以及合乎伦理的行为——这些是我们所做一切的根本。守则既写明了学校对学生的期望，也写明了学校如何帮助学生达成这些期望，从而营造一个彼此支持、互相尊重、生机勃勃的学习与研究环境。",
        "What’s covered":
            "涵盖哪些内容",
        "You can find the Student Code of Conduct (pdf), along with "
        "all other University policies, procedures and schedules, in "
        "the Monash Policy Bank.":
            "Student Code of Conduct（学生行为守则，pdf）以及学校其他所有政策、流程和附则，都可以在 "
            "Monash Policy Bank（政策库）里找到。",
    },
    "fees": {
        "Access your fees statement and understand what it means.":
            "查看你的费用清单，并看懂上面写的是什么。",
        "Depending on the circumstances, you may be eligible for a "
        "refund, or a remission of loan debt or credit.":
            "视具体情况而定，你可能符合退费、贷款债务豁免或额度返还的条件。",
        "Do you have Overseas student health cover? \n\n find out about "
        "oshc":
            "你买了留学生医疗保险（OSHC）吗？\n\n 了解 OSHC",
        "Find out when and how to pay your fees, and plan your "
        "payments.":
            "了解学费什么时候交、怎么交，并把缴费计划安排好。",
        "Foreign financial aid":
            "外国财政资助",
        "Monash Study app Check your timetable, find classrooms,\nand "
        "view your assessment info\n\n Get the app":
            "Monash Study app（Monash 学习 app）　查看课表、找教室、看考核信息\n\n 下载 app",
        "Other costs and fees":
            "其他费用与开销",
        "Penalties (encumbrances)":
            "处罚（encumbrances 学籍限制）",
        "Sponsorship and financial aid":
            "资助与财政援助",
        "Understand the SSAF and other miscellaneous study costs.":
            "了解 SSAF（学生服务与设施费）以及其他杂项学习开销。",
        "Use the fee calculator tools to calculate your course fees.":
            "用学费计算工具算一算你的学位课程要交多少钱。",
        "Where to get financial assistance":
            "去哪里寻求经济上的帮助",
    },
    "important-dates": {
        "Archived principal dates":
            "往年的重要日期存档",
        "Assessment (exam) dates":
            "考核（考试）日期",
        "Calendars and holidays":
            "校历与假期",
        "Final assessment dates":
            "期末考核日期",
        "Holidays and closedown":
            "假期与停工期",
        "Important dates See what's coming up\n\n Take a look":
            "重要日期　看看接下来有什么\n\n 去看看",
        "Monash Study app Check your timetable, find classrooms,\nand "
        "view your assessment info\n\n Get the app":
            "Monash Study app（Monash 学习 app）　查看课表、找教室、看考核信息\n\n 下载 app",
        "Principal dates for the current year":
            "本年度重要日期",
        "Results release dates":
            "成绩公布日期",
        "Semester summary 2026–2028":
            "2026–2028 学期一览",
        "Teaching and census dates":
            "教学日期与 census dates（学籍统计日）",
        "Web Enrolment System (WES)":
            "WES（学生系统）",
        "What are census dates?":
            "什么是 census dates（学籍统计日）？",
    },
    "academic-progress": {
        "About academic progress":
            "关于学业进度审查",
        "Academic progress is about keeping you on track with your "
        "studies. So twice a year we review your progress to see "
        "whether you need any additional support to successfully "
        "complete your course.":
            "学业进度审查是为了帮你把学业维持在正轨上。我们每年检查两次，看看你是否需要额外的支持才能顺利完成学位课程。",
        "Academic progress is the University’s way of checking in and "
        "helping you find the right support to successfully complete "
        "your degree.":
            "学业进度审查，是学校主动了解你近况、并帮你找到合适支持以顺利完成学位的方式。",
        "Attending an Academic Progress Committee hearing":
            "参加学业进度委员会听证会",
        "Find the information you need, so that you know how to "
        "prepare and what to expect on the day of your hearing.":
            "这里有你需要的信息，帮你知道该怎么准备、以及听证当天会发生什么。",
        "Getting support and advice":
            "获取支持与建议",
        "If you aren’t happy with the outcome of the academic progress "
        "process, you may have the option to appeal or request a "
        "review.":
            "如果你对学业进度审查的结果不满意，可能可以提出申诉或申请复核。",
        "If you need support or advice, we can offer counselling, "
        "financial advice, and health and wellbeing support. Your "
        "student association can also provide you with free and "
        "confidential support, advice, and representation.":
            "如果你需要支持或建议，我们可以提供心理咨询、财务咨询，以及健康与身心方面的支持。你所在的学生会也能为你提供免费且保密的支持、建议与代表服务。",
        "If you receive an email telling you that your progress is "
        "unsatisfactory, there’s no need to worry. We’ll tell you what "
        "you need to do to help get you back on track.":
            "如果你收到邮件说你的学业进度不达标，先别慌。我们会告诉你需要做些什么，帮你回到正轨。",
        "My Progress and Support tool":
            "My Progress and Support（我的进度与支持）工具",
        "Policies and procedures":
            "政策与流程",
        "Receiving an email about unsatisfactory progress":
            "收到学业进度不达标的邮件",
        "Student academic progress":
            "学生学业进度审查",
        "Student academic progress - Monash University":
            "学生学业进度审查 — Monash 大学",
        "The outcome of a hearing will vary depending on your "
        "circumstances and may include enrolment with conditions, "
        "recommended actions you need to take and, in some cases, "
        "exclusion.":
            "听证会的结果因人而异，可能包括：附条件的选课注册、要求你采取的整改措施，以及在某些情况下的退学处理（exclusion）。",
    },
    "international-students": {
        "After you arrive\n\nBreak down your big move into small "
        "steps.\n\n\n\n\n\n\nFind out how":
            "抵达之后\n\n把这场大迁徙拆成一个个小步骤。\n\n\n\n\n\n了解怎么做",
        "Before you leave\n\nGet ready to live and study in "
        "Australia.\n\n\n\n\n\n\nFind out how":
            "出发之前\n\n为在澳大利亚生活和学习做好准备。\n\n\n\n\n\n了解怎么做",
        "Check what’s available":
            "看看有哪些资源",
        "During your studies\n\nGet the most out of your Monash "
        "experience.\n\n\n\n\n\n\nFind out how":
            "在读期间\n\n把 Monash 的这段经历用足。\n\n\n\n\n\n了解怎么做",
        "Education Services for Overseas Students (ESOS)\n \nLearn how "
        "ESOS protects you while you’re studying in Australia, and "
        "understand your rights and responsibilities.":
            "Education Services for Overseas Students（ESOS，海外学生教育服务法）\n \n了解 "
            "ESOS 如何在你留学澳大利亚期间保护你，以及你有哪些权利与责任。",
        "Everyday costs are rising – we want to help":
            "日常开销在涨——我们想帮上忙",
        "Indigenous PhD scholarships now open\n \n\n\n \n Monash University "
        "is proud to support Indigenous-led research and is currently "
        "inviting applications for Indigenous PhD opportunities.\n \n "
        "\n\nOpportunities":
            "原住民博士奖学金现已开放申请\n \n\n\n \n Monash "
            "大学很自豪能支持由原住民主导的研究，目前正在招收原住民博士研究生。\n \n \n\n机会",
        "International current students":
            "国际在读学生",
        "International students under 18\n \nIf you’re under 18 and "
        "coming to Monash from overseas, we’ll make sure you have the "
        "right support before and during your studies. Find out what "
        "you need to do before you leave home, and how we help you and "
        "your family prepare for life in Australia.":
            "未满 18 岁的国际学生\n \n如果你未满 18 岁、要从海外来 Monash "
            "读书，我们会确保你在入学前和在读期间都有合适的支持。这里说明了你离家之前需要做什么，以及我们如何帮助你和家人为澳大利亚的生活做准备。",
        "Late arrival support sessions for international students\n "
        "\nArrived late or missed Orientation? Join one of our late "
        "arrival support sessions to get up to speed and feel "
        "confident as you start your Monash journey.":
            "国际学生迟到支持场次\n \n来晚了、错过了迎新周？参加我们的迟到支持场次，把进度补上，安心开始你的 Monash 之旅。",
        "Looking ahead\n\nGear up for graduation and arrange to go home "
        "or stay in Australia.\n\n\n\n\n\n\nFind out how":
            "往前看\n\n为毕业做准备，并安排好回国或留在澳大利亚的事。\n\n\n\n\n\n了解怎么做",
        "Need help or support?\n \nIf you’ve got a question or need some "
        "support, you can reach out to the International Students Team "
        "through Monash Connect.":
            "需要帮助或支持？\n \n如果你有疑问、或者需要支持，可以通过 Monash Connect（学生服务中心）联系国际学生团队。",
        "New cost-relief initiative":
            "新的费用纾困措施",
        "Orientation Week Peer Mentees\n \n\n\n \n Welcome to Orientation "
        "Week! Designed to help students transition smoothly into "
        "university life, it's a week filled with excitement, new "
        "experiences, and opportunities to make lasting connections.\n "
        "\n \n\nOpportunities":
            "迎新周朋辈辅导\n \n\n\n \n "
            "欢迎来到迎新周！这一周是为帮助学生顺利过渡到大学生活而设的，充满新鲜体验、各种机会，以及结识长久友谊的可能。\n \n "
            "\n\n机会",
        "Pre-arrival webinars\nArriving for semester two 2026? We can’t "
        "wait to welcome you to Monash and Australia!We’ve created a "
        "series of pre-arrival webinars just for you. Each session "
        "will guide you step-by-step through what to do before you "
        "leave home.\n\n Check out our webinars":
            "行前线上讲座\n2026 年第二学期入学？我们已经迫不及待要在 Monash "
            "和澳大利亚迎接你了！我们专门为你准备了一系列行前线上讲座，一步步带你搞清离家之前要做的事。\n\n 查看讲座安排",
        "Returning international students – ready for your next "
        "chapter?\nBuild on your Monash experience by expanding your "
        "social circle, levelling up your English and getting a head "
        "start on your career.\n\n See what's on offer":
            "回来继续读的国际学生——准备好开启下一段了吗？\n在已有的 Monash "
            "经历之上，把社交圈拓宽、把英文提上去，并为将来的职业早做打算。\n\n 看看有什么",
        "Stay safe online\n \n\n\n \n It’s important to maintain data "
        "privacy and protect yourself from cyber stalking, online "
        "blackmail, scams and technology-facilitated abuse.\n \n "
        "\n\nInternational students":
            "上网安全\n \n\n\n \n 保护好个人数据隐私，别让自己暴露在网络跟踪、网络勒索、诈骗和借助技术实施的侵害之下。\n \n "
            "\n\n国际学生",
        "We’re providing all students at our Australian campuses with "
        "a package of support. You can access up to $50 on a prepaid "
        "student card, free flu vaccinations, enjoy easier, cheaper "
        "travel options and free food on campus.":
            "我们为澳大利亚各校区的所有学生提供了一揽子支持：预付学生卡最高可领 50 "
            "澳元、免费流感疫苗、更便捷更便宜的出行选择，以及校内免费餐食。",
        "What to do. How to do it. And when. \n Your Monash journey "
        "from start to finish.":
            "做什么、怎么做、什么时候做。\n 从头到尾，你的 Monash 之路。",
        "Your student visa\n \nFind out how to apply for a student visa "
        "if you’re a new student, and how to keep your visa valid if "
        "you’re a returning student.":
            "你的学生签证\n \n新生请了解如何申请学生签证；在读学生请了解如何让签证保持有效。",
    },
    "working-on-a-student-visa": {
        "For more information, go to bringing a partner or family "
        "(Department of Home Affairs) and visa condition 8104.":
            "更多信息请查看「携伴侣或家人同行」（Department of Home Affairs（澳大利亚内政部））以及签证条件 "
            "8104。",
        "If you have any concerns about your work rights and "
        "restrictions in Australia, you should get independent legal "
        "advice. Take a look at Study Melbourne’s free work rights "
        "legal services for international students.":
            "如果你对自己在澳大利亚的工作权利和限制有任何疑虑，应当寻求独立的法律意见。可以看看 Study Melbourne "
            "面向国际学生的免费工作权利法律服务。",
        "If your family members are travelling with you on your "
        "student visa, they’ll receive permission to work when the "
        "visa is granted. Your family members won’t be allowed to work "
        "until you have started your course. Conditions of their "
        "working rights vary depending on the type of course you'll be "
        "studying.":
            "如果家庭成员随你的学生签证一同前来，签证获批时他们也会获得工作许可，但要等你开课之后才能开始工作。他们工作权利的具体条件，取决于你所读学位课程的类型。",
        "If you’ll be working while in Australia, you’ll need to "
        "understand your workplace rights about things like pay, "
        "working conditions, and health and safety.":
            "如果你打算在澳大利亚工作，就需要了解自己在薪酬、工作条件、以及健康与安全等方面的职场权利。",
        "If you’re on a student visa, make sure that you’re aware of "
        "any changes to work restrictions and other visa conditions. "
        "For the most up-to-date information, check your visa details "
        "and conditions (Department of Home Affairs).":
            "如果你持学生签证，务必留意工作限制和其他签证条件的任何变动。最新信息请查看你的签证详情与签证条件（Department "
            "of Home Affairs（澳大利亚内政部））。",
        "See visa condition 8105 for more details about work "
        "restrictions.":
            "工作限制的更多细节见签证条件 8105。",
        "Seeking work in Australia":
            "在澳大利亚找工作",
        "The 48-hour work restriction doesn’t apply if:":
            "下列情形不受 48 小时工作时长限制：",
        "The rules for working on a student visa cover employment, "
        "industry experience, internships and placements.":
            "持学生签证工作的规定，涵盖受雇工作、行业实践、实习和实践课程。",
        "Work rights for family members":
            "家庭成员的工作权利",
        "Working on a student visa":
            "持学生签证工作",
        "You can confirm your work restrictions and other visa "
        "conditions by using the Visa Entitlement Verification Online "
        "(VEVO) system.":
            "你可以通过 Visa Entitlement Verification "
            "Online（VEVO，签证权利在线核验系统）确认自己的工作限制和其他签证条件。",
        "You can work unlimited hours:":
            "下列情形下工作时长不受限制：",
        "You can work up to 48 hours every two weeks once the teaching "
        "period begins for your course. The 48-hour limit applies "
        "during teaching and assessment periods. You must not work "
        "before your course starts.":
            "你所读学位课程的开课学期开始之后，每两周最多可工作 48 小时。这个 48 小时上限适用于教学期和考核期。开课之前不得工作。",
        "You’ll need to continue balancing your study and work "
        "commitments even though there’s flexibility in the number of "
        "hours you can work.":
            "即便工作时长上有一定弹性，你仍然需要把学习和工作之间的平衡把握好。",
        "during scheduled course breaks":
            "在学位课程排定的假期期间",
        "the work is a registered component of your CRICOS registered "
        "course – e.g. some industry experience, placements, "
        "internships and work-based training units (to check, enter "
        "your CRICOS course code and make sure there's a ‘YES’ next to "
        "Work Component), or":
            "该工作是你所读 CRICOS "
            "注册学位课程中已登记的组成部分——例如某些行业实践、实习和以工作为基础的实践课程（查询方法：输入你的 CRICOS "
            "课程代码，确认 Work Component 一栏显示 YES）；或者",
        "when the final assessment period has ended":
            "期末考核期结束之后",
        "when you’ve finished your course.":
            "你已完成学位课程之后。",
        "you’ve started a master's by research or a doctorate degree.":
            "你已经开始攻读研究型硕士或博士学位。",
    },
    "malaysia-student-services": {
        "All Monash students can access a range of support services, "
        "including services for student advisory, counselling, "
        "disability, insurance and more.":
            "所有 Monash 学生都可以使用一系列支持服务，包括学生咨询、心理咨询、无障碍支持、保险等。",
        "Be an active member of our student community. Get all the "
        "latest news from Monash, including tips, opportunities and "
        "what's happening on the campus.":
            "在学生社群里活跃起来。第一时间获取 Monash 的各类资讯，包括实用提示、各种机会，以及校园里正在发生的事。",
        "Current Students Home - new - Current Students, Monash "
        "University Malaysia":
            "在读学生首页 — Monash 大学马来西亚校区",
        "Decided to take up a study adventure with us? What a great "
        "decision. We can help you enjoy the best of Malaysia, and "
        "prepare for your departure and arrival.":
            "决定来我们这里开启一段求学之旅了？这个决定很棒。我们可以帮你享受马来西亚最好的一面，并为出发和抵达做好准备。",
        "Discover a world of fun activities and events on campus to "
        "enrich your social life and improve your work/study balance.":
            "校园里有各式各样有意思的活动，既能丰富你的社交生活，也能让工作、学习与生活更平衡。",
        "Discover information that can guide you through your first "
        "semester.":
            "这里的信息，会陪你走完第一个学期。",
        "Expand your networks, gain employability advantages and "
        "prepare for a career in academic research.":
            "拓展人脉，增强就业竞争力，为学术研究方向的职业道路做准备。",
        "International students":
            "国际学生",
        "Isn't an education supposed to broaden your horizon? "
        "Experience the hidden and untold norms that can only be "
        "revealed when experiencing a country at its own pace. Step up "
        "to the challenge abroad.":
            "教育不就是为了开阔眼界吗？有些风土人情，只有以当地的节奏亲身生活过才能体会。去接受海外这场挑战吧。",
        "Looking for a new opportunity? Perhaps you need to put that "
        "finishing touch on your resume. Our career centre can help.":
            "在找新机会？又或者简历还差最后一点打磨？我们的职业中心可以帮你。",
        "Mental Health Hotline\n(T) +6015 4877 0403 or (WhatsApp) +6011 "
        "3011 6610\nFind out more":
            "心理健康热线\n（电话）+6015 4877 0403 或（WhatsApp）+6011 3011 6610\n了解更多",
        "Monash Malaysia Connect\nThis one-stop centre has been put "
        "together to provide the services and support you need.\nFind "
        "out more":
            "Monash Malaysia "
            "Connect（马来西亚校区学生服务中心）\n这个一站式中心汇集了你需要的各项服务与支持。\n了解更多",
        "Monash Warwick Alliance":
            "Monash–Warwick 联盟",
        "Report a hazard or incident":
            "上报隐患或事故",
        "Scholarships and financial assistance":
            "奖学金与经济资助",
        "Student administration":
            "学生事务办理",
        "Supporting the disadvantaged. Rewarding high achievers. There "
        "are many ways we can help financially so you can focus on "
        "learning.":
            "帮助有需要的人，奖励表现优异的人。我们有多种方式提供经济上的支持，好让你能专心学习。",
        "TRY THE NEW STUDENT PORTAL\nGet access to all the key Monash "
        "systems, information and resources now in one convenient "
        "place\nCheck it out":
            "试试新版学生门户\n把 Monash 的各个关键系统、信息和资源，全都集中到一个地方\n去看看",
        "Undergraduate Research Program":
            "本科生科研项目",
        "We believe every student should have an opportunity for an "
        "international study experience during their studies at Monash "
        "University Malaysia.":
            "我们认为，每一位在 Monash 大学马来西亚校区就读的学生，都应当有机会获得一段海外学习经历。",
        "We make filling in paperwork easy. Whether you're enrolling "
        "for the first time, looking for a timetable or preparing for "
        "graduation, it's all here.":
            "各类手续，我们尽量帮你办得简单。无论是第一次选课注册、查课表，还是准备毕业，都能在这里找到。",
        "Your Health and Safety is important to us.\n\nThe university "
        "strives to provide a healthy and safe study environment for "
        "students.\n\nOur Safety and Risk Analysis Hub (SARAH) makes it "
        "easy for you to report OHS-related hazards and incidents.":
            "你的健康与安全对我们很重要。\n\n学校致力于为学生提供健康、安全的学习环境。\n\n通过我们的 Safety and Risk "
            "Analysis Hub（SARAH，安全与风险分析平台），你可以方便地上报职业健康安全方面的隐患与事故。",
    },
    "gpa": {
        "Assessment and Academic Integrity Policy (pdf)":
            "Assessment and Academic Integrity Policy（考核与学术诚信政策，pdf）",
        "CGPA = 250.92 ÷ 78\nCGPA = 3.217":
            "CGPA = 250.92 ÷ 78\nCGPA = 3.217",
        "Correcting a mark or grade":
            "更正分数或成绩等级",
        "Examples of marking or grading errors may include:":
            "评分或定级错误的例子包括：",
        "Final assessments:":
            "期末考核：",
        "For example, your grades might be a pass, credit, high "
        "distinction, distinction and so on. All grades, including "
        "fail grades and grades from any repeated units, are given a "
        "numerical value and then those values are averaged which "
        "gives you your GPA.":
            "举例来说，你的成绩等级可能是 pass、credit、high distinction、distinction "
            "等。所有成绩等级——包括不及格，以及重修课程所得的成绩——都会换算成一个数值，再把这些数值取平均，就得到你的 "
            "GPA（平均绩点）。",
        "For the cost, see Student letters - standard format on our "
        "miscellaneous fees page.":
            "费用请查看「杂项费用」页面上的 Student letters - standard format（学生证明信 · "
            "标准格式）。",
        "Format and deadlines":
            "格式与截止期限",
        "GPA = 229.80 ÷ 78\nGPA = 2.946":
            "GPA = 229.80 ÷ 78\nGPA = 2.946",
        "If you fail a major assessment (worth 20% or more of your "
        "unit’s total mark) it will be automatically re-marked before "
        "your result is finalised – so there’s no need to request one.":
            "如果你某项主要考核不及格（占该课程总分 20% 或以上），系统会在成绩最终确定前自动重新评阅一次，不需要你另行申请。",
        "If you think there’s been a mistake in how your mark or grade "
        "was calculated, you can contact the chief examiner about "
        "having it corrected.":
            "如果你认为分数或成绩等级的计算有误，可以联系主考官（chief examiner）请求更正。",
        "If you’re applying for jobs in Malaysia and you need your "
        "Cumulative Grade Point Average (CGPA) for your resume, you "
        "can request a letter which states your CGPA from Student "
        "Services in Malaysia or Monash Connect in Australia. For "
        "further details, see the Malaysia tab below.":
            "如果你在马来西亚求职、简历上需要填 CGPA（累计平均绩点），可以向马来西亚的 Student "
            "Services（学生服务处）、或澳大利亚的 Monash Connect（学生服务中心）申请一封载明 CGPA "
            "的证明信。详见下方的「马来西亚」标签页。",
        "In-semester assessments – within ten working days of your "
        "mark’s release.":
            "学期内考核——自分数公布起十个工作日之内。",
        "Just keep in mind, while your work is being marked, you can’t "
        "contact staff about an assessment or thesis examination issue "
        "– not even to complain informally.":
            "但要记住：在你的作业还在评阅期间，你不能就该考核或论文评审的问题联系工作人员，非正式的抱怨也不行。",
        "Keep in mind that the following are not considered marking "
        "errors:":
            "请注意，下列情形不算评分错误：",
        "Marking and Feedback Procedure (pdf)":
            "Marking and Feedback Procedure（评分与反馈规程，pdf）",
        "Outside of this process, in most cases you’re not entitled to "
        "a re-mark, and it’s unlikely that a complaint about a "
        "faculty’s refusal to re-mark will be successful.":
            "除上述流程之外，多数情况下你无权要求重新评阅；就学院拒绝重新评阅一事提出投诉，也很难得到支持。",
        "Policy and procedure":
            "政策与流程",
        "Scheduled Final Assessments Procedure (pdf)":
            "Scheduled Final Assessments Procedure（已排定期末考核规程，pdf）",
        "Seeking feedback on your assessments\n \nFind out where you can "
        "view feedback for an explanation of why you received a "
        "certain mark for an assessment.":
            "查看考核反馈\n \n了解可以在哪里查看反馈，弄清自己某项考核为何得到这个分数。",
        "This is your first step in addressing your complaint. If "
        "you’re unable to resolve the issue with your chief examiner, "
        "see how to raise and resolve a complaint for what to do next.":
            "这是处理投诉的第一步。如果你无法与主考官（chief "
            "examiner）把问题解决，请查看「如何提出并解决投诉」了解下一步该怎么做。",
        "To request a CGPA letter, contact Student Services in "
        "Malaysia or Monash Connect in Australia. Once we have your "
        "payment, we'll produce the letter within one business day and "
        "mail it to your nominated address.":
            "要申请 CGPA（累计平均绩点）证明信，请联系马来西亚的 Student Services（学生服务处）或澳大利亚的 "
            "Monash Connect（学生服务中心）。收到付款后，我们会在一个工作日内出具信件，并寄往你指定的地址。",
        "Your request for a correction needs to be in writing, so "
        "email the chief examiner. Make sure you do this within this "
        "timeframe below:":
            "更正请求必须以书面形式提出，请发邮件给主考官（chief examiner），并务必在下列时限之内：",
        "friends or colleagues think you deserved a higher mark.":
            "朋友或同学认为你该拿更高的分。",
        "receiving a late penalty even though you submitted on time.":
            "明明按时提交却被扣了迟交分。",
        "semester one –- within six weeks of the release of your unit "
        "results.":
            "第一学期——自课程成绩公布起六周之内。",
        "semester two –- before the end of week one of semester one "
        "the next year.":
            "第二学期——在次年第一学期第一周结束之前。",
        "the marker doesn’t agree with your summary, data or findings":
            "评阅人不认同你的结论、数据或研究发现",
        "you disagree with how the marker weighed parts of your "
        "assessment":
            "你不认同评阅人对考核各部分的权重处理",
        "you expected a higher mark based on your past performance":
            "你根据以往表现，本以为能拿更高的分",
        "you feel you didn’t get enough explanation for your mark":
            "你觉得关于分数的解释不够充分",
        "your mark is inconsistent with what you received for similar "
        "assessments":
            "你的分数与类似考核所得的分数不一致",
        "your marks having been been summed up incorrectly":
            "你的分数被加总错了",
    },
    "fee-payment-dates": {
        "Course fee payment dates":
            "学位课程学费缴纳日期",
        "Ensure you pay your fees by the due date; otherwise, we may "
        "place an encumbrance on your account.":
            "请务必在到期日之前缴清学费，否则我们可能会对你的账户施加 encumbrance（学籍限制）。",
        "Full year (extended)":
            "全学年（延长）",
        "Full year teaching period":
            "全学年开课学期",
        "If you’re a CSP Monash Online student, you’ll need to check "
        "your fees statement for your payment due dates – they may be "
        "different to the dates published here.":
            "如果你是联邦资助学额（CSP）的 Monash Online "
            "学生，请以自己费用清单上的缴费到期日为准——它可能与这里公布的日期不同。",
        "Monash Online fee invoice periods":
            "Monash Online 的费用账单周期",
        "November teaching period":
            "11 月教学期",
        "Penalties for fees non-payment":
            "未缴学费的处罚",
        "Research Q1: 1 Jan – 31 Mar":
            "研究季度 1：1 月 1 日至 3 月 31 日",
        "Research Q2: 1 Apr – 30 Jun":
            "研究季度 2：4 月 1 日至 6 月 30 日",
        "Research Q3: 1 Jul – 30 Sep":
            "研究季度 3：7 月 1 日至 9 月 30 日",
        "Research Q4: 1 Oct – 31 Dec":
            "研究季度 4：10 月 1 日至 12 月 31 日",
        "Research degree fee invoice periods":
            "研究型学位的费用账单周期",
        "Semester 1 (extended)":
            "第一学期（延长）",
        "Semester 1 (northern)":
            "第一学期（北半球）",
        "Semester 2 (extended)":
            "第二学期（延长）",
        "Semester 2 (northern)":
            "第二学期（北半球）",
        "Semester 2 - semester 1":
            "第二学期至第一学期",
        "Semester 2 - summer A":
            "第二学期至夏季学期 A",
        "Semester one fee invoice cycle includes these teaching periods":
            "第一学期的费用账单周期涵盖下列开课学期",
        "Semester one teaching periods":
            "第一学期的各开课学期",
        "Semester two fee invoice cycle includes these teaching periods":
            "第二学期的费用账单周期涵盖下列开课学期",
        "Semester two teaching periods":
            "第二学期的各开课学期",
        "Spring fee invoice cycle includes these teaching periods":
            "春季的费用账单周期涵盖下列开课学期",
        "Spring teaching periods":
            "春季的各开课学期",
        "Student Services and Amenities Fee (SSAF)":
            "学生服务与设施费（SSAF）",
        "Summer A - semester 1":
            "夏季学期 A 至第一学期",
        "Summer A fee invoice cycle includes these teaching periods":
            "夏季学期 A 的费用账单周期涵盖下列开课学期",
        "Summer A teaching periods":
            "夏季学期 A 的各开课学期",
        "Summer B fee invoice cycle includes these teaching periods":
            "夏季学期 B 的费用账单周期涵盖下列开课学期",
        "Summer B teaching periods":
            "夏季学期 B 的各开课学期",
        "Summer semester 3 (MC)":
            "夏季学期 3（MC）",
        "Teaching period code":
            "开课学期代码",
        "Teaching period codes and names":
            "开课学期代码与名称",
        "Teaching period name":
            "开课学期名称",
        "The fee amount and payment due dates are listed on your fees "
        "statement. For instructions on how to make a payment, see pay "
        "your fees.":
            "费用金额和缴费到期日都列在你的费用清单上。缴费方式请见「如何缴纳学费」。",
        "Trimester A (Joint MU/MC)":
            "学段 A（MU/MC 联合）",
        "Trimester B (Joint MU/MC)":
            "学段 B（MU/MC 联合）",
        "Trimester C (Joint MU/MC)":
            "学段 C（MU/MC 联合）",
        "Understanding your fees statement":
            "看懂你的费用清单",
        "Winter fee invoice cycle includes these teaching periods":
            "冬季的费用账单周期涵盖下列开课学期",
        "Winter teaching periods":
            "冬季的各开课学期",
        "You don't need to pay for the whole year's units at the same "
        "time. Your fees amount may change if you change your "
        "enrolment – we’ll send you a new fees statement if that "
        "happens.":
            "你不需要一次性交清全年所有课程的学费。如果你改动选课注册，费用金额可能会变——遇到这种情况我们会给你发一份新的费用清单。",
    },
    "results-legend": {
        "0–49 You lack satisfactory demonstration of fundamental "
        "knowledge, skills and expected attributes.":
            "0–49　你未能令人满意地展现出应有的基础知识、技能与素养。",
        "45 This grade means you didn't satisfactorily complete all "
        "hurdle requirements but would have otherwise achieved a mark "
        "of 45 or above in the unit.":
            "45　这个成绩表示你未能达标完成全部及格门槛要求，否则本可以在该课程取得 45 分或以上。",
        "50 to <60":
            "50 至 <60",
        "50–59 Satisfactory. You’ve demonstrated fundamental "
        "knowledge, skills and attributes at a satisfactory level.":
            "50–59　合格。你在基础知识、技能与素养上达到了合格水平。",
        "60 to <70":
            "60 至 <70",
        "60–69 You’ve demonstrated fundamental knowledge, skills and "
        "attributes at a proficient level, showing fluency in concepts.":
            "60–69　你在基础知识、技能与素养上达到熟练水平，对概念的运用较为流畅。",
        "70 to <80":
            "70 至 <80",
        "70–79 You’ve demonstrated extended knowledge, skills and "
        "attributes at a superior level, showing fluency, emerging "
        "originality and integration of concepts.":
            "70–79　你在拓展性的知识、技能与素养上达到优秀水平，运用流畅，已显现出一定的原创性，并能把概念融会贯通。",
        "80–100 You’ve demonstrated extended knowledge, skills and "
        "attributes at an exceptional level, showing fluency, "
        "originality and integration of concepts.":
            "80–100　你在拓展性的知识、技能与素养上达到卓越水平，运用流畅、富有原创性，并能把概念融会贯通。",
        "A (MBA results pre-1990)":
            "A（1990 年前 MBA 成绩）",
        "A deferred assessment is an assessment postponed to a later "
        "date. These are held:":
            "延期考核指的是被推迟到之后进行的考核，安排在：",
        "A fail grade used for study abroad, exchange, and "
        "complementary study units when Monash has not taught and "
        "assessed the unit. The mark provided by the other institution "
        "is not recorded.":
            "用于海外学习、交换和辅修课程的不及格成绩，适用于该课程并非由 Monash 授课和评核的情形。对方院校给出的分数不予记录。",
        "A pass grade used for study abroad, exchange, and "
        "complementary study units when Monash has not taught and "
        "assessed the unit. The mark provided by the other institution "
        "is not recorded.":
            "用于海外学习、交换和辅修课程的及格成绩，适用于该课程并非由 Monash 授课和评核的情形。对方院校给出的分数不予记录。",
        "A+ (MBA results pre-1990)":
            "A+（1990 年前 MBA 成绩）",
        "Assessment Incomplete: Subject assessed over more than one "
        "semester":
            "考核未完成：该科目的评核跨越一个以上学期",
        "B (MBA results pre-1990)":
            "B（1990 年前 MBA 成绩）",
        "C (MBA results pre-1990)":
            "C（1990 年前 MBA 成绩）",
        "Chisholm Institute of Technology and Caulfield Institute of "
        "TechnologyThe following grades were used:Monash University "
        "College Gippsland and Gippsland Institute of Advanced "
        "EducationThese grades were used before 1993. Gippsland "
        "changed its point system in 1994:Frankston Teachers "
        "College/State College of Victoria at Frankston "
        "(1959-1981)Course started before 1973Course started after 1972":
            "Chisholm Institute of Technology 与 Caulfield Institute of "
            "Technology\n使用过下列成绩等级：\nMonash University College Gippsland 与 "
            "Gippsland Institute of Advanced Education\n下列成绩等级用于 1993 "
            "年之前；Gippsland 于 1994 年更改了计分体系：\nFrankston Teachers College / "
            "State College of Victoria at Frankston（1959–1981）\n1973 "
            "年之前入学\n1972 年之后入学",
        "Code, grade and mark range for academic transcript results "
        "for 2017 to 2019":
            "2017 至 2019 年成绩单上的代码、成绩等级与分数区间",
        "D (MBA results pre-1990)":
            "D（1990 年前 MBA 成绩）",
        "Did not complete assessment requirement":
            "未完成考核要求",
        "Eligible to sit for Supplementary Examination":
            "符合参加补考的条件",
        "Extended assessment period":
            "延长的考核期",
        "F (MBA results pre-1990)":
            "F（1990 年前 MBA 成绩）",
        "Faculty Requirements Unsatisfied":
            "未满足学院要求",
        "Fail - Supplementary Examination Granted":
            "不及格——已获准补考",
        "From 2020 to 2021, Monash University introduced a modified "
        "grading scale system in response to the COVID-19 pandemic.":
            "2020 至 2021 年，为应对新冠疫情，Monash 大学启用过一套调整后的评分体系。",
        "From 6 October 2021, students graduating with a master’s "
        "degree by coursework with a WAM of 80 or above will see "
        "Awarded with distinction on their official academic record "
        "(transcript), award certificate (testamur) and Australian "
        "Higher Education Graduation Statement (AHEGS).":
            "自 2021 年 10 月 6 日起，授课型硕士毕业生若 WAM（加权平均分）达到 80 "
            "或以上，其正式学业记录（成绩单）、学位证书（testamur）以及澳大利亚高等教育毕业说明书（AHEGS）上，都会注明 "
            "Awarded with distinction（优等授予）。",
        "Grade and description on academic transcripts for Chisholm "
        "Institute of Technology and Caulfield Institute of Technology.":
            "Chisholm Institute of Technology 与 Caulfield Institute of "
            "Technology 成绩单上的成绩等级与说明。",
        "Grade and description on academic transcripts for Monash "
        "University College Gippsland and Gippsland Institute of "
        "Advanced Education.":
            "Monash University College Gippsland 与 Gippsland Institute of "
            "Advanced Education 成绩单上的成绩等级与说明。",
        "Grade and description on academic transcripts for Monash "
        "before 1992.":
            "1992 年之前 Monash 成绩单上的成绩等级与说明。",
        "Grade and description on academic transcripts for course "
        "listed above.":
            "该学位课程成绩单上的成绩等级与说明。",
        "Grade and description on academic transcripts for the five "
        "courses listed above.":
            "上列五个学位课程成绩单上的成绩等级与说明。",
        "Grade and description on academic transcripts for the four "
        "courses listed above.":
            "上列四个学位课程成绩单上的成绩等级与说明。",
        "Grade and description on academic transcripts for the three "
        "courses listed above.":
            "上列三个学位课程成绩单上的成绩等级与说明。",
        "Grade and mark in academic transcripts before 1997.":
            "1997 年之前成绩单上的成绩等级与分数。",
        "Grade point average (GPA)":
            "GPA（平均绩点）",
        "Grade, description and dates of use in academic transcript "
        "results from 1992 to 2016.":
            "1992 至 2016 年成绩单上的成绩等级、说明及使用年份。",
        "Help with your results":
            "成绩方面需要帮助",
        "High level of achievement":
            "达成度较高",
        "Honours Discipline assessed over more than one year":
            "荣誉学位专业方向的评核跨越一年以上",
        "Incomplete (still to be assessed)":
            "未完成（尚待评核）",
        "NSR was also used in eligible teaching periods during "
        "2020–2021 to allow students to exclude failed units from "
        "their GPA/CGPA and WAM calculations. This was in recognition "
        "of the impact of the COVID-19 pandemic on their studies.":
            "2020–2021 年的部分开课学期也使用过 NSR，让学生可以把不及格课程排除在 GPA／CGPA 和 WAM "
            "的计算之外，以体谅新冠疫情对学业造成的影响。",
        "Next 10% of students":
            "其后 10% 的学生",
        "Next 20% of students":
            "其后 20% 的学生",
        "Next 40% of students":
            "其后 40% 的学生",
        "No Pass (Lower Standard)":
            "不及格（较低标准）",
        "Outstanding level of achievement":
            "达成度卓越",
        "Pass (Higher Standard)":
            "及格（较高标准）",
        "Pass (Lower Standard)":
            "及格（较低标准）",
        "Pass (No Higher Grade Available)":
            "及格（无更高等级可授）",
        "Pass Division II - Supplementary Examination":
            "及格 二等——补考",
        "Pass Grade Only. No higher grade available":
            "仅记及格，无更高等级可授",
        "Pass Laboratory Work":
            "实验课作业及格",
        "Pass after supplementary examination":
            "补考后及格",
        "Pass, Qualified to continue - No higher grade is awarded":
            "及格，具备继续修读资格——不授予更高等级",
        "Result Subject to Review":
            "成绩待复核",
        "Result annulled by Discipline Committee - deemed to be a "
        "failure":
            "成绩经纪律委员会裁定作废——视为不及格",
        "Results cancelled by Discipline Committee":
            "成绩经纪律委员会取消",
        "Results – reading your marks":
            "成绩——如何看懂分数",
        "SFR was also used in eligible teaching periods during "
        "2020–2021 to allow students to exclude units with a passing "
        "grade from their GPA/CGPA and WAM calculations. This was in "
        "recognition of the impact of the COVID-19 pandemic on their "
        "studies.":
            "2020–2021 年的部分开课学期也使用过 SFR，让学生可以把已及格的课程排除在 GPA／CGPA 和 WAM "
            "的计算之外，以体谅新冠疫情对学业造成的影响。",
        "Satisfactorily completed (ungraded)":
            "达标完成（不评等级）",
        "Supplementary Assessment Granted":
            "已获准补考",
        "The assessment marking is incomplete and a final grade has "
        "not yet been determined. This could be because:":
            "考核尚未评阅完毕，最终成绩等级还没确定。可能的原因有：",
        "This allowed students to exclude eligible units from their "
        "GPA/CGPA and WAM calculations by applying NSR to failed units "
        "and SFR to units with a passing grade.":
            "这使学生可以对不及格课程使用 NSR、对已及格课程使用 SFR，从而把符合条件的课程排除在 GPA／CGPA 和 WAM "
            "的计算之外。",
        "This grade is used to finalise a unit undertaken on a "
        "non-assessed, non-award basis.":
            "该成绩用于结清以「不评核、不计学位」方式修读的课程。",
        "This grade used to be awarded based on extreme circumstances, "
        "occuring or taking effect after the Withdrawn Fail period. "
        "The WI grade was not a passing grade because it meant you "
        "hadn’t completed the requirements of the unit. \n This grade "
        "is not included in GPA or WAM calculations and only applied "
        "to units that started before 22 July 2024. \nStudents are no "
        "longer awarded Withdrawn Incomplete grades.":
            "该成绩过去用于在 Withdrawn Fail 期之后发生或生效的极端情况。WI "
            "不是及格成绩，因为它意味着你没有完成该课程的要求。\n 该成绩不计入 GPA 或 WAM，且仅适用于 2024 年 7 月 "
            "22 日之前开始的课程。\n学校已不再授予 Withdrawn Incomplete（退课未完成）成绩。",
        "This table outlines the Monash grading system, providing a "
        "key to results on the academic record (transcript) according "
        "to the year of study. You should also refer to the Grading "
        "Schema Procedure (pdf, 0.30 mb).":
            "下表列出 Monash 的评分体系，按修读年份提供学业记录（成绩单）上成绩的对照说明。你也可以参阅 Grading "
            "Schema Procedure（成绩等级体系规程，pdf，0.30 mb）。",
        "Top 10% of students":
            "前 10% 的学生",
        "Weighted average mark (WAM)":
            "WAM（加权平均分）",
        "Withdrawal without penalty":
            "无处罚退课",
        "Withdrawn No Load or Withdrawn Late":
            "退课不计负荷，或逾期退课",
        "Withdrawn without Approval":
            "未经批准退课",
        "You haven’t fulfilled the unit requirements.":
            "你没有满足该课程的要求。",
        "You withdrew from this unit after the census date and before "
        "the Withdrawn Fail period. The WDN grade is not a pass grade, "
        "because the unit requirements have not been completed. This "
        "grade is not included in the WAM or GPA.":
            "你是在 census date（学籍统计日）之后、Withdrawn Fail 期之前退选这门课程的。WDN "
            "不是及格成绩，因为课程要求并未完成。该成绩不计入 WAM 或 GPA。",
        "You withdrew from this unit between the start of the "
        "Withdrawn Fail period and the end of the teaching period.":
            "你是在 Withdrawn Fail 期开始之后、开课学期结束之前退选这门课程的。",
        "You've been granted a supplementary assessment.":
            "你已获准补考。",
        "You’ve fulfilled the unit requirements.":
            "你已满足该课程的要求。",
        "during the official deferred assessment period":
            "在官方规定的延期考核期内",
        "or at a time determined by your faculty. They will email your "
        "Monash account with the details, giving you at least five "
        "University working days' notice.":
            "或由你所在学院另行确定时间。学院会把详情发到你的 Monash 邮箱，并至少提前五个学校工作日通知。",
        "the host institution for your Study Abroad or complementary "
        "units hasn't yet submitted your results from your time "
        "overseas":
            "你海外学习或辅修课程的接收院校尚未提交你在海外期间的成绩",
        "you have a pending academic misconduct investigation":
            "你有一项学术不端调查尚未了结",
        "you have an extension to finish outstanding assessment tasks":
            "你获得了延期，用于完成尚未做完的考核任务",
        "you haven’t finished all your assessments":
            "你还没有完成全部考核",
        "your assessment is still being marked and your final unit "
        "result will be updated shortly.":
            "你的考核仍在评阅中，该课程的最终成绩很快就会更新。",
    },
    "malaysia-student-pass": {
        "1. Explanation Letter of the reason for the change of course; "
        "2. Optional: Supporting documents":
            "1. 说明更换学位课程原因的说明信；2. 可选：证明材料",
        "1. If you are in Malaysia and planning to stay until the "
        "commencement of the new semester, you will need to ensure "
        "that your student pass is valid at all times. A Special Pass "
        "may apply to you if your student pass has expired/ will be "
        "expiring in 14 days. 2. If you are in Malaysia and planning "
        "to return to your home country until you receive an eVAL "
        "before returning to Malaysia. Please submit your passport to "
        "ISP (Building 2, Level 1) for the cancellation of your "
        "student pass.":
            "1. 如果你人在马来西亚，并打算一直留到新学期开学，就必须确保学生准证（student "
            "pass）始终在有效期内。若你的学生准证（student pass）已过期、或将在 14 "
            "天内到期，可能需要申请特别准证（Special Pass）。2. 如果你人在马来西亚，并打算先回国、等拿到 eVAL "
            "再返回马来西亚，请把护照交到 ISP（2 号楼 1 层）办理学生准证（student pass）注销。",
        "1. If your student pass exceeds one year validity, you will "
        "need to cancel your student pass, exit Malaysia and apply for "
        "a new student pass that takes eight (8) weeks processing "
        "time. 2. If your student pass is valid for a year: If you "
        "have studied less than a year of the current enrolled course, "
        "you do not need to exit Malaysia during your new student pass "
        "application processing. If you have studied more than a year "
        "of the current enrolled course, you will need to cancel your "
        "student pass, exit Malaysia and apply for a new student pass "
        "that takes eight (8) weeks processing time. 3. Application "
        "for a new student pass due to a change of course is permitted "
        "up to a maximum of two times throughout your period of study "
        "in Malaysia.":
            "1. 如果你的学生准证（student "
            "pass）有效期超过一年，需要先注销准证、离境马来西亚，再重新申请新的学生准证（student pass），办理约需 8 "
            "周。\n2. 如果你的学生准证（student "
            "pass）有效期为一年：当前所读学位课程就读不满一年的，在新准证办理期间无需离境；就读超过一年的，则需要注销准证、离境马来西亚，再重新申请新的学生准证（student "
            "pass），办理约需 8 周。\n3. 因更换学位课程而申请新学生准证（student "
            "pass），在你于马来西亚就读期间最多只能办理两次。",
        "1. Letter of confirmation of enrolment by your home "
        "institution on your home institution's letterhead that has "
        "been issued recently (must be entirely in English; otherwise, "
        "English translations must be stamped and verified by your "
        "home institution). You may refer to this sample; 2. Insurance "
        "coverage premium.":
            "1. "
            "由你所属院校出具、使用该校信笺抬头且近期签发的在读证明信（必须全文为英文；否则英文译本须经所属院校盖章确认）。可参考这份样本；2. "
            "保险费。",
        "1. Release Letter and attendance report (attendance should "
        "not be less than 80%); 2. A copy of the latest valid pass "
        "and/or exit stamp (if the previous pass has been cancelled "
        "and you are outside Malaysia). 3. Optional : A Special Pass "
        "may apply to you if you are in Malaysia and your pass has "
        "expired/ will be expiring in 14 days.":
            "1. 放行信（Release Letter）与出勤报告（出勤率不得低于 80%）；2. "
            "最新有效准证的复印件，和／或出境章（若原准证已注销且你人在马来西亚境外）。3. "
            "可选：如果你人在马来西亚，且准证已过期或将在 14 天内到期，可能需要申请特别准证（Special Pass）。",
        "Additional documents and/or actions required":
            "需要补充的材料和／或需要办理的事项",
        "After the Immigration Department of Malaysia approves your "
        "student pass application, you will receive an email "
        "notification from ISP. You may download a softcopy of your "
        "Electronic Visa Approval Letter, which is also known as eVAL.":
            "马来西亚移民局批准你的学生准证（student pass）申请之后，你会收到 ISP "
            "发来的邮件通知，并可以下载电子签证批准函（eVAL）的电子版。",
        "As an international student coming to study at the University "
        "for a full-time course, you must accept your offer and apply "
        "for a student pass before coming to Malaysia to start your "
        "course.":
            "作为来本校就读全日制学位课程的国际学生，你必须先接受录取并申请学生准证（student "
            "pass），然后才能来马来西亚开始学业。",
        "Before arriving Malaysia, you will need to ensure that you "
        "have prepared and completed the necessary pre-arrival steps "
        "as per the Entry Guideline and follow on with the arrival "
        "steps accordingly, as it is unlikely that you will have "
        "difficulties with the Immigration Officer upon arrival at the "
        "airport if you followed the steps provided.":
            "抵达马来西亚之前，你需要按照 Entry "
            "Guideline（入境指引）把行前各项准备做完，抵达后再依次完成入境步骤。按这些步骤办理的话，在机场遇到移民官时一般不会有麻烦。",
        "Changing course within Monash (Internal Course Transfer)":
            "在 Monash 内部更换学位课程（校内转课程）",
        "Country of citizenship":
            "国籍",
        "Do not make any arrangements to enter Malaysia until you have "
        "obtained the approval of your visa application.":
            "在签证申请获批之前，不要做任何入境马来西亚的安排。",
        "Documents required (softcopy):Additional documents and/or "
        "actions are required and to be provided during the submission "
        "of your student pass application if you are under these "
        "categories:":
            "所需材料（电子版）：如果你属于下列情形，提交学生准证（student pass）申请时还需要补充材料和／或办理其他事项：",
        "Exchange and Study Abroad":
            "交换与海外学习",
        "For Undergraduates and Post Graduate Coursework students, you "
        "can start applying for your student pass as early as four "
        "months but no later than two months before the commencement "
        "of your course.":
            "本科生和授课型研究生最早可在开课前四个月开始申请学生准证（student pass），但最迟不得晚于开课前两个月。",
        "For research students, please submit your request to amend "
        "your course commencement date in your offer letter if it is "
        "lesser than the minimum two months processing time.":
            "研究型学生如果距开课不足两个月的最短办理时间，请提交申请，修改录取通知书上的开课日期。",
        "Have you lodged an application for a Malaysian student pass "
        "before?":
            "你此前申请过马来西亚学生准证（student pass）吗？",
        "IMPORTANT The estimated Student Pass Endorsement processing "
        "time by the Immigration Department of Malaysia is 6 weeks. "
        "You are advised not to make any travel plans until your "
        "passport has been returned with your student pass sticker.":
            "重要提示：马来西亚移民局办理学生准证签注预计需要 6 周。在护照连同学生准证贴纸退回给你之前，建议不要做任何出行计划。",
        "If your student pass has expired/will be expiring in 14 days "
        "from the date of your submission to ISP, you will be advised "
        "to apply for a Special Pass. A Special Pass ensures you have "
        "a valid pass while your renewal application is being "
        "processed and is issued at the discretion of Immigration.If "
        "advised by ISP to apply for a Special Pass, please submit the "
        "following documents to ISP, Building 2 Level 1:Make payment "
        "for the Special Pass fee of RM300 and submit the proof of "
        "payment at the Finance Helpdesk.Do you have more questions? "
        "Fret not, we have a collection of frequently asked questions "
        "here.":
            "如果自你向 ISP 提交之日起，学生准证（student pass）已过期或将在 14 天内到期，ISP "
            "会建议你申请特别准证（Special "
            "Pass）。特别准证的作用是在续期申请办理期间让你保持有效身份，是否签发由移民局酌情决定。如果 ISP "
            "建议你申请，请把下列材料提交到 ISP（2 号楼 1 层）：并在 Finance Helpdesk（财务服务台）缴纳 "
            "RM300 特别准证费用、提交付款凭证。还有其他疑问？别担心，我们整理了一份常见问题集。",
        "Please follow the steps below1. Medical screening must be "
        "completed within seven (7) days at an EMGS appointed clinic "
        "or hospital. The nearest clinics to Monash University "
        "Malaysia are located in Subang Jaya. Please ensure that the "
        "clinic has an in-house X-ray facility for your convenience. "
        "Bring along the following:**You are only required to print "
        "the above documents2. Please drop by the ISP Counter located "
        "at Building 2, Level 1, with the following items:3. Wait for "
        "the release of your passport with the issuance of a student "
        "pass sticker. This process will take an estimated time of six "
        "(6) working weeks and you are not advised to make any travel "
        "arrangements without a physical passport.4. You will be "
        "notified via email once your passport is ready for "
        "collection.5. An i-Kad will be issued two weeks after you "
        "receive your passport. You will also receive an email "
        "notification from us once it is ready for collection. An "
        "i-Kad is an identification card for international students "
        "and can be used as a means of identification, but not as a "
        "replacement of your passport. A renewal of i-Kad for Direct "
        "Applicants (one-off) is required three months prior to expiry.":
            "请按下列步骤办理：\n1. 体检必须在 7 天内、到 EMGS 指定的诊所或医院完成。离 Monash "
            "马来西亚校区最近的诊所在 Subang Jaya。为方便起见，请确认该诊所自带 X "
            "光设备。请携带以下材料：**以上材料只需打印即可\n2. 请携带以下物品到 2 号楼 1 层的 ISP 柜台：\n3. "
            "等待护照连同已签发的学生准证贴纸退回。此过程预计需要 6 个工作周，在拿到实体护照之前，建议不要做出行安排。\n4. "
            "护照可领取时，我们会发邮件通知你。\n5. 领到护照两周后会发放 i-Kad。可以领取时我们同样会发邮件通知你。i-Kad "
            "是国际学生的身份识别卡，可用于证明身份，但不能替代护照。直接申请者（Direct Applicants）需在 i-Kad "
            "到期前三个月办理一次性续期。",
        "Please liaise with the respective Embassy in Malaysia for the "
        "required document if you are a citizen from: Iran - Letter of "
        "Eligibility (LOE) . Oman - No Objection Letter (NOL) . Sudan "
        "- No Objection Certificate (NOC) . Libya - Letter of "
        "Eligibility (LOE) .":
            "如果你是下列国家的公民，请与该国驻马来西亚使馆联系，取得所需文件：伊朗——Letter of "
            "Eligibility（LOE，资格函）；阿曼——No Objection Letter（NOL，无异议函）；苏丹——No "
            "Objection Certificate（NOC，无异议证明）；利比亚——Letter of "
            "Eligibility（LOE，资格函）。",
        "Progressing or transferring from another institution":
            "从其他院校升学或转学而来",
        "Progressing within Monash":
            "在 Monash 内部升学",
        "Students coming for an exchange or study abroad program must "
        "apply directly with EMGS for one (1) semester , and must "
        "apply for a student pass duration of six (6) months , while "
        "students attending two (2) semesters must apply for a student "
        "pass duration of twelve (12) months .":
            "参加交换或海外学习项目的学生必须直接向 EMGS 申请：读一个学期的，申请 6 个月有效期的学生准证（student "
            "pass）；读两个学期的，申请 12 个月有效期的学生准证（student pass）。",
        "You are required to opt for DIRECT STUDENT PASS APPLICATION* "
        "where you have to apply directly to EMGS . Read this guide "
        "prior to applying for your student pass. *All direct "
        "applicants are advised to apply for a one-off student pass "
        "which covers the entire course duration.":
            "你需要选择 DIRECT STUDENT PASS APPLICATION（直接申请）*，即自行向 EMGS "
            "提交申请。申请前请先阅读这份指南。*建议所有直接申请者申请一次性覆盖整个学位课程期限的学生准证（student pass）。",
        "You are required to opt for NON-DIRECT STUDENT PASS "
        "APPLICATION where Monash will apply for your student pass. "
        "Fill out this form to start applying for your student pass.":
            "你需要选择 NON-DIRECT STUDENT PASS APPLICATION（非直接申请），即由 Monash "
            "代你提交学生准证（student pass）申请。请填写这份表格开始办理。",
        "You may check the status of your student pass application "
        "after 14 working days upon submitting the complete documents "
        "and payment to either EMGS (DA) or through the University "
        "(NDA).":
            "在向 EMGS（直接申请）或学校（非直接申请）提交完整材料并付款后，满 14 个工作日即可查询学生准证（student "
            "pass）申请进度。",
    },
    "malaysia-insurance": {
        "100 % Capital Sum Insured":
            "保额的 100%",
        "Accidental Death on Public Common Conveyance":
            "乘坐公共交通工具时的意外身故",
        "All Monash University Malaysia students are covered in this "
        "policy.":
            "Monash 马来西亚校区全体学生均在本保单承保范围内。",
        "For more information about the policy, kindly refer to the "
        "full policy.":
            "关于本保单的更多信息，请查阅完整保单条款。",
        "Group Personal Accident (GPA) Insurance Policy":
            "团体人身意外险（GPA）保单",
        "International Student Insurance":
            "国际学生保险",
        "International Travel Insurance":
            "国际旅行保险",
        "International students with a valid Student Pass studying at "
        "Monash University Malaysia.":
            "在 Monash 马来西亚校区就读、且持有有效学生准证（Student Pass）的国际学生。",
        "Kindly refer to the information page on medical insurance for "
        "international students website for more details.":
            "更多细节请查看国际学生医疗保险信息页。",
        "Kindly refer to the information page on medical insurance for "
        "international students website.":
            "请查看国际学生医疗保险信息页。",
        "Medical Reimbursement":
            "医疗费用报销",
        "Monash University Malaysia has appointed AXA Affin General "
        "Insurance Berhad as our Medical Insurance provider with "
        "effect from 1st January 2021.":
            "自 2021 年 1 月 1 日起，Monash 马来西亚校区指定 AXA Affin General Insurance "
            "Berhad 为医疗保险承保方。",
        "Monash University Malaysia has appointed Willis Tower Watson "
        "as our insurance broker and AIG Malaysia Insurance Berhad as "
        "our provider for the Group Personal Accident insurance.":
            "Monash 马来西亚校区指定 Willis Tower Watson 为保险经纪，AIG Malaysia "
            "Insurance Berhad 为团体人身意外险的承保方。",
        "Monash University Malaysia students studying abroad on "
        "University-approved programs only.":
            "仅限参加学校批准项目、在海外学习的 Monash 马来西亚校区学生。",
        "Permanent Disablement":
            "永久伤残",
        "Policy Summary: Sum Insured: RM 30,000Main benefits :":
            "保单摘要：保额 RM 30,000。主要保障：",
        "RM 2,000":
            "RM 2,000",
        "RM 30,000":
            "RM 30,000",
        "The Student Group Personal Accident policy also provides "
        "coverage during internship or placement periods.":
            "学生团体人身意外险在实习或实践期间同样提供保障。",
        "The policy number is HCR/04697625/64.":
            "保单号为 HCR/04697625/64。",
        "The policy number is PA20002720.":
            "保单号为 PA20002720。",
        "The travel insurance provider is Liberty International "
        "Underwriters":
            "旅行保险的承保方为 Liberty International Underwriters",
        "Up to RM 3,000":
            "最高 RM 3,000",
        "Up to RM 30,000.00":
            "最高 RM 30,000.00",
        "Up to RM 5,000":
            "最高 RM 5,000",
        "We ensure that you are all covered with the required "
        "insurance coverage while studying in Monash Malaysia.":
            "我们会确保你在 Monash 马来西亚校区就读期间，都有所需的保险保障。",
        "You may submit your claim here.":
            "理赔申请请在此提交。",
    },
    "malaysia-student-admin": {
        "Assessments & Results":
            "考核与成绩",
        "Check out here for Student forms, application for student "
        "letters, MPass cards, official documents and education "
        "verifications.":
            "学生表格、学生证明信申请、MPass 卡、正式文件与学历验证，都在这里。",
        "Find out how to apply to graduate so that you receive your "
        "award at the earliest possible time.":
            "了解如何申请毕业，好尽早拿到你的学位。",
        "Find out when exams are held and when results are released.":
            "了解考试什么时候进行、成绩什么时候公布。",
        "For information on when you can re-enrol, exam dates, results "
        "release and those all important census dates.":
            "关于什么时候可以重新注册、考试日期、成绩公布，以及那些至关重要的 census dates（学籍统计日）。",
        "Graduations & Verify Qualifications":
            "毕业与学历验证",
        "Learn how to setup your class timetable and avoid potential "
        "clashes":
            "了解如何排课表，以及怎样避开可能的时间冲突",
        "Online Forms Now Available!":
            "在线表格现已开放！",
        "STUDENT ADMINISTRATION\nHow can we assist you?":
            "学生事务\n有什么可以帮你？",
        "Student administration - Monash University Malaysia":
            "学生事务 — Monash 马来西亚校区",
        "Student forms, Letters, Documents & Identity":
            "学生表格、证明信、文件与身份证件",
        "Try out the course planner here. Plan your course and select "
        "the right units.":
            "试试这里的课程规划工具，规划你的学位课程、选对课程。",
        "Whether you are new to Monash or re-enrolling, find out how "
        "to manage your enrolment.":
            "无论你是刚来 Monash 还是要重新注册，都可以在这里了解如何管理自己的选课注册。",
    },
    "malaysia-exam-rules": {
        "Bag":
            "包袋",
        "Books, study materials":
            "书籍、学习资料",
        "Calculators":
            "计算器",
        "Cap, hooded top":
            "帽子、连帽上衣",
        "Cheating can come in many forms, and can occur in exams and "
        "other types of assessments. To cheat could be to copy the "
        "work of others, to get someone to do your assessment for you, "
        "or to bring unauthorised materials into an eExam. Cheating "
        "breaches academic integrity and Monash University has various "
        "methods of detecting it.":
            "作弊有很多种形式，可能发生在考试里，也可能发生在其他类型的考核中。抄袭他人作业、找人代做考核、把未经许可的材料带进 "
            "eExam（线上考试），都属于作弊。作弊违反学术诚信，Monash 大学也采用多种方法侦测作弊行为。",
        "Cheating is a very serious offence and could result in "
        "suspension or exclusion from the University.":
            "作弊是非常严重的违规行为，可能导致停学或被学校退学处理（exclusion）。",
        "Closed-book exams don’t allow you to take notes, books or any "
        "other reference material into the exam. You need to rely "
        "entirely on your memory to answer questions.":
            "闭卷考试不允许你带笔记、书本或任何其他参考资料进场，只能完全靠记忆作答。",
        "Closed-book remote eExams":
            "远程闭卷 eExam（线上考试）",
        "Clock":
            "计时器",
        "Dictionaries (electronic)":
            "词典（电子版）",
        "Dictionaries (hard copy)":
            "词典（纸质版）",
        "During the eExam, you must not have a calculator, pencil "
        "case, mobile phone, smart watch/device, or any books, notes, "
        "paper, writing on any part of your body, or any other "
        "materials which haven’t been authorised for the exam. "
        "Possession of unauthorised materials, or attempting to cheat "
        "or cheating in an exam, is a disciplinary offence.":
            "考试期间不得携带计算器、笔袋、手机、智能手表或智能设备，也不得有任何书本、笔记、纸张、写在身体任何部位的字迹，或其他未经本场考试许可的材料。持有未经许可的材料、试图作弊或在考试中作弊，均属于纪律违规。",
        "During your exam, you must not speak with other students or "
        "persons outside the University. You should only communicate "
        "with your online supervisor or exam staff. Colluding with "
        "others to gain an unfair advantage in your assessment is a "
        "disciplinary offence.":
            "考试期间不得与其他学生或校外人员交谈，只能与线上监考员或考务人员沟通。与他人串通以在考核中取得不正当优势，属于纪律违规。",
        "If your eExam is supervised, you must stay in sight of your "
        "webcam throughout the eExam session. If you need to leave the "
        "room to use the toilet, you’ll need to leave your phone and "
        "any exam materials in the exam room in front of the camera so "
        "it’s visible. The session will continue to be recorded while "
        "you’re out of the room.":
            "如果你的 "
            "eExam（线上考试）有监考，全程都必须待在摄像头可见范围内。如需离开房间上洗手间，要把手机和所有考试材料留在考场内、放在摄像头前可见的位置。离开房间期间，考试会话仍会继续录制。",
        "Learn more about academic integrity, plagiarism and collusion.":
            "进一步了解学术诚信、抄袭与合谋作弊。",
        "Mask-wearing is required for indoor settings and optional in "
        "an outdoor setting. You’ll also need to use the hand "
        "sanitiser provided on arrival and follow social distancing "
        "guidelines.":
            "室内须佩戴口罩，室外可自行选择。抵达时还需使用现场提供的免洗洗手液，并遵守社交距离规定。",
        "Monash University is committed to honesty and academic "
        "integrity. There are serious consequences for plagiarism, "
        "collusion and cheating.":
            "Monash 大学重视诚实与学术诚信。抄袭、合谋作弊和作弊都会带来严重后果。",
        "On-campus eExams eExams with online supervision: You’ll need "
        "to bring a headset or headphones with a built-in microphone "
        "so you can communicate with your online supervisor clearly "
        "and minimise disruption to other students in the same exam "
        "room. eExams without online supervision: You can use the "
        "noise-cancelling function of headphones, or earplugs, to "
        "minimise distractions. Off-campus eExams Headsets or "
        "headphones with a built-in microphone are optional for "
        "off-campus supervised eExams. They must be used only for "
        "communicating with your online supervisor. You’re not allowed "
        "to listen to music, audio files or speak with anyone other "
        "than your online supervisor during your exam.":
            "校内 eExam（线上考试）：有线上监考时，你需要自带带麦克风的耳机或耳麦，以便与线上监考员清楚沟通，同时尽量不打扰同一考场的其他学生；无线上监考时，可以使用耳机的降噪功能或耳塞来减少干扰。校外 eExam（线上考试）：校外有监考的场次可以选择使用带内置麦克风的耳机或耳麦，但只能用于与线上监考员沟通。考试期间不得听音乐或音频文件，也不得与线上监考员以外的任何人交谈。",
        "Open-book exams allow you to access notes, texts or resource "
        "materials in your exam.":
            "开卷考试允许你在考试中查阅笔记、教材或参考资料。",
        "Open-book remote eExams":
            "远程开卷 eExam（线上考试）",
        "Exam Rules":
            "考试规则",
        "Face masks":
            "口罩",
        "Food and drink":
            "食物和饮料",
        "Headphones":
            "耳机或耳麦",
        "Item":
            "物品",
        "No":
            "不允许",
        "Notes":
            "笔记",
        "Paper, including blank A4 paper":
            "纸张，包括空白 A4 纸",
        "Pencil cases":
            "笔袋",
        "Smartphones":
            "智能手机",
        "Specifically permitted items":
            "特别许可物品",
        "Stationery":
            "文具",
        "There is an inbuilt timer on your eExam screen that will "
        "count down the time you have left.":
            "eExam（线上考试）界面自带计时器，会倒数你剩余的时间。",
        "This information will also appear on the landing page of your "
        "eExam. You should read this information carefully before you "
        "start your eExam and make sure all of your materials and "
        "devices are authorised. We'll regard any material or item on "
        "your desk, chair, or person to be in your possession. Having "
        "any unauthorised materials in an exam is a disciplinary "
        "offence.":
            "这些信息也会显示在 "
            "eExam（线上考试）的首页上。开考前请仔细阅读，确认你的所有材料和设备都是经许可的。桌面、椅子或你身上的任何材料或物品，都会被视为由你持有。在考试中持有任何未经许可的材料，均属于纪律违规。",
        "To ensure you get your full exam time, log into the "
        "eAssessment platform 30 minutes before the scheduled start "
        "time (if it’s supervised) or 10 minutes before if you have an "
        "exam without supervision.":
            "为确保你能用满全部考试时间：有监考的，请在预定开始时间前 30 分钟登录 eAssessment 平台；无监考的，请提前 "
            "10 分钟登录。",
        "Watches (digital and smart watches)":
            "手表（电子表与智能手表）",
        "What you’re allowed to bring to your eExam":
            "eExam（线上考试）可以带什么",
        "Where any of our monitoring identifies a suspected breach of "
        "exam rules, footage of your exam session and session logs may "
        "be referred to a Monash faculty administrator for "
        "investigation. See privacy and security for more information.":
            "如果监控发现疑似违反考试规则的情况，你本场考试的录像和会话日志可能会被移交 Monash "
            "学院管理人员进行调查。详见隐私与安全说明。",
        "Yes, but you’re not allowed to access soft copy notes on the "
        "device you’re using for your eExam (unless specifically "
        "instructed by your teaching staff or faculty).":
            "可以，但不得在你用来考 eExam（线上考试）的那台设备上查看电子版笔记（除非任课教师或学院另有明确指示）。",
        "Yes":
            "允许",
        "Yes, food and drink are allowed in your private exam space. "
        "If you have an on-campus eExam, please ensure any food you "
        "bring with you won't disturb those around you.":
            "可以，你自己的考试空间里允许饮食。如果是校内 eExam（线上考试），请确保带来的食物不会打扰周围的人。",
        "Yes. You can have blue or black pens or HB/2B pencils. You "
        "can't have glitter ink pens, as the ink may affect the photo "
        "quality of any handwritten responses that may be required.":
            "可以。你可以带蓝色或黑色的笔，以及 HB/2B 铅笔。不能用闪粉墨水笔，因为墨水会影响手写作答拍照的清晰度。",
        "You can check your unit’s Moodle page to find out if:":
            "你可以在该课程的 Moodle 页面上查看：",
        "You can have your smartphone with you, but it must be "
        "switched to 'do not disturb' mode and placed face down on "
        "your desk. You'll need to use your phone to log in to your "
        "eExam with multi-factor authentication and again, at the end "
        "of your exam, to upload photographs of any required "
        "handwritten responses – don't access your phone until the "
        "instructions appear on your screen.":
            "你可以带智能手机，但必须调到「勿扰」模式并正面朝下放在桌上。手机的用途是：用多因素认证登录 "
            "eExam（线上考试），以及在考试结束时上传手写作答的照片（如需要）。在屏幕出现相关指示前，不得使用手机。",
        "You can wear a cap or hooded top, but you may be asked to "
        "remove it as part of your online supervision so we can verify "
        "your identity. Your online supervisor may ask you to remove "
        "your hood at any time.":
            "你可以戴帽子或穿连帽上衣，但线上监考为核验身份可能要求你摘下帽子或放下帽兜。线上监考员可以随时要求你放下帽兜。",
        "You can’t cancel or reschedule your eExam. By starting your "
        "eExam, you’re confirming that you’re well enough to do the "
        "exam. If you suddenly become unwell during your exam, tell "
        "your supervisor straight away – they’ll tell you what you "
        "need to do. We recommend you try to finish your exam if "
        "you’re able to because in most circumstances, if you’ve seen "
        "and/or attempted to answer the exam questions, you won't be "
        "eligible for a deferred assessment.":
            "你不能取消或改期 "
            "eExam（线上考试）。一旦开考，就等于确认自己身体状况适合参加考试。如果考试中途突然不适，请立刻告知监考员，他们会告诉你该怎么做。如果身体状况允许，建议尽量完成考试；在大多数情况下，如果你已经看过试题或尝试作答，就不再符合延期考核的申请条件。",
        "You must have your M-Pass (student ID card) or a "
        "government-issued photo ID (e.g. your passport) if you’re "
        "sitting a supervised eExam or an unsupervised eExam on "
        "campus. If you have a supervised eExam, your webcam and "
        "microphone must be working – if the online supervisor can't "
        "see or hear you, you won't be allowed to sit your eExam.":
            "参加有监考的 eExam（线上考试）、或在校内参加无监考 eExam（线上考试）时，必须携带 "
            "M-Pass（学生证）或政府签发的带照片身份证件（例如护照）。有监考的场次，摄像头和麦克风必须正常工作；如果线上监考员看不到或听不到你，你将无法参加 eExam（线上考试）。",
        "You must remove your smartwatch and place it face down on "
        "your desk for the duration of your eExam. The eExam on-screen "
        "timer will show you how much exam time you have left.":
            "整场 eExam（线上考试）期间，必须摘下智能手表并正面朝下放在桌上。屏幕上的计时器会显示你还剩多少考试时间。",
        "Your exam duration includes reading time; however, you can "
        "start answering as soon as the exam begins if you want to.":
            "考试时长包含阅读时间；不过如果你愿意，开考即可开始作答。",
        "Your lecturer can confirm whether your eExam is an open or "
        "closed-book assessment.":
            "你的 eExam（线上考试）是开卷还是闭卷，可以向任课教师确认。",
        "Your lecturer will tell you if there are any specifically "
        "permitted items you need to take into your exam. These will "
        "also be listed on your exam home screen if they apply. For "
        "example, you may be permitted to use a translation dictionary "
        "for your exam or a single A4 page of pre-prepared notes.":
            "如果有特别许可携带进考场的物品，任课教师会告知你；适用时，这些物品也会列在考试首页上。例如，某些考试可能允许你使用翻译词典，或携带一张预先写好笔记的 A4 纸。",
        "Your personal belongings are allowed to be in the room, but "
        "they must not be in reach during your exam.":
            "个人物品可以放在房间里，但考试期间不得放在伸手可及之处。",
        "Your phone must be switched to 'do not disturb' mode and "
        "placed faced down on your desk. You must only use your phone "
        "to log in to your eExam with multi-factor authentication and, "
        "at the end off your exam, to upload photographs of any "
        "required handwritten responses – don’t access your phone "
        "until the instructions appear on your screen.":
            "手机必须调到「勿扰」模式并正面朝下放在桌上。只能用于两件事：用多因素认证登录 "
            "eExam（线上考试），以及在考试结束时上传所需的手写作答照片。在屏幕出现相关指示前，不得使用手机。",
        "You’ll need to check with your lecturer to see whether your "
        "exam requires the use of a calculator and, if so, whether "
        "there are restrictions on the type you’re allowed to use.":
            "你需要向任课教师确认本场考试是否需要用计算器，以及对可用机型是否有限制。",
        "You’re only allowed to have sheets of paper with you if "
        "they’re authorised for your exam. Check the list of "
        "authorised materials on your unit’s Moodle page and the "
        "landing page of your eExam.":
            "只有经本场考试许可的纸张才可以带在身边。许可材料清单请查看该课程的 Moodle 页面，以及 eExam（线上考试）的首页。",
        "USB devices":
            "USB 设备",
        "eExam rules":
            "eExam（线上考试）规则",
        "the eExam spell check function will be disabled.":
            "eExam（线上考试）的拼写检查功能会被停用。",
        "you need any additional authorised materials or approved "
        "devices":
            "你是否需要额外的许可材料或经批准的设备",
    },
    "malaysia-special-consideration": {
        "A few important tips...":
            "几点提醒……",
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
        "Assessment Regime Procedure (pdf)":
            "Assessment Regime Procedure（考核制度规程，pdf）",
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
        "Defer your final assessment":
            "申请期末考核延期",
        "Extension through special consideration (generally longer)":
            "通过特殊考虑（special consideration）申请延期（时长通常更久）",
        "Extensions and special consideration":
            "延期与特殊考虑（special consideration）",
        "Get a short extension":
            "申请短期延期",
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
        "instead)":
            "如果延期并不合适，我们可能会为你安排一种替代的、难度相当的考核形式。如果你的申请结果是替代考核，你就必须完成它（不能改成延期）",
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
        "If we approve your application, you’ll get an extension of "
        "two calendar days from the original due date of the "
        "assessment task.":
            "如果申请获批，你将从考核任务的原定截止日起获得 2 个日历日的延期。",
        "If we don’t approve your application, you’ll still need to "
        "submit your assessment.":
            "如果申请未获批，你仍然需要提交考核。",
        "If you apply and get an extension, it doesn’t guarantee that "
        "the rest of your group will be granted one as well. Your "
        "chief examiner will decide which outcome best suits your "
        "circumstances and let you know.":
            "你申请并拿到延期，并不代表小组里其他人也会一并获批。主考官（chief "
            "examiner）会判断哪种处理最符合你的情况，并通知你。",
        "If you give false information":
            "提供虚假信息的后果",
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
        "If you’ve already been given a short extension for an "
        "assessment but you need more time, you’ll need to then apply "
        "for an extension through special consideration with "
        "supporting documents.":
            "如果你已经为某项考核拿到短期延期但仍需更多时间，接下来需要通过特殊考虑（special "
            "consideration）申请延期，并提交证明材料。",
        "If you’ve already been given an extension but you're unable "
        "to complete your assessment by the revised due date, you’ll "
        "need to submit a new application with new supporting "
        "documents. Your supporting documents must explain why you are "
        "unable to complete your assessment by the revised due date "
        "and how much longer you need.":
            "如果你已经拿到过延期，但仍无法在新截止日前完成考核，就需要提交一份新申请和新的证明材料。材料中必须说明你为何无法在新截止日前完成，以及还需要多久。",
        "In-class assessments and mid-semester tests":
            "课堂考核与期中测验",
        "Long-term or ongoing circumstances":
            "长期或持续性的情况",
        "Marking and Feedback Procedure (pdf)":
            "Marking and Feedback Procedure（评分与反馈规程，pdf）",
        "Medical certificate from UHS\n \nYou can get a medical "
        "certificate from a Monash University Health Services (UHS) "
        "doctor to support your application for special consideration.":
            "UHS 开具的 medical certificate（医疗证明）\n \n你可以找 Monash University "
            "Health Services（UHS，校内医疗服务）的医生开具 medical "
            "certificate（医疗证明），用于支持你的特殊考虑（special consideration）申请。",
        "Medical documentation clarifications":
            "医疗材料要求说明",
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
        "Need an extension?":
            "需要延期？",
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
        "Reschedule your deferred assessment":
            "为延期考核改期",
        "Short extension (two calendar days)":
            "短期延期（两个日历日）",
        "Some assessments will require complex arrangements to be put "
        "in place and additional time may be needed to assess your "
        "application and provide an outcome.":
            "有些考核需要安排的事项比较复杂，评估你的申请并给出结果可能需要更长时间。",
        "Special Consideration Procedure (pdf)":
            "Special Consideration Procedure（特殊考虑规程，pdf）",
        "Successful application":
            "申请获批",
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
        "When you apply for an extension through special "
        "consideration, you need to provide supporting documents to "
        "show why you can’t complete your assessment as scheduled due "
        "to immediate and exceptional circumstances beyond your "
        "control. Make sure to apply as soon as possible, but no later "
        "than 11.55pm on the day your assessment is due.":
            "通过特殊考虑（special "
            "consideration）申请延期时，你需要提交证明材料，说明自己为何因突发且无法控制的特殊情况而不能按时完成考核。请尽快提出申请，最迟不得晚于考核截止当天 "
            "23:55。",
        "When you apply for an extension, you must give us information "
        "that’s true, accurate and complete, without intending to "
        "mislead or gain advantage. If you make a false statement or "
        "provide a falsified supporting document, we won't approve "
        "your application and we'll refer the matter to Student "
        "Conduct and Complaints to investigate for academic misconduct.":
            "申请延期时，你提供的信息必须真实、准确、完整，不得有误导或谋取便利的意图。如果你作出虚假陈述，或提交伪造的证明材料，我们不会批准你的申请，并会将此事移交 "
            "Student Conduct and Complaints（学生行为与投诉办公室）按学术不端立案调查。",
        "When you’re not eligible":
            "不符合条件的情形",
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
        "a group assessment":
            "小组考核",
        "a mid-semester test":
            "期中测验",
        "a practical assessment (including laboratories)":
            "实践考核（含实验课）",
        "a scheduled final assessment.":
            "已排定的期末考核。",
        "all the members of your group might be granted an extension.":
            "小组全体成员可能一并获得延期。",
        "an in-class test/assessment (including presentations)":
            "课堂测验或课堂考核（含口头报告）",
        "disruption caused by international conflict":
            "国际冲突造成的影响",
        "family (relationship breakdown)":
            "家庭（关系破裂）",
        "financial/employment issues":
            "经济或就业问题",
        "gender-based violence":
            "性别暴力",
        "losing your Moodle access because you didn’t complete a "
        "compulsory module":
            "因为没完成必修模块而被停用 Moodle",
        "loss or bereavement":
            "亲人离世与哀伤",
        "loss or bereavement: death of a person with whom you had a "
        "significant relationship":
            "亲人离世与哀伤：与你有重要关系的人过世",
        "medical condition (including COVID-19)":
            "健康问题（含新冠）",
        "mental health condition":
            "心理健康问题",
        "military, jury or emergency services obligations":
            "兵役、陪审团或紧急救援服务义务",
        "mistaking your assessment due date":
            "记错了考核截止日期",
        "obligations as athlete, artist or performer registered with "
        "Elite Student Performer Scheme or as representative of "
        "University in other key events and programs":
            "作为已在 Elite Student Performer "
            "Scheme（ESPS，精英学生表现者计划）登记的运动员、艺术家或表演者所负的义务，或代表学校参加其他重要赛事和项目的义务",
        "other exceptional circumstances beyond your control.":
            "其他你无法控制的特殊情况。",
        "other extreme circumstances.":
            "其他极端情况。",
        "religious or cultural obligations":
            "宗教或文化义务",
        "representing a club or society as a volunteer":
            "以志愿者身份代表某个社团或学会",
        "scheduled final assessment (exam) (apply for a deferred "
        "assessment instead).":
            "已排定的期末考核（考试）——请改为申请延期考核。",
        "serious and debilitating medical condition":
            "严重且使人失能的健康问题",
        "severe mental health condition":
            "严重心理健康问题",
        "technical disruption":
            "技术故障",
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
    },
    "academic-transcripts": {
        "About your academic record":
            "关于你的学业记录",
        "Academic records (transcripts)":
            "学业记录（成绩单）",
        "Access your transcript in My eQuals (you’ll receive an email "
        "with instructions).":
            "在 My eQuals 中获取成绩单（我们会发邮件告诉你具体怎么做）。",
        "An academic record (or transcript) is a formal record of your "
        "academic history at the University. You’ll get a free "
        "transcript, in digital format, when you graduate.":
            "学业记录（academic record，也叫 transcript "
            "成绩单）是你在本校学业历程的正式记录。毕业时你会免费获得一份电子版成绩单。",
        "As a past student, you can buy your official academic record "
        "(transcript) in digital format.":
            "作为往届学生，你可以购买电子版的正式学业记录（成绩单）。",
        "At the top of the screen, select your name to see the "
        "drop-down menu.":
            "点击页面顶部你的姓名，展开下拉菜单。",
        "At the top right of the screen, select your name to see a "
        "drop-down menu.":
            "点击页面右上角你的姓名，展开下拉菜单。",
        "Award certificate (testamur)":
            "学位证书（testamur）",
        "Before ordering a transcript, you’ll need to check your "
        "details are up to date in the Web Enrolment System (WES).":
            "订购成绩单之前，请先在 WES（学生系统）里确认你的个人信息是最新的。",
        "Before viewing your documents, you’ll need to make sure your "
        "personal email address is verified in My eQuals:":
            "查看文件之前，需要先确认你的个人邮箱已在 My eQuals 中通过验证：",
        "Check if I'm course completed":
            "查看我是否已完成学位课程",
        "Check your email for how to activate your account.\nIf you "
        "don’t see the activation email, check your spam folder or "
        "click Can’t sign in?":
            "查收邮件，按说明激活账户。\n如果没看到激活邮件，请查看垃圾邮件文件夹，或点击 Can't sign in?（无法登录？）",
        "Check your email for how to activate your account. \nIf you "
        "don’t see the activation email, check your spam folder or "
        "click Can’t sign in?":
            "查收邮件，按说明激活账户。\n如果没看到激活邮件，请查看垃圾邮件文件夹，或点击 Can't sign in?（无法登录？）",
        "Check your inbox for the verification email from My eQuals "
        "and select Verify.":
            "在收件箱中找到 My eQuals 发来的验证邮件，点击 Verify（验证）。",
        "Click Account settings.":
            "点击 Account settings（账户设置）。",
        "Click Profile settings.":
            "点击 Profile settings（个人资料设置）。",
        "Click Submit Request\nYou’ll see a request summary and be "
        "asked whether you want to make another request":
            "点击 Submit Request（提交申请）\n你会看到申请摘要，并被询问是否要再提交一份申请",
        "Click on your name on the top-right corner of the screen.":
            "点击页面右上角你的姓名。",
        "Courier fee (contact Monash Connect for exact fee based on "
        "location) in addition to hard-copy fee: $31–$93":
            "在纸质版费用之外另加快递费（具体金额视寄送地区而定，请联系 Monash Connect（学生服务中心）确认）：31–93 "
            "澳元",
        "Digital (My eQuals portal): $26":
            "电子版（My eQuals 门户）：26 澳元",
        "Enter your credit or debit card details and click Pay Now.":
            "填写信用卡或借记卡信息，点击 Pay Now（立即支付）。",
        "Enter your personal email address.":
            "填入你的个人邮箱地址。",
        "For details on how My eQuals collects and handles your "
        "personal information, see the My eQuals HES Privacy Policy.":
            "My eQuals 如何收集和处理你的个人信息，详见 My eQuals HES 隐私政策。",
        "For faster overseas delivery, you can make a payment and "
        "arrange for Express Post delivery by calling Monash Connect "
        "on +61 3 9902 6011. This can take up to two weeks.":
            "寄往海外若想更快，可以致电 Monash Connect（学生服务中心）+61 3 9902 6011 付款并安排 "
            "Express Post 快递，最长约需两周。",
        "For more information, see course completion.":
            "更多信息见「学位课程完成」。",
        "For more information, see how to view your graduation "
        "documents.":
            "更多信息见「如何查看你的毕业文件」。",
        "GPA – Grade Point Average":
            "GPA — 平均绩点",
        "Go to Account settings.":
            "进入 Account settings（账户设置）。",
        "Graduates and past students":
            "毕业生与往届学生",
        "Graduation statement (AHEGS)":
            "毕业说明书（AHEGS）",
        "Hard copies take five to ten days to deliver (or three to "
        "five weeks if you’re overseas).":
            "纸质版寄送需要 5 至 10 天（寄往海外则需 3 至 5 周）。",
        "Hard copy (standard mail): $53":
            "纸质版（普通邮寄）：53 澳元",
        "How to order your digital academic record":
            "如何订购电子版学业记录",
        "How to order your digital record":
            "如何订购电子版记录",
        "How to use My eQuals":
            "怎么用 My eQuals",
        "If you can't log in because you've forgotten your details, "
        "you can recover your login through the My eQuals portal – "
        "just select Can’t sign in? on the login screen.If this isn’t "
        "the problem, there could be a few reasons why you’re not able "
        "to log into My eQuals.You need to sign into My eQuals with "
        "the personal (non-Monash) email address you provided in WES "
        "when you applied to graduate. You’ll receive an email a few "
        "weeks after your graduation round confirming the email "
        "address you need to use.You’ll only be able to log in and see "
        "your digital transcript if your My eQuals account uses the "
        "same personal email address you have in WES.Haven’t received "
        "the emailIf you're unsure what non-Monash email you provided, "
        "and you haven't received the email with your sign-up details, "
        "check your email spam folder. If it's not there, contact "
        "Monash Connect for help.Changed personal email addressIf "
        "you’ve changed your personal email address and now you can’t "
        "sign into My eQuals, get in touch with Monash Connect.":
            "如果因为忘了登录信息而进不去，可以在 My eQuals 门户找回——在登录页点击 Can't sign "
            "in?（无法登录？）即可。如果问题不在这里，登不上 My eQuals 还可能有别的原因。你必须用申请毕业时在 "
            "WES（学生系统）里填写的个人邮箱（非 Monash 邮箱）登录 My "
            "eQuals。毕业批次结束后几周，你会收到一封邮件，确认应当使用哪个邮箱地址。只有当你的 My eQuals "
            "账户使用的邮箱与 WES 里填的那个一致时，你才能登录并看到电子成绩单。没收到邮件：如果你不确定当初填的是哪个非 "
            "Monash 邮箱，又没收到含注册信息的邮件，请先看垃圾邮件文件夹；仍然没有的话，请联系 Monash "
            "Connect（学生服务中心）求助。换过个人邮箱：如果你换了个人邮箱、现在登不上 My eQuals，请联系 Monash "
            "Connect（学生服务中心）。",
        "If you’re a past student, you can buy digital letters for up "
        "to 12 months after you’ve been course completed.":
            "如果你已经毕业，在学位课程完成后的 12 个月内都可以购买电子版证明信。",
        "If you’re currently enrolled at Monash University, you can "
        "buy an official academic record in digital format. You’ll "
        "also be able to provide potential employers (and other "
        "people) with a link so they can view a verified copy of the "
        "transcript online.":
            "如果你目前在 Monash "
            "大学在读，可以购买电子版的正式学业记录。你还可以把一个链接发给潜在雇主（或其他人），让他们在线查看经过验证的成绩单副本。",
        "In the week following your graduation round, you’ll receive "
        "your official academic record in digital format. We'll email "
        "you once it’s available.":
            "毕业批次结束后的那一周，你会收到电子版的正式学业记录。可以领取时我们会发邮件通知你。",
        "Link your account to your personal email":
            "把账户与你的个人邮箱关联",
        "Log into the Web Enrolment System (WES).":
            "登录 WES（学生系统）。",
        "Log into your Monash University account when prompted (this "
        "will link your account).":
            "按提示登录你的 Monash 大学账号（这一步会完成账户关联）。",
        "Make sure your My eQuals account is linked to Monash "
        "University, otherwise you won't be able to access your "
        "academic record.":
            "请确认你的 My eQuals 账户已与 Monash 大学关联，否则无法查看学业记录。",
        "Make sure you’ve verified your email address:New (or soon to "
        "be) graduatesIf you’ve signed into My eQuals and can’t see "
        "any documents, it could be because:Past studentsIf you’ve "
        "signed into My eQuals and can’t see any documents, it could "
        "be because:If you bought an academic record, you might not be "
        "able to see it because:Past students (who graduated before "
        "2017)You can access your academic record (transcript) in My "
        "eQuals – for step-by-step instructions, see our academic "
        "records (transcripts) page.Other documents like your testamur "
        "and AHEGS are only available in hard copy.For instructions, "
        "see:":
            "请先确认你的邮箱已通过验证：\n应届（或即将）毕业生\n如果你已登录 My eQuals "
            "却看不到任何文件，可能是因为：\n往届学生\n如果你已登录 My eQuals "
            "却看不到任何文件，可能是因为：\n如果你买过学业记录却看不到，可能是因为：\n2017 年之前毕业的往届学生\n你可以在 My "
            "eQuals 中获取学业记录（成绩单）——具体步骤见我们的「学业记录（成绩单）」页面。\n学位证书（testamur）和 "
            "AHEGS 等其他文件只有纸质版。\n具体说明见：",
        "My eQuals troubleshooting":
            "My eQuals 问题排查",
        "Once you're in WES:":
            "进入 WES（学生系统）之后：",
        "Once your account is activated, log into My eQuals.":
            "账户激活之后，登录 My eQuals。",
        "Option 1: Go to the Documents screen and click Share in the "
        "Actions column.":
            "方式一：进入 Documents（文件）页面，在 Actions（操作）一列点击 Share（分享）。",
        "Option 2: Open the document and click Share.":
            "方式二：打开该文件，点击 Share（分享）。",
        "Option 3: Create a learner profile in My eQuals, which "
        "includes your name, some details about you (including a "
        "photo, if you’d like) and the documents you want to share. "
        "Then share your profile. See this video for instructions.":
            "方式三：在 My eQuals 里创建一份学习者档案（learner "
            "profile），内含你的姓名、一些个人信息（愿意的话还可以放照片），以及你想分享的文件，然后把这份档案分享出去。具体操作见这段视频。",
        "Order and pay for your transcript.\nWithin one working day, "
        "you'll receive your transcript in My eQuals.":
            "订购并支付成绩单费用。\n一个工作日之内，成绩单会出现在 My eQuals 里。",
        "Order your digital academic record (transcript)":
            "订购电子版学业记录（成绩单）",
        "Ordering a record after completing your course":
            "完成学位课程之后订购学业记录",
        "Other official documents":
            "其他正式文件",
        "Please visit our page on qualification verification and "
        "replacement documents for former MSA students, for important "
        "information.":
            "原 MSA 学生请查看「学历验证与补发文件」页面，那里有重要信息。",
        "Provide your personal email address.":
            "填写你的个人邮箱地址。",
        "Select Address update > Postal address to check your postal "
        "address, and update it if needed.":
            "依次选择 Address update（地址更新）>  Postal "
            "address（邮寄地址），核对邮寄地址，如有需要请更新。",
        "Select Link another email.":
            "点击 Link another email（关联另一个邮箱）。",
        "Select Monash University as the institution.":
            "在院校一栏选择 Monash University。",
        "Sharing your digital documents View":
            "分享你的电子文件 查看",
        "Sign up to My eQuals using your Monash email account (choose "
        "Monash as your institution).":
            "用你的 Monash 邮箱注册 My eQuals（院校选择 Monash）。",
        "Sign up to My eQuals using your personal email.":
            "用你的个人邮箱注册 My eQuals。",
        "Signing up to My eQuals View":
            "注册 My eQuals 查看",
        "Tick the checkbox to agree to the terms and conditions":
            "勾选复选框，同意条款与条件",
        "To complete the transaction, click No, Finish Transaction":
            "点击 No, Finish Transaction（否，完成交易）以结束本次交易",
        "To get a complete record after completing your course, you "
        "need to be course completed. This isn't the same as "
        "completing your course and your faculty does this to verify "
        "you have met all requirements of the course.":
            "读完之后要拿到完整的学业记录，学籍状态必须是「已完成学位课程」（course "
            "completed）。这与你自己读完课程不是一回事——它是由学院核实你已满足学位课程全部要求之后才标记的。",
        "To link your personal email:":
            "关联个人邮箱的方法：",
        "Under Education provider accounts:":
            "在 Education provider accounts（院校账户）下：",
        "Under Email accounts, check that your personal email address "
        "is either verified or primary.":
            "在 Email accounts（邮箱账户）下，确认你的个人邮箱状态是 verified（已验证）或 "
            "primary（主邮箱）。",
        "Under Email accounts:":
            "在 Email accounts（邮箱账户）下：",
        "Use the WES (login) for past students. If you studied before "
        "1997, you may not have access to your unofficial record in "
        "WES. If you receive an error when trying to order a "
        "transcript, contact Monash Connect.":
            "请使用往届学生的 WES（学生系统）登录入口。如果你是 1997 年之前就读的，可能无法在 WES "
            "里看到非正式记录。订购成绩单时如果报错，请联系 Monash Connect（学生服务中心）。",
        "Verify your email address in My e Q uals":
            "在 My eQuals 中验证你的邮箱地址",
        "WAM – Weighted Average Mark":
            "WAM — 加权平均分",
        "Web Enrolment System (WES)":
            "WES（学生系统）",
        "Within one working-day, your record will become available in "
        "My eQuals. You'll receive an email with instructions on how "
        "to set up your My eQuals account and collect your digital "
        "transcript.":
            "一个工作日之内，你的记录就会出现在 My eQuals 里。我们会发一封邮件告诉你如何设置 My eQuals "
            "账户并领取电子成绩单。",
        "You can check your course completion status in our virtual "
        "assistant (VA). It only takes a moment and you’ll need to be "
        "logged in to your Monash student account.":
            "你可以在我们的虚拟助手（VA）里查询学位课程完成状态，只需片刻，但需要先登录 Monash 学生账号。",
        "You can order a hard copy online using the WES (login) for "
        "past students. If you attended or completed your course "
        "before 1997, allow three to four weeks for delivery.":
            "你可以用往届学生的 WES（学生系统）登录入口在线订购纸质版。如果你是 1997 "
            "年之前就读或毕业的，请预留三到四周的寄送时间。",
        "You can order and pay for a hard copy academic record in WES, "
        "which will be sent by mail. After paying, you can check the "
        "progress of your order online.":
            "你可以在 WES（学生系统）里订购并支付纸质版学业记录，我们会邮寄给你。付款之后可以在线查看订单进度。",
        "You can order and pay for an official record at any time "
        "during your studies. Digital copies are faster to receive and "
        "cheaper than hard copies.":
            "在读期间你随时可以订购并支付正式学业记录。电子版比纸质版更快、也更便宜。",
        "You can share your documents in My eQuals in a number of "
        "different ways:":
            "在 My eQuals 里分享文件有好几种方式：",
        "You can view an unofficial record of your results (unless "
        "you're encumbered) in the:":
            "你可以在下列位置查看非正式的成绩记录（账户被施加 encumbrance（学籍限制）时除外）：",
        "Your academic record confirms your progress or, when you're "
        "complete, your final qualification. You can use it to:":
            "学业记录用于证明你的学业进度；读完之后，则用于证明你最终取得的学历。它可以用来：",
        "Your academic record has the following information about "
        "you:If a unit is marked as Incomplete on your academic "
        "transcript, it simply means the result isn't available "
        "yet.Masters awarded with distinctionFrom 6 October 2021, a "
        "student graduating with a master’s degree by coursework with "
        "a WAM of 80 or above will see ‘awarded with distinction’ on "
        "their transcript.Credit points not showing for some unit "
        "exemptionsSometimes exempted units listed in your academic "
        "record don’t have credit points attached. This is because "
        "you’ve been exempted from studying a particular unit (based "
        "on prior study), but you’re required to complete another unit "
        "in its place.":
            "你的学业记录包含以下关于你的信息：如果成绩单上某门课程标注为 "
            "Incomplete（未完成），只是表示成绩尚未公布。硕士优等毕业（awarded with distinction）：自 "
            "2021 年 10 月 6 日起，以授课型硕士学位毕业且 WAM（加权平均分）达到 80 "
            "分及以上的学生，成绩单上会显示「awarded with "
            "distinction」。部分免修课程不显示学分：成绩单上列出的免修课程有时没有对应学分，这是因为你（基于此前的学习）获准免修某门课程，但需要另修一门课程来替代。",
        "Your digital transcript will be issued to My eQuals using "
        "your personal email address. Just make sure your My eQuals "
        "account uses the same email address (otherwise you won’t be "
        "able to see your transcript).":
            "电子成绩单会以你的个人邮箱签发到 My eQuals。请务必确认你的 My eQuals "
            "账户使用的是同一个邮箱地址，否则看不到成绩单。",
        "Your record usually includes all unit attempts and your grade "
        "for each unit. If you were enrolled in more than one course, "
        "it lists all courses and all units studied at Monash. You can "
        "also request a hard copy transcript for a specific course "
        "only – we’ll include a statement that the document is not a "
        "complete record of all your studies at Monash.":
            "学业记录通常包含你所有课程的修读记录和每门课的成绩等级。如果你注册过不止一个学位课程，记录会列出你在 Monash "
            "修读的全部学位课程和全部课程。你也可以只针对某一个学位课程申请纸质成绩单——那样我们会加上一句声明，说明该文件并非你在 "
            "Monash 全部学业的完整记录。",
        "You’ll also need to link your My eQuals account to Monash "
        "University to be able to access your digital documents:":
            "你还需要把 My eQuals 账户与 Monash 大学关联，才能查看电子文件：",
        "You’ll need to have signed up to My eQuals to receive any "
        "digital documents. To order your academic transcript:":
            "要领取任何电子文件，都必须先注册 My eQuals。订购成绩单的方法：",
        "You’ll need to link your account to a personal email address "
        "so you can access your documents after you graduate.":
            "你需要把账户关联到一个个人邮箱，这样毕业之后才能继续查看自己的文件。",
    },
    "add-or-withdraw-units": {
        "If you can’t add or withdraw from a unit":
            "如果你无法添加或退选课程",
        "Academic penalties may apply to some teaching periods":
            "部分开课学期还可能有学业方面的处罚",
        "Add or withdraw from units":
            "添加或退选课程",
        "Adding units from other faculties":
            "添加其他学院的课程",
        "After the start of a teaching period, you need to allow up to "
        "24 hours for your unit changes to appear in Moodle.":
            "开课学期开始之后，选课变动最多需要 24 小时才会显示在 Moodle 上。",
        "After you’ve made unit changes in WES":
            "在 WES（学生系统）里改完课程之后",
        "Before making changes to your units, find out more about time "
        "limits to finish your course and check the processes for "
        "underloading and overloading.":
            "改动课程之前，先了解完成学位课程的年限规定，并查看减少学习负荷（underloading）和超额选课（overloading）的办理流程。",
        "By Friday of week two of the teaching period":
            "在开课学期第二周的周五之前",
        "CSP and HELP loan students":
            "联邦资助学额（CSP）与 HELP 贷款学生",
        "Census date description, code and penalty for missing it.":
            "census date（学籍统计日）的说明、代码，以及错过它的处罚。",
        "Census date for teaching period":
            "该开课学期的 census date（学籍统计日）",
        "Changing your study load":
            "改变学习负荷",
        "Changing your study load from full-time to part-time could "
        "affect your Centrelink payments.":
            "把学习负荷从全日制改为非全日制，可能会影响你的 Centrelink 补助。",
        "Check your unit enrolment using our VA":
            "用我们的虚拟助手查看你的课程注册情况",
        "Click SUBMIT to save your changes.":
            "点击 SUBMIT（提交）保存改动。",
        "Click To add units click here at the top of the enrolment "
        "form.":
            "点击注册表单顶部的 To add units click here（添加课程请点这里）。",
        "Confirmation of Enrolment (CoE)":
            "入学确认书（CoE）",
        "Coursework Enrolment Procedure (pdf)":
            "Coursework Enrolment Procedure（授课型选课注册规程，pdf）",
        "Financial : no refund available (you’ll be liable for your "
        "fees) Academic : recorded on transcript as 'WDN' (mark not "
        "included in calculating WAM and GPA)":
            "财务：不予退费（学费仍需你承担）　学业：在成绩单上记为 WDN（退课），该分数不计入 WAM（加权平均分）和 "
            "GPA（平均绩点）",
        "Financial : no refund available (you’ll be liable for your "
        "fees) Academic : recorded on transcript as a 'WN' fail grade "
        "(grade of zero included in calculating WAM and GPA)":
            "财务：不予退费（学费仍需你承担）　学业：在成绩单上记为 WN 不及格，以零分计入 WAM（加权平均分）和 GPA（平均绩点）",
        "Financial : see fee policies and procedures Academic : not "
        "recorded on transcript":
            "财务：见学费政策与流程　学业：不记入成绩单",
        "Financial: no financial penalty applies (you’re not liable "
        "for your fees) Academic: not recorded on transcript":
            "财务：不产生任何费用处罚（学费无需你承担）　学业：不记入成绩单",
        "Financial: no refund available (you’ll be liable for your "
        "fees) Academic: recorded on transcript as WDN (not included "
        "in calculating GPA and WAM)":
            "财务：不予退费（学费仍需你承担）　学业：在成绩单上记为 WDN（退课），该分数不计入 WAM（加权平均分）和 "
            "GPA（平均绩点）",
        "Financial: no refund available (you’ll be liable for your "
        "fees) Academic: recorded on transcript as a WN fail grade "
        "(grade of zero included in calculating GPA and WAM )":
            "财务：不予退费（学费仍需你承担）　学业：在成绩单上记为 WN 不及格，以零分计入 WAM（加权平均分）和 GPA（平均绩点）",
        "How to withdraw from a unit":
            "如何退选一门课程",
        "If you can’t add or withdraw from a unit in WES, submit an "
        "Enrolment Amendment Form. Research students need to contact "
        "their Graduate Research Faculty Office.":
            "如果你在 WES（学生系统）里无法添加或退选课程，请提交 Enrolment Amendment "
            "Form（选课注册变更表）。研究型学生请联系所在的 Graduate Research Faculty "
            "Office（研究生研究学院办公室）。",
        "If you get an error message saying you haven't enrolled in "
        "enough credit points, you'll need to add more units before "
        "WES will let you submit. To enrol in less than 48 credit "
        "points for the year, submit an Enrolment Amendment Form.":
            "如果系统提示你所选学分不足，就需要先添加更多课程，WES（学生系统）才允许提交。若全年要选不足 48 学分，请提交 "
            "Enrolment Amendment Form（选课注册变更表）。",
        "If you have any trouble adding units in WES, see "
        "troubleshooting in WES.":
            "如果在 WES（学生系统）里添加课程遇到问题，请查看 WES 的问题排查说明。",
        "If you need help selecting units or enrolling in WES, take a "
        "look at our video below.":
            "如果你在选课或在 WES（学生系统）里注册时需要帮助，可以看下面这段视频。",
        "If you withdraw from all of your units, you'll need to:":
            "如果你退选了全部课程，就需要：",
        "If you're on a student visa then you’ll have study load "
        "requirements to maintain. Changing your study load may "
        "require you to update your:":
            "如果你持学生签证，就必须满足学习负荷方面的要求。改变学习负荷时，你可能需要同步更新：",
        "If you’ve got free elective space and you’re looking to "
        "explore another area of study, take a look at Monash Enrich – "
        "you’ll find electives from other faculties, programs and "
        "overseas study opportunities.":
            "如果你还有自由选修的名额，又想接触别的领域，可以看看 Monash "
            "Enrich——那里有其他学院的选修课、各类项目，以及海外学习机会。",
        "International students":
            "国际学生",
        "It's important to check the census and penalty dates for your "
        "teaching period before withdrawing from a unit, or you may "
        "face academic and financial penalties. These include having a "
        "fail recorded on your academic record and incurring fees or a "
        "loan debt.":
            "退选课程之前，一定要先查清你所在开课学期的 census "
            "date（学籍统计日）和处罚日期，否则可能面临学业和费用上的处罚，包括在成绩单上留下不及格记录、以及产生学费或贷款债务。",
        "Log into WES and click on Unit Enrolment.":
            "登录 WES（学生系统），点击 Unit Enrolment（课程注册）。",
        "Log into the Unit Enrolment section of WES to view a summary "
        "page of your current unit enrolment.":
            "登录 WES（学生系统）的 Unit Enrolment（课程注册）一节，即可看到你当前选课情况的汇总页面。",
        "Once your unit changes appear in Allocate+ you can enter "
        "preference for new units and change preferences for any other "
        "units affected. Allocate+ will automatically remove withdrawn "
        "units.":
            "课程变动在 Allocate+ 中显示出来之后，你就可以为新课程填写志愿，并调整其他受影响课程的志愿。Allocate+ "
            "会自动移除已退选的课程。",
        "Overloading: If you want to enrol in more than the standard "
        "number of units you need to first request to overload. You’ll "
        "also need to meet some conditions.":
            "超额选课（overloading）：如果你想选的课程超出标准数量，需要先提出超额选课申请，并且要满足一些条件。",
        "Overseas Student Health Cover (OSHC)":
            "留学生医疗保险（OSHC）",
        "Part-time: If you’re enrolled as a full-time student you may "
        "not be able to withdraw from units unless you’re officially "
        "recorded as part-time. If you’re on a student visa you also "
        "have study load requirements to maintain. For more about "
        "this, see underloading.":
            "非全日制：如果你是以全日制身份注册的，除非学籍上正式记为非全日制，否则可能无法退选课程。持学生签证的学生还必须满足学习负荷要求。详见减少学习负荷（underloading）说明。",
        "Penalties for withdrawing late":
            "迟退选的处罚",
        "Remove your unit/s with the buttons in the Action column next "
        "to the unit code.":
            "用课程代码旁 Action（操作）一列中的按钮移除课程。",
        "Save your changes by clicking SUBMIT ENROLMENT.":
            "点击 SUBMIT ENROLMENT（提交注册）保存改动。",
        "Search for the unit/s you want to add, but don’t click SUBMIT "
        "until you have:":
            "搜索你想添加的课程，但先别急着点 SUBMIT（提交）——要等你已经：",
        "See your student visa for more information.":
            "更多信息见「学生签证」页面。",
        "Student Fees Policy (pdf)":
            "Student Fees Policy（学费政策，pdf）",
        "Student Fees Procedure (pdf)":
            "Student Fees Procedure（学费流程，pdf）",
        "Student Fees Refunds Procedure (pdf)":
            "Student Fees Refunds Procedure（学费退费流程，pdf）",
        "Teaching period start date":
            "开课学期开始日期",
        "Teaching weeks end date: Last day to withdraw from units. "
        "After this date, you cannot withdraw from units.":
            "教学周结束日：退选课程的最后一天。此日期之后就无法再退选课程。",
        "The Friday before the teaching period starts":
            "开课学期开始前的那个周五",
        "The University will not backdate your changes to avoid "
        "payment or academic penalties unless we have made a proven "
        "error.":
            "除非确属学校的过失并经查证，否则学校不会把你的变动日期回溯，以规避费用或学业上的处罚。",
        "Timing of unit withdrawal and their penalty types":
            "退选课程的时间点与对应的处罚类型",
        "Unit changes will appear in Allocate+ within two hours. If "
        "you submit your changes using a form, please allow staff "
        "several days to process the units.":
            "课程变动会在两小时内显示到 Allocate+ 中。如果你是用表格提交的变动，请留出几个工作日让工作人员处理。",
        "Unit types and when to add them":
            "课程类型，以及各自该在什么时候添加",
        "Units added (with faculty approval) after the census date "
        "cannot be Commonwealth-supported. The University charges the "
        "full course fee and you can't get FEE-HELP for these units. "
        "Your fee statement will be updated to reflect the changes.":
            "在 census "
            "date（学籍统计日）之后（经学院批准）添加的课程，不能算作联邦资助学额（CSP）。学校会按全额学费收取，这些课程也无法使用 "
            "FEE-HELP 贷款。你的费用清单会相应更新。",
        "WES will email you a transaction number (starting with U) "
        "after you’ve successfully updated your enrolment. Keep this "
        "record.":
            "成功更新选课注册后，WES（学生系统）会把一个以 U 开头的交易号发到你邮箱，请留存好。",
        "Withdrawing from units":
            "退选课程",
        "You can also use the Handbook to find more information on the "
        "units you’re interested in.":
            "你也可以在 Handbook 里查到感兴趣课程的更多信息。",
        "You can use the Web Enrolment System (WES) to add or withdraw "
        "from most units.":
            "多数课程都可以在 WES（学生系统）里添加或退选。",
        "You need to wait a couple of hours for changes to come "
        "through from WES before you can log into Allocate+ to update "
        "your timetable.":
            "改动从 WES（学生系统）同步过来需要几个小时，之后你才能登录 Allocate+ 调整课表。",
        "Your fee statement will be updated to reflect the changes. "
        "See access your fee statement.":
            "你的费用清单会相应更新。请查看「如何查看费用清单」。",
        "added all your new units and reached enough credit points for "
        "the year":
            "把新课程全部加好，并且全年学分已经达标",
        "apply for intermission (study leave), if you want to return "
        "to study.":
            "如果你还打算回来读书，就申请休学（intermission，即 study leave）。",
        "discontinue your course, or":
            "退课；或者",
        "finished swapping units (dropping one and adding another).":
            "换课已经换完（退掉一门、加上另一门）。",
        "student visa":
            "学生签证",
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
        "Assessment at Monash":
            "Monash 的考核",
        "Assessment deadlines":
            "考核截止期限",
        "Assessments of learning provide a measure of your achievement "
        "in relation to the learning outcomes of the unit. These "
        "assessments are designed to test how much you’ve learnt (i.e. "
        "your knowledge, understanding and skills), and they’re "
        "usually set after the teaching weeks end.":
            "「对学习的考核」衡量的是你相对于课程学习成果的达成度。这类考核用来检验你学到了多少（即知识、理解与技能），通常安排在教学周结束之后。",
        "Before you start an assessment task, you should check the "
        "marking criteria and use it as a guide in developing your "
        "response to the task.":
            "着手做某项考核任务之前，先看看评分标准，并据此规划你的作答思路。",
        "Blind marking policy":
            "匿名评阅制度",
        "Each assessment you do will either be for your learning or of "
        "your learning:":
            "你做的每一项考核，要么是「为了学习」，要么是「对学习的检验」：",
        "For each additional day the assessment is overdue (up to "
        "seven days after the due date), a further 5% penalty will be "
        "applied (maximum total penalty of 35%). You can find the "
        "marking penalty information for your unit (including any "
        "exceptions) in Moodle.":
            "此后每逾期一天（最多到截止日后第七天），再扣 5%，累计最高扣 35%。你所在课程的扣分规则（含各种例外）可以在 "
            "Moodle 上查到。",
        "For related policy and procedures, see assessment policy and "
        "processes.":
            "相关政策与流程请见「考核政策与流程」。",
        "Go to defer or reschedule your final assessment (exam) for "
        "details about deferring your scheduled final assessment or "
        "rescheduling your deferred assessment.":
            "已排定期末考核的延期、以及延期考核的改期，详见「为已排定的期末考核（考试）申请延期或改期」。",
        "If you submit an assessment task more than seven days after "
        "the due date, your assessment won’t be marked – you’ll "
        "receive a mark of zero and you won’t get any feedback.":
            "如果考核任务在截止日之后超过七天才提交，我们不会评阅——你会得零分，也不会收到任何反馈。",
        "It’s likely that you’ll complete a variety of different "
        "assessments that will give you lots of opportunities to "
        "develop your skills and demonstrate your progression.":
            "你多半会做到各种不同类型的考核，它们能给你许多机会去锻炼能力、展现自己的进步。",
        "Most assessment tasks you complete will contribute to your "
        "overall result for the unit. For more information, see:":
            "你完成的多数考核任务都会计入该课程的总成绩。更多信息见：",
        "Some of your assessments will have deadlines (which you can "
        "find in Moodle), but most will be scheduled – you’ll find a "
        "timetable of your scheduled assessments in Allocate+. For "
        "more information, see dates and timetables.":
            "有些考核有截止期限（可以在 Moodle 上查到），但多数是排定时间的——已排定考核的时间表可以在 Allocate+ "
            "里找到。更多信息见「日期与课表」。",
        "The marking criteria for an assessment helps you understand "
        "what’s expected of you, and how your performance can be "
        "improved. The format of the marking criteria will vary on "
        "your unit and the type of assessment you’re doing.":
            "考核的评分标准能帮你弄清别人对你的期待是什么、以及可以从哪里改进。评分标准的具体形式，因课程和考核类型而异。",
        "The types of assessments you’ll need to complete will depend "
        "on the unit and course you’re enrolled in – your unit "
        "information will outline how and when your learning will be "
        "assessed.":
            "你需要完成哪些类型的考核，取决于你注册的课程和学位课程——课程信息里会写明你的学习将以何种方式、在什么时候受到检验。",
        "We use blind marking for final assessments. Blind marking is "
        "anonymous, and ensures consistency. For example, when your "
        "chief examiner is reviewing an eExam, they won’t see your "
        "name (just your student ID number and your responses).":
            "期末考核采用匿名评阅。匿名评阅不显示身份，以保证评分的一致性。例如，主考官在评阅 "
            "eExam（线上考试）时看不到你的姓名，只能看到你的学号和作答内容。",
        "When you start a unit, you’ll be able to access your "
        "assessment information in Moodle, including:":
            "开始一门课程之后，你就可以在 Moodle 上看到该课程的考核信息，包括：",
        "When you submit work for assessment, you must adhere to the "
        "values of honesty, trust, fairness, respect and "
        "responsibility. To ensure that you complete your assessments "
        "with integrity, see academic integrity, plagiarism and "
        "collusion.":
            "提交作业接受考核时，你必须守住诚实、信任、公平、尊重与负责这些价值。如何以符合学术诚信的方式完成考核，请见「学术诚信、抄袭与合谋作弊」。",
        "You can apply for a short extension of two calendar days if "
        "you can’t complete your assessment on time due to short-term "
        "difficult circumstances, such as a medical condition, carer "
        "responsibilities (including for your children) or a car "
        "accident. A short extension is available for most types of "
        "assessments (e.g. an assignment or quiz), but not for an "
        "in-class test, a mid-semester test or a scheduled final "
        "assessment. No reason is needed on your first application for "
        "a particular unit.":
            "如果你因短期困难而无法按时完成考核——例如健康问题、照护责任（包括照顾子女）或遭遇车祸——可以申请两个日历日的短期延期。多数类型的考核都可以申请短期延期（例如作业或小测），但课堂测验、期中测验和已排定的期末考核不行。同一门课程的第一次申请不需要说明理由。",
        "Your assessments may involve some or all of the following:":
            "你的考核可能涉及下列部分或全部形式：",
        "case studies":
            "案例分析",
        "electronic exams (eExams).":
            "电子考试（eExams）。",
        "essays and reports":
            "论文与报告",
        "group projects":
            "小组项目",
        "how you can apply for an extension":
            "如何申请延期",
        "laboratory work":
            "实验课作业",
        "online quizzes (Moodle)":
            "线上小测（Moodle）",
        "oral assessments and presentations":
            "口头考核与口头报告",
        "peer-to-peer assessments":
            "同侪互评",
        "performance and studio assessments":
            "表演与工作室考核",
        "posters and presentations":
            "海报与展示",
        "problem-based learning scenarios":
            "问题导向学习情境",
        "reading your marks.":
            "如何看懂分数。",
        "self-assessment":
            "自我评估",
        "take-home assessments":
            "带回家完成的考核",
        "the marking penalties applied for late submissions.":
            "迟交的扣分规则。",
        "the types of assessments you’ll complete":
            "你要完成哪些类型的考核",
        "when and how you can access your results":
            "什么时候、以什么方式查成绩",
        "when they’re due":
            "各项考核什么时候截止",
        "when you’ll receive feedback":
            "什么时候能收到反馈",
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
        "1 Nov 2027 – 11 Feb 2028":
            "2027年11月1日至2028年2月11日",
        "1 Nov 2027 – 23 Jun 2028":
            "2027年11月1日至2028年6月23日",
        "1 Nov 2028 – 16 Feb 2029":
            "2028年11月1日至2029年2月16日",
        "10 Jan – 18 Mar 2028":
            "2028年1月10日至3月18日",
        "10 Jan – 25 Feb 2028":
            "2028年1月10日至2月25日",
        "10 May – 30 Jul 2027":
            "2027年5月10日至7月30日",
        "11 May – 31 Jul 2026":
            "2026年5月11日至7月31日",
        "11 Sep – 15 Dec 2028":
            "2028年9月11日至12月15日",
        "13 Sep – 17 Dec 2027":
            "2027年9月13日至12月17日",
        "14 Sep – 18 Dec 2026":
            "2026年9月14日至12月18日",
        "15 Jun – 17 Jul 2026":
            "2026年6月15日至7月17日",
        "17 Apr – 10 Jun 2028":
            "2028年4月17日至6月10日",
        "17 Jan – 17 Nov 2028":
            "2028年1月17日至11月17日",
        "17 Jan – 23 Jun 2028":
            "2028年1月17日至6月23日",
        "18 Jan – 19 Nov 2027":
            "2027年1月18日至11月19日",
        "18 Jan – 25 Jun 2027":
            "2027年1月18日至6月25日",
        "19 Apr – 12 Jun 2027":
            "2027年4月19日至6月12日",
        "19 Jan – 20 Nov 2026":
            "2026年1月19日至11月20日",
        "19 Jan – 26 Jun 2026":
            "2026年1月19日至6月26日",
        "19 Jun – 17 Nov 2028":
            "2028年6月19日至11月17日",
        "19 Jun – 21 Jul 2028":
            "2028年6月19日至7月21日",
        "2 Nov 2026 – 12 Feb 2027":
            "2026年11月2日至2027年2月12日",
        "2 Nov 2026 – 25 Jun 2027":
            "2026年11月2日至2027年6月25日",
        "20 Jul – 12 Sep 2026":
            "2026年7月20日至9月12日",
        "2026 Census dates for all teaching periods (sorted by census "
        "date) Close":
            "2026 年全部开课学期的 census dates（学籍统计日）（按学籍统计日排序） 收起",
        "2027 Census dates for all teaching periods (sorted by census "
        "date) View":
            "2027 年全部开课学期的 census dates（学籍统计日）（按学籍统计日排序） 查看",
        "2028 Census dates for all teaching periods (sorted by census "
        "date) View":
            "2028 年全部开课学期的 census dates（学籍统计日）（按学籍统计日排序） 查看",
        "21 Aug – 10 Nov 2028":
            "2028年8月21日至11月10日",
        "21 Feb – 23 Jun 2028":
            "2028年2月21日至6月23日",
        "21 Jun – 19 Nov 2027":
            "2027年6月21日至11月19日",
        "21 Jun – 23 Jul 2027":
            "2027年6月21日至7月23日",
        "22 Feb – 25 Jun 2027":
            "2027年2月22日至6月25日",
        "22 Jun – 20 Nov 2026":
            "2026年6月22日至11月20日",
        "23 Feb – 26 Jun 2026":
            "2026年2月23日至6月26日",
        "23 Nov 2026 – 12 Feb 2027":
            "2026年11月23日至2027年2月12日",
        "23 Oct 2028 – 9 Feb 2029":
            "2028年10月23日至2029年2月9日",
        "24 Jul 2028 – 16 Feb 2029":
            "2028年7月24日至2029年2月16日",
        "24 Jul 2028 – 22 Jun 2029":
            "2028年7月24日至2029年6月22日",
        "24 Jul – 17 Nov 2028":
            "2028年7月24日至11月17日",
        "24 Jul – 18 Nov 2028":
            "2028年7月24日至11月18日",
        "25 Oct 2027 – 11 Feb 2028":
            "2027年10月25日至2028年2月11日",
        "25 Sep – 18 Nov 2028":
            "2028年9月25日至11月18日",
        "26 Jul 2027 – 11 Feb 2028":
            "2027年7月26日至2028年2月11日",
        "26 Jul 2027 – 23 Jun 2028":
            "2027年7月26日至2028年6月23日",
        "26 Jul – 19 Nov 2027":
            "2027年7月26日至11月19日",
        "26 Oct 2026 – 12 Feb 2027":
            "2026年10月26日至2027年2月12日",
        "27 Apr – 20 Jun 2026":
            "2026年4月27日至6月20日",
        "27 Jul 2026 – 12 Feb 2027":
            "2026年7月27日至2027年2月12日",
        "27 Jul 2026 – 25 Jun 2027":
            "2026年7月27日至2027年6月25日",
        "27 Jul – 18 Nov 2026":
            "2026年7月27日至11月18日",
        "27 Sep – 20 Nov 2027":
            "2027年9月27日至11月20日",
        "28 Aug – 13 Oct 2028":
            "2028年8月28日至10月13日",
        "28 Feb – 17 Nov 2028":
            "2028年2月28日至11月17日",
        "28 Feb – 23 Jun 2028":
            "2028年2月28日至6月23日",
        "28 Jun – 13 Aug 2027":
            "2027年6月28日至8月13日",
        "28 Sep – 21 Nov 2026":
            "2026年9月28日至11月21日",
        "29 Jun – 14 Aug 2026":
            "2026年6月29日至8月14日",
        "3 Nov 2025 – 26 Jun 2026":
            "2025年11月3日至2026年6月26日",
        "30 Oct 2028 – 9 Feb 2029":
            "2028年10月30日至2029年2月9日",
        "31 Jan – 10 Jun 2028":
            "2028年1月31日至6月10日",
        "Census dates and teaching periods":
            "census dates（学籍统计日）与开课学期",
        "Census dates and teaching periods 2026–2028":
            "2026–2028 年 census dates（学籍统计日）与开课学期",
        "Census dates for 2023 teaching periods (sorted by teaching "
        "period start date)":
            "2023 年各开课学期的 census dates（学籍统计日）（按开课学期开始日期排序）",
        "Final assessment dates":
            "期末考核日期",
        "Financial penalties apply Academic penalties apply to some "
        "teaching periods":
            "会产生费用方面的处罚；部分开课学期还会有学业方面的处罚",
        "Find out more about census dates and why they're so important.":
            "进一步了解 census dates（学籍统计日），以及它为什么这么重要。",
        "For on-campus units, you have up until the end of the first "
        "two weeks of the teaching period.":
            "校内课程可以加课到开课学期前两周结束为止。",
        "Full-year (extended) (FY-32)":
            "全学年（延长）（FY-32）",
        "If you’re studying a postgraduate law degree, your faculty "
        "might refer to your start dates as follows:":
            "如果你读的是法学研究生学位，学院可能会用下面这些说法来指代你的开学日期：",
        "Monash Indonesia Semester 1 (MI-S1)":
            "Monash Indonesia（印尼校区） 第一学期（MI-S1）",
        "Monash Indonesia Semester 2 (MI-S2)":
            "Monash Indonesia（印尼校区） 第二学期（MI-S2）",
        "Monash Indonesia term 1 (MI-T1-6)":
            "Monash Indonesia（印尼校区） 第 1 学季（MI-T1-6）",
        "Monash Indonesia term 2 (MI-T2-6)":
            "Monash Indonesia（印尼校区） 第 2 学季（MI-T2-6）",
        "Monash Indonesia term 3 (MI-T3-6)":
            "Monash Indonesia（印尼校区） 第 3 学季（MI-T3-6）",
        "Monash Indonesia term 4 (MI-T4-6)":
            "Monash Indonesia（印尼校区） 第 4 学季（MI-T4-6）",
        "Monash Online 1 (MO-TP1-01)":
            "Monash Online（在线） 1（MO-TP1-01）",
        "Monash Online 2 (MO-TP2-01)":
            "Monash Online（在线） 2（MO-TP2-01）",
        "Monash Online 3 (MO-TP3-01)":
            "Monash Online（在线） 3（MO-TP3-01）",
        "Monash Online 4 (MO-TP4-01)":
            "Monash Online（在线） 4（MO-TP4-01）",
        "Monash Online 5 (MO-TP5-01)":
            "Monash Online（在线） 5（MO-TP5-01）",
        "Monash Online 6 (MO-TP6-01)":
            "Monash Online（在线） 6（MO-TP6-01）",
        "Non-standard unit withdrawal dates":
            "非标准的课程退选日期",
        "November intake – Australia (NOV12)":
            "11 月入学（澳大利亚）（NOV12）",
        "October intake – Malaysia (OCT-MY-01)":
            "10 月入学（马来西亚）（OCT-MY-01）",
        "Other important dates":
            "其他重要日期",
        "Research Q1 (RES-Q1)":
            "研究季度 1（RES-Q1）",
        "Research Q2 (RES-Q2)":
            "研究季度 2（RES-Q2）",
        "Research Q3 (RES-Q3)":
            "研究季度 3（RES-Q3）",
        "Research Q4 (RES-Q4)":
            "研究季度 4（RES-Q4）",
        "Semester 1 (extended) (S1-32)":
            "第一学期（延长）（S1-32）",
        "Semester 1 (northern) (S1-60)":
            "第一学期（北半球）（S1-60）",
        "Semester 2 (extended) (S2-32)":
            "第二学期（延长）（S2-32）",
        "Semester 2 (northern) (S2-60)":
            "第二学期（北半球）（S2-60）",
        "Semester 2 – semester 1 (S2-S1-02)":
            "第二学期 – 第一学期（S2-S1-02）",
        "Semester 2 – summer A (S2-SS-02)":
            "第二学期 – 夏季学期 A（S2-SS-02）",
        "Semester dates summary":
            "学期日期一览",
        "Semester one (S1-01)":
            "第一学期（S1-01）",
        "Semester two (S2-01)":
            "第二学期（S2-01）",
        "Some units have different withdrawal dates to the standard "
        "dates of the same teaching period. To check the dates and "
        "enrolment information for these units, see units with "
        "non-standard dates.":
            "有些课程的退选日期与同一开课学期的标准日期不同。这类课程的日期和选课注册信息，请查看「非标准日期的课程」。",
        "Summer A – semester 1 (SS-S1-01)":
            "夏季学期 A – 第一学期（SS-S1-01）",
        "Summer semester A (SSA-02)":
            "夏季学期 A（SSA-02）",
        "Summer semester B (SSB-01)":
            "夏季学期 B（SSB-01）",
        "Teaching period (includes teaching weeks through to final "
        "assessment period)":
            "开课学期（自教学周起，至期末考核期止）",
        "Teaching weeks end – last day to withdraw from units":
            "教学周结束——退选课程的最后一天",
        "The census date is the last day:":
            "census date（学籍统计日）是以下事项的最后一天：",
        "The deadline to add units to your enrolment is earlier than "
        "withdrawing.":
            "加课的截止日比退选更早。",
        "Winter semester (WS-01)":
            "冬季学期（WS-01）",
        "Withdrawn Fail starts":
            "Withdrawn Fail（退课不及格）期开始",
        "Withdrawn Late starts":
            "Withdrawn Late（逾期退课）期开始",
        "academic and financial penalties":
            "学业与费用方面的处罚",
        "before you become liable for fees for the units in which "
        "you're enrolled":
            "在你开始为已注册课程承担学费之前",
        "past census dates and teaching periods archive":
            "往年 census dates（学籍统计日）与开课学期存档",
        "you can withdraw from a unit without Withdrawn showing on "
        "your academic record (there are some exceptions).":
            "你可以退选一门课程而不在成绩单上留下 Withdrawn（退课）记录（有少数例外）。",
        "Check the details at add or withdraw from units.":
            "详情请见「添加或退选课程」页面。",
        "If you withdraw from a unit after a certain date, your academic record may show Withdrawn or Withdrawn Fail. You should understand how census and withdrawal dates can affect your fees and academic record. For more information, see:":
            "在某个日期之后退选课程，你的学业记录上可能会显示 Withdrawn（退课）或 Withdrawn Fail（退课记为不及格）。你应当了解 census date（学籍统计日）和退选日期会如何影响你的学费与学业记录。更多信息请见：",
        "You have until 11.59pm (Melbourne time) on the census date to withdraw from units without financial or academic penalty.":
            "你可以在 census date（学籍统计日）当天 23:59（墨尔本时间）之前退选课程，不会受到费用或学业方面的处罚。",
    },
    "census-dates-explained": {
        "During and after enrolling":
            "选课注册期间与之后",
        "Non-standard dates and Withdrawn Early":
            "非标准日期与 Withdrawn Early（提前退选）",
        "What are census dates?":
            "什么是 census dates（学籍统计日）？",
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
        "Applying for a new CoE":
            "申请新的 CoE（入学确认书）",
        "Confirmation of Enrolment (CoE)":
            "入学确认书（CoE）",
        "Exception for Australia Awards students":
            "Australia Awards 学生的例外情形",
        "If you hold an Australia Awards Scholarship, you don’t need a "
        "CoE – instead, you’ll have an agreement with the Department "
        "of Foreign Affairs and Trade that confirms you’re staying in "
        "Australia to study.":
            "如果你持有 Australia Awards 奖学金，就不需要 "
            "CoE（入学确认书）——取而代之的是你与澳大利亚外交贸易部（DFAT）之间的协议，该协议确认你留在澳大利亚学习。",
        "If you'd like to extend your stay, take a look at our page on "
        "Australia Awards Scholarship extensions.":
            "如果你想延长停留时间，请查看「Australia Awards 奖学金延期」页面。",
        "If your application is approved, we’ll send your new CoE to "
        "your Monash email address within seven working days of your "
        "application.":
            "如果申请获批，我们会在你提交申请后七个工作日内，把新的 CoE（入学确认书）发到你的 Monash 邮箱。",
        "We can only approve a new CoE if you can demonstrate one of "
        "the following:":
            "只有在你能证明存在下列情形之一时，我们才能批准新的 CoE（入学确认书）：",
        "You can apply for a new CoE two months before your visa "
        "expires.":
            "你可以在签证到期前两个月申请新的 CoE（入学确认书）。",
        "an academic progress intervention:":
            "学业进度方面的干预措施：",
        "an approved deferment or intermission of study.":
            "已获批的推迟入学或休学（intermission）。",
        "approving you to underload your studies.":
            "批准你减少学习负荷（underload）。",
        "compassionate or compelling circumstances":
            "compassionate or compelling circumstances（体恤或不可抗情形）",
        "imposing an enrolment condition on you":
            "对你的选课注册附加条件",
        "referring you to University services to assist you "
        "academically":
            "把你转介到学校的相关服务，以在学业上给予帮助",
        "warning you about your academic progress":
            "就你的学业进度向你发出警示",
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
        "Allocate+ dates\n \nTake a look at the Allocate+ dates to find "
        "out when you can enter preferences and make changes to your "
        "timetable.":
            "Allocate+ 日期\n \n查看 Allocate+ 日期，了解什么时候可以填志愿、什么时候可以调整课表。",
        "Ask our virtual assistant\n \nOur virtual assistant has answers "
        "to most common questions, including finding unit information, "
        "choosing a major or minor, getting credit for prior study, "
        "and much more. If it can’t find an answer, it can connect you "
        "to a real person or help you make an online enquiry.":
            "问问我们的虚拟助手\n "
            "\n常见问题它多半答得上来，包括查课程信息、选主修或副修、既往学习学分减免等等。如果它答不上来，可以帮你转接真人，或协助你提交在线咨询。",
        "Can’t complete your assessment?\n \nLearn about your options if "
        "you couldn’t – or can’t – complete an assessment when "
        "required.":
            "无法完成考核？\n \n了解在你当时无法、或现在无法按要求完成考核时，有哪些选择。",
        "Census dates and teaching periods\n \nCheck the census date for "
        "your teaching period before you withdraw from a unit or make "
        "changes to your enrolment.":
            "census dates（学籍统计日）与开课学期\n \n退选课程或改动选课注册之前，先查清你所在开课学期的 census "
            "date（学籍统计日）。",
        "Changing my enrolment":
            "变更我的选课注册",
        "Changing my study load":
            "改变我的学习负荷",
        "Changing units?\nCheck the deadlines for adding or dropping "
        "units\n\n\nView dates":
            "要改课？\n查看加课和退课的截止日期\n\n\n查看日期",
        "Choose a topicChanging my study loadCourse or campus "
        "transferCredit for prior learningEnrolling in units and areas "
        "of studyChanging my enrolment":
            "选择一个主题：改变我的学习负荷／转学位课程或转校区／既往学习学分减免／选课与专业方向注册／变更我的选课注册",
        "Complementary study\n \nYou can apply to study a unit at "
        "another institution within Australia or New Zealand and "
        "receive credit towards your course.":
            "辅修学习（complementary study）\n "
            "\n你可以申请到澳大利亚或新西兰境内的其他院校修读一门课程，并计入你的学位课程。",
        "Course maps\n \nIf you need help choosing units, check the "
        "course map for your degree. Course maps give you a visual "
        "outline of your degree’s structure, including units and "
        "electives.":
            "课程地图\n \n如果你在选课上拿不定主意，看看自己学位的课程地图。课程地图会用图示的方式呈现学位结构，包括各门课程和选修安排。",
        "Course or campus transfer":
            "转学位课程或转校区",
        "Course planning tools View":
            "课程规划工具 查看",
        "Course progression check\n \nTo check how you’re progressing "
        "through your degree, submit a Course Advice Request.":
            "学业进度查询\n \n想知道自己学位读到哪一步了，请提交 Course Advice Request（课程咨询申请）。",
        "Credit for prior learning":
            "既往学习的学分减免",
        "Discontinuing your course\n \nIf you’re unsure about continuing "
        "your course, we’re here to help you understand your options "
        "so you can make the decision that’s right for you.":
            "退课\n \n如果你对是否继续读拿不定主意，我们可以帮你把各种选择弄清楚，好让你做出适合自己的决定。",
        "Enquiry response times":
            "咨询回复时长",
        "Enrolling in units and areas of study":
            "选课与专业方向注册",
        "Enrolment and credit":
            "选课注册与学分减免",
        "Graduating with an alternative exit\n \nIf you choose to leave "
        "your course early, you may be eligible for an alternative "
        "exit. Check your course details in the Handbook to find out "
        "if you're eligible.":
            "以替代出口学位毕业\n \n如果你选择提前离开学位课程，可能符合替代出口学位的条件。请在 Handbook "
            "里查看你的学位课程详情，确认自己是否符合。",
        "If you’re seeking an alternative exit, you should get some "
        "course advice first. All you have to do is submit a Course "
        "Advice Request form and we’ll get back to you.":
            "如果你想走替代出口学位，最好先做一次课程咨询。只要提交一份 Course Advice "
            "Request（课程咨询申请）表，我们就会回复你。",
        "Important dates View":
            "重要日期 查看",
        "Industry experiences\n \nTake a look at the various ways you "
        "can gain industry experience while at Monash.":
            "行业实践\n \n看看在 Monash 期间可以通过哪些方式积累行业经验。",
        "Monash Enrich\n \nGot a free elective space? Diversify your "
        "learning with units and programs from across the University.":
            "Monash Enrich\n \n还有自由选修的名额？用全校各院系的课程和项目，把学习的面铺得更开。",
        "Request course advice\n If you still need help, you can "
        "request course advice using this form. Right now we have a "
        "large number of enquiries so it may take a bit longer than "
        "usual to get back to you (up to five working days).You’ll "
        "need to be enrolled in at least one unit before you can "
        "access course advice through this form. We recommend you "
        "enrol in units as best you can before seeking course "
        "advice.\n\n Course Advice Request form":
            "申请课程咨询\n "
            "如果你还需要帮助，可以用这份表格申请课程咨询。目前咨询量较大，回复可能比平时慢一些（最长五个工作日）。你需要至少注册了一门课程，才能通过这份表格获得课程咨询。建议你先尽可能把课选好，再来寻求课程咨询。\n\n "
            "Course Advice Request（课程咨询申请）表",
        "Right now we have a large number of enquiries, so it will "
        "take a bit longer than usual to get back to you. If you’ve "
        "sent an enquiry, please wait for a reply before contacting us "
        "again. We anticipate a response time of five working days. "
        "Thanks for your patience.":
            "目前咨询量较大，回复会比平时慢一些。如果你已经提交过咨询，请先等回复，不必重复联系。预计回复时长为五个工作日。谢谢你的耐心。",
        "Semester dates\n \nFind the key dates for semesters one and two "
        "(including swot vac, mid-semester break, final assessment "
        "period, etc.).":
            "学期日期\n \n查看第一、第二学期的关键日期（含 swot vac 复习周、学期中假期、期末考核期等）。",
        "Student placement and opportunities View":
            "学生实习与各类机会 查看",
        "Study abroad and exchange programs\n \nGo to our Monash Abroad "
        "page to learn how you can experience the world through your "
        "studies.":
            "海外学习与交换项目\n \n打开 Monash Abroad（海外学习与交换）页面，看看如何借由学业去看世界。",
        "Supplementary assessments\n \nIf you fail a unit, you may be "
        "eligible for a supplementary assessment. Go to our "
        "supplementary assessment page to learn how they work and if "
        "you’re eligible.":
            "补考\n \n如果某门课程不及格，你可能符合补考的条件。请打开「补考」页面，了解补考如何进行、以及自己是否符合条件。",
        "Support services\nCheck out all the ways we provide support to "
        "students\n\n\nTake a look":
            "支持服务\n看看我们为学生提供的各种支持\n\n\n去看看",
        "Taking a break or leaving your course View":
            "暂停学业或离开学位课程 查看",
        "Taking a study break\n \nThere are many reasons why you might "
        "need to take a break – make sure you explore your options and "
        "the support available before you make a decision.":
            "暂停学业\n \n需要暂停学业的原因有很多——做决定之前，务必把各种选择和能拿到的支持都了解一遍。",
        "The Handbook\n \nYou can see your course requirements in the "
        "Handbook from the year you started your course. Once you’ve "
        "checked your course requirements, use the current year’s "
        "Handbook to find units to enrol in.":
            "Handbook\n \n你入学那一年的 Handbook 里写着你的学位课程要求。确认过要求之后，再用当年度的 "
            "Handbook 去找可选的课程。",
        "What would you like help with?":
            "你想了解哪方面？",
        "eExams\n \nFind out everything you need to know about eExams: "
        "learn how they work, what the rules are, and how you can "
        "prepare.":
            "eExams（线上考试）\n \n关于 eExams 你需要知道的一切：它怎么进行、有哪些规定，以及该如何准备。",
        "If you apply to take a break or discontinue your course, we’ll automatically get in contact with you to discuss your options.":
            "如果你申请休息一段时间或退出学位课程，我们会主动联系你，一起讨论可选的方案。",
    },
    "defer-final-assessment": {
        "A medical support staff member can assess you and, if "
        "necessary, provide written confirmation that you’re unfit to "
        "continue and complete your assessment.":
            "考场医护人员可以为你做评估；必要时会出具书面确认，证明你不适合继续和完成考核。",
        "Additionally, you need to submit both your application and "
        "supporting documents in time for us to reschedule your "
        "assessment and for you to complete it within 90 calendar days "
        "of results release for the original assessment period (see "
        "successful application). We may ask you to show that you can "
        "complete a rescheduled assessment within this timeframe.":
            "此外，你的申请和证明材料都必须及早提交，好让我们来得及为你重新排考，并让你在原考核期成绩公布之日起 90 "
            "个日历日内完成（见「申请获批」）。我们可能会要求你证明自己能在这个时限内完成改期后的考核。",
        "Apply to defer your assessment":
            "申请延期考核",
        "Assessment and Academic Integrity Policy (pdf)":
            "Assessment and Academic Integrity Policy（考核与学术诚信政策，pdf）",
        "Before you apply View":
            "申请之前 查看",
        "Before you apply to reschedule your deferred assessment "
        "(exam), make sure you carefully check all requirements. They "
        "are not the same as the ones that you needed to defer your "
        "assessment.":
            "在申请为延期考核（考试）改期之前，请仔细核对全部条件——它们与当初申请延期时的条件并不相同。",
        "Defer or reschedule your scheduled final assessment (exam)":
            "为已排定的期末考核（考试）申请延期或改期",
        "Deferring your assessment":
            "申请考核延期",
        "Department-run assessments View":
            "院系自行组织的考核 查看",
        "Eligibility for deferred assessment":
            "延期考核的资格条件",
        "Eligibility for rescheduled deferred assessment":
            "延期考核改期的资格条件",
        "Exam medical support staff are available during final "
        "assessment periods only.":
            "考场医护人员只在期末考核期间提供服务。",
        "For details about your course structure, take a look at the "
        "Handbook (make sure you check the Handbook for the year you "
        "started your course). You can also check the Handbook for the "
        "current year for unit prerequisite and co-requisite "
        "information.":
            "学位课程结构的细节请查看 Handbook（注意查看你入学那一年的版本）。课程的先修和同修要求，则可以查看当年度的 "
            "Handbook。",
        "Here are exceptional circumstances that may make you eligible "
        "for a deferral:":
            "下列特殊情况可能使你符合延期的条件：",
        "If a condition applies, your managing faculty will let you "
        "know.":
            "如果对你附加了某项条件，负责你的学院会通知你。",
        "If this happens, don’t worry, just get in touch with your "
        "faculty or reach out to Monash Connect and they will let you "
        "know what you need to do.":
            "遇到这种情况不必慌张，联系你所在学院、或找 Monash Connect（学生服务中心），他们会告诉你该怎么办。",
        "If you become unwell during a deferred eExam assessment, you "
        "must alert your online supervisor or contact the exam support "
        "hotline. If you don’t inform your supervisor or contact the "
        "exam support hotline we may not consider your application to "
        "defer your assessment.":
            "如果你在延期的 "
            "eExam（线上考试）过程中身体不适，必须当场告知线上监考员、或拨打考试支持热线。没有告知监考员、也没有联系热线的，我们可能不会受理你的考核延期申请。",
        "If you can’t complete a scheduled final assessment during the "
        "time it is set in Allocate+ due to exceptional circumstances, "
        "you can apply to defer it (or reschedule it if you’ve already "
        "deferred it).":
            "如果确有特殊情况使你无法在 Allocate+ 排定的时间内完成期末考核，你可以申请延期（若已经延期过，则申请改期）。",
        "If you complete a deferred assessment, you won’t be eligible "
        "for a supplementary assessment.":
            "参加过延期考核之后，就不再符合补考的条件。",
        "If you don't have your supporting documents yet, check how to "
        "submit your application without supporting documents and "
        "provide them later.":
            "如果证明材料还没拿到，请查看如何先提交申请、之后再补交材料。",
        "If you have a non-scheduled final assessment due on the same "
        "day you have to sit a scheduled final assessment, you can "
        "apply for a short extension for the non-scheduled assessment "
        "(but you can’t defer your scheduled one).":
            "如果某项非排定的期末考核，恰好与你必须参加的已排定期末考核同一天到期，你可以为那项非排定考核申请短期延期（但不能为已排定的那一场申请延期）。",
        "If you have a scheduled final assessment or you’re approved "
        "for a deferred assessment and are participating in a Monash "
        "program overseas or interstate (e.g. GIG), you’re still "
        "expected to complete your deferred assessment on the "
        "scheduled date and time – even if it overlaps with your "
        "program.":
            "如果你有已排定的期末考核、或已获批延期考核，同时正在参加 Monash 的海外或跨州项目（例如 "
            "GIG），你仍须按排定的日期和时间完成延期考核——即使它与项目时间冲突。",
        "If you have questions about re-enrolment, concerns about your "
        "academic progress or need support, contact your faculty or "
        "request course advice.":
            "如果你对重新注册有疑问、对自己的学业进度有担心，或者需要支持，请联系所在学院或申请课程咨询。",
        "If you missed the assessment because you were unwell, or "
        "because of some other exceptional circumstances, you need to "
        "provide supporting documents. For example, you need to "
        "immediately get a medical certificate (or an approved "
        "alternative) from your doctor or a campus health service to "
        "be considered eligible to defer your assessment.":
            "如果你是因为身体不适、或其他特殊情况错过了考核，就需要提交证明材料。例如，你需要立刻找医生或校内医疗服务开一份 "
            "medical certificate（医疗证明，或经认可的同等材料），才符合申请考核延期的条件。",
        "If you provide your documents too late for us to reschedule "
        "your assessment within 90 calendar days of the results "
        "release date of your original assessment period, we’ll grant "
        "you a Withdrawn (WDN) grade for the unit.":
            "如果你交材料太晚，使我们无法在原考核期成绩公布之日起 90 个日历日内为你重新排考，我们会为这门课程记 "
            "Withdrawn（WDN，退课）成绩。",
        "If you're registered with DSS, you’ll still need to provide "
        "supporting documents.":
            "即使你已在 DSS 登记，仍然需要提交证明材料。",
        "If your application is approved, we’ll defer your scheduled "
        "final assessment and you’ll get an interim DEF (deferred "
        "assessment) result. This may affect your enrolment in the "
        "next teaching period if your unit is a prerequisite.":
            "如果申请获批，我们会为你的已排定期末考核办理延期，你会先拿到一个 "
            "DEF（延期考核）的临时成绩。如果这门课是别的课程的先修课，这可能会影响你下一个开课学期的选课注册。",
        "If your deferral application has been approved, but you "
        "decide to go ahead and sit your assessment on its original "
        "set date, the deferral is no longer valid.":
            "如果你的延期申请已获批，却仍决定按原定日期参加考核，那么该延期即告失效。",
        "If you’re affected by long-term or ongoing circumstances, "
        "such as a recurring medical condition, we encourage you to "
        "register with Disability Support Services (DSS). DSS can "
        "support you with reasonable adjustments.":
            "如果你受长期或持续性情况影响，例如反复发作的健康问题，我们建议你到 Disability Support "
            "Services（DSS，无障碍支持服务）登记。DSS 可以为你安排合理调整。",
        "If you’re approved for a rescheduled deferred assessment and "
        "are participating in a Monash program overseas or interstate "
        "(e.g. GIG), you’re still expected to complete your "
        "rescheduled deferred assessment on the scheduled date and "
        "time – even if it overlaps with your program.":
            "如果你的延期考核改期已获批，同时正在参加 Monash 的海外或跨州项目（例如 "
            "GIG），你仍须按排定的日期和时间完成改期后的延期考核——即使它与项目时间冲突。",
        "If you’re in a time zone where your final assessment is "
        "scheduled to start before 5am or finish after 12.30am in your "
        "local time, you can apply for special arrangements to have "
        "your assessment start time moved to the next suitable "
        "timetabled session.":
            "如果你所在时区使期末考核的开始时间早于当地凌晨 5 点、或结束时间晚于当地次日 0 点 30 "
            "分，你可以申请特殊安排，把考核开始时间挪到下一个合适的排定场次。",
        "If you’re in a time zone where your rescheduled deferred "
        "assessment is scheduled to start before 5am or finish after "
        "12.30am in your local time, you can apply for special "
        "arrangements to have your assessment start time moved to the "
        "next suitable timetabled session.":
            "如果你所在时区使改期后的延期考核的开始时间早于当地凌晨 5 点、或结束时间晚于当地次日 0 点 30 "
            "分，你可以申请特殊安排，把考核开始时间挪到下一个合适的排定场次。",
        "If you’re not eligible to reschedule your deferred "
        "assessment, we’ll:":
            "如果你不符合延期考核改期的条件，我们会：",
        "If you’re sitting a deferred department-run assessment, "
        "you’ll need to advise your Chief Examiner that you’re unwell "
        "and arrange to see a medical professional as soon as "
        "possible. You need to get a medical certificate (or an "
        "approved alternative) from your doctor or a campus health "
        "service to be eligible to reschedule your deferred "
        "assessment. The medical certificate must demonstrate that you "
        "were affected by a medical condition during the assessment, "
        "making it impractical for you to continue or complete the "
        "assessment.":
            "如果你参加的是院系自行组织的延期考核，需要告知主考官（Chief "
            "Examiner）你身体不适，并尽快安排就医。你需要找医生或校内医疗服务开一份 medical "
            "certificate（医疗证明，或经认可的同等材料），才符合为延期考核改期的条件。这份证明必须能显示：你在考核期间确实受某种健康问题影响，以致无法继续或完成考核。",
        "Impacts on your results and enrolment":
            "对成绩和选课注册的影响",
        "Long-term or ongoing circumstances":
            "长期或持续性的情况",
        "Make sure you apply by 11.55pm on the date your final "
        "assessment is set.":
            "请务必在期末考核排定当天的 23:55 之前提交申请。",
        "Make sure you attach all supporting documents required as "
        "evidence of your unresolved circumstances or new extreme "
        "circumstances. If you don't have your supporting documents "
        "yet, check  how to submit your application without supporting "
        "documents and provide them later .":
            "请务必附上全部所需的证明材料，作为你情况尚未解决、或出现新极端情况的证据。如果材料还没拿到，请查看如何先提交申请、之后再补交材料。",
        "Marking and Feedback Procedure (pdf)":
            "Marking and Feedback Procedure（评分与反馈规程，pdf）",
        "Missed your assessment":
            "错过了考核",
        "Off-campus final assessments (eExams)":
            "校外期末考核（eExams 线上考试）",
        "On-campus final assessments (eExams)":
            "校内期末考核（eExams 线上考试）",
        "Once results are released, we won’t accept any applications "
        "to defer or reschedule assessments.":
            "成绩一旦公布，我们就不再受理任何考核延期或改期的申请。",
        "Other things to know View":
            "其他需要知道的事 查看",
        "Policy and procedure":
            "政策与流程",
        "Prerequisite units View":
            "先修课程 查看",
        "Rescheduling your deferred assessment":
            "为延期考核改期",
        "Special Consideration Procedure (pdf)":
            "Special Consideration Procedure（特殊考虑规程，pdf）",
        "Successful application View":
            "申请获批 查看",
        "Successful applications View":
            "申请获批 查看",
        "Time zone differences":
            "时区差异",
        "To be eligible, you must:":
            "要符合条件，你必须：",
        "Unsuccessful application View":
            "申请未获批 查看",
        "Unsuccessful applications View":
            "申请未获批 查看",
        "Unwell during your assessment":
            "考核期间身体不适",
        "We can’t give you a deferral for things like:":
            "下列这类原因我们不会给予延期：",
        "We won’t accept an application for a deferred or rescheduled "
        "assessment after the deadline (11.55pm on its set date) "
        "unless you can show with supporting documents that "
        "exceptional circumstances beyond your control prevented you "
        "from applying on time (e.g. you might have been hospitalised "
        "with a serious illness).":
            "考核延期或改期的申请一旦超过截止时间（排定当天 "
            "23:55）就不予受理，除非你能凭证明材料显示：确有你无法控制的特殊情况使你不能按时申请（例如你因重病住院）。",
        "We'll email you the outcome of your application within five "
        "University working days as long as you've submitted a "
        "complete application with all the required supporting "
        "documents.":
            "只要你提交的申请完整、所需证明材料齐备，我们会在五个学校工作日内把结果邮件发给你。",
        "We'll email you the outcome of your application within two "
        "University working days as long as you’ve submitted a "
        "complete application with all the required supporting "
        "documents.":
            "只要你提交的申请完整、所需证明材料齐备，我们会在两个学校工作日内把结果邮件发给你。",
        "When you should apply":
            "什么时候该申请",
        "When you should apply for an extension instead":
            "什么时候该改为申请延期",
        "When you're not eligible":
            "不符合条件的情形",
        "You can apply to defer your scheduled (in Allocate+ "
        "timetable) final assessment if you couldn’t complete it on "
        "the set date due to exceptional circumstances beyond your "
        "control.":
            "如果确有你无法控制的特殊情况，使你无法在排定日期完成期末考核（即 Allocate+ 课表上的那一场），你可以申请延期。",
        "You may be eligible to defer your scheduled final assessment "
        "(exam) if you couldn’t complete it on the set date due to "
        "exceptional circumstances beyond your control.":
            "如果确有你无法控制的特殊情况，使你无法在排定日期完成已排定的期末考核（考试），你可能符合申请延期的条件。",
        "You may wish to get support and advice.":
            "你也可以去寻求支持与建议。",
        "Your managing faculty may place conditions on your enrolment, "
        "such as:":
            "负责你的学院可能会对你的选课注册附加条件，例如：",
        "You’ll need to complete your assessment on the new date and "
        "within 90 calendar days of results release for the original "
        "assessment period.":
            "你需要在新的日期参加考核，并且要在原考核期成绩公布之日起 90 个日历日之内完成。",
        "You’ll need to provide a copy of this written confirmation "
        "with your application – along with supplementary supporting "
        "documents verifying your condition at the time of the "
        "assessment – to be eligible to apply to reschedule the "
        "assessment.":
            "申请时你需要附上这份书面确认的副本，连同能证明你考核当时状况的补充材料，才符合申请考核改期的条件。",
        "a brief interruption to power and/or internet service where "
        "you’re given additional time to complete your assessment":
            "电力或网络短暂中断、而你已经获得额外时间完成考核的情形",
        "consider you for a Withdrawn (WDN) grade if you meet the "
        "eligibility requirements, or":
            "在你符合条件时，考虑为你记 Withdrawn（WDN，退课）成绩；或者",
        "disruption caused by international conflict":
            "国际冲突造成的影响",
        "eExams View":
            "eExams（线上考试） 查看",
        "family (relationship breakdown)":
            "家庭（关系破裂）",
        "financial/employment issues":
            "经济或就业问题",
        "gender-based violence":
            "性别暴力",
        "have an ongoing disability registered with Disability Support "
        "Services (DSS) that directly prevented you from sitting your "
        "deferred assessment (such as a serious and debilitating "
        "medical condition or severe mental health condition) – see "
        "DSS-registered condition for details – or":
            "你有已在 Disability Support "
            "Services（DSS，无障碍支持服务）登记的持续性障碍，并因此直接无法参加延期考核（例如严重且使人失能的健康问题、或严重心理健康问题）——详见「已在 "
            "DSS 登记的状况」；或者",
        "limit to the credit points you can enrol in for a specific "
        "teaching period":
            "限制你在某个开课学期可以选的学分数",
        "losing your Moodle access because you didn’t complete a "
        "compulsory module":
            "因为没完成必修模块而被停用 Moodle",
        "loss or bereavement":
            "亲人离世与哀伤",
        "loss or bereavement: death of a person with whom you had a "
        "significant relationship":
            "亲人离世与哀伤：与你有重要关系的人过世",
        "mandatory enrolment in specific units":
            "必须选修指定的课程",
        "medical condition (including COVID-19)":
            "健康问题（含新冠）",
        "mental health condition":
            "心理健康问题",
        "military, jury or emergency services obligations":
            "兵役、陪审团或紧急救援服务义务",
        "missing your assessment due to mistaking its set date, time "
        "or location":
            "因为记错考核的日期、时间或地点而错过考核",
        "obligations as athlete, artist or performer registered with "
        "Elite Student Performer Scheme or as representative of "
        "University in other key events and programs":
            "作为已在 Elite Student Performer "
            "Scheme（ESPS，精英学生表现者计划）登记的运动员、艺术家或表演者所负的义务，或代表学校参加其他重要赛事和项目的义务",
        "other exceptional circumstances beyond your control.":
            "其他你无法控制的特殊情况。",
        "other extreme circumstances.":
            "其他极端情况。",
        "provide evidence of one or more of these extreme "
        "circumstances beyond your control:":
            "提供证据，证明存在下列一种或多种你无法控制的极端情况：",
        "religious or cultural obligations":
            "宗教或文化义务",
        "representing a club or society as a volunteer.":
            "以志愿者身份代表某个社团或学会。",
        "requirement to successfully pass specific units or a number "
        "of credit points.":
            "要求你必须通过指定课程、或修满一定学分。",
        "serious and debilitating medical condition":
            "严重且使人失能的健康问题",
        "severe mental health condition":
            "严重心理健康问题",
        "show that the exceptional circumstances approved for your "
        "deferred assessment have not yet been resolved by providing "
        "updated supporting documents or":
            "提交更新后的证明材料，显示当初获批延期考核时的那些特殊情况至今仍未解决；或者",
        "technical disruption":
            "技术故障",
        "technical issues you might have avoided by uploading the "
        "correct files, allowing enough time for uploading and having "
        "the right equipment":
            "本可以避免的技术问题，例如上传了正确的文件、留出足够的上传时间、或备好合适的设备就不会发生的那些",
        "victim of crime or concerns about safety":
            "遭受犯罪侵害，或对人身安全的担忧",
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
        "Consider your options":
            "先把各种选择考虑清楚",
        "Course Discontinuation Request form":
            "Course Discontinuation Request form（退课申请表）",
        "Discontinue your course":
            "退课",
        "Enrolment Procedure 7.1 - 7.4 (pdf)":
            "Enrolment Procedure（选课注册规程）7.1–7.4（pdf）",
        "International student":
            "国际学生",
        "Step 1: When to request discontinuation":
            "第 1 步：什么时候提出退课申请",
        "Step 2: Submit the form":
            "第 2 步：提交表格",
        "Thinking about leaving your course?":
            "在考虑离开这个学位课程？",
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
        "Enrol for the first time":
            "第一次选课注册",
        "For information on unit changes, course and campus transfers, "
        "taking a break, discontinuing your course and how to update "
        "your personal details.":
            "关于改课、转学位课程与转校区、暂停学业、退课，以及如何更新个人信息。",
        "For students new to Monash. You'll also find information here "
        "on credit, complementary and cross-institutional study or "
        "options to defer your course.":
            "写给刚来 Monash 的同学。这里也有学分减免、辅修与跨校学习，以及推迟入学等方面的信息。",
        "Government support and loans":
            "政府资助与贷款",
        "Important dates See what's coming up\n\n Take a look":
            "重要日期　看看接下来有什么\n\n 去看看",
        "Looking for electives? Check out Monash Enrich\nOur Monash "
        "Enrich website has information on elective units from across "
        "the University that don't require any prerequisites or "
        "corequisites. Take a look and diversify your learning.\n\n See "
        "Monash Enrich":
            "在找选修课？看看 Monash Enrich\nMonash Enrich "
            "网站汇总了全校各院系不设先修和同修要求的选修课程，去看看，把学习的面铺得更开一些。\n\n 打开 Monash Enrich",
        "Monash Study app Check your timetable, find classrooms,\nand "
        "view your assessment info\n\n Get the app":
            "Monash Study app（Monash 学习 app）　查看课表、找教室、看考核信息\n\n 下载 app",
        "Some students may be eligible for government income support "
        "through schemes, fee loans or grants.":
            "部分学生可能符合条件，通过各类计划、学费贷款或补助金获得政府的收入支持。",
        "Summer and winter semester":
            "夏季学期与冬季学期",
        "These semesters allow you to complete units outside the "
        "standard semesters' dates. Helpful if you need to re-do a "
        "unit.":
            "这两个学期让你可以在标准学期之外修课，需要重修某门课程时尤其有用。",
        "Unit attendance mode":
            "课程的授课形式",
        "Continuing students must re-enrol for the entire following year – or apply for intermission – during the specified re-enrolment period.":
            "在读学生必须在规定的重新注册期内，完成次年整年的重新注册，或者申请休学（intermission）。",
    },
    "final-assessment-dates": {
        "10 Aug 2026 (if eExams are scheduled)":
            "2026年8月10日（如已排定 eExams 线上考试）",
        "17 Jul 2024 for semester one (S1-01) 2024":
            "2024年7月17日（用于（S1-01）2024）",
        "18 May 2026 (if eExams are scheduled)":
            "2026年5月18日（如已排定 eExams 线上考试）",
        "19 Oct 2026 (if eExams are scheduled)":
            "2026年10月19日（如已排定 eExams 线上考试）",
        "2 Feb 2026 (if eExams are scheduled)":
            "2026年2月2日（如已排定 eExams 线上考试）",
        "2024 teaching periods View":
            "2024 年各开课学期 查看",
        "2025 teaching periods View":
            "2025 年各开课学期 查看",
        "2026 teaching periods View":
            "2026 年各开课学期 查看",
        "22 Jul 2026 for semester one (S1-01) 2026":
            "2026年7月22日（用于（S1-01）2026）",
        "23 Jul 2025 for semester one (S1-01) 2025":
            "2025年7月23日（用于（S1-01）2025）",
        "25 Jan – 29 Jan 2027":
            "2027年1月25日至1月29日",
        "28 Oct – 15 Nov 2024":
            "2024年10月28日至11月15日",
        "28 Sep –- 1 Oct 2025":
            "9月28日 –- 2025年10月1日",
        "3 Jan 2025 for semester two (S2-01) 2024.":
            "2025年1月3日（用于（S2-01）2024.）",
        "4 Jan 2027  for semester two (S2-01) 2026.":
            "2027年1月4日（用于（S2-01）2026.）",
        "5 Jan 2026 for semester two (S2-01) 2025.":
            "2026年1月5日（用于（S2-01）2025.）",
        "5 Oct 2026 (if eExams are scheduled)":
            "2026年10月5日（如已排定 eExams 线上考试）",
        "Allocate+: The dates and times for some final assessments "
        "(including eExams) are published in Allocate+ from 12pm on "
        "the timetable release dates (shown in the tables below).":
            "Allocate+：部分期末考核（含 eExams 线上考试）的日期和时间，会在课表发布日当天 12:00 起在 "
            "Allocate+ 上公布（发布日见下表）。",
        "Alternative assessment arrangements":
            "替代考核安排",
        "Assessment timetable publication":
            "考核课表公布",
        "Assessment timetable release":
            "考核课表发布",
        "Can't complete your assessment?":
            "无法完成考核？",
        "Census dates and teaching periods\n \nCheck the census date for "
        "your teaching period to find out until when you can withdraw "
        "from units.":
            "census dates（学籍统计日）与开课学期\n \n查看你所在开课学期的 census "
            "date（学籍统计日），弄清可以退选课程到哪一天为止。",
        "Deadline for deferred, supplementary & rescheduled assessments":
            "延期考核、补考与改期考核的截止期限",
        "Deferred and supplementary assessment period":
            "延期考核与补考期",
        "Deferred and supplementary assessment timetables are released "
        "on:":
            "延期考核与补考的课表发布日期：",
        "Deferred and supplementary assessments":
            "延期考核与补考",
        "Deferred assessments":
            "延期考核",
        "Final assessment dates":
            "期末考核日期",
        "Final assessment period":
            "期末考核期",
        "For all other teaching periods, you’ll be given notice of at "
        "least five University working days of the date of your "
        "deferred or supplementary assessment.":
            "其余各开课学期，延期考核或补考的日期会至少提前五个学校工作日通知你。",
        "Full-year (extended)":
            "全学年（延长）",
        "Full-year (extended) (FY-32)":
            "全学年（延长）（FY-32）",
        "If your teaching period isn’t listed, there is no defined "
        "final assessment period. If you’re unsure when your final "
        "assessments will be held, check Moodle or contact your "
        "faculty.":
            "如果表里没有你的开课学期，说明它没有固定的期末考核期。不确定期末考核什么时候进行的话，请查看 Moodle 或联系所在学院。",
        "It applies to these teaching periods:":
            "适用于下列开课学期：",
        "MBA 1 ( MBA-TP1-01 )":
            "MBA 1（MBA-TP1-01）",
        "MBA 2 ( MBA-TP2-01 )":
            "MBA 2（MBA-TP2-01）",
        "Monash Indonesia Semester 2 (MI-S2)":
            "Monash Indonesia（印尼校区） 第二学期（MI-S2）",
        "Monash Indonesia Term 4 (MI-T4-6)":
            "Monash Indonesia（印尼校区） 第 4 学季（MI-T4-6）",
        "Monash Indonesia term 1 ( MI-T1-6 )":
            "Monash Indonesia（印尼校区） 第 1 学季（MI-T1-6）",
        "Monash Indonesia term 1 (2024)":
            "Monash Indonesia（印尼校区） 第 1 学季（2024）",
        "Monash Indonesia term 1 (MI-T1-6)":
            "Monash Indonesia（印尼校区） 第 1 学季（MI-T1-6）",
        "Monash Indonesia term 2 (2023–2024)":
            "Monash Indonesia（印尼校区） 第 2 学季（2023–2024）",
        "Monash Indonesia term 2 (2024)":
            "Monash Indonesia（印尼校区） 第 2 学季（2024）",
        "Monash Indonesia term 2 (2025)":
            "Monash Indonesia（印尼校区） 第 2 学季（2025）",
        "Monash Indonesia term 2 (MI-T2-6)":
            "Monash Indonesia（印尼校区） 第 2 学季（MI-T2-6）",
        "Monash Indonesia term 3 ( MI-T3-6 )":
            "Monash Indonesia（印尼校区） 第 3 学季（MI-T3-6）",
        "Monash Indonesia term 3 (2023–2024)":
            "Monash Indonesia（印尼校区） 第 3 学季（2023–2024）",
        "Monash Indonesia term 3 (2024)":
            "Monash Indonesia（印尼校区） 第 3 学季（2024）",
        "Monash Indonesia term 3 (MI-T3-6)":
            "Monash Indonesia（印尼校区） 第 3 学季（MI-T3-6）",
        "Monash Indonesia term 4 ( MI-T4-6 )":
            "Monash Indonesia（印尼校区） 第 4 学季（MI-T4-6）",
        "Monash Indonesia term 4 (2023–2024)":
            "Monash Indonesia（印尼校区） 第 4 学季（2023–2024）",
        "Monash Indonesia term 4 (2024)":
            "Monash Indonesia（印尼校区） 第 4 学季（2024）",
        "Monash Indonesia term 4 (MI-T4-6)":
            "Monash Indonesia（印尼校区） 第 4 学季（MI-T4-6）",
        "Monash Indonesia term 5 (MI-T5-6)":
            "Monash 印尼校区第 5 学季（MI-T5-6）",
        "Monash Online 1 (MO-TP1-01)":
            "Monash Online（在线） 1（MO-TP1-01）",
        "Monash Online 2 (MO-TP2-01)":
            "Monash Online（在线） 2（MO-TP2-01）",
        "Monash Online 3 (MO-TP3-01":
            "Monash Online（在线） 3（MO-TP3-01",
        "Monash Online 3 (MO-TP3-01)":
            "Monash Online（在线） 3（MO-TP3-01）",
        "Monash Online 4 ( MO-TP4-01 )":
            "Monash Online（在线） 4（MO-TP4-01）",
        "Monash Online 4 (MO-TP4-01)":
            "Monash Online（在线） 4（MO-TP4-01）",
        "Monash Online 5 ( MO-TP5-01 )":
            "Monash Online（在线） 5（MO-TP5-01）",
        "Monash Online 5 (MO-TP5-01)":
            "Monash Online（在线） 5（MO-TP5-01）",
        "Monash Online 6 ( MO-TP6-01 )":
            "Monash Online（在线） 6（MO-TP6-01）",
        "Monash Online 6 (MO-TP6-01)":
            "Monash Online（在线） 6（MO-TP6-01）",
        "Moodle: Take a look at each unit’s final assessment "
        "information for any assignments, department-run assessments "
        "or other types of assessment due in the final assessment "
        "period.":
            "Moodle：查看每门课程的期末考核信息，了解在期末考核期内到期的作业、院系自行组织的考核，以及其他类型的考核。",
        "Most teaching periods have swot vac – a week without teaching "
        "activities so you can prepare for your final assessments.":
            "多数开课学期都有 swot vac（复习周）——这一周没有教学活动，供你准备期末考核。",
        "November intake (Australia)":
            "11 月入学（澳大利亚）",
        "November intake – Australia":
            "11 月入学（澳大利亚）",
        "November intake – Australia (NOV12)":
            "11 月入学（澳大利亚）（NOV12）",
        "October intake (Malaysia)":
            "10 月入学（马来西亚）",
        "October intake – Malaysia":
            "10 月入学（马来西亚）",
        "October intake – Malaysia ( OCT-MY-01 )":
            "10 月入学（马来西亚）（OCT-MY-01）",
        "October intake – Malaysia (OCT-MY-01)":
            "10 月入学（马来西亚）（OCT-MY-01）",
        "Rescheduled deferred assessment period":
            "改期后的延期考核期",
        "Rescheduled deferred assessments":
            "改期后的延期考核",
        "Research Q1 (RES-Q1)":
            "研究季度 1（RES-Q1）",
        "Research Q2 (RES-Q2)":
            "研究季度 2（RES-Q2）",
        "Research Q3 (RES-Q3)":
            "研究季度 3（RES-Q3）",
        "Research Q4 (RES-Q4)":
            "研究季度 4（RES-Q4）",
        "Search by teaching period or code. Results will appear as you "
        "type.":
            "可按开课学期或代码搜索，边输入边出结果。",
        "See the final assessment and results release dates for the "
        "2024 teaching periods below – only scheduled assessments "
        "(those included in your Allocate+ timetable) are listed here.":
            "2024 年各开课学期的期末考核与成绩公布日期见下——这里只列出已排定的考核（即出现在你 Allocate+ "
            "课表上的那些）。",
        "See the final assessment periods and results release dates "
        "for the 2025 teaching periods below.":
            "2025 年各开课学期的期末考核期与成绩公布日期见下。",
        "See the final assessment periods and results release dates "
        "for the 2026 teaching periods below.":
            "2026 年各开课学期的期末考核期与成绩公布日期见下。",
        "Semester 1 (extended)":
            "第一学期（延长）",
        "Semester 1 (extended) (S1-32)":
            "第一学期（延长）（S1-32）",
        "Semester 1 (northern)":
            "第一学期（北半球）",
        "Semester 1 (northern) (S1-60)":
            "第一学期（北半球）（S1-60）",
        "Semester 2 (extended)":
            "第二学期（延长）",
        "Semester 2 (extended) (S2-32)":
            "第二学期（延长）（S2-32）",
        "Semester 2 (northern)":
            "第二学期（北半球）",
        "Semester 2 (northern) (S2-60)":
            "第二学期（北半球）（S2-60）",
        "Semester 2 – semester 1":
            "第二学期 – 第一学期",
        "Semester 2 – semester 1 ( S2-S1-02 )":
            "第二学期 – 第一学期（S2-S1-02）",
        "Semester 2 – semester 1 (S2-S1-02)":
            "第二学期 – 第一学期（S2-S1-02）",
        "Semester 2 – summer A":
            "第二学期 – 夏季学期 A",
        "Semester 2 – summer A ( S2-SS-02 )":
            "第二学期 – 夏季学期 A（S2-SS-02）",
        "Semester 2 – summer A (S2-SS-02)":
            "第二学期 – 夏季学期 A（S2-SS-02）",
        "Semester dates summary\n \nTake a look at the most important "
        "dates for your semester, including orientation week, swot "
        "vac, mid-sem break and more.":
            "学期日期一览\n \n查看本学期最重要的那些日期，包括迎新周、swot vac（复习周）、学期中假期等。",
        "Semester one (S1-01)":
            "第一学期（S1-01）",
        "Semester one (S1-01) and associated teaching periods":
            "第一学期（S1-01）及相关开课学期",
        "Semester one (and associated teaching periods)":
            "第一学期（及相关开课学期）",
        "Semester one: 27–31 May 2024\nSemester two: 21–25 Oct "
        "2024\nNovember intake 2024: 27–31 Jan 2025":
            "第一学期：2024年5月27日至31日\n第二学期：2024年10月21日至25日\n11 月入学 2024: "
            "2025年1月27日至31日",
        "Semester two (S2-01)":
            "第二学期（S2-01）",
        "Semester two (S2-01) and associated teaching periods":
            "第二学期（S2-01）及相关开课学期",
        "Semester two (S2-02)":
            "第二学期（S2-02）",
        "Semester two (and associated teaching periods)":
            "第二学期（及相关开课学期）",
        "Summer A – semester 1":
            "夏季学期 A – 第一学期",
        "Summer A – semester 1 ( SS-S1-01 )":
            "夏季学期 A – 第一学期（SS-S1-01）",
        "Summer A – semester 1 (SS-S1-01)":
            "夏季学期 A – 第一学期（SS-S1-01）",
        "Summer semester A (SSA-02)":
            "夏季学期 A（SSA-02）",
        "Summer semester A (SSA-02), summer semester B (SSB-01), "
        "October intake – Malaysia (OCT-MY-01) and November intake – "
        "Australia (NOV12)":
            "夏季学期 A（SSA-02）、夏季学期 B（SSB-01）、10 月入学（马来西亚）（OCT-MY-01）、11 "
            "月入学（澳大利亚）（NOV12）",
        "Summer semester B (SSB-01)":
            "夏季学期 B（SSB-01）",
        "Summer, October and November teaching periods":
            "夏季、10 月与 11 月教学期",
        "Supplementary assessments":
            "补考",
        "Teaching period, code and their deferred and supplementary "
        "assessment period with rescheduled deferred and supplementary "
        "assessments deadline.":
            "开课学期、代码，及其延期考核与补考期，以及改期后延期考核与补考的截止期限。",
        "Teaching period, code and their final assessment period and "
        "results release date":
            "开课学期、代码，及其期末考核期与成绩公布日期",
        "The deadline to complete a rescheduled assessment is 90 "
        "calendar days from the results release date of the original "
        "assessment period.":
            "改期后的考核必须在原考核期成绩公布之日起 90 个日历日内完成。",
        "Timetable release 12pm in Allocate+":
            "课表于 12:00 在 Allocate+ 发布",
        "To find out when your final assessments will be, you’ll need "
        "to check Allocate+ and Moodle:":
            "想知道期末考核什么时候进行，需要同时查看 Allocate+ 和 Moodle：",
        "Trimester 1 (Faculty of Law units only)":
            "第 1 学段（仅限法学院课程）",
        "Trimester 1 (T1-58) (Except Faculty of Law units)":
            "第 1 学段（T1-58）（法学院课程除外）",
        "Trimester 1 (T1-58) (Except JD Law units)":
            "第 1 学段（T1-58）（JD 法学课程除外）",
        "Trimester 1 (T1-58) (Faculty of Law units only)":
            "第 1 学段（T1-58）（仅限法学院课程）",
        "Trimester 1 (T1-58) (JD Law units only)":
            "第 1 学段（T1-58）（仅限 JD 法学课程）",
        "Trimester 2 (Faculty of Law units only)":
            "第 2 学段（仅限法学院课程）",
        "Trimester 2 (T2-58) (Except Faculty of Law units)":
            "第 2 学段（T2-58）（法学院课程除外）",
        "Trimester 2 (T2-58) (Faculty of Law units only)":
            "第 2 学段（T2-58）（仅限法学院课程）",
        "Trimester 3 (Faculty of Law units only)":
            "第 3 学段（仅限法学院课程）",
        "Trimester 3 (T3-58) (Except Faculty of Law units)":
            "第 3 学段（T3-58）（法学院课程除外）",
        "Trimester 3 (T3-58) (Faculty of Law units only)":
            "第 3 学段（T3-58）（仅限法学院课程）",
        "Winter semester (WS-01)":
            "冬季学期（WS-01）",
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
            "更多细节，请查看 compassionate or compelling "
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
            "Report（HPR，健康专业人员报告），作为按 compassionate or compelling "
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
            "如果你不是持学生签证，可以直接申请休学（intermission）——不需要证明存在 compassionate or "
            "compelling circumstances（体恤或不可抗情形）。",
        "If you're on a student visa, approval for study leave is "
        "given only in compassionate or compelling circumstances "
        "(unless intermission was recommended by an Academic Progress "
        "Committee panel).":
            "如果你持学生签证，只有在存在 compassionate or compelling "
            "circumstances（体恤或不可抗情形）时，study "
            "leave（休学）才会获批（除非休学是学业进度审查委员会小组建议的）。",
        "If you're only taking leave for one semester or teaching "
        "period, don’t forget to re-enrol for the following semester "
        "or teaching period – see re-enrolment dates and details.":
            "如果你只休一个学期或一个开课学期的假，别忘了为下一个学期或开课学期重新注册选课——请查看重新注册的日期与说明。",
        "If you’re granted study leave for compassionate or compelling "
        "circumstances, there are a few things you’ll need to do:":
            "如果你因 compassionate or compelling circumstances（体恤或不可抗情形）获批 "
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
        "2026 OSHC price list":
            "2026 年 OSHC（留学生医疗保险）价目表",
        "Allianz Care Australia OSHC Essentials":
            "Allianz Care Australia OSHC（留学生医疗保险）要点",
        "Allianz Care Australia Policy Wording Documents":
            "Allianz Care Australia 保单条款文件",
        "Allianz Care Australia pregnancy fact sheet (pdf, 0.74 mb)":
            "Allianz Care Australia 孕产保障说明（pdf，0.74 mb）",
        "Allianz Care OSHC doesn’t cover you for services like dental, "
        "optical and physiotherapy. You can purchase an extras policy "
        "for common health services like dental, optical, "
        "physiotherapy, chiropractic and osteopathy. Learn more about "
        "extras for international students.":
            "Allianz Care 的 "
            "OSHC（留学生医疗保险）不涵盖牙科、验光配镜和物理治疗等服务。你可以另外购买附加保障保单，涵盖牙科、验光配镜、物理治疗、脊椎按摩治疗和整骨治疗等常见医疗服务。详见「国际学生附加保障」。",
        "As a Monash student, you also have access to all the "
        "University Health Services.":
            "作为 Monash 学生，你还可以使用 University Health Services（校内医疗服务）的全部服务。",
        "Belgian student who has a Europese ziekteverzekeringskaart "
        "(EZVK) – Carte Européenne d'Assurance Maladie (CEAM) from "
        "your mutualiteit – mutualité in Belgium.":
            "比利时学生，且持有本国医保机构（mutualiteit / mutualité）签发的欧洲健康保险卡（Europese "
            "ziekteverzekeringskaart，EZVK／Carte Européenne d'Assurance "
            "Maladie，CEAM）。",
        "Continuing students – calculate 2026 prices":
            "在读学生——计算 2026 年价格",
        "DOWNLOAD AND REGISTER FOR SONDER":
            "下载并注册 Sonder",
        "Download the Sonder app from your app store.":
            "从应用商店下载 Sonder app。",
        "Enter the three fields below:":
            "填写下面三项：",
        "Extras cover for ancillary services (optional)":
            "附加服务保障（可选）",
        "Go to the MyHealth portal.":
            "打开 MyHealth 门户。",
        "If an organisation or scholarship pays for your OSHC policy, "
        "you may need to upgrade the policy at your own expense. "
        "Please refer to your International Student Course Agreement "
        "(ISCA) or your sponsorship/scholarship letter for further "
        "information.":
            "如果你的 OSHC（留学生医疗保险）保单由某个机构或奖学金支付，你可能需要自费升级保单。详情请查看你的 "
            "International Student Course "
            "Agreement（ISCA，国际学生入学协议）或资助／奖学金函件。",
        "If you choose for Monash to arrange your OSHC for you, we’ll "
        "arrange your OSHC policy with Allianz Care Australia and will "
        "provide your personal details to them so they can schedule "
        "your policy. Monash receives an administration fee from "
        "Allianz Care for the services performed by Monash for "
        "students and Allianz in respect of the provision of Allianz "
        "Care’s OSHC policies. View the Allianz Care Australia Policy "
        "Wording Documents.":
            "如果你选择由 Monash 代为办理 OSHC（留学生医疗保险），我们会向 Allianz Care Australia "
            "为你投保，并把你的个人信息提供给他们以便安排保单。就 Monash 为学生和 Allianz 双方在提供 Allianz "
            "Care 的 OSHC（留学生医疗保险）保单方面所做的工作，Monash 会从 Allianz Care "
            "收取一笔管理费。详见 Allianz Care Australia 保单条款文件。",
        "If you haven’t received your COI or can’t find it, contact "
        "Allianz Care Australia.":
            "如果你没收到 COI（保险凭证）、或者找不到了，请联系 Allianz Care Australia。",
        "If you need to extend your stay in Australia, it's important "
        "you have ongoing health cover for the duration of your visa.":
            "如果你需要延长在澳大利亚停留的时间，务必确保在整个签证有效期内都有持续的医疗保险保障。",
        "If you're with Allianz Care Australia, you can find out the "
        "total cost of dual or multi-family cover by obtaining a quote "
        "or calling a representative on 13 67 42 from 8.30am–5pm, "
        "Monday–Friday (Melbourne time). If you're with another "
        "provider, contact them directly to do this.":
            "如果你投保的是 Allianz Care Australia，可以在周一至周五 8:30–17:00（墨尔本时间）拨打 "
            "13 67 42 索取报价或咨询客服，了解双人或多人家庭保障的总费用。如果你投保的是其他保险公司，请直接联系该公司办理。",
        "International students on a student visa must have health "
        "cover for the length of their visa while studying in "
        "Australia. The Monash-preferred OSHC provider is Allianz Care "
        "Australia and the benefits of this policy include:":
            "持学生签证的国际学生，在澳大利亚学习期间必须在整个签证有效期内持有医疗保险保障。Monash 首选的 "
            "OSHC（留学生医疗保险）承保方是 Allianz Care Australia，这份保单的保障包括：",
        "New students – calculate 2026 prices":
            "新生——计算 2026 年价格",
        "Norwegian student who is a member of the Norwegian Health "
        "Economics Administration (HELFO)":
            "挪威学生，且为挪威健康经济管理局（HELFO）的参保人",
        "Once you've purchased your Allianz Care Australia OSHC policy":
            "在你购买 Allianz Care Australia 的 OSHC（留学生医疗保险）保单之后",
        "Once you've renewed your cover, notify Monash University:":
            "续保之后，请通知 Monash 大学：",
        "Open the email on your phone and select the link to complete "
        "the process.":
            "在手机上打开这封邮件，点击其中的链接完成后续步骤。",
        "Overseas Student Health Cover (OSHC)":
            "留学生医疗保险（OSHC）",
        "Overseas Student Health Cover Policy – see section 6 of the "
        "Student Fees Policy (pdf, 0.1mb)":
            "留学生医疗保险政策——见 Student Fees Policy（学费政策，pdf，0.1mb）第 6 节",
        "Overseas Student Health Cover fact sheet (pdf)":
            "留学生医疗保险说明（pdf）",
        "REGISTER FOR ALLIANZ MYHEALTH":
            "注册 Allianz MyHealth",
        "Swedish student who is a member of CSN International (the "
        "Swedish National Board of Student Aid) or Kammarkollegiet "
        "(the Swedish Legal, Financial and Administration Agency) or":
            "瑞典学生，且为 CSN International（瑞典国家学生资助委员会）或 "
            "Kammarkollegiet（瑞典法律、财务与行政事务管理局）的成员；或者",
        "Tap reset password and enter your Monash email address.":
            "点击「重置密码」，填入你的 Monash 邮箱地址。",
        "Tap the log in button.":
            "点击登录按钮。",
        "The Department of Health also has information about health "
        "cover for students and visitors.":
            "澳大利亚卫生部也有面向学生和访客的医疗保险信息。",
        "Times to meet an OSHC adviser on campus":
            "校内 OSHC（留学生医疗保险）顾问的接待时间",
        "Upgrading your OSHC to dual or multi-family cover":
            "把你的 OSHC（留学生医疗保险）升级为双人或多人家庭保障",
        "We strongly encourage international visitors who are not on a "
        "student visa to purchase personal health cover for their time "
        "in Australia. See health cover options for overseas visitors.":
            "对于不持学生签证的海外访客，我们强烈建议自行购买在澳期间的个人医疗保险。请查看「海外访客医疗保险选择」。",
        "Work out how many more months of OSHC you need.":
            "算一算你还需要多少个月的 OSHC（留学生医疗保险）。",
        "You don’t need to purchase OSHC if you’re a:":
            "属于下列情形的，不需要购买 OSHC（留学生医疗保险）：",
        "You will receive a password reset email.":
            "你会收到一封重置密码的邮件。",
        "You'll receive your COI through email.":
            "COI（保险凭证）会通过邮件发给你。",
        "access to Sonder at no extra cost (which includes 24/7 "
        "safety, mental health and medical support)":
            "免费使用 Sonder（含 7×24 小时的安全、心理健康与医疗支持）",
        "access to the Allianz Care Australia Student Hub to help you "
        "get the most from your cover.":
            "可使用 Allianz Care Australia Student Hub，帮你把保险保障用足。",
        "complete the declaration with the start and end dates of your "
        "OSHC.":
            "填写声明，写明你 OSHC（留学生医疗保险）的起止日期。",
        "date of birth":
            "出生日期",
        "first three characters of your family name.":
            "姓氏的前三个字符。",
        "log into WES (Web Enrolment System)":
            "登录 WES（学生系统）",
        "on-campus Allianz Care Australia agent":
            "校内 Allianz Care Australia 代表",
        "policy number (on your Certificate of Insurance – COI)":
            "保单号（在你的 Certificate of Insurance（COI，保险凭证）上）",
        "read the statement and click Continue":
            "阅读声明后点击 Continue（继续）",
        "select Overseas Student Health Cover (OSHC)":
            "选择 Overseas Student Health Cover（OSHC）",
        "waived waiting periods for mental health":
            "心理健康服务免等待期",
        "waived waiting periods for pregnancy-related claims on "
        "policies with a duration of two years or more":
            "保单期限满两年及以上的，孕产相关理赔免等待期",
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
        "2025 Principal dates":
            "2025 年重要日期",
        "Allocate+ allocation adjustment closes at 5pm: November "
        "intake (NOV12)":
            "Allocate+ 分配调整于 17:00 关闭：11 月入学（NOV12）",
        "Allocate+ allocation adjustment closes at 5pm: Semester one "
        "(S1-01)":
            "Allocate+ 分配调整于 17:00 关闭：第一学期（S1-01）",
        "Allocate+ allocation adjustment closes at 5pm: Semester two "
        "(S2-01)":
            "Allocate+ 分配调整于 17:00 关闭：第二学期（S2-01）",
        "Allocate+ allocation adjustment opens at 10am: November "
        "intake (NOV12) and summer A (SSB-02)":
            "Allocate+ 分配调整于 10:00 开放：11 月入学（NOV12）、夏季学期 A（SSB-02）",
        "Allocate+ allocation adjustment opens at 10am: Semester one "
        "(S1-01)":
            "Allocate+ 分配调整于 10:00 开放：第一学期（S1-01）",
        "Allocate+ allocation adjustment opens at 10am: Semester two "
        "(S2-01)":
            "Allocate+ 分配调整于 10:00 开放：第二学期（S2-01）",
        "Allocate+ allocation adjustment opens at 10am: Summer B "
        "(SSB-01) 2027":
            "Allocate+ 分配调整于 10:00 开放：夏季学期 B（SSB-01）2027",
        "Allocate+ preference entry closes at 5pm: Semester one (S1-01)":
            "Allocate+ 志愿填报于 17:00 关闭：第一学期（S1-01）",
        "Allocate+ preference entry closes at 5pm: Semester two (S2-01)":
            "Allocate+ 志愿填报于 17:00 关闭：第二学期（S2-01）",
        "Allocate+ preference entry opens at 10am: Semester one (S1-01)":
            "Allocate+ 志愿填报于 10:00 开放：第一学期（S1-01）",
        "Allocate+ preference entry opens at 10am: Semester two (S2-01)":
            "Allocate+ 志愿填报于 10:00 开放：第二学期（S2-01）",
        "Bachelor of Pharmacy placement dates for years three and four.":
            "药学学士学位第三、第四年的实习日期。",
        "Census date: Full-year extended (FY-32). Last day to withdraw "
        "from units without incurring fees. Units withdrawn after this "
        "date will show as Withdrawn on your academic record":
            "census "
            "date（学籍统计日）：全学年（延长）（FY-32）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 "
            "Withdrawn（退课）",
        "Census date: November intake (NOV12). Last day to withdraw "
        "from units without incurring fees. Units withdrawn after this "
        "date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：11 "
            "月入学（NOV12）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Semester 1 (northern) (S1-60). Last day to "
        "withdraw from units without incurring fees. Units withdrawn "
        "after this date will show as Withdrawn on your academic record":
            "census "
            "date（学籍统计日）：第一学期（北半球）（S1-60）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 "
            "Withdrawn（退课）",
        "Census date: Semester 2 (extended) (S2-32). Last day to "
        "withdraw from units without incurring fees. Units withdrawn "
        "after this date will show as Withdrawn on your academic record":
            "census "
            "date（学籍统计日）：第二学期（延长）（S2-32）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 "
            "Withdrawn（退课）",
        "Census date: Semester 2 (northern) (S2-60). Last day to "
        "withdraw from units without incurring fees. Units withdrawn "
        "after this date will show as Withdrawn on your academic record":
            "census "
            "date（学籍统计日）：第二学期（北半球）（S2-60）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 "
            "Withdrawn（退课）",
        "Census date: Semester 2 - semester 1 (S2-S1-02). Last day to "
        "withdraw from units without incurring fees. Units withdrawn "
        "after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：第二学期 - "
            "第一学期（S2-S1-02）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 "
            "Withdrawn（退课）",
        "Census date: Semester 2 - summer A (S2-SS-02). Last day to "
        "withdraw from units without incurring fees. Units withdrawn "
        "after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：第二学期 - 夏季学期 "
            "A（S2-SS-02）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Summer A - semester 1 (SS-S1-01). Last day to "
        "withdraw from units without incurring fees. Units withdrawn "
        "after this date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：夏季学期 A - "
            "第一学期（SS-S1-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 "
            "Withdrawn（退课）",
        "Census date: Summer semester A (SSA-02). Last day to withdraw "
        "from units without incurring fees. Units withdrawn after this "
        "date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：夏季学期 "
            "A（SSA-02）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Summer semester B (SSB-01). Last day to withdraw "
        "from units without incurring fees. Units withdrawn after this "
        "date will show as Withdrawn on your academic record":
            "census date（学籍统计日）：夏季学期 "
            "B（SSB-01）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Term 4 (T4-57). Last day to withdraw from units "
        "without incurring fees. Units withdrawn after this date will "
        "show as Withdrawn on your academic record":
            "census date（学籍统计日）：第 4 "
            "学季（T4-57）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Census date: Trimester 3 (T3-58). Last day to withdraw from "
        "units without incurring fees. Units withdrawn after this date "
        "will show as Withdrawn on your academic record":
            "census date（学籍统计日）：第 3 "
            "学段（T3-58）。退选课程且不产生学费的最后一天。此日期之后退选的课程，会在成绩单上记为 Withdrawn（退课）",
        "Course transfers: Applications close at 11.59pm (Melbourne "
        "time) for semester one (S1-01) 2027":
            "转学位课程：申请于 23:59（墨尔本时间）截止——第一学期（S1-01）2027",
        "Course transfers: Applications close at 11.59pm (Melbourne "
        "time) for semester two (S2-01)":
            "转学位课程：申请于 23:59（墨尔本时间）截止——第二学期（S2-01）",
        "Course transfers: Applications open at 9am (Melbourne time) "
        "for semester one (S1-01) 2027":
            "转学位课程：申请于 09:00（墨尔本时间）开放——第一学期（S1-01）2027",
        "Course transfers: Applications open at 9am (Melbourne time) "
        "for semester two (S2-01)":
            "转学位课程：申请于 09:00（墨尔本时间）开放——第二学期（S2-01）",
        "Course transfers: Change of preference deadline at 11.59pm "
        "(Melbourne time) for semester one (S1-01) 2027":
            "转学位课程：更改志愿的截止时间为 23:59（墨尔本时间）——第一学期（S1-01）2027",
        "Course transfers: Change of preference deadline at 11.59pm "
        "(Melbourne time) for semester two (S2-01)":
            "转学位课程：更改志愿的截止时间为 23:59（墨尔本时间）——第二学期（S2-01）",
        "Course transfers: Eligible international students will "
        "receive an International Student Course Agreement (ISCA). To "
        "accept an offer for semester one (S1-01) 2027, students must "
        "return their completed ISCA by Sunday 31 January 2027":
            "转学位课程：符合条件的国际学生会收到 International Student Course "
            "Agreement（ISCA，国际学生入学协议）。要接受 2027 年第一学期（S1-01）的录取，须在 2027 年 1 "
            "月 31 日（周日）前交回填妥的 ISCA",
        "Course transfers: Eligible international students will "
        "receive an International Student Course Agreement (ISCA). To "
        "accept an offer for semester two (S2-01), students must "
        "return their completed ISCA by Wed 22 July":
            "转学位课程：符合条件的国际学生会收到 International Student Course "
            "Agreement（ISCA，国际学生入学协议）。要接受第二学期（S2-01）的录取，须在 7 月 22 "
            "日（周三）前交回填妥的 ISCA",
        "Course transfers: Last day for domestic students to accept an "
        "offer for semester one (S1-01) 2027":
            "转学位课程：本地学生接受录取的最后一天——第一学期（S1-01）2027",
        "Course transfers: Last day for domestic students to accept an "
        "offer for semester two (S2-01)":
            "转学位课程：本地学生接受录取的最后一天——第二学期（S2-01）",
        "Course transfers: Last day for international students to "
        "accept an offer for semester one (S1-01) by submitting their "
        "ISCA":
            "转学位课程：国际学生接受录取的最后一天——第一学期（S1-01），方式是提交 ISCA（国际学生入学协议）",
        "Course transfers: Last day for international students to "
        "accept an offer for semester two (S2-01) by submitting their "
        "ISCA":
            "转学位课程：国际学生接受录取的最后一天——第二学期（S2-01），方式是提交 ISCA（国际学生入学协议）",
        "Course transfers: Offer notifications sent to students by 5pm "
        "(Melbourne time) for semester one (S1-01) 2027":
            "转学位课程：录取通知于 17:00（墨尔本时间）前发送给学生——第一学期（S1-01）2027",
        "Course transfers: Offer notifications sent to students by 5pm "
        "(Melbourne time) for semester two (S2-01)":
            "转学位课程：录取通知于 17:00（墨尔本时间）前发送给学生——第二学期（S2-01）",
        "Coursework scholarship applications close: 2026":
            "授课型奖学金申请截止：2026",
        "Coursework scholarship applications close: Mid-year 2026":
            "授课型奖学金申请截止：年中2026",
        "Coursework scholarship applications open: 2026":
            "授课型奖学金申请开放：2026",
        "Coursework scholarship applications open: Mid-year 2026":
            "授课型奖学金申请开放：年中2026",
        "Daylight saving ends: Turn clocks back one hour":
            "夏令时结束：时钟拨慢一小时",
        "Daylight saving starts: Turn clocks forward one hour":
            "夏令时开始：时钟拨快一小时",
        "Deferred and supplementary assessments end: Semester one "
        "(S1-01)":
            "延期考核与补考结束：第一学期（S1-01）",
        "Deferred and supplementary assessments start: Semester one "
        "(S1-01)":
            "延期考核与补考开始：第一学期（S1-01）",
        "Deferred and supplementary final assessments end: Semester "
        "two (S2-01) 2025":
            "延期期末考核与补考结束：第二学期（S2-01）2025",
        "Deferred and supplementary final assessments end: Summer "
        "semester A (SSA-02) 2025, November intake (NOV12) 2025, and "
        "summer semester B (SSB-01) 2026":
            "延期期末考核与补考结束：夏季学期 A（SSA-02）2025、11 月入学（NOV12）2025、夏季学期 "
            "B（SSB-01）2026",
        "Deferred and supplementary final assessments start: Semester "
        "two (S2-01) 2025":
            "延期期末考核与补考开始：第二学期（S2-01）2025",
        "Deferred and supplementary final assessments start: Summer "
        "semester A (SSA-02) 2025, November intake (NOV12) 2025, and "
        "summer semester B (SSB-01) 2026":
            "延期期末考核与补考开始：夏季学期 A（SSA-02）2025、11 月入学（NOV12）2025、夏季学期 "
            "B（SSB-01）2026",
        "Deferred and supplementary final assessments timetable "
        "published: Semester one (S1-01)":
            "延期期末考核与补考课表公布：第一学期（S1-01）",
        "Deferred and supplementary final assessments timetable "
        "published: Semester two (S1-02) 2025":
            "延期期末考核与补考课表公布：第二学期（S1-02）2025",
        "Faculty of Medicine, Nursing and Health Science":
            "医学、护理与健康科学学院",
        "Faculty of Pharmacy and Pharmaceutical Sciences":
            "药学与制药科学学院",
        "Fees due: Semester 2 - semester 1 (S2-S1-02), semester 2 - "
        "summer A (S2-SS-02), trimester 3 (T3-58), semester 1 "
        "(northern) (S1-60), and term 4 (T4-57). A late payment "
        "penalty will apply after this date (typically an encumbrance)":
            "学费到期：第二学期 - 第一学期（S2-S1-02）、第二学期 - 夏季学期 A（S2-SS-02）、第 3 "
            "学段（T3-58）、第一学期（北半球）（S1-60）、第 4 学季（T4-57）。逾期缴纳会产生滞纳处罚，通常是 "
            "encumbrance（学籍限制）",
        "Fees due: Semester one (S1-01). A late payment penalty will "
        "apply after this date (typically an encumbrance)":
            "学费到期：第一学期（S1-01）。逾期缴纳会产生滞纳处罚，通常是 encumbrance（学籍限制）",
        "Fees due: Summer semester 3 (MC) (SS-29A), summer semester A "
        "(SSA-02), and November intake (NOV12). A late payment penalty "
        "will apply after this date (typically an encumbrance)":
            "学费到期：夏季学期 3（MC）（SS-29A）、夏季学期 A（SSA-02）、11 "
            "月入学（NOV12）。逾期缴纳会产生滞纳处罚，通常是 encumbrance（学籍限制）",
        "Fees due: Summer semester B (SSB-01) 2026, summer A - "
        "semester 1 (SS-S1-01), term 1 (T1-57), trimester 1 (T1-58), "
        "and semester 1 (extended) (S1-32). A late payment penalty "
        "will apply after this date (typically an encumbrance)":
            "学费到期：夏季学期 B（SSB-01）2026、夏季学期 A - 第一学期（SS-S1-01）、第 1 "
            "学季（T1-57）、第 1 学段（T1-58）、第一学期（延长）（S1-32）。逾期缴纳会产生滞纳处罚，通常是 "
            "encumbrance（学籍限制）",
        "Fees due: Winter teaching period (WS-01). A late payment "
        "penalty will apply after this date (typically an encumbrance)":
            "学费到期：冬季开课学期（WS-01）。逾期缴纳会产生滞纳处罚，通常是 encumbrance（学籍限制）",
        "Final assessment and teaching periods end: Summer semester A "
        "(SSA-02) 2025, November intake (NOV12) 2025, and summer "
        "semester B (SSB-01) 2026":
            "期末考核与开课学期结束：夏季学期 A（SSA-02）2025、11 月入学（NOV12）2025、夏季学期 "
            "B（SSB-01）2026",
        "Final assessment dates":
            "期末考核日期",
        "Final assessments and teaching period end: Trimester 1 (T1-58)":
            "期末考核与开课学期结束：第 1 学段（T1-58）",
        "Final assessments and teaching period end: Trimester 2 (T2-58)":
            "期末考核与开课学期结束：第 2 学段（T2-58）",
        "Final assessments and teaching periods end: Semester two "
        "(S2-01), full-year (FY-01), and full-year (extended) (FY-32)":
            "期末考核与开课学期结束：第二学期（S2-01）、全学年（FY-01）、全学年（延长）（FY-32）",
        "Final assessments end: Semester one (S1-01), semester 1 "
        "(extended) (S1-32), semester 2 (northern) (S2-60), and summer "
        "A - semester 1 (SS-S1-01)":
            "期末考核结束：第一学期（S1-01）、第一学期（延长）（S1-32）、第二学期（北半球）（S2-60）、夏季学期 A - "
            "第一学期（SS-S1-01）",
        "Final assessments end: Trimester 3 (T3-58) (Faculty of Law "
        "units only)":
            "期末考核结束：第 3 学段（T3-58）（仅限法学院课程）",
        "Final assessments end: Trimester 3 (T3-58) (except Faculty of "
        "Law units)":
            "期末考核结束：第 3 学段（T3-58）（法学院课程除外）",
        "Final assessments start: November intake (NOV12) 2025 and "
        "summer semester B (SSB-01) 2026":
            "期末考核开始：11 月入学（NOV12）2025、夏季学期 B（SSB-01）2026",
        "Final assessments start: Semester one (S1-01), semester 1 "
        "(extended) (S1-32), semester 2 (northern) (S2-60), and summer "
        "A - semester 1 (SS-S1-01)":
            "期末考核开始：第一学期（S1-01）、第一学期（延长）（S1-32）、第二学期（北半球）（S2-60）、夏季学期 A - "
            "第一学期（SS-S1-01）",
        "Final assessments start: Semester two (S2-01), full-year "
        "(FY-01), full-year (extended) (FY-32) and trimester 3 (T3-58) "
        "(except Faculty of Law units)":
            "期末考核开始：第二学期（S2-01）、全学年（FY-01）、全学年（延长）（FY-32）、第 3 "
            "学段（T3-58）（法学院课程除外）",
        "Final assessments start: Summer semester A (SSA-02) 2025":
            "期末考核开始：夏季学期 A（SSA-02）2025",
        "Final assessments start: Trimester 1 (T1-58)":
            "期末考核开始：第 1 学段（T1-58）",
        "Final assessments start: Trimester 2 (T2-58)":
            "期末考核开始：第 2 学段（T2-58）",
        "Final assessments start: Trimester 3 (T3-58) (Faculty of Law "
        "units only)":
            "期末考核开始：第 3 学段（T3-58）（仅限法学院课程）",
        "Final assessments timetable published: Semester one (S1-01), "
        "semester 1 (extended) (S1-32), and summer A - semester 1 "
        "(SS-S1-01)":
            "期末考核课表公布：第一学期（S1-01）、第一学期（延长）（S1-32）、夏季学期 A - 第一学期（SS-S1-01）",
        "Final assessments timetable published: Semester two (S2-01), "
        "full-year (FY-01), full-year (extended) (FY-32) and and "
        "semester 2 (extended) (S2-32)":
            "期末考核课表公布：第二学期（S2-01）、全学年（FY-01）、全学年（延长）（FY-32）、第二学期（延长）（S2-32）",
        "Final assessments timetable published: Summer semester A "
        "(SSA-02) 2025, November intake (NOV12) 2025, semester 2 - "
        "summer A (S2-SS-02), and summer semester B (SSB-01) 2026":
            "期末考核课表公布：夏季学期 A（SSA-02）2025、11 月入学（NOV12）2025、第二学期 - 夏季学期 "
            "A（S2-SS-02）、夏季学期 B（SSB-01）2026",
        "Graduate research scholarships close: Round 1/2026 "
        "(international students)":
            "研究生研究奖学金申请截止：1 批次／2026 年（国际学生）",
        "Graduate research scholarships close: Round 2/2026 (domestic "
        "students)":
            "研究生研究奖学金申请截止：2 批次／2026 年（本地学生）",
        "Graduate research scholarships close: Round 3/2026 "
        "(international students)":
            "研究生研究奖学金申请截止：3 批次／2026 年（国际学生）",
        "Graduate research scholarships open: Round 1/2026 "
        "(international students)":
            "研究生研究奖学金申请开放：1 批次／2026 年（国际学生）",
        "Graduate research scholarships open: Round 2/2026 (domestic "
        "students)":
            "研究生研究奖学金申请开放：2 批次／2026 年（本地学生）",
        "Graduate research scholarships open: Round 3/2026 "
        "(international students)":
            "研究生研究奖学金申请开放：3 批次／2026 年（国际学生）",
        "Graduate research scholarships open: Round 4/2026 (domestic "
        "students)":
            "研究生研究奖学金申请开放：4 批次／2026 年（本地学生）",
        "Graduate research scholarships: close for Round 4/2026 "
        "(domestic students)":
            "研究生研究奖学金申请截止——4 批次／2026 年（本地学生）",
        "Graduation applications close: April/May round (Australia)":
            "毕业申请截止：4／5 月批次（澳大利亚）",
        "Graduation applications close: December round (Australia)":
            "毕业申请截止：12 月批次（澳大利亚）",
        "Graduation applications close: October round (Australia)":
            "毕业申请截止：10 月批次（澳大利亚）",
        "Graduation applications open: December round (Australia)":
            "毕业申请开放：12 月批次（澳大利亚）",
        "Graduation applications open: October round (Australia)":
            "毕业申请开放：10 月批次（澳大利亚）",
        "Graduation ceremonies end: April/May round (Australia)":
            "毕业典礼结束：4／5 月批次（澳大利亚）",
        "Graduation ceremonies end: December round (Australia)":
            "毕业典礼结束：12 月批次（澳大利亚）",
        "Graduation ceremonies end: October round (Australia)":
            "毕业典礼结束：10 月批次（澳大利亚）",
        "Graduation ceremonies start: April/May round (Australia)":
            "毕业典礼开始：4／5 月批次（澳大利亚）",
        "Graduation ceremonies start: December round (Australia)":
            "毕业典礼开始：12 月批次（澳大利亚）",
        "Graduation ceremonies start: October round (Australia)":
            "毕业典礼开始：10 月批次（澳大利亚）",
        "Important dates home page":
            "重要日期首页",
        "Last day to add on-campus units: Semester one (S1-01) and "
        "full-year (FY-01)":
            "校内课程加课截止日：第一学期（S1-01）、全学年（FY-01）",
        "Last day to add on-campus units: Semester two (S2-01)":
            "校内课程加课截止日：第二学期（S2-01）",
        "Last day to withdraw from semester 1 (extended) (S1-32) units "
        "with Withdrawn showing on your academic record. Units "
        "withdrawn after this date will show as Withdrawn Fail":
            "退选截止日——第一学期（延长）（S1-32）的课程，成绩单上会显示 Withdrawn（退课）。此日期之后退选的课程会记为 "
            "Withdrawn Fail（退课不及格）",
        "Last day to withdraw from semester 2 (extended) (S2-32) units "
        "with Withdrawn showing on your academic record. Units "
        "withdrawn after this date will show as Withdrawn Fail":
            "退选截止日——第二学期（延长）（S2-32）的课程，成绩单上会显示 Withdrawn（退课）。此日期之后退选的课程会记为 "
            "Withdrawn Fail（退课不及格）",
        "Last day to withdraw from semester 2 (northern) (S2-60) units "
        "with Withdrawn showing on your academic record. Units "
        "withdrawn after this date will show as Withdrawn Fail":
            "退选截止日——第二学期（北半球）（S2-60）的课程，成绩单上会显示 "
            "Withdrawn（退课）。此日期之后退选的课程会记为 Withdrawn Fail（退课不及格）",
        "Last day to withdraw from semester two (S2-01) units with "
        "Withdrawn showing on your academic record. Units withdrawn "
        "after this date will show as Withdrawn Fail":
            "退选截止日——第二学期（S2-01）的课程，成绩单上会显示 Withdrawn（退课）。此日期之后退选的课程会记为 "
            "Withdrawn Fail（退课不及格）",
        "Last day to withdraw from term 1 (T1-57) units with Withdrawn "
        "showing on your academic record. Units withdrawn after this "
        "date will show as Withdrawn Fail":
            "退选截止日——第 1 学季（T1-57）的课程，成绩单上会显示 Withdrawn（退课）。此日期之后退选的课程会记为 "
            "Withdrawn Fail（退课不及格）",
        "Last day to withdraw from term 2 (T2-57) units with Withdrawn "
        "showing on your academic record. Units withdrawn after this "
        "date will show as Withdrawn Fail":
            "退选截止日——第 2 学季（T2-57）的课程，成绩单上会显示 Withdrawn（退课）。此日期之后退选的课程会记为 "
            "Withdrawn Fail（退课不及格）",
        "Last day to withdraw from term 3 (T3-57) units with Withdrawn "
        "showing on your academic record. Units withdrawn after this "
        "date will show as Withdrawn Fail":
            "退选截止日——第 3 学季（T3-57）的课程，成绩单上会显示 Withdrawn（退课）。此日期之后退选的课程会记为 "
            "Withdrawn Fail（退课不及格）",
        "Mid-semester break ends: Semester one (S1-01)":
            "学期中假期结束：第一学期（S1-01）",
        "Mid-semester break ends: Semester two (S2-01)":
            "学期中假期结束：第二学期（S2-01）",
        "Mid-semester break starts: Semester one (S1-01)":
            "学期中假期开始：第一学期（S1-01）",
        "Mid-semester break starts: Semester two (S2-01)":
            "学期中假期开始：第二学期（S2-01）",
        "Mid-year Orientation Week ends: Semester two (S2-01)":
            "年中迎新周结束：第二学期（S2-01）",
        "Mid-year Orientation Week starts: Semester two (S2-01)":
            "年中迎新周开始：第二学期（S2-01）",
        "Monash Online 6 (MO-TP6-01)":
            "Monash Online（在线） 6（MO-TP6-01）",
        "November teaching period (2026–2027)":
            "11 月教学期（2026–2027）",
        "Orientation ends: Semester one (S1-01)":
            "迎新结束：第一学期（S1-01）",
        "Orientation starts: Semester one (S1-01)":
            "迎新开始：第一学期（S1-01）",
        "Other campuses and locations":
            "其他校区与地点",
        "Other important dates":
            "其他重要日期",
        "Pre-Orientation events start: Semester one (S1-01)":
            "迎新前活动开始：第一学期（S1-01）",
        "Principal dates archive":
            "重要日期存档",
        "Principal dates for Monash Indonesia":
            "Monash 印尼校区重要日期",
        "Principal dates for Monash Malaysia":
            "Monash 马来西亚校区重要日期",
        "Re-enrolment (late) ends: 2027":
            "逾期重新注册结束：2027",
        "Re-enrolment (late) starts: 2027 (a late fee applies)":
            "逾期重新注册开始：2027（会收取滞纳金）",
        "Re-enrolment (timely) ends: 2027":
            "正常重新注册结束：2027",
        "Re-enrolment (timely) starts: 2027":
            "正常重新注册开始：2027",
        "Rescheduled deferred and supplementary final assessments end: "
        "Summer semester A (SSA-02), November intake (NOV12) 2025, and "
        "summer semester B (SSB-01)":
            "改期后的延期期末考核与补考结束：夏季学期 A（SSA-02）、11 月入学（NOV12）2025、夏季学期 "
            "B（SSB-01）",
        "Rescheduled deferred and supplementary final assessments "
        "start: Summer semester A (SSA-02), November intake (NOV12) "
        "2025, and summer semester B (SSB-01)":
            "改期后的延期期末考核与补考开始：夏季学期 A（SSA-02）、11 月入学（NOV12）2025、夏季学期 "
            "B（SSB-01）",
        "Rescheduled deferred and supplementary final assessments "
        "timetable published: Summer semester A (SSA-02), November "
        "intake (NOV12) 2025, and summer semester B (SSB-01)":
            "改期后的延期期末考核与补考课表公布：夏季学期 A（SSA-02）、11 月入学（NOV12）2025、夏季学期 "
            "B（SSB-01）",
        "Rescheduled deferred assessments end: Semester one (S1-01) "
        "and associated teaching periods":
            "改期后的延期考核结束：第一学期（S1-01）及相关开课学期",
        "Rescheduled deferred assessments start: Semester one (S1-01) "
        "and associated teaching periods":
            "改期后的延期考核开始：第一学期（S1-01）及相关开课学期",
        "Rescheduled deferred assessments timetable published: "
        "Semester one (S1-01) and associated teaching periods":
            "改期后的延期考核课表公布：第一学期（S1-01）及相关开课学期",
        "Rescheduled deferred final assessments end: Semester two "
        "(S2-01) 2025 and associated teaching periods":
            "改期后的延期期末考核结束：第二学期（S2-01）2025及相关开课学期",
        "Rescheduled deferred final assessments start: Semester two "
        "(S2-01) 2025 and associated teaching periods":
            "改期后的延期期末考核开始：第二学期（S2-01）2025及相关开课学期",
        "Results released: Semester 2 - summer A (S2-SS-02) 2025":
            "成绩公布：第二学期 - 夏季学期 A（S2-SS-02）2025",
        "Results released: Semester one (S1-01), semester 1 (extended) "
        "(S1-32), semester 2 (northern) (S2-60), and summer A - "
        "semester 1 (SS-S1-01)":
            "成绩公布：第一学期（S1-01）、第一学期（延长）（S1-32）、第二学期（北半球）（S2-60）、夏季学期 A - "
            "第一学期（SS-S1-01）",
        "Results released: Semester two (S2-01), full-year (FY-01), "
        "full-year (extended) (FY-32), semester 2 (extended) (S2-32), "
        "and trimester 3 (T3-58) (except Faculty of Law units)":
            "成绩公布：第二学期（S2-01）、全学年（FY-01）、全学年（延长）（FY-32）、第二学期（延长）（S2-32）、第 "
            "3 学段（T3-58）（法学院课程除外）",
        "Results released: Summer semester A (SSA-02) 2025, November "
        "intake (NOV12) 2025, semester 1 (northern) (S1-60) 2025, term "
        "4 (T4-57) 2025, and summer semester B (SSB-01) 2026":
            "成绩公布：夏季学期 A（SSA-02）2025、11 "
            "月入学（NOV12）2025、第一学期（北半球）（S1-60）2025、第 4 学季（T4-57）2025、夏季学期 "
            "B（SSB-01）2026",
        "Results released: Term 1 (T1-57)":
            "成绩公布：第 1 学季（T1-57）",
        "Results released: Term 2 (T2-57)":
            "成绩公布：第 2 学季（T2-57）",
        "Results released: Term 3 (T3-57)":
            "成绩公布：第 3 学季（T3-57）",
        "Results released: Trimester 1 (T1-58) (including Faculty of "
        "Law units)":
            "成绩公布：第 1 学段（T1-58）（含法学院课程）",
        "Results released: Trimester 2 (T2-58) (Faculty of Law units "
        "only)":
            "成绩公布：第 2 学段（T2-58）（仅限法学院课程）",
        "Results released: Trimester 2 (T2-58) (except Faculty of Law "
        "units)":
            "成绩公布：第 2 学段（T2-58）（法学院课程除外）",
        "Results released: Trimester 3 (T3-58) (Faculty of Law units "
        "only)":
            "成绩公布：第 3 学段（T3-58）（仅限法学院课程）",
        "Results released: Winter semester (WS-01)":
            "成绩公布：冬季学期（WS-01）",
        "See all dates for the November teaching period (NOV12).":
            "查看 11 月教学期（NOV12）的全部日期。",
        "See full year listing":
            "查看全年列表",
        "Summer and winter semester":
            "夏季学期与冬季学期",
        "Swot vac ends: Semester one (S1-01), semester 2 - semester 1 "
        "(S2-S1-02), semester 2 (northern) (S2-60), and summer A - "
        "semester 1 (SS-S1-01)":
            "swot vac（复习周）结束：第一学期（S1-01）、第二学期 - "
            "第一学期（S2-S1-02）、第二学期（北半球）（S2-60）、夏季学期 A - 第一学期（SS-S1-01）",
        "Swot vac ends: Semester two (S2-01) and full-year (FY-01)":
            "swot vac（复习周）结束：第二学期（S2-01）、全学年（FY-01）",
        "Swot vac starts: Semester one (S1-01), semester 2 - semester "
        "1 (S2-S1-02), semester 2 (northern) (S2-60), and summer A - "
        "semester 1 (SS-S1-01)":
            "swot vac（复习周）开始：第一学期（S1-01）、第二学期 - "
            "第一学期（S2-S1-02）、第二学期（北半球）（S2-60）、夏季学期 A - 第一学期（SS-S1-01）",
        "Swot vac starts: Semester two (S2-01) and full-year (FY-01)":
            "swot vac（复习周）开始：第二学期（S2-01）、全学年（FY-01）",
        "Teaching ends: Full-year extended (FY-32), semester 2 "
        "(extended) (S2-32) and trimester 3 (T3-58). Last day to "
        "withdraw from units (units cannot be withdrawn after this "
        "date)":
            "教学结束：全学年（延长）（FY-32）、第二学期（延长）（S2-32）、第 3 "
            "学段（T3-58）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Monash Online 1 (MO-TP1-01). Last day to "
        "withdraw from units (units cannot be withdrawn after this "
        "date)":
            "教学结束：Monash Online（在线） 1（MO-TP1-01）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Monash Online 2 (MO-TP2-01). Last day to "
        "withdraw from units (units cannot be withdrawn after this "
        "date)":
            "教学结束：Monash Online（在线） 2（MO-TP2-01）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Monash Online 3 (MO-TP3-01). Last day to "
        "withdraw from units (units cannot be withdrawn after this "
        "date)":
            "教学结束：Monash Online（在线） 3（MO-TP3-01）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Monash Online 4 (MO-TP4-01). Last day to "
        "withdraw from units (units cannot be withdrawn after this "
        "date)":
            "教学结束：Monash Online（在线） 4（MO-TP4-01）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Monash Online 5 (MO-TP5-01). Last day to "
        "withdraw from units (units cannot be withdrawn after this "
        "date)":
            "教学结束：Monash Online（在线） 5（MO-TP5-01）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Monash Online 6 (MO-TP6-01). Last day to "
        "withdraw from units (units cannot be withdrawn after this "
        "date)":
            "教学结束：Monash Online（在线） 6（MO-TP6-01）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Semester 1 (extended) (S1-32). Last day to "
        "withdraw from units (units cannot be withdrawn after this "
        "date)":
            "教学结束：第一学期（延长）（S1-32）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Semester 1 (northern) (S1-60). Last day to "
        "withdraw from units (units cannot be withdrawn after this "
        "date)":
            "教学结束：第一学期（北半球）（S1-60）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Semester one (S1-01), semester 2 (northern) "
        "(S2-60), semester 2 - semester 1 (S2-S1-02), and summer A - "
        "semester 1 (SS-S1-01). Last day to withdraw from units (units "
        "cannot be withdrawn after this date)":
            "教学结束：第一学期（S1-01）、第二学期（北半球）（S2-60）、第二学期 - 第一学期（S2-S1-02）、夏季学期 "
            "A - 第一学期（SS-S1-01）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Semester two (S2-01) and full-year (FY-01). "
        "Last day to withdraw from units with Withdrawn Fail showing "
        "on your academic record (units cannot be withdrawn after this "
        "date)":
            "教学结束：第二学期（S2-01）、全学年（FY-01）。退选课程的最后一天，成绩单上会显示 Withdrawn "
            "Fail（退课不及格）（此日期之后无法再退选课程）",
        "Teaching ends: Summer semester A (SSA-02) 2025. Last day to "
        "withdraw from units (units cannot be withdrawn after this "
        "date)":
            "教学结束：夏季学期 A（SSA-02）2025。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Summer semester B (SSB-01). Last day to "
        "withdraw from units (units cannot be withdrawn after this "
        "date)":
            "教学结束：夏季学期 B（SSB-01）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Term 1 (T1-57). Last day to withdraw from "
        "units (units cannot be withdrawn after this date)":
            "教学结束：第 1 学季（T1-57）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Term 2 (T2-57). Last day to withdraw from "
        "units (units cannot be withdrawn after this date)":
            "教学结束：第 2 学季（T2-57）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Term 3 (T3-57). Last day to withdraw from "
        "units (units cannot be withdrawn after this date)":
            "教学结束：第 3 学季（T3-57）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Term 4 (T4-57). Last day to withdraw from "
        "units (units cannot be withdrawn after this date)":
            "教学结束：第 4 学季（T4-57）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Trimester 1 (T1-58). Last day to withdraw from "
        "units (units cannot be withdrawn after this date)":
            "教学结束：第 1 学段（T1-58）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Trimester 2 (T2-58). Last day to withdraw from "
        "units (units cannot be withdrawn after this date)":
            "教学结束：第 2 学段（T2-58）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching ends: Winter semester (WS-01). Last day to withdraw "
        "from units (units cannot be withdrawn after this date)":
            "教学结束：冬季学期（WS-01）。退选课程的最后一天（此日期之后无法再退选课程）",
        "Teaching periods for Bachelor of Medicine and Bachelor of "
        "Surgery":
            "医学学士与外科学学士的开课学期",
        "Teaching starts: Monash Online 3 (MO-TP3-01)":
            "开课：Monash Online（在线） 3（MO-TP3-01）",
        "Teaching starts: Monash Online 4 (MO-TP4-01)":
            "开课：Monash Online（在线） 4（MO-TP4-01）",
        "Teaching starts: Monash Online 5 (MO-TP5-01)":
            "开课：Monash Online（在线） 5（MO-TP5-01）",
        "Teaching starts: November intake (NOV12)":
            "开课：11 月入学（NOV12）",
        "Teaching starts: Semester 1 (extended) (S1-32) and full-year "
        "extended (FY-32)":
            "开课：第一学期（延长）（S1-32）、全学年（延长）（FY-32）",
        "Teaching starts: Semester 1 (northern) (S1-60)":
            "开课：第一学期（北半球）（S1-60）",
        "Teaching starts: Semester 2 (extended) (S2-32)":
            "开课：第二学期（延长）（S2-32）",
        "Teaching starts: Semester 2 (northern) (S2-60)":
            "开课：第二学期（北半球）（S2-60）",
        "Teaching starts: Semester one (S1-01), full-year (FY-01), and "
        "Monash Online 2 (MO-TP2-01)":
            "开课：第一学期（S1-01）、全学年（FY-01）、Monash Online（在线） 2（MO-TP2-01）",
        "Teaching starts: Semester two (S2-01), semester 2 - summer A "
        "(S2-SS-02), and semester 2 - semester 1 (S2-S1-02)":
            "开课：第二学期（S2-01）、第二学期 - 夏季学期 A（S2-SS-02）、第二学期 - 第一学期（S2-S1-02）",
        "Teaching starts: Summer semester A (SSA-02)":
            "开课：夏季学期 A（SSA-02）",
        "Teaching starts: Summer semester B (SSB-01) 2026, Monash "
        "Online 1 (MO-TP1-01), term 1 (T1-57), and trimester 1 (T1-58)":
            "开课：夏季学期 B（SSB-01）2026、Monash Online（在线） 1（MO-TP1-01）、第 1 "
            "学季（T1-57）、第 1 学段（T1-58）",
        "Teaching starts: Term 2 (T2-57)":
            "开课：第 2 学季（T2-57）",
        "Teaching starts: Term 3 (T3-57)":
            "开课：第 3 学季（T3-57）",
        "Teaching starts: Term 4 (T4-57)":
            "开课：第 4 学季（T4-57）",
        "Teaching starts: Trimester 2 (T2-58)":
            "开课：第 2 学段（T2-58）",
        "Teaching starts: Trimester 3 (T3-58)":
            "开课：第 3 学段（T3-58）",
        "Teaching starts: Winter semester (WS-01)":
            "开课：冬季学期（WS-01）",
        "The dates for summer and winter semester vary from unit to "
        "unit. For more information, see summer and winter units.":
            "夏季学期和冬季学期的日期因课程而异。更多信息见「夏季与冬季课程」。",
        "Type a search term, such as census or assessments, to find "
        "these listings for the whole year.":
            "输入搜索词（例如 census 或 assessments），即可在全年列表中查找。",
        "University closed: Anzac Day (no replacement holiday)":
            "学校放假：澳新军团日（不另行补假）",
        "University closed: Boxing Day":
            "学校放假：节礼日",
        "University closed: Christmas Day":
            "学校放假：圣诞节",
        "University closed: Easter Monday":
            "学校放假：复活节星期一",
        "University closed: Easter Tuesday":
            "学校放假：复活节星期二",
        "University closed: Good Friday":
            "学校放假：耶稣受难日",
        "University closed: Grand Final Friday":
            "学校放假：总决赛星期五",
        "University closed: New Year's Day":
            "学校放假：元旦",
        "University closed: Public holiday":
            "学校放假：公共假日",
        "University closed: Reopens Monday 4 January 2027":
            "学校放假：重新开放：2027年1月4日（周一）",
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
        "Admission and Credit Policy (pdf)":
            "Admission and Credit Policy（录取与学分减免政策，pdf）",
        "Apply for faculty approval":
            "申请学院批准",
        "Apply to the host institution":
            "向接收院校提出申请",
        "Attach the unit syllabus from the host institution (see "
        "instructions on the form).":
            "附上接收院校的课程大纲（具体要求见表格上的说明）。",
        "Changing your enrolment":
            "变更选课注册",
        "Credit Procedure (pdf)":
            "Credit Procedure（学分减免流程，pdf）",
        "Credit will not be granted if your approved enrolment at the "
        "other institution is varied without Monash faculty "
        "authorisation.":
            "如果你在他校已获批的选课未经 Monash 学院授权就发生变动，将不予学分减免。",
        "Enrolment Procedure – sections 4.1 to 4.6 (pdf)":
            "Enrolment Procedure（选课注册规程）第 4.1 至 4.6 节（pdf）",
        "Fill out a Complementary study application form (pdf, 0.18 "
        "mb).":
            "填写 Complementary study application form（辅修学习申请表，pdf，0.18 mb）。",
        "If seeking government assistance through a HELP loan for your "
        "complementary enrolment, you need to submit a request for "
        "HECS or FEE-HELP form to the host institution.":
            "如果你想为这部分辅修选课申请 HELP 贷款的政府资助，需要向接收院校提交 HECS 或 FEE-HELP 申请表。",
        "If you need to change your complementary enrolment, you must "
        "get approval from your Monash faculty to ensure the units "
        "will be credited towards your course. If approved, you need "
        "to amend your complementary enrolment at both Monash and the "
        "host institution by the deadlines to avoid fees and fail "
        "grades.":
            "如果需要变更辅修选课，必须先取得 Monash "
            "学院的批准，以确保这些课程仍能计入你的学位课程。获批之后，你需要在截止日期前同时在 Monash "
            "和接收院校两边修改选课，以免产生费用和不及格成绩。",
        "If you wish to study at another institution and receive "
        "credit towards your course, you must seek approval in writing "
        "from your managing faculty at Monash. Complementary study is "
        "normally only approved if the unit is not offered by Monash "
        "University and will contribute to the progression of your "
        "course.":
            "如果你想在其他院校修课并计入自己的学位课程，必须事先取得所属学院的书面批准。辅修学习通常只有在该课程 Monash "
            "大学没有开设、且有助于你学位课程进度的情况下才会获批。",
        "If your application is approved, your faculty will add the "
        "units to the Web Enrolment System (WES) and they will appear "
        "on your academic record. You still need to enrol in the units "
        "with the host institution.":
            "如果申请获批，学院会把这些课程加进 "
            "WES（学生系统），它们也会出现在你的学业记录上。但你仍然需要自行到接收院校完成选课注册。",
        "Information Technology":
            "信息技术学院",
        "Law students need to submit an extra form. See Law students – "
        "complementary study.":
            "法学院学生需要另外提交一份表格，详见「法学院学生——辅修学习」。",
        "Once your application is approved by your faculty at Monash, "
        "you can apply to enrol in units at the host institution by "
        "their closing date.":
            "在 Monash 的学院批准你的申请之后，你就可以在接收院校的截止日期前申请选课注册。",
        "Pay your fees for complementary units to the host "
        "institution. They may offer you either a full-fee or "
        "Commonwealth supported place (CSP). This does not depend on "
        "the type of place that you currently have at Monash.":
            "辅修课程的学费直接交给接收院校。他们可能给你全额自费学额，也可能给你联邦资助学额（CSP）——这与你目前在 Monash "
            "的学额类型无关。",
        "See Monash University census dates.":
            "请查看 Monash 大学的 census dates（学籍统计日）。",
        "See below for faculty information on credit limits for "
        "students applying for complementary study:":
            "各学院对辅修学习学分上限的规定见下：",
        "Start by applying for faculty approval before enrolling in "
        "any units at another university.":
            "在他校选任何课之前，先申请学院批准。",
        "Study at another institution – complementary study":
            "在其他院校修课——辅修学习（complementary study）",
        "Submit an enquiry through MoVA with the application attached. "
        "This will be forwarded to your faculty, who will advise you "
        "in writing of the outcome.":
            "通过 MoVA 提交咨询并附上申请表，系统会转交给你所在的学院，学院会以书面形式告知结果。",
        "To change your enrolment, submit the Enrolment Amendment Form.":
            "如需变更选课注册，请提交 Enrolment Amendment Form（选课注册变更表）。",
        "To have your results credited to your Monash course:":
            "要把成绩计入你的 Monash 学位课程：",
        "You can apply for complementary study to enrol in a single "
        "unit or units at another institution (within Australia or New "
        "Zealand) and have them count toward your Monash award course.":
            "你可以申请辅修学习（complementary "
            "study），到澳大利亚或新西兰境内的其他院校修读一门或多门课程，并计入你的 Monash 学位课程。",
        "You need to apply to Monash for approval to have study at "
        "another institution credited towards your course, and to the "
        "host institution to enrol. This means you need to apply early "
        "to allow time for both of applications to be processed.":
            "你需要向 Monash "
            "申请批准，才能把在他校修的课计入自己的学位课程；同时还要向接收院校申请选课注册。也就是说，两边的申请都要留出处理时间，务必尽早提交。",
        "request an academic record of your results from the host "
        "institution":
            "向接收院校索取成绩的学业记录",
        "submit this to your managing faculty at Monash within six "
        "weeks of results release.":
            "并在成绩公布后六周之内提交给 Monash 负责你的学院。",
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
        "All other year levels":
            "其他所有年级",
        "All units designated as first year are weighted 0.5, "
        "regardless of the sequence or year in which you take the "
        "unit. For example, if you complete a first-year unit in your "
        "third year of study, it will be weighted 0.5, not 1.0.":
            "凡被划为一年级的课程，权重一律是 "
            "0.5，与你在第几年修读、按什么顺序修读无关。举例来说，你在第三年修一门一年级课程，它的权重仍然是 0.5，不是 1.0。",
        "An example of how WAM is calculated for nine units with a "
        "range of grades and unit credit points across year levels.":
            "一个示例：九门课程、成绩等级各异、学分不同、分属不同年级，WAM（加权平均分）是怎么算出来的。",
        "Assessment and Academic Integrity Policy (pdf)":
            "Assessment and Academic Integrity Policy（考核与学术诚信政策，pdf）",
        "Calculate to three decimal places.":
            "计算保留三位小数。",
        "Calculating Honours Weighted Average (HWA) for honours "
        "courses that started before Jan 2021:":
            "2021 年 1 月之前开始的荣誉学位课程，其 Honours Weighted "
            "Average（HWA，荣誉学位加权平均分）的算法：",
        "Correcting a mark or grade":
            "更正分数或成绩等级",
        "Divide the sum of the weighted marks by the sum of the "
        "weighted credit points":
            "用加权分数之和除以加权学分之和",
        "Examples of marking or grading errors may include:":
            "评分或定级错误的例子包括：",
        "Final assessments:":
            "期末考核：",
        "Final calculation:":
            "最终计算：",
        "First year (undergraduate)":
            "一年级（本科）",
        "Format and deadlines":
            "格式与截止期限",
        "Grades not included in the calculation:":
            "不计入计算的成绩等级：",
        "Grading Schema Procedure (pdf)":
            "Grading Schema Procedure（成绩等级体系规程，pdf）",
        "How to find out your WAM":
            "怎么查自己的 WAM（加权平均分）",
        "If you believe your WAM is incorrect, message Monash Connect "
        "and we’ll investigate it for you.":
            "如果你认为自己的 WAM（加权平均分）算错了，请给 Monash Connect（学生服务中心）留言，我们会为你核查。",
        "If you fail a major assessment (worth 20% or more of your "
        "unit’s total mark) it will be automatically re-marked before "
        "your result is finalised – so there’s no need to request one.":
            "如果你某项主要考核不及格（占该课程总分 20% 或以上），系统会在成绩最终确定前自动重新评阅一次，不需要你另行申请。",
        "If you think there’s been a mistake in how your mark or grade "
        "was calculated, you can contact the chief examiner about "
        "having it corrected.":
            "如果你认为分数或成绩等级的计算有误，可以联系主考官（chief examiner）请求更正。",
        "If you want to know what the GPA equivalent of your WAM is, "
        "simply use our Grade point average (GPA) calculator.":
            "想知道自己的 WAM（加权平均分）大致相当于多少 GPA（平均绩点），用我们的 GPA 计算器算一下即可。",
        "In-semester assessments – within ten working days of your "
        "mark’s release.":
            "学期内考核——自分数公布起十个工作日之内。",
        "Just keep in mind, while your work is being marked, you can’t "
        "contact staff about an assessment or thesis examination issue "
        "– not even to complain informally.":
            "但要记住：在你的作业还在评阅期间，你不能就该考核或论文评审的问题联系工作人员，非正式的抱怨也不行。",
        "Keep in mind that the following are not considered marking "
        "errors:":
            "请注意，下列情形不算评分错误：",
        "Marking and Feedback Procedure (pdf)":
            "Marking and Feedback Procedure（评分与反馈规程，pdf）",
        "Multiply the unit credit point value by the year level "
        "weighting":
            "把课程学分乘以年级权重",
        "Multiply the unit mark by unit credit point value and then by "
        "the year level weighting":
            "把课程分数乘以课程学分，再乘以年级权重",
        "NSR (not satisfied faculty requirements)":
            "NSR（未满足学院要求）",
        "Outside of this process, in most cases you’re not entitled to "
        "a re-mark, and it’s unlikely that a complaint about a "
        "faculty’s refusal to re-mark will be successful.":
            "除上述流程之外，多数情况下你无权要求重新评阅；就学院拒绝重新评阅一事提出投诉，也很难得到支持。",
        "PGO (pass grade only)":
            "PGO（仅记及格）",
        "Policy and procedure":
            "政策与流程",
        "SFR (satisfied faculty requirements)":
            "SFR（已满足学院要求）",
        "Scheduled Final Assessments Procedure (pdf)":
            "Scheduled Final Assessments Procedure（已排定期末考核规程，pdf）",
        "Seeking feedback on your assessments\n \nFind out where you can "
        "view feedback for an explanation of why you received a "
        "certain mark for an assessment.":
            "查看考核反馈\n \n了解可以在哪里查看反馈，弄清自己某项考核为何得到这个分数。",
        "Sum the resulting values (weighted credit points)":
            "把所得数值相加（加权学分）",
        "Sum the resulting values (weighted marks)":
            "把所得数值相加（加权分数）",
        "The Weighted Average Mark (WAM) is a more precise measurement "
        "of your academic performance than the Grade Point Average. "
        "This is because we base the calculation on your actual marks "
        "(eg: 78, 89, 63, 48 and so on) and the year level of each "
        "unit. Therefore, the WAM is the average mark you achieve "
        "across all completed units in a course, including any failed "
        "and repeated units. The WAM is out of 100.":
            "WAM（加权平均分）比 GPA（平均绩点）更能精确地反映你的学业表现，因为它以你的实际分数（例如 78、89、63、48 "
            "等）和每门课程的年级为依据。也就是说，WAM 是你在一个学位课程中所有已修课程分数的平均值，包括不及格和重修的课程。WAM "
            "满分为 100。",
        "This is your first step in addressing your complaint. If "
        "you’re unable to resolve the issue with your chief examiner, "
        "see how to raise and resolve a complaint for what to do next.":
            "这是处理投诉的第一步。如果你无法与主考官（chief "
            "examiner）把问题解决，请查看「如何提出并解决投诉」了解下一步该怎么做。",
        "Use the online calculator to estimate your WAM.":
            "用在线计算器估算你的 WAM（加权平均分）。",
        "WAM =\n\nΣ (first year unit marks x unit credit points x 0.5) + "
        "Σ (later year unit marks x unit credit points × 1.0) \n÷\n Σ "
        "(first year unit credit points x 0.5) + Σ (later year unit "
        "credit points x 1.0)":
            "WAM =\n\nΣ（一年级课程分数 × 课程学分 × 0.5）＋ Σ（其他年级课程分数 × 课程学分 × 1.0）\n÷\n "
            "Σ（一年级课程学分 × 0.5）＋ Σ（其他年级课程学分 × 1.0）",
        "WAM = 4692 ÷ 63\nWAM = 74.476":
            "WAM = 4692 ÷ 63\nWAM = 74.476",
        "WAM is weighted according to the:":
            "WAM（加权平均分）的权重取决于：",
        "WI (withdrawn incomplete)":
            "WI（退课未完成）",
        "We use the WAM as an entry requirement for some honours and "
        "graduate courses.":
            "部分荣誉学位课程和研究生课程会把 WAM（加权平均分）作为入学要求。",
        "We will calculate your WAM for your award course if you "
        "started on or after semester one, 2008. We don't calculate "
        "the WAM for Masters by Research and PhD courses.":
            "如果你是 2008 年第一学期或之后入学的，我们会为你的学位课程计算 WAM（加权平均分）。研究型硕士和博士学位课程不计算 "
            "WAM。",
        "Weighted average mark (WAM)":
            "WAM（加权平均分）",
        "Year level of unit and its weighting.":
            "课程所属年级及其权重。",
        "Year level weighting":
            "年级权重",
        "You can also see your WAM in the Student Portal (either in "
        "the course progress screen or through the GPA/WAM widget).":
            "你也可以在学生门户里看到自己的 WAM（加权平均分）（在「课程进度」页面，或通过 GPA/WAM 小工具）。",
        "You can use our online calculator below to estimate your WAM.":
            "可以用下面的在线计算器估算你的 WAM（加权平均分）。",
        "You can view your latest WAM in your unofficial academic "
        "record in the Web Enrolment System (WES) at any time. It will "
        "be calculated using the results from all of your completed "
        "semesters.":
            "你随时可以在 WES（学生系统）的非正式学业记录里查看最新的 WAM（加权平均分）。它是用你已完成的所有学期的成绩算出来的。",
        "Your WAM will also appear on your academic record "
        "(transcript). You’ll receive a free academic record when you "
        "graduate.":
            "你的 WAM（加权平均分）也会出现在学业记录（成绩单）上。毕业时你会免费获得一份学业记录。",
        "Your request for a correction needs to be in writing, so "
        "email the chief examiner. Make sure you do this within this "
        "timeframe below:":
            "更正请求必须以书面形式提出，请发邮件给主考官（chief examiner），并务必在下列时限之内：",
        "credit point value of each unit":
            "每门课程的学分",
        "friends or colleagues think you deserved a higher mark.":
            "朋友或同学认为你该拿更高的分。",
        "receiving a late penalty even though you submitted on time.":
            "明明按时提交却被扣了迟交分。",
        "semester one –- within six weeks of the release of your unit "
        "results.":
            "第一学期——自课程成绩公布起六周之内。",
        "semester two –- before the end of week one of semester one "
        "the next year.":
            "第二学期——在次年第一学期第一周结束之前。",
        "the marker doesn’t agree with your summary, data or findings":
            "评阅人不认同你的结论、数据或研究发现",
        "year level weighting of each unit.":
            "每门课程的年级权重。",
        "you disagree with how the marker weighed parts of your "
        "assessment":
            "你不认同评阅人对考核各部分的权重处理",
        "you expected a higher mark based on your past performance":
            "你根据以往表现，本以为能拿更高的分",
        "you feel you didn’t get enough explanation for your mark":
            "你觉得关于分数的解释不够充分",
        "your mark is inconsistent with what you received for similar "
        "assessments":
            "你的分数与类似考核所得的分数不一致",
        "your marks having been been summed up incorrectly":
            "你的分数被加总错了",
        "DEF (deferred assessment)":
            "DEF（延期考核）",
        "NS (supplementary assessment)":
            "NS（补考）",
        "Weighted credit points":
            "加权学分",
    },
}


# Reviewed page-specific overrides are kept out of the global glossary because
# short labels such as "Pass", "Credit", "View" and "Withdrawn" depend on the
# guide in which they appear. This map was audited against all 45 guide payloads.
GUIDE_AUDIT_OVERRIDES: dict[str, dict[str, str]] = {
    "academic-progress": {"Hearing decisions": "听证决定"},
    "academic-transcripts": {
        "About your results": "关于你的成绩",
        "Click Add.": "点击“添加”。",
        "Click Continue.": "点击“继续”。",
        "Click Link Account.": "点击“关联账户”。",
        "Current students": "在读学生",
        "Digital format": "电子版",
        "Hard copy format": "纸质版",
        "Log into My eQuals.": "登录 My eQuals。",
        "Monash Study app.": "Monash Study 应用。",
        "Official record": "正式学业记录",
        "Past students": "往届学生",
        "Results legend": "成绩等级说明",
        "Unofficial record": "非正式学业记录",
        "View": "查看",
        "Your privacy View": "你的隐私（查看）",
    },
    "add-or-withdraw-units": {
        "Adding units": "添加课程",
        "Before enrolling": "选课注册前",
        "Domestic students": "澳大利亚本地学生",
        "How to add a unit": "如何添加课程",
        "Dates to check": "需要留意的日期",
        "Relevant policies": "相关政策",
        "Selecting units": "选择课程",
        "Withdrawn Early": "提前退课",
        "Withdrawn Fail": "退课不及格",
        "Withdrawn Late": "逾期退课",
        "Withdrawn fail": "退课不及格",
        "WN (withdrawn fail)": "WN（退课不及格）",
        "WD-EARLY": "WD-EARLY（提前退课）",
        "WD-LATE": "WD-LATE（逾期退课）",
        "WD-FAIL": "WD-FAIL（退课不及格）",
    },
    "assessment-at-monash": {
        "Extensions": "延期提交",
        "Grading and results": "评分与成绩",
        "Late submissions": "逾期提交",
        "Marking criteria": "评分标准",
        "Relevant procedures": "相关流程",
    },
    "census-dates": {"View": "查看"},
    "census-dates-explained": {
        "Academic penalties": "学业后果",
        "Before enrolling": "选课注册前",
        "Financial penalties": "财务后果",
        "HELP loans": "HELP 学生贷款",
        "Research students": "研究型学位学生",
    },
    "changing-your-enrolment": {
        "Honours students": "荣誉学位学生",
        "Study load": "修读负荷",
        "University changes": "学校对选课的调整",
    },
    "course-advice": {"Assessments View": "考核（查看）", "View": "查看"},
    "defer-final-assessment": {
        "Apply to reschedule": "申请改期",
        "Late applications": "逾期申请",
        "View": "查看",
    },
    "discontinue-course": {
        "Go back": "返回",
        "How to discontinue": "如何退读学位课程",
        "Re-enrolling": "重新选课注册",
        "What happens next": "接下来会怎样？",
    },
    "enrolments": {
        "Double degrees": "双学位",
        "Enrolments": "选课注册",
        "Making changes": "更改选课注册",
        "Re-enrol": "重新选课注册",
        "Study load": "修读负荷",
    },
    "fees": {
        "Course fees": "学位课程学费",
        "Fees and payments": "学费与缴费",
        "Fees statements": "费用账单",
        "Payments": "缴费",
    },
    "final-assessment-dates": {
        "Final assessments": "期末考核",
        "Swot vac": "SWOT Vac（复习周）",
        "View": "查看",
    },
    "gpa": {
        "Converting your GPA": "GPA 换算",
        "Cumulative Grade Point Average (CGPA)": "累计平均绩点（CGPA）",
        "How to find out your GPA": "如何查看 GPA",
        "How to get your CGPA": "如何计算 CGPA",
        "Methodology": "计算方法",
        "Re-marking": "复核评分",
        "Hurdle fail": "未达到及格门槛",
        "Withdrawn fail": "退课不及格",
        "SFR (satisfied faculty requirements)": "SFR（已满足学院要求）",
        "NE (not examinable)": "NE（无需参加考试）",
        "NAS (not assessed)": "NAS（未评定）",
        "WI (withdrawn incomplete)": "WI（退课未完成）",
        "PGO (pass grade only)": "PGO（仅评定为及格）",
        "N (fail)": "N（不及格）",
        "WN (withdrawn fail)": "WN（退课不及格）",
    },
    "important-dates": {"Principal dates": "校历主要日期", "Semester dates": "学期日期"},
    "intermission": {"Go back": "返回", "View": "查看"},
    "malaysia-insurance": {"Study Interruption": "学业中断"},
    "malaysia-special-consideration": {
        "Applying late": "逾期申请",
        "Examples": "示例",
        "Group assessments": "小组考核",
    },
    "malaysia-student-admin": {
        "MonPlan": "MonPlan 学业规划系统",
        "Principal dates": "校历主要日期",
        "Timetabling": "排课与课表",
    },
    "malaysia-student-pass": {"Documents": "文件", "No": "不允许", "Yes": "允许"},
    "malaysia-student-services": {
        "Career services": "就业服务",
        "New to Monash": "Monash 新生",
        "News and Events": "新闻与活动",
        "Support services": "支持服务",
    },
    "oshc": {"Pricing": "费用"},
    "principal-dates": {
        "Australian campuses": "澳大利亚各校区",
        "Principal dates": "校历主要日期",
        "University reopens": "大学恢复开放",
        "Full year – 2026": "2026 全学年",
    },
    "results-legend": {
        "2020 to 2021: Temporary grading system":
            "2020–2021 年 COVID-19 疫情期间临时成绩评定制度",
        "Credit": "良好（Credit）",
        "Deferred Assessment": "延期考核",
        "Did Not Sit": "未参加考试",
        "Discontinued": "已终止修读",
        "Distinction": "优秀（Distinction）",
        "Exempt": "豁免",
        "Faculty Pass": "学院评定及格",
        "Fail": "不及格",
        "First Class Honours": "一等荣誉",
        "High Distinction": "最高等级优秀（High Distinction）",
        "High Satisfactory": "高度满意",
        "Higher Distinction": "更高等级优秀",
        "Honours course grades": "荣誉学位课程成绩等级",
        "Hurdle Fail": "未达到及格门槛",
        "Incomplete": "未完成",
        "Lower Level Pass": "低等级及格",
        "Masters awarded with distinction": "获授优秀等级的硕士学位",
        "Merit": "优良（Merit）",
        "NGO (Fail)": "NGO（不及格）",
        "Near Pass": "接近及格",
        "Non Assessed": "未评定",
        "Non-Assessed": "未评定",
        "Not Assessed": "未评定",
        "Not Examinable": "无需参加考试",
        "Not Satisfied Requirements": "未满足要求",
        "Not-Examinable": "无需参加考试",
        "PGO (Pass)": "PGO（及格）",
        "Pass": "及格",
        "Pass Applies only to students who started on or after 1 January 2021":
            "及格——仅适用于 2021 年 1 月 1 日或之后入学的学生",
        "Pass Division I": "一等及格",
        "Pass Division II": "二等及格",
        "Pass Division IIE": "二等及格（补考）",
        "Pass Grade Only. No higher grade available":
            "仅评定为及格，不提供更高等级",
        "Pass Grade Only (no higher grade available)":
            "仅评定为及格（不提供更高等级）",
        "Pass on Appeal": "申诉后评定及格",
        "Pass with Credit": "良好及格",
        "Provisional Grade": "暂定成绩",
        "Satisfied Faculty Requirements": "已满足学院要求",
        "Second Class Honours Division A": "二等荣誉 A 级",
        "Second Class Honours Division B": "二等荣誉 B 级",
        "Supplementary Assessment": "补考",
        "Supplementary Assessment Granted": "已获准补考",
        "Sound pass": "稳健及格",
        "Subject Not Graded": "该科目不评定等级",
        "The Monash grading system": "Monash 成绩评定体系",
        "Third Class Honours": "三等荣誉",
        "Third Class Honours Applies only to students who started before 2021":
            "三等荣誉——仅适用于 2021 年之前入学的学生",
        "2020–2021 Temporary grading system in response to COVID-19":
            "2020–2021 年应对 COVID-19 的临时成绩评定制度",
        "Withheld": "暂缓公布",
        "Withdrawn": "已退课",
        "Withdrawn Fail": "退课不及格",
        "Withdrawn Incomplete": "退课未完成",
        "Assessment Deferred": "考核延期",
        "Literal Marks": "原始分数",
        "Not Pass": "不及格",
        "Satisfactory": "满意",
        "Unsatisfactory": "不满意",
    },
    "special-consideration": {
        "Applying late": "逾期申请",
        "Examples": "示例",
        "Group assessments": "小组考核",
    },
    "student-conduct": {"Breaches": "违规行为"},
    "student-visa": {
        "Processing times": "签证审理时间",
        "Study load": "修读负荷",
        "Study mode": "修读方式",
    },
    "study-at-another-institution": {
        "Closing dates": "申请截止日期",
        "Fees and offers": "费用与录取通知",
        "Limits on credit": "学分限制",
        "To apply": "申请方法",
    },
    "supporting-documents": {
        "Extension documents": "延期申请所需文件",
        "Impact statement": "影响情况说明",
        "Loss or bereavement": "亲友去世或丧亲",
        "View": "查看",
    },
    "visa-changes": {"Extending your stay": "延长在澳停留时间"},
    "wam": {
        "Converting your WAM": "WAM 换算",
        "HWA for Engineering": "工程学院 HWA",
        "HWA for Law": "法学院 HWA",
        "Methodology": "计算方法",
        "N (fail)": "N（不及格）",
        "NAS (not assessed)": "NAS（未评定）",
        "NE (not examinable)": "NE（无需参加考试）",
        "NGO (fail grade)": "NGO（不及格成绩）",
        "Re-marking": "复核评分",
        "WDN (withdrawn)": "WDN（已退课）",
        "WH (withheld)": "WH（暂缓公布）",
        "WN (withdrawn fail)": "WN（退课不及格）",
    },
    "working-on-a-student-visa": {"The current rules": "现行规定"},
}


# Headings which were already readable in the generated Chinese are pinned as
# reviewed too. This keeps a later machine-translation refresh from changing
# navigation terminology that was checked during the same all-guide audit.
GUIDE_REVIEWED_HEADINGS: dict[str, dict[str, str]] = {
    "about-academic-progress": {
        "Review periods": "审核周期",
        "What we review": "审核内容",
    },
    "academic-integrity": {"Troubleshooting": "问题排查"},
    "academic-progress": {"Appeals and reviews": "申诉与复核"},
    "academic-transcripts": {"Graduates": "毕业生"},
    "add-or-withdraw-units": {"Update Allocate+": "更新 Allocate+（排课系统）"},
    "assessment-at-monash": {
        "Academic integrity": "学术诚信",
        "Assessment details": "考核详情",
        "Types of assessment": "考核类型",
    },
    "census-dates-explained": {"Exceptions": "例外情况"},
    "confirmation-of-enrolment": {"Application outcome": "申请结果"},
    "course-advice": {"Course advice": "学位课程咨询"},
    "defer-final-assessment": {"How to apply": "如何申请", "Outcome": "申请结果"},
    "discontinue-course": {"Related links": "相关链接"},
    "enrolments": {"Study options": "修读选项"},
    "fee-payment-dates": {"Related links": "相关链接"},
    "fees": {"Refunds": "退款"},
    "final-assessment-dates": {"Related links": "相关链接"},
    "gpa": {
        "Australia": "澳大利亚",
        "Calculation steps": "计算步骤",
        "CGPA calculator": "CGPA 计算器",
        "Example": "示例",
        "GPA calculation formula": "GPA 计算公式",
        "GPA calculator": "GPA 计算器",
        "Malaysia": "马来西亚校区",
    },
    "graduations": {"Graduations": "毕业典礼"},
    "important-dates": {
        "Important dates": "重要日期",
        "System access dates": "系统开放日期",
    },
    "intermission": {
        "Before you apply": "申请前",
        "Exception": "例外情况",
        "Exceptions": "例外情况",
        "Fees": "学费",
        "How to apply": "如何申请",
        "Related links": "相关链接",
    },
    "international-students": {"Student news": "学生资讯"},
    "malaysia-special-consideration": {
        "Eligibility": "申请资格",
        "Outcome": "申请结果",
        "Quick links": "快捷链接",
    },
    "malaysia-student-admin": {"Enrolment": "选课注册"},
    "malaysia-student-services": {
        "Campus Life": "校园生活",
        "Study abroad": "海外学习与交换",
    },
    "oshc": {"Advice": "咨询", "Renewing your OSHC": "续保 OSHC"},
    "principal-dates": {
        "Exceptions": "例外情况",
        "Monash Indonesia": "Monash 印度尼西亚校区",
        "Monash Malaysia": "Monash 马来西亚校区",
        "Previous years": "往年",
        "This month": "本月",
    },
    "results-legend": {
        "Marks from previous years": "往年成绩",
        "Related links": "相关链接",
    },
    "special-consideration": {
        "Eligibility": "申请资格",
        "Outcome": "申请结果",
        "Quick links": "快捷链接",
    },
    "student-visa": {
        "After you apply": "申请后",
        "Applying for a visa": "申请签证",
        "Before you apply": "申请前",
        "Visa conditions": "签证条件",
    },
    "study-abroad": {
        "Contact Us": "联系我们",
        "Monash Abroad": "Monash Abroad（海外学习与交换）",
        "Study Overseas": "海外学习",
    },
    "study-at-another-institution": {
        "Eligibility": "申请资格",
        "Related links": "相关链接",
        "Semester one": "第一学期",
        "Semester two": "第二学期",
        "Unit results": "课程成绩",
    },
    "wam": {
        "Calculation steps": "计算步骤",
        "Example": "示例",
        "Formula": "计算公式",
        "Related links": "相关链接",
        "WAM calculator": "WAM 计算器",
    },
    "working-on-a-student-visa": {"Exceptions": "例外情况"},
}
for _guide_slug, _headings in GUIDE_REVIEWED_HEADINGS.items():
    GUIDE_AUDIT_OVERRIDES.setdefault(_guide_slug, {}).update(_headings)


# The principal-dates page exposes weekday abbreviations as separate table
# cells. Translating them one at a time produced nonsense such as “卫星1号” for
# “Sat 01” and “结婚 28” for “Wed 28”. Pin every possible calendar cell.
_WEEKDAYS_ZH = {
    "Mon": "周一",
    "Tue": "周二",
    "Wed": "周三",
    "Thu": "周四",
    "Fri": "周五",
    "Sat": "周六",
    "Sun": "周日",
}
GUIDE_AUDIT_OVERRIDES["principal-dates"].update({
    f"{weekday} {day:02d}": f"{chinese} {day:02d}"
    for weekday, chinese in _WEEKDAYS_ZH.items()
    for day in range(1, 32)
})
GUIDE_AUDIT_OVERRIDES["principal-dates"].update({
    month: f"{number} 月"
    for number, month in enumerate((
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ), start=1)
})


for _guide_slug, _reviewed_strings in GUIDE_AUDIT_OVERRIDES.items():
    GUIDE_BODIES.setdefault(_guide_slug, {}).update(_reviewed_strings)


# Extractor v6 removes the nested-accordion button word from headings. Keep the
# old source keys for a safe rolling deploy, and add the cleaned keys so the
# reviewed Chinese survives the next crawl instead of falling back to a new
# machine translation.
for _guide_strings in GUIDE_BODIES.values():
    for _english, _chinese in list(_guide_strings.items()):
        if not _english.endswith((" View", " Close")):
            continue
        _clean_english = _english.rsplit(" ", 1)[0]
        _clean_chinese = _chinese
        for _suffix in (" 查看", " 收起", "（查看）", "（收起）", " (查看)", " (收起)"):
            if _clean_chinese.endswith(_suffix):
                _clean_chinese = _clean_chinese.removesuffix(_suffix)
                break
        _guide_strings.setdefault(_clean_english, _clean_chinese)


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
    seeds += [
        TranslationSeed(
            ZH, UNIT, code, "content",
            strings={english: chinese},
            note="课程名称人工翻译：机器在无句子上下文的名词短语上失手",
        )
        for code, (english, chinese) in UNIT_TITLES.items()
    ]
    for slug, (question, answer) in FAQ_ZH.items():
        seeds.append(TranslationSeed(ZH, FAQ_ENTRY, slug, "question", text=question))
        seeds.append(TranslationSeed(ZH, FAQ_ENTRY, slug, "answer", text=answer))
    return tuple(seeds)


TRANSLATION_SEEDS: tuple[TranslationSeed, ...] = all_seeds()
