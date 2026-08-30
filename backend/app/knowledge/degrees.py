"""Degree names, composed rather than translated.

A degree name is not a sentence and must not be handed to a translator as one.
English names it front-to-back — *Bachelor of Science* — and Chinese names it
back-to-front — 理学学士. A general model asked for the whole string has to both
translate and reorder, and measured over the 502 degrees actually in the
catalogue it reliably fails at one or the other:

    Bachelor of Science            学士            (the discipline vanished)
    Master of Teaching             师傅            (a master craftsman)
    Master of Accounting           大师会计        (a guru, then a noun)
    Master of Public Health        大师公共卫生
    Bachelor of Engineering        学士工程        (English order, Chinese words)
    Doctor of Podiatric Medicine   儿科医生        (podiatric read as paediatric)
    Bachelor of Speech Pathology   病理学演讲学士

These are the most-read strings on the site - every degree card, the planner's
picker, the heading of every degree page - so they are worth building instead of
guessing at.

The shape is regular, so it is taken apart rather than translated whole: an
award ("Bachelor"), a discipline ("Science"), and any number of trailing
parenthetical qualifiers ("(Honours)"). The award and the qualifiers come from
the tables below. The discipline is translated by whatever the caller passes -
the ordinary pipeline, glossary and all - because the discipline is the part a
translator is actually good at: 应用数据科学 for "Applied Data Science" needs no
help. Then the pieces are put back in Chinese order.

Anything whose shape is not that - a double degree joined by "and", a name with
a dash in it - returns ``None`` and is left to the ordinary path. Composing is
only allowed to improve on the existing answer, never to invent a new way of
being wrong.
"""
from __future__ import annotations

import re

LOCALES = ("zh", "ja", "ko")

# Whole Chinese titles that were checked against the 2026 Handbook catalogue.
#
# The ordinary composer below is deliberately conservative: it understands an
# award, a discipline and a small closed list of qualifiers.  Some official
# titles are not that shape, and some short disciplines are ambiguous enough
# that a general translator repeatedly chose the wrong sense (``retrieval`` as
# information retrieval, ``perfusion`` as transfusion, ``professional`` as a
# person).  Exact source strings are safer than teaching the general glossary a
# meaning that would be wrong in prose.  The seeder also publishes these as
# human-reviewed course-title string maps, so they take effect on deployment
# without waiting for another machine-translation batch.
ZH_TITLE_OVERRIDES: dict[str, str] = {
    # Malaysia undergraduate titles reported by readers.
    "Bachelor of Digital Media and Communication": "数字媒体与传播学士学位",
    "Bachelor of Actuarial Science and Master of Actuarial Studies":
        "精算学学士和精算学硕士",
    "Bachelor of Business and Commerce": "商业与贸易学士学位",
    "Bachelor of Business and Commerce (Honours)": "商业与贸易学士学位（荣誉）",
    "Bachelor of Business and Commerce and Bachelor of Computer Science":
        "商业学士和计算机科学学士",
    "Bachelor of Business and Commerce and Bachelor of Digital Media and Communication":
        "商业与贸易学士学位和数字媒体与传播学士学位",

    # Undergraduate names where a conjunction, modifier or subtitle was lost.
    "Bachelor of Arts and Social Sciences": "文学与社会科学学士",
    "Bachelor of Banking and Finance": "银行与金融学士",
    "Bachelor of Criminology and Policing": "犯罪学与警务学士",
    "Bachelor of Engineering (Honours) Dual Bachelors International":
        "工程学士（荣誉学位）国际双学位项目",
    "Bachelor of Food Science and Technology": "食品科学与技术学士",
    "Bachelor of Learning Design and Technology": "学习设计与技术学士",
    "Bachelor of Medical Science (Honours)": "医学科学学士（荣誉学位）",
    "Bachelor of Nutrition Science": "营养科学学士",
    "Bachelor of Politics, Philosophy and Economics": "政治、哲学与经济学学士",
    "Bachelor of Politics, Philosophy and Economics and Bachelor of Arts":
        "政治、哲学与经济学学士和文学学士",
    "Bachelor of Psychology and Business": "心理学与商业学士",
    "Bachelor of Radiography and Medical Imaging (Honours)":
        "放射学与医学影像学士（荣誉学位）",
    "Bachelor of Science Advanced - Global Challenges (Honours)":
        "高级理学学士（全球挑战）（荣誉学位）",
    "Bachelor of Science Advanced - Research (Honours)":
        "高级理学学士（研究）（荣誉学位）",

    # Diplomas, pathways and higher degrees with a misleading literal reading.
    "Diploma of Languages": "语言文凭",
    "Doctor of Science (Medical and Health Sciences)": "理学博士（医学与健康科学）",
    "Monash Access Program": "Monash 入学衔接课程",
    "Monash Advanced Preparation Program": "Monash 高级预科课程",
    "Monash Transition Program": "Monash 过渡课程",
    "Postgraduate Diploma in Business and Commerce": "商业与贸易研究生文凭",

    # Certificates and diplomas whose noun phrase was translated in the wrong sense.
    "Graduate Certificate of Advanced Pharmacy Practice": "高级药学实践研究生证书",
    "Professional Certificate of Advanced Pharmacy Practice": "高级药学实践专业证书",
    "Graduate Certificate of Aeromedical Retrieval": "航空医疗转运研究生证书",
    "Graduate Certificate of Corporate and Financial Regulation": "公司与金融监管研究生证书",
    "Graduate Certificate of Communications and Media Studies": "传播与媒体研究研究生证书",
    "Graduate Certificate of Employment Regulation": "雇佣关系监管研究生证书",
    "Graduate Certificate of Food Science and Agribusiness": "食品科学与农业商业研究生证书",
    "Graduate Certificate of Forensic Nursing and Midwifery": "法医护理与助产研究生证书",
    "Graduate Certificate of Health Administration": "卫生行政管理研究生证书",
    "Graduate Certificate of Health Professions Education": "卫生专业教育研究生证书",
    "Professional Certificate of Health Professions Education": "卫生专业教育专业证书",
    "Graduate Certificate of Innovation for Sustainability": "可持续发展创新研究生证书",
    "Graduate Certificate of Business Management": "商业管理研究生证书",
    "Graduate Certificate of Marketing and Digital Communications":
        "市场营销与数字传播研究生证书",
    "Graduate Certificate of Pharmacist Prescribing": "药师处方权研究生证书",
    "Graduate Certificate of Wound Care": "伤口护理研究生证书",
    "Graduate Certificate of X-ray Image Interpretation": "X 射线影像判读研究生证书",
    "Graduate Diploma of Occupational and Environmental Health": "职业与环境健康研究生文凭",
    "Graduate Diploma of Professional Psychology": "专业心理学研究生文凭",
    "Graduate Diploma of Wound Care": "伤口护理研究生文凭",
    "Professional Certificate of Specialised Health and Legal Interpreting":
        "专业医疗与法律口译专业证书",

    # Master's titles affected by the same recurring terminology errors.
    "Master of Actuarial Studies": "精算学硕士",
    "Master of Advanced Finance": "高级金融硕士",
    "Master of Applied Econometrics and Master of Advanced Finance":
        "应用计量经济学硕士和高级金融硕士",
    "Master of Advanced Health Care Practice": "高级医疗实践硕士",
    "Master of Arts Research Training": "文学研究训练硕士",
    "Master of Banking and Finance": "银行与金融硕士",
    "Master of Biomedical and Health Science": "生物医学与健康科学硕士",
    "Master of Business Information Systems": "商业信息系统硕士",
    "Master of Business Information Systems and Master of Global Business":
        "商业信息系统硕士和全球商业硕士",
    "Master of Business Information Systems and Master of Management":
        "商业信息系统硕士和管理学硕士",
    "Master of Business Management": "商业管理硕士",
    "Master of Business Management and Master of Human Resource Management":
        "商业管理硕士和人力资源管理硕士",
    "Master of Business Management and Master of Marketing and Digital Communications":
        "商业管理硕士和市场营销与数字传播硕士",
    "Master of Business Management and Master of Project Management":
        "商业管理硕士和项目管理硕士",
    "Master of Cardiovascular Perfusion": "心血管灌注硕士",
    "Master of Communications and Media Studies": "传播与媒体研究硕士",
    "Master of Critical Care Paramedicine": "重症监护辅助医疗硕士",
    "Master of Engineering Research (Monash - Southeast University)":
        "工程研究硕士（Monash－东南大学）",
    "Master of Environment and Sustainability": "环境与可持续发展硕士",
    "Master of Food Science and Agribusiness": "食品科学与农业商业硕士",
    "Master of Forensic Medicine": "法医学硕士",
    "Master of Geographical Information Science and Technology": "地理信息科学与技术硕士",
    "Master of Global Medicines Development": "全球药物研发硕士",
    "Master of Global Business and Master of Advanced Finance": "全球商业硕士和高级金融硕士",
    "Master of Global Business and Master of Marketing and Digital Communications":
        "全球商业硕士和市场营销与数字传播硕士",
    "Master of Health Administration": "卫生行政管理硕士",
    "Master of Health Professions Education": "卫生专业教育硕士",
    "Master of Indigenous Business Leadership": "原住民商业领导力硕士",
    "Master of Interpreting and Translation Studies": "口笔译研究硕士",
    "Master of Management and Master of Advanced Finance": "管理学硕士和高级金融硕士",
    "Master of Management and Master of Marketing and Digital Communications":
        "管理学硕士和市场营销与数字传播硕士",
    "Master of Marketing and Digital Communications": "市场营销与数字传播硕士",
    "Master of Marketing and Digital Communications and Master of Cultural and Creative Industries":
        "市场营销与数字传播硕士和文化与创意产业硕士",
    (
        "Master of Marketing and Digital Communications and Master of International "
        "Sustainable Tourism Management"
    ):
        "市场营销与数字传播硕士和国际可持续旅游管理硕士",
    "Master of Medical Ultrasound": "医学超声硕士",
    "Master of Nutrition and Dietetics": "营养与饮食学硕士",
    "Master of Occupational and Environmental Health": "职业与环境健康硕士",
    "Master of Professional Accounting": "专业会计硕士",
    "Master of Professional Counselling": "专业咨询硕士",
    "Master of Professional Engineering": "专业工程硕士",
    "Master of Professional Psychology": "专业心理学硕士",
    "Master of Transport and Mobility Planning": "交通与出行规划硕士",
    "Master of Transportation Systems": "交通系统硕士",
    "Master of Wound Care": "伤口护理硕士",

    # Partner names are proper nouns; the model invented 焦塘 and punctuation.
    "Master of International Relations (Double Masters with Shanghai Jiao Tong University)":
        "国际关系硕士（与上海交通大学合作双硕士）",
    (
        "Master of Strategic Communications Management "
        "(Double Masters with Shanghai Jiao Tong University)"
    ):
        "战略传播管理硕士（与上海交通大学合作双硕士）",
}

# The award, which in Chinese goes last. Longest first when matching, so
# "Graduate Certificate" is not read as "Certificate".
AWARDS: dict[str, dict[str, str]] = {
    "Executive Master": {"zh": "高级管理硕士", "ja": "エグゼクティブ修士", "ko": "경영자 석사"},
    "Postgraduate Certificate": {
        "zh": "研究生证书", "ja": "大学院サーティフィケート", "ko": "대학원 수료증",
    },
    "Professional Certificate": {
        "zh": "专业证书", "ja": "専門サーティフィケート", "ko": "전문 수료증",
    },
    "Graduate Certificate": {
        "zh": "研究生证书", "ja": "大学院サーティフィケート", "ko": "대학원 수료증",
    },
    "Graduate Diploma": {"zh": "研究生文凭", "ja": "大学院ディプロマ", "ko": "대학원 디플로마"},
    "Bachelor": {"zh": "学士", "ja": "学士", "ko": "학사"},
    "Master": {"zh": "硕士", "ja": "修士", "ko": "석사"},
    "Doctor": {"zh": "博士", "ja": "博士", "ko": "박사"},
    "Diploma": {"zh": "文凭", "ja": "ディプロマ", "ko": "디플로마"},
    "Certificate": {"zh": "证书", "ja": "サーティフィケート", "ko": "수료증"},
}

# Disciplines whose Chinese name is a convention rather than a translation, or
# which the model gets wrong. "Science" in a degree is 理学, not 科学; 药学 is
# what a pharmacy degree is called. Everything not listed here is translated by
# the caller, which handles the long tail well - the failures were concentrated
# in the award and the word order, not in the subject.
DISCIPLINES: dict[str, dict[str, str]] = {
    "Science": {"zh": "理学", "ja": "理学", "ko": "이학"},
    "Arts": {"zh": "文学", "ja": "文学", "ko": "문학"},
    "Commerce": {"zh": "商学", "ja": "商学", "ko": "상학"},
    "Business": {"zh": "商学", "ja": "経営学", "ko": "경영학"},
    "Laws": {"zh": "法学", "ja": "法学", "ko": "법학"},
    "Law": {"zh": "法学", "ja": "法学", "ko": "법학"},
    "Medicine": {"zh": "医学", "ja": "医学", "ko": "의학"},
    "Surgery": {"zh": "外科学", "ja": "外科学", "ko": "외과학"},
    "Philosophy": {"zh": "哲学", "ja": "哲学", "ko": "철학"},
    "Education": {"zh": "教育学", "ja": "教育学", "ko": "교육학"},
    "Teaching": {"zh": "教育", "ja": "教職", "ko": "교육"},
    "Engineering": {"zh": "工程", "ja": "工学", "ko": "공학"},
    "Accounting": {"zh": "会计学", "ja": "会計学", "ko": "회계학"},
    "Nursing": {"zh": "护理学", "ja": "看護学", "ko": "간호학"},
    "Psychology": {"zh": "心理学", "ja": "心理学", "ko": "심리학"},
    "Pharmacy": {"zh": "药学", "ja": "薬学", "ko": "약학"},
    "Pharmaceutical Science": {"zh": "药学", "ja": "薬科学", "ko": "약학"},
    "Physiotherapy": {"zh": "物理治疗", "ja": "理学療法", "ko": "물리치료"},
    "Occupational Therapy": {"zh": "职业治疗", "ja": "作業療法", "ko": "작업치료"},
    "Speech Pathology": {"zh": "言语病理学", "ja": "言語病理学", "ko": "언어병리학"},
    "Podiatric Medicine": {"zh": "足病医学", "ja": "足病医学", "ko": "족부의학"},
    "Paramedicine": {"zh": "院前急救医学", "ja": "救急救命学", "ko": "응급구조학"},
    "Health Sciences": {"zh": "健康科学", "ja": "健康科学", "ko": "보건과학"},
    "Health Science": {"zh": "健康科学", "ja": "健康科学", "ko": "보건과학"},
    "Public Health": {"zh": "公共卫生", "ja": "公衆衛生", "ko": "공중보건"},
    "Fine Art": {"zh": "美术", "ja": "美術", "ko": "미술"},
    "Music": {"zh": "音乐", "ja": "音楽", "ko": "음악"},
    "Design": {"zh": "设计", "ja": "デザイン", "ko": "디자인"},
    "Architecture": {"zh": "建筑学", "ja": "建築学", "ko": "건축학"},
    "Economics": {"zh": "经济学", "ja": "経済学", "ko": "경제학"},
    "Finance": {"zh": "金融学", "ja": "金融学", "ko": "금융학"},
    "Criminology": {"zh": "犯罪学", "ja": "犯罪学", "ko": "범죄학"},
    "Social Work": {"zh": "社会工作", "ja": "ソーシャルワーク", "ko": "사회복지"},
    "Actuarial Science": {"zh": "精算学", "ja": "保険数理学", "ko": "보험계리학"},
    "Addictive Behaviours": {"zh": "成瘾行为", "ja": "嗜癖行動", "ko": "중독 행동"},
    "Biomedical Science": {"zh": "生物医学", "ja": "生物医科学", "ko": "생물의학"},
    "Mathematics": {"zh": "数学", "ja": "数学", "ko": "수학"},
    "Biostatistics": {"zh": "生物统计学", "ja": "生物統計学", "ko": "생물통계학"},
    "Journalism": {"zh": "新闻学", "ja": "ジャーナリズム", "ko": "저널리즘"},
    "Management": {"zh": "管理学", "ja": "経営管理", "ko": "경영관리"},
    "Marketing": {"zh": "市场营销", "ja": "マーケティング", "ko": "마케팅"},
    "Architectural Studies": {"zh": "建筑学", "ja": "建築学", "ko": "건축학"},
    "Architectural Design": {"zh": "建筑设计", "ja": "建築デザイン", "ko": "건축디자인"},
    "Regulation and Compliance": {
        "zh": "监管与合规", "ja": "規制とコンプライアンス", "ko": "규제와 컴플라이언스",
    },
}

# Qualifiers that trail a degree name in brackets.
QUALIFIERS: dict[str, dict[str, str]] = {
    "Honours": {"zh": "荣誉学位", "ja": "オナーズ", "ko": "우등"},
    "Research": {"zh": "研究型", "ja": "研究型", "ko": "연구형"},
    "by Research": {"zh": "研究型", "ja": "研究型", "ko": "연구형"},
    "Digital": {"zh": "数字方向", "ja": "デジタル", "ko": "디지털"},
    "Executive": {"zh": "高级管理方向", "ja": "エグゼクティブ", "ko": "경영자 과정"},
    "Industry": {"zh": "产业方向", "ja": "産業", "ko": "산업"},
    "Practice-based": {"zh": "实践型", "ja": "実践型", "ko": "실무형"},
}

_AWARD_ALTERNATION = "|".join(
    re.escape(a) for a in sorted(AWARDS, key=lambda a: (-len(a), a))
)
# "<Award> of <Discipline>" or "<Award> in <Discipline>", then any brackets.
_SHAPE = re.compile(
    rf"^(?P<award>{_AWARD_ALTERNATION})\s+(?:of|in)\s+(?P<rest>.+)$",
    re.IGNORECASE,
)
_BRACKET = re.compile(r"\s*\(([^()]*)\)\s*$")

# A dash introduces a subtitle ("Science Advanced - Global Challenges") and a
# "with" introduces a partner arrangement. Neither is a shape this understands,
# and half-composing them would be worse than leaving them.
_TOO_COMPLEX = re.compile(r"\bwith\b|[-–—]|/")

# What joins the two halves of a double degree.
JOINERS = {"zh": "与", "ja": "および", "ko": " 및 "}


# A translator sometimes ends a fragment as though it were a sentence. Composing
# then puts the award after the full stop: "Architectural Studies" came back as
# 建筑研究。 and the degree read 建筑研究。学士.
_TRAILING_STOP = re.compile(r"[。．.，,、；;：:\s]+$")


def _tidy(rendered: str) -> str:
    return _TRAILING_STOP.sub("", rendered.strip())


def _lookup(table: dict[str, dict[str, str]], written: str, locale: str) -> str | None:
    for key, renderings in table.items():
        if key.lower() == written.strip().lower():
            return renderings.get(locale)
    return None


def compose(title: str, locale: str, translate) -> str | None:
    """The degree's name in ``locale``, or ``None`` to leave it to the caller.

    ``translate`` renders the discipline when it is not one of the conventional
    names above. It is called with English and must return the translation or
    ``None``; returning the English unchanged is treated as no translation, so a
    half-English name is never produced.
    """
    if locale not in LOCALES:
        return None
    title = title.strip()

    if locale == "zh" and title in ZH_TITLE_OVERRIDES:
        return ZH_TITLE_OVERRIDES[title]

    # A double degree is two names joined by "and", and each half composes on
    # its own. The split is only taken when both halves are themselves degree
    # names: "Bachelor of Arts and Social Sciences" is one degree whose subject
    # happens to contain the word, and splitting it would invent an award the
    # student cannot enrol in.
    halves = _as_double(title)
    if halves:
        rendered = [compose(half, locale, translate) for half in halves]
        if all(rendered):
            return JOINERS[locale].join(rendered)
        return None

    shape = _SHAPE.match(title)
    if not shape:
        return None

    rest = shape.group("rest").strip()

    # Peel the trailing brackets off, innermost last, so "(Honours)" and
    # "(Research)" both survive on the names that carry two.
    qualifiers: list[str] = []
    while True:
        bracket = _BRACKET.search(rest)
        if not bracket:
            break
        rendered = _lookup(QUALIFIERS, bracket.group(1), locale)
        if rendered is None:
            # An unknown qualifier - a partner university, a campus. Not worth
            # guessing at, and its presence means this name is not the simple
            # shape this function is for.
            return None
        qualifiers.insert(0, rendered)
        rest = rest[: bracket.start()].strip()

    if not rest or _TOO_COMPLEX.search(rest):
        return None

    award = _lookup(AWARDS, shape.group("award"), locale)
    if not award:
        return None

    discipline = _lookup(DISCIPLINES, rest, locale)
    if discipline is None:
        rendered = translate(rest)
        # No translation, or the model handed back the English: composing would
        # produce "Applied Data Science硕士". The whole name goes to the
        # ordinary path instead.
        if not rendered or rendered.strip() == rest:
            return None
        discipline = _tidy(rendered)
        if not discipline:
            return None

    composed = f"{discipline}{award}"
    for qualifier in qualifiers:
        composed += _bracket_for(locale, qualifier)
    return composed


def _as_double(title: str) -> list[str] | None:
    """The two halves of a double degree, or ``None`` if it is a single one.

    Split at one "and", not at every one. A subject can contain the word:
    *Master of Global Business and Master of Regulation and Compliance* is two
    degrees, the second of which is "Regulation and Compliance". Cutting at
    every "and" produced three fragments, none of which paired up, so the whole
    string fell through to the single-degree path and its subject - award word
    and all - went to the translator, which is how 大师 ended up in front of
    硕士.

    The first cut where both sides are themselves degree names wins. The right
    half is composed recursively, so a genuine triple degree still comes apart.
    """
    for cut in re.finditer(r"\s+and\s+", title):
        left, right = title[: cut.start()].strip(), title[cut.end() :].strip()
        if left and right and _SHAPE.match(left) and _SHAPE.match(right):
            return [left, right]
    return None


def _bracket_for(locale: str, inner: str) -> str:
    return f"（{inner}）" if locale in ("zh", "ja") else f"({inner})"
