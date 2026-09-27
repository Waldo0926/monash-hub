"""How students actually phrase things, for search only.

The glossary (``app/knowledge/glossary.py``) maps an English Handbook term to
the Chinese a translator must use for it. Read backwards it is a decent search
index, but only for the words Monash itself writes: nobody translating a policy
page ever needed 挂科, 转专业 or 续签, and those are exactly the words a student
types. Searching 学生签证续签 answered with the withdrawal FAQ because 续签 meant
nothing to search and 签证 alone matched a sentence about visas inside it.

So this table is the other half: the student's word on the left, the English
the official page uses for it on the right. Every alternative on the right is
one ``websearch_to_tsquery`` phrase, and the alternatives are ORed - any one of
them is the same concept.

Nothing here is ever shown to a reader. It widens what a query can find; it
never changes what a page says, which is why it can be looser than the glossary
and does not need a translator's sign-off.

Keep keys at least two characters. A single ideograph does duty in too many
words to mean one thing (课 is in 选课, 退课 and 课表).
"""
from __future__ import annotations

ZH_TERMS: dict[str, tuple[str, ...]] = {
    # --- visas and international students -----------------------------------
    "学生签证": ("student visa",),
    "签证": ("visa",),
    # 续签 is only ever said of a visa, so every alternative carries the word:
    # a bare "extension" sent it to the assignment-extension page.
    "续签": ("renew visa", "visa renewal", "extend visa", "visa extension", "new visa",
           "visa"),
    "签证延期": ("visa extension", "extend visa", "new visa"),
    "签证变更": ("visa changes",),
    "学生准证": ("student pass",),
    "入学确认": ("confirmation of enrolment", "coe"),
    "打工": ("work", "working"),
    "兼职": ("work", "part-time"),
    "工作时长": ("work hours", "working hours"),
    "留学生": ("international student",),
    "国际学生": ("international student",),
    "医保": ("oshc", "health cover", "health insurance"),
    "保险": ("insurance", "health cover"),
    "全日制": ("full-time",),
    # --- enrolment ----------------------------------------------------------
    "选课": ("enrol", "enrolment", "add units"),
    "加课": ("add units", "enrol"),
    "退课": ("withdraw", "drop"),
    "退选": ("withdraw", "drop"),
    "退学": ("discontinue",),
    "休学": ("intermission",),
    "请假": ("leave", "intermission"),
    "转专业": ("change course", "course transfer", "change enrolment"),
    "换专业": ("change course", "course transfer", "change enrolment"),
    "转课程": ("change course",),
    "重新注册": ("re-enrol",),
    "学分转换": ("credit transfer", "credit", "advanced standing"),
    "学分减免": ("credit", "exemption", "advanced standing"),
    "学分豁免": ("credit", "exemption", "advanced standing"),
    "转学分": ("credit transfer", "credit", "advanced standing"),
    "课程规划": ("course advice", "course planning"),
    "课表": ("timetable",),
    "排课": ("timetable", "allocate"),
    "截止日期": ("deadline", "census", "due date"),
    "截止": ("deadline", "census"),
    "学籍统计日": ("census date",),
    # --- assessment and results ---------------------------------------------
    "考试时间": ("exam timetable", "final assessment dates", "exam dates"),
    "考试安排": ("exam timetable", "final assessment dates"),
    "考试": ("exam", "examination", "final assessment"),
    "期末": ("final", "exam"),
    "延期考试": ("deferred assessment", "deferred exam", "defer"),
    "缓考": ("deferred assessment", "defer"),
    "补考": ("supplementary assessment", "deferred assessment", "supplementary"),
    "延期": ("extension", "defer", "deferred"),
    "延期交": ("extension",),
    "特殊考虑": ("special consideration",),
    "病假": ("sick", "illness", "medical certificate", "special consideration"),
    "生病": ("sick", "illness", "medical"),
    "医生证明": ("medical certificate",),
    "病假条": ("medical certificate",),
    "证明材料": ("supporting documents",),
    "挂科": ("fail", "failed"),
    "不及格": ("fail",),
    "重修": ("repeat", "fail"),
    "成绩单": ("transcript", "academic record"),
    "成绩": ("results", "grades", "marks"),
    "出分": ("results",),
    "均分": ("wam", "weighted average mark"),
    "绩点": ("gpa", "grade point average"),
    "学术诚信": ("academic integrity",),
    "抄袭": ("plagiarism",),
    "作弊": ("cheating", "collusion", "academic integrity"),
    "学术进展": ("academic progress",),
    "学业进展": ("academic progress",),
    "学业进度": ("academic progress",),
    "学业预警": ("academic progress", "unsatisfactory progress"),
    "劝退": ("exclusion", "excluded", "unsatisfactory progress"),
    "开除": ("exclusion", "excluded"),
    # --- fees and dates -----------------------------------------------------
    "学费": ("fees", "tuition"),
    "缴费": ("fee payment", "pay fees"),
    "交学费": ("fee payment", "pay fees"),
    "奖学金": ("scholarship",),
    "重要日期": ("important dates", "key dates"),
    "开学": ("semester start", "orientation"),
    "学期": ("semester", "teaching period"),
    "毕业典礼": ("graduation ceremony",),
    "毕业": ("graduation", "graduate"),
    # --- exchange -----------------------------------------------------------
    "交换": ("exchange", "study abroad"),
    "海外交换": ("exchange", "study abroad"),
    # --- campus life (no official page yet; the words still reach posts) ------
    "图书馆": ("library",),
    "停车": ("parking",),
    "住宿": ("accommodation",),
    "宿舍": ("accommodation",),
    "心理咨询": ("counselling",),
    "学生证": ("student id card",),
    # --- degree levels ------------------------------------------------------
    "本科": ("bachelor", "undergraduate"),
    "学士": ("bachelor",),
    "硕士": ("master",),
    "研究生": ("master", "postgraduate", "graduate"),
    "博士": ("doctor", "phd"),
    "双学位": ("double degree",),
    "文凭": ("diploma",),
    "证书": ("certificate",),
    # --- fields of study ----------------------------------------------------
    # Degree titles are English and short; these are what a student searching
    # for a degree types instead.
    "商科": ("commerce", "business"),
    "商学": ("commerce", "business"),
    "商业": ("business",),
    "会计": ("accounting",),
    "金融": ("finance",),
    "经济": ("economics",),
    "精算": ("actuarial",),
    "市场营销": ("marketing",),
    "管理": ("management",),
    "法律": ("law", "laws"),
    "法学": ("law", "laws"),
    "计算机科学": ("computer science",),
    "计算机": ("computer science", "computing", "information technology"),
    "信息技术": ("information technology",),
    "软件工程": ("software engineering",),
    "数据科学": ("data science",),
    "人工智能": ("artificial intelligence",),
    "机器学习": ("machine learning",),
    "网络安全": ("cybersecurity", "cyber security"),
    "数据库": ("database", "databases"),
    "算法": ("algorithm", "algorithms"),
    "编程": ("programming",),
    "工程": ("engineering",),
    "土木": ("civil engineering",),
    "机械": ("mechanical engineering",),
    "电气": ("electrical engineering",),
    "化工": ("chemical engineering",),
    "医学": ("medicine", "medical"),
    "护理": ("nursing",),
    "药学": ("pharmacy", "pharmaceutical"),
    "公共卫生": ("public health",),
    "心理学": ("psychology",),
    "心理": ("psychology",),
    "教育": ("education", "teaching"),
    "艺术": ("arts",),
    "文科": ("arts",),
    "设计": ("design",),
    "建筑": ("architecture",),
    "数学": ("mathematics",),
    "统计": ("statistics",),
    "物理": ("physics",),
    "化学": ("chemistry",),
    "生物": ("biology", "biological"),
    "生物医学": ("biomedical", "biomedicine"),
    "传媒": ("media", "communication"),
    "媒体": ("media",),
    "新闻": ("journalism",),
    "翻译": ("translation", "interpreting"),
    "语言学": ("linguistics",),
    "历史": ("history",),
    "哲学": ("philosophy",),
    "政治": ("politics",),
    "国际关系": ("international relations",),
    "环境": ("environment", "environmental"),
    "科学": ("science",),
}
