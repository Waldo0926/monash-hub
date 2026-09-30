"""Labels a Handbook page is built from, put together rather than translated.

``structure_zh.py`` holds the wording for every such label seen in the 2026 and
early-2027 Handbook. This module is for the *next* one: the labels have shapes,
and a shape can be rendered without asking a model.

    Part B. Breadth studies             B 部分。通识课程（Breadth studies）
    Level 8 - Bachelor Honours Degree   第 8 级 - 荣誉学士学位
    Essay (2,000 words)                 论文（2,000 字）

The reason it matters is the one at the top of ``structure_zh.py``: the model
renders the words inside these labels differently every time it sees them, and
"Part B." is the heading of every requirement group on every degree page. A
shape that is not recognised, or a title that is not in the table, returns
``None`` and goes to the ordinary path, exactly as before. Nothing in here is
allowed to invent a wording - a title has to be in ``PART_TITLES`` to be used.
"""
from __future__ import annotations

import re

LOCALES = ("zh",)

# Titles of "Part X. <title>" requirement groups, lower-cased.
PART_TITLES: dict[str, str] = {
    "foundation knowledge": "基础知识", "foundation studies": "基础课程",
    "discipline knowledge": "学科知识", "discipline studies": "学科课程",
    "specialist core studies": "专业核心课程", "core studies": "核心课程",
    "coursework studies": "授课型课程", "coursework": "授课型课程",
    "foundation": "基础", "foundations": "基础",
    "advanced preparatory studies": "高级预备课程",
    "advanced applied studies": "高级应用课程", "advanced design studies": "高级设计课程",
    "advanced expertise": "高级专业能力",
    "apac level 1-accredited sequence": "APAC 第 1 级认证序列",
    "applied academic studies in clinical psychology": "临床心理学应用学术课程",
    "applied studies": "应用课程", "clinical studies": "临床课程",
    "core and project studies": "核心与项目课程",
    "core digital communications studies": "数字传播核心课程",
    "core foundation studies": "核心基础课程",
    "core prescribing skills studies": "核心处方技能课程",
    "core research studies": "核心研究课程", "critical contexts": "批判性语境",
    "data challenges": "数据挑战",
    "engineering fundamentals and design studies": "工程基础与设计课程",
    "food science studies": "食品科学课程",
    "foundation specialist studies": "基础专业方向课程",
    "intern training program": "实习培训项目", "major studies": "主修课程",
    "operational knowledge": "运营知识", "orientation": "入门引导",
    "orientation to education": "教育入门",
    "professional development studies": "专业发展课程",
    "professional studies": "专业课程", "psychology sequence": "心理学序列",
    "research": "研究", "research foundation studies": "研究基础课程",
    "research studies": "研究课程", "science specified study": "理学指定课程",
    "specialist studies": "专业方向课程", "specified studies": "指定课程",
    "studio practices": "工作室实践", "capstone studies": "综合实践课程",
    "advanced application studies": "高级应用课程",
    "advanced clinical placement": "高级临床实习",
    "advanced design applications": "高级设计应用",
    "advanced health science core studies": "高级健康科学核心课程",
    "advanced research studies": "高级研究课程",
    "advanced scholarly practice": "高级学术实践", "advanced studies": "高级课程",
    "advanced theory and practice": "高级理论与实践",
    "breadth studies": "通识课程（Breadth studies）", "business studies": "商科课程",
    "civil engineering studies": "土木工程课程", "clinical placement": "临床实习",
    "clinical placement in psychology": "心理学临床实习",
    "clinical skills and practice": "临床技能与实践", "core case studies": "核心案例课程",
    "core marketing studies": "营销核心课程",
    "core prescribing microcredentials": "核心处方微证书",
    "core specialist studies": "核心专业方向课程", "disciplinary practices": "学科实践",
    "discipline elective studies": "学科选修课程", "discipline streams": "学科方向",
    "education studies": "教育学课程",
    "education studies (not applicable to this specialisation)":
        "教育学课程（不适用于本专业方向）",
    "elective studies": "选修课程", "expert studies in education": "教育专家课程",
    "expert studies in educational leadership": "教育领导力专家课程",
    "expert studies in tesol": "TESOL 专家课程", "exploration": "探索",
    "food agribusiness studies": "食品与农业企业课程",
    "free elective studies": "自由选修课程", "global mobility": "全球交流",
    "music theory and ear training": "乐理与视唱练耳",
    "organisational skills": "组织技能", "policing studies": "警务课程",
    "practice development": "实践发展", "professional experience": "专业经历",
    "professional practice": "专业实践", "professional practice studies": "专业实践课程",
    "research project": "研究项目", "science listed major": "理学指定主修",
    "specialisation preparatory studies": "专业方向预备课程",
    "specified elective studies": "指定选修课程", "specified elective units": "指定选修课程",
    "specified electives": "指定选修课", "techniques for data science": "数据科学技术",
    "application studies": "应用课程", "advanced discipline studies": "高级学科课程",
    "advanced midwifery studies": "高级助产学课程", "advanced practice": "高级实践",
    "aerospace engineering knowledge and application": "航空航天工程知识与应用",
    "applied disciplinary practices": "应用学科实践",
    "applied radiation therapy practice": "放射治疗应用实践",
    "applied studies (jgu students only)": "应用课程（仅限 JGU 学生）",
    "architecture design studios": "建筑设计工作室",
    "biomedical engineering knowledge and application": "生物医学工程知识与应用",
    "chemical engineering knowledge and application": "化学工程知识与应用",
    "civil engineering knowledge and application": "土木工程知识与应用",
    "context studies": "背景课程", "curriculum studies": "课程研究（Curriculum studies）",
    "elective specialist studies": "专业选修课程", "elective study": "选修课程",
    "electives studies": "选修课程",
    "electrical and computer systems engineering knowledge and application":
        "电气与计算机系统工程知识与应用",
    "environmental engineering knowledge and application": "环境工程知识与应用",
    "free elective study": "自由选修课程", "free electives": "自由选修课",
    "free electives studies": "自由选修课程", "integration": "整合",
    "language studies": "语言课程",
    "materials engineering knowledge and application": "材料工程知识与应用",
    "mechanical engineering knowledge and application": "机械工程知识与应用",
    "partner studies": "合作院校课程", "professional advancement": "职业进阶",
    "professional inquiry": "专业探究",
    "professional practice and placement": "专业实践与实习",
    "professional practice and research": "专业实践与研究",
    "research project and professional practice": "研究项目与专业实践",
    "research project or work integrated learning": "研究项目或工作综合学习（WIL）",
    "robotics and mechatronics engineering knowledge and application":
        "机器人与机电一体化工程知识与应用",
    "software engineering knowledge and application": "软件工程知识与应用",
    "specialist elective studies": "专业选修课程", "applied practice": "应用实践",
    "extended studies": "延伸课程", "honours program": "荣誉学位项目",
    "impact through science project": "科学影响力项目",
    "indonesian studies": "印度尼西亚研究", "discipline electives": "学科选修课",
    "indonesian studies - for the indonesia offering only":
        "印度尼西亚研究 - 仅限印度尼西亚校区开设",
    "professional practice domain": "专业实践领域",
}

# "Part C. Applied studies - Malaysia": what may follow the dash.
_SUFFIXES = {
    "malaysia": "马来西亚校区", "caulfield": "Caulfield 校区", "seu": "SEU",
    "marketing and digital communications": "营销与数字传播",
    "public policy and management": "公共政策与管理",
    "cultural and creative industries": "文化与创意产业",
    "international development practice": "国际发展实践",
    "international relations": "国际关系",
    "international sustainable tourism management": "国际可持续旅游管理",
    "specialisation": "专业方向",
}
_BRACKETS = {"i&t": "I&T", "seu": "SEU"}

# Levels of the Australian Qualifications Framework as the Handbook labels them.
_LEVELS = {
    "Level 5 - Diploma": "第 5 级 - 文凭",
    "Level 7 - Bachelor Degree": "第 7 级 - 学士学位",
    "Level 8 - Bachelor Honours Degree": "第 8 级 - 荣誉学士学位",
    "Level 8 - Graduate Certificate": "第 8 级 - 研究生证书",
    "Level 8 - Graduate Diploma": "第 8 级 - 研究生文凭",
    "Level 9 - Master's Degree (Coursework)": "第 9 级 - 硕士学位（授课型）",
    "Level 9 - Master's Degree (Extended)": "第 9 级 - 硕士学位（延伸型）",
    "Level 9 - Master's Degree (Research)": "第 9 级 - 硕士学位（研究型）",
    "Level 10 - Doctoral Degree": "第 10 级 - 博士学位",
    "Level 10 - Higher Doctoral Degree": "第 10 级 - 高等博士学位",
}

# The name of an assessment, when it follows "1 - " in a unit's assessment list.
_ASSESSMENTS = {
    "Written": "书面考核", "Exercise": "练习", "Quiz / Test": "小测 / 测验",
    "Presentation": "口头报告", "Examination": "考试", "Project": "项目",
    "Report": "报告", "Assignment": "作业", "Essay": "论文", "Test": "测验",
    "Quiz": "小测", "Reflection": "反思", "Participation": "参与",
    "Case study": "案例研究", "Portfolio": "作品集", "Artefact": "作品成果",
    "Practical": "实操", "Performance": "表演", "Oral": "口试",
    "Research task": "研究任务", "Task": "任务", "Thesis": "学位论文",
    "Competency": "能力达标",
}

_PART = re.compile(r"^Part\s+([A-Z]|\d+)\s*[.:]?\s*(.*)$", re.DOTALL)
_TWO_PARTS = re.compile(r"^(.*?)\s+and\s+Part\s+([A-Z])\.?\s*(.*)$")
_SUFFIX = re.compile(r"^(.*?) - (.+)$")
_TRAILING_BRACKET = re.compile(r"^(.*?)\s*\(([^()]*)\)$")
_OR_POINTS = re.compile(r"^(\d+) or (\d+) (?:credit )?points$")
_WORDS = re.compile(r"^([\d][\d,]*) words$")
_BRACKETED_WORDS = re.compile(r"^\(([\d][\d,\s]*) words\)$")
_NUMBERED = re.compile(r"^(\d+) - (.+)$")


def _bracket(inner: str) -> str | None:
    lowered = inner.strip().lower()
    if lowered in _BRACKETS:
        return f"（{_BRACKETS[lowered]}）"
    match = _OR_POINTS.match(lowered)
    if match:
        return f"（{match.group(1)} 或 {match.group(2)} 学分）"
    return None


def _part_title(title: str) -> str | None:
    title = re.sub(r"\s+", " ", title.strip()).rstrip(".")
    known = PART_TITLES.get(title.lower())
    if known:
        return known
    split = _SUFFIX.match(title)
    if split:
        head = _part_title(split.group(1))
        suffix = _SUFFIXES.get(split.group(2).strip().lower())
        return f"{head} - {suffix}" if head and suffix else None
    trailing = _TRAILING_BRACKET.match(title)
    if trailing:
        head = _part_title(trailing.group(1))
        bracket = _bracket(trailing.group(2))
        if head and bracket:
            return head + bracket
    return None


def compose_part(text: str) -> str | None:
    """``Part B. Breadth studies`` in Chinese, or ``None`` if any piece is unknown."""
    match = _PART.match(text.strip())
    if not match:
        return None
    label, rest = match.group(1), match.group(2)
    if not rest:
        return None
    head = f"第 {label} 部分" if label.isdigit() else f"{label} 部分"
    two = _TWO_PARTS.match(rest)
    if two:
        first, second = _part_title(two.group(1)), _part_title(two.group(3))
        if first and second:
            return f"{head}。{first}与 {two.group(2)} 部分。{second}"
        return None
    title = _part_title(rest)
    return f"{head}。{title}" if title else None


def compose_level(text: str) -> str | None:
    """An AQF level label, or two of them joined by a slash."""
    parts = [part.strip().replace("’", "'") for part in text.split(" / ")]
    if all(part in _LEVELS for part in parts):
        return " / ".join(_LEVELS[part] for part in parts)
    return None


def compose_assessment(text: str) -> str | None:
    """``3000 words``, ``(3,000 words)`` and ``2 - Quiz / Test``."""
    text = text.strip()
    match = _WORDS.match(text)
    if match:
        return f"{match.group(1)} 字"
    match = _BRACKETED_WORDS.match(text)
    if match:
        return f"（{match.group(1).strip()} 字）"
    match = _NUMBERED.match(text)
    if match and match.group(2) in _ASSESSMENTS:
        return f"{match.group(1)} - {_ASSESSMENTS[match.group(2)]}"
    return None


def compose(text: str, locale: str) -> str | None:
    """The Chinese for a label whose shape is known, else ``None``."""
    if locale != "zh":
        return None
    for build in (compose_part, compose_level, compose_assessment):
        rendered = build(text)
        if rendered:
            return rendered
    return None
