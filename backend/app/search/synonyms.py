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

The table is in two halves. Admin words - fees, visas, exams, graduation - are
questions for the official pages, and the unit search leaves them alone: 学费
used to list 199 units, every exchange unit whose overview mentions fees, above
the fees page. Subject and degree words reach units and degrees as well.
"""
from __future__ import annotations

ZH_ADMIN_TERMS: dict[str, tuple[str, ...]] = {
    # --- visas and international students -----------------------------------
    # Both campuses' documents: Monash Malaysia students call their Student
    # Pass 学生签证 too. A campus named in the question picks one.
    "学生签证": ("student visa", "student pass"),
    "签证": ("visa",),
    # 续签 is only ever said of a visa, so every alternative carries the word:
    # a bare "extension" sent it to the assignment-extension page.
    # Not a bare "visa" either: with it 学生签证续签 ranked "Your student visa"
    # above "Extending your stay (student visas)".
    "续签": ("renew visa", "visa renewal", "extend visa", "visa extension", "new visa",
           "extending your stay"),
    "签证延期": ("visa extension", "extend visa", "new visa"),
    "签证变更": ("visa changes",),
    "学生准证": ("student pass",),
    "入学确认": ("confirmation of enrolment", "coe"),
    "打工": ("work", "working"),
    "兼职": ("work", "part-time"),
    "工作时长": ("work hours", "working hours"),
    "打工时长": ("work hours", "working hours", "work rights"),
    "留学生": ("international student",),
    "雅思": ("ielts",),
    "语言要求": ("english language requirements",),
    # What students call the two campuses. Inside a longer question these are
    # taken out and used to narrow the search (service.campus_in_query); alone,
    # they are a search for that campus.
    "马莫": ("monash malaysia", "malaysia"),
    "澳莫": ("monash australia", "australia"),
    "国际学生": ("international student",),
    "医保": ("oshc", "health cover", "health insurance"),
    "保险": ("insurance", "health cover"),
    "全日制": ("full-time",),
    # --- getting to campus --------------------------------------------------
    "交通": ("transport",),
    "校车": ("shuttle bus", "shuttle"),
    "班车": ("shuttle bus", "shuttle"),
    "公交": ("bus", "transport"),
    "公车": ("bus", "transport"),
    "轻轨": ("lrt", "brt", "transport"),
    "地铁": ("lrt", "ktm", "transport"),
    "停车场": ("car park", "parking"),
    "校园地图": ("campus map",),
    "学校地图": ("campus map",),
    "怎么去学校": ("getting to the campus", "transport"),
    "去机场": ("airport", "klia"),
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
    "转校区": ("campus transfer", "transfer campus", "change campus", "course or campus transfer"),
    "换校区": ("campus transfer", "transfer campus", "change campus"),
    "转校": ("campus transfer", "transfer to another", "course transfer"),
    "重新注册": ("re-enrol",),
    "学分转换": ("credit transfer", "credit", "advanced standing"),
    "学分": ("credit points",),
    "辅修": ("minor",),
    "主修": ("major",),
    "选修课": ("elective",),
    "选修": ("elective",),
    "在读证明": ("student letter", "enrolment verification"),
    "学分减免": ("credit", "exemption", "advanced standing"),
    "学分豁免": ("credit", "exemption", "advanced standing"),
    "转学分": ("credit transfer", "credit", "advanced standing"),
    "课程规划": ("course advice", "course planning"),
    "课程地图": ("course map", "course maps", "course progression"),
    "课程规划图": ("course map", "course maps"),
    "修读顺序": ("course map", "course progression"),
    "选课顺序": ("course map", "course progression"),
    "必修课": ("core units", "course map"),
    # Monash Malaysia's MPU units are what most students mean; Australia's
    # breadth studies are the same idea and the glossary's 通识课程.
    "通识课程": ("general studies", "breadth studies"),
    "通识课": ("general studies", "mpu", "breadth studies"),
    "通识": ("general studies", "mpu", "breadth studies"),
    "马来西亚必修课": ("general studies", "mpu"),
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
    # Not a bare "defer": that is also deferring a course offer, and it put
    # "Enrol for the first time (or defer)" second for 延期考试.
    "延期考试": ("deferred assessment", "deferred exam", "defer final assessment"),
    "缓考": ("deferred assessment", "defer final assessment"),
    "补考": ("supplementary assessment", "deferred assessment", "supplementary"),
    "延期": ("extension", "defer", "deferred"),
    "延期交": ("extension",),
    "迟交": ("late submission", "late penalty", "extension"),
    "晚交": ("late submission", "late penalty", "extension"),
    "申诉": ("appeal",),
    "成绩复查": ("review of results", "results"),
    "查分": ("results",),
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
    "缴费": ("fee payment", "pay fees", "payment methods"),
    "交学费": ("fee payment", "pay fees", "payment methods"),
    "交费": ("fee payment", "pay fees", "payment methods"),
    "奖学金": ("scholarship",),
    "重要日期": ("important dates", "key dates"),
    "开学": ("semester dates", "principal dates", "orientation"),
    "学期": ("semester", "teaching period"),
    "毕业典礼": ("graduation ceremony", "graduations"),
    # Not "graduate": that is half the postgraduate degree titles, and 毕业
    # listed 83 Graduate Certificates. The stemmer already takes "graduation"
    # to the pages that say "apply to graduate".
    "毕业": ("graduation",),
    "申请毕业": ("apply to graduate",),
    "毕业证": ("testamur", "award certificate", "graduation documents"),
    "毕业证书": ("testamur", "award certificate", "graduation documents"),
    "学位证": ("testamur", "award certificate"),
    "学位证书": ("testamur", "award certificate"),
    "学位授予": ("conferral", "conferred"),
    "缺席毕业": ("in absentia",),
    "毕业要求": ("course requirements", "graduation eligibility"),
    "校历": ("principal dates", "important dates", "semester dates"),
    "假期": ("non-teaching period", "break"),
    "退款": ("refund",),
    "退费": ("refund", "fee reversal"),
    "欠费": ("encumbrance", "non-payment"),
    # --- exchange -----------------------------------------------------------
    "交换": ("exchange", "study abroad"),
    "海外交换": ("exchange", "study abroad"),
    # --- campus life (no official page yet; the words still reach posts) ------
    "图书馆": ("library",),
    "停车": ("parking",),
    "住宿": ("accommodation",),
    "宿舍": ("accommodation",),
    "心理咨询": ("counselling",),
    "学生证": ("student id card", "m-pass"),
    "校园卡": ("m-pass", "id card"),
    "邮箱": ("email",),
    "密码": ("password",),
    "租房": ("accommodation", "rent"),
    "打印": ("printing", "print"),
}

ZH_FIELD_TERMS: dict[str, tuple[str, ...]] = {
    # --- degree levels ------------------------------------------------------
    "本科": ("bachelor", "undergraduate"),
    "学士": ("bachelor",),
    "硕士": ("master",),
    "研究生": ("master", "postgraduate", "graduate"),
    "博士": ("doctor", "phd"),
    "双学位": ("double degree", "and bachelor"),
    "荣誉学位": ("honours",),
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
    # Unit names as students say them. Each is the title Monash gives the
    # unit, so a Chinese query lands on the unit before the units that only
    # mention the topic.
    "编程入门": ("introduction to programming",),
    "数据结构": ("data structures",),
    "操作系统": ("operating systems",),
    "计算机网络": ("computer networks",),
    "离散数学": ("discrete mathematics",),
    "线性代数": ("linear algebra",),
    "微积分": ("calculus",),
    "概率": ("probability",),
    "软件测试": ("software testing",),
    "人机交互": ("human-computer interaction", "interaction design"),
    "网页开发": ("web development", "web"),
    "前端": ("front-end", "web"),
    "移动开发": ("mobile application development", "app development"),
    "云计算": ("cloud computing",),
    "计算机视觉": ("computer vision",),
    "自然语言处理": ("natural language processing",),
    "深度学习": ("deep learning",),
    "信息安全": ("information security", "cybersecurity"),
    "密码学": ("cryptography",),
    "数据可视化": ("data visualisation",),
    "项目管理": ("project management",),
    "面向对象": ("object oriented",),
    "并行计算": ("parallel computing",),
    "区块链": ("blockchain",),
    "游戏开发": ("game development",),
    "毕业设计": ("final year project", "capstone"),
    "实习": ("placement", "internship", "industry experience",
           "work integrated learning"),
    "论文": ("thesis",),
    "计量经济": ("econometrics",),
    "微观经济": ("microeconomics",),
    "宏观经济": ("macroeconomics",),
    "有机化学": ("organic chemistry",),
    "生物化学": ("biochemistry",),
    "解剖": ("anatomy",),
    "生理": ("physiology",),
    "药理": ("pharmacology",),
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

ZH_TERMS: dict[str, tuple[str, ...]] = {**ZH_ADMIN_TERMS, **ZH_FIELD_TERMS}
