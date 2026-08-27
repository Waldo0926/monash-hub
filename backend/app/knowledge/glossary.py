"""The terms a translation is not allowed to get wrong.

Free machine translation is good enough for the shape of a sentence and bad
exactly where this product cannot afford it. Measured on the real pages: it
renders *census date* as 人口普查日期 (a population census), *unit* as 单位,
*credit points* as 信用点, *hurdle* as 阈值障碍, and *Programming paradigms* as
方案拟订模式. Those are the words a student acts on - the ones that cost money or
a semester when they are wrong.

So the terms below never reach the translator. Each occurrence is swapped for an
opaque placeholder first, the sentence is translated around it, and the agreed
wording is put back afterwards. What the machine contributes is grammar; what
the term means is decided here.

Placeholders are letters, not digits: ``Zqa``, ``Zqb``, … Digits get rewritten
by the model (``XX1XX`` came back as ``X22XX``), letter tokens survive intact.

Adding a term
-------------
Put it in ``TERMS`` with a translation for every locale, longest form first -
matching is longest-first, so "weighted average mark" wins over "mark". Keep the
English in brackets after the Chinese for anything a student will also meet in
English on an official page: they have to be able to match the two up.
"""
from __future__ import annotations

import re

LOCALES = ("zh", "ja", "ko")

# English term -> {locale: translation}
#
# Ordered roughly by how much damage a wrong rendering does, not alphabetically,
# because the top of this list is what a reviewer should read first.
TERMS: dict[str, dict[str, str]] = {
    # --- deadlines and money -------------------------------------------------
    "census date": {
        # English first, matching translations_seed.py: this is a term the
        # student will meet in English on every official page and in WES, and
        # the two have to be matchable.
        "zh": "census date（学籍统计日）",
        "ja": "履修取消期限（census date）",
        "ko": "수강 철회 마감일(census date)",
    },
    "census dates": {
        "zh": "census dates（学籍统计日）",
        "ja": "履修取消期限（census dates）",
        "ko": "수강 철회 마감일(census dates)",
    },
    "withdraw": {
        "zh": "退选",
        "ja": "履修取消する",
        "ko": "철회하다",
    },
    "withdrawal": {
        "zh": "退选",
        "ja": "履修取消",
        "ko": "철회",
    },
    "discontinue": {
        "zh": "退课",
        "ja": "履修を取りやめる",
        "ko": "수강 중단",
    },
    "intermission": {
        "zh": "休学（intermission）",
        "ja": "休学（intermission）",
        "ko": "휴학(intermission)",
    },
    "tuition fees": {
        "zh": "学费",
        "ja": "授業料",
        "ko": "학비",
    },
    "fee liability": {
        "zh": "学费责任",
        "ja": "授業料の支払い義務",
        "ko": "학비 납부 의무",
    },
    "HECS-HELP": {
        "zh": "HECS-HELP 贷款",
        "ja": "HECS-HELP ローン",
        "ko": "HECS-HELP 대출",
    },
    "FEE-HELP": {
        "zh": "FEE-HELP 贷款",
        "ja": "FEE-HELP ローン",
        "ko": "FEE-HELP 대출",
    },
    "Commonwealth supported place": {
        "zh": "联邦资助学额（CSP）",
        "ja": "連邦政府支援枠（CSP）",
        "ko": "연방 지원 정원(CSP)",
    },

    # --- marks and progression ----------------------------------------------
    "weighted average mark": {
        "zh": "加权平均分（WAM）",
        "ja": "加重平均点（WAM）",
        "ko": "가중 평균 점수(WAM)",
    },
    "WAM": {
        "zh": "WAM（加权平均分）",
        "ja": "WAM（加重平均点）",
        "ko": "WAM(가중 평균 점수)",
    },
    "grade point average": {
        "zh": "平均绩点（GPA）",
        "ja": "成績評価平均（GPA）",
        "ko": "평균 평점(GPA)",
    },
    "GPA": {
        "zh": "GPA（平均绩点）",
        "ja": "GPA（成績評価平均）",
        "ko": "GPA(평균 평점)",
    },
    "hurdle requirement": {
        "zh": "及格门槛要求",
        "ja": "必須到達要件",
        "ko": "필수 통과 요건",
    },
    "hurdle": {
        "zh": "及格门槛",
        "ja": "必須到達要件",
        "ko": "필수 통과 요건",
    },
    "pass mark": {
        "zh": "及格分数",
        "ja": "合格点",
        "ko": "합격 점수",
    },
    "marks": {
        "zh": "分数",
        "ja": "点数",
        "ko": "점수",
    },
    "mark": {
        "zh": "分数",
        "ja": "点数",
        "ko": "점수",
    },
    "grades": {
        "zh": "成绩等级",
        "ja": "成績評価",
        "ko": "성적 등급",
    },
    "grade": {
        "zh": "成绩等级",
        "ja": "成績評価",
        "ko": "성적 등급",
    },
    "results": {
        "zh": "成绩",
        "ja": "成績",
        "ko": "성적",
    },
    "academic progress": {
        "zh": "学业进度审查",
        "ja": "学業進捗審査",
        "ko": "학업 진도 심사",
    },
    "unsatisfactory progress": {
        "zh": "学业进度不达标", "ja": "学業進捗不良", "ko": "학업 진도 미달",
    },
    "exclusion": {
        "zh": "退学处理（exclusion）",
        "ja": "除籍（exclusion）",
        "ko": "제적(exclusion)",
    },
    "academic integrity": {
        "zh": "学术诚信",
        "ja": "学術的誠実性",
        "ko": "학문적 진실성",
    },
    "plagiarism": {
        "zh": "抄袭",
        "ja": "剽窃",
        "ko": "표절",
    },
    "collusion": {
        "zh": "合谋作弊",
        "ja": "共謀不正",
        "ko": "공모 부정행위",
    },

    # --- assessment ----------------------------------------------------------
    "special consideration": {
        "zh": "特殊考虑（special consideration）",
        "ja": "特別配慮（special consideration）",
        "ko": "특별 고려(special consideration)",
    },
    "deferred assessment": {
        "zh": "延期考核",
        "ja": "追試",
        "ko": "추후 평가",
    },
    "supplementary assessment": {
        "zh": "补考",
        "ja": "再評価",
        "ko": "보충 평가",
    },
    "final assessment": {
        "zh": "期末考核",
        "ja": "期末評価",
        "ko": "기말 평가",
    },
    "assessment task": {
        "zh": "考核任务",
        "ja": "評価課題",
        "ko": "평가 과제",
    },
    "assessment": {
        "zh": "考核",
        "ja": "評価",
        "ko": "평가",
    },
    "examination": {
        "zh": "考试",
        "ja": "試験",
        "ko": "시험",
    },
    "eExam": {
        "zh": "电子考试（eExam）",
        "ja": "eExam（電子試験）",
        "ko": "eExam(전자 시험)",
    },
    "quiz": {
        "zh": "小测",
        "ja": "小テスト",
        "ko": "퀴즈",
    },
    # Terms the model reached for an anatomy textbook to render. "in-semester
    # assessments" - the plural, which was not here - came back as 子宫内评估,
    # an intrauterine assessment, on the paragraph that says what it takes to
    # pass; "ductile versus brittle" as 阴道与刚性; "a cover letter" as 封面信,
    # a letter about a book jacket.
    "in-semester assessments": {
        "zh": "学期内考核", "ja": "学期中の評価", "ko": "학기 중 평가",
    },
    "in-semester": {"zh": "学期内", "ja": "学期中", "ko": "학기 중"},
    "cover letter": {"zh": "求职信", "ja": "カバーレター", "ko": "자기소개서"},
    "ductile": {"zh": "韧性", "ja": "延性", "ko": "연성"},
    "brittle": {"zh": "脆性", "ja": "脆性", "ko": "취성"},
    "threshold mark hurdles": {
        "zh": "及格门槛分数要求", "ja": "最低到達点の要件", "ko": "최저 통과 점수 요건",
    },
    "threshold mark": {"zh": "及格门槛分数", "ja": "最低到達点", "ko": "최저 통과 점수"},
    "fail grade": {"zh": "不及格成绩", "ja": "不合格の成績", "ko": "불합격 성적"},

    # The field names a Handbook entry is most likely to use, and the ones a
    # general translator renders as ordinary words: "Deep learning" is a unit
    # title and came back as 深入学习, studying something in depth.
    "deep learning": {"zh": "深度学习", "ja": "深層学習", "ko": "딥러닝"},
    "reinforcement learning": {"zh": "强化学习", "ja": "強化学習", "ko": "강화학습"},
    "supervised learning": {"zh": "监督学习", "ja": "教師あり学習", "ko": "지도학습"},
    "unsupervised learning": {"zh": "无监督学习", "ja": "教師なし学習", "ko": "비지도학습"},
    "neural networks": {"zh": "神经网络", "ja": "ニューラルネットワーク", "ko": "신경망"},
    "neural network": {"zh": "神经网络", "ja": "ニューラルネットワーク", "ko": "신경망"},
    "natural language processing": {
        "zh": "自然语言处理", "ja": "自然言語処理", "ko": "자연어 처리",
    },
    "computer vision": {"zh": "计算机视觉", "ja": "コンピュータビジョン", "ko": "컴퓨터 비전"},
    "data science": {"zh": "数据科学", "ja": "データサイエンス", "ko": "데이터 사이언스"},
    "in-semester assessment": {
        "zh": "学期内考核",
        "ja": "学期中の評価",
        "ko": "학기 중 평가",
    },
    "extension": {
        "zh": "延期",
        "ja": "提出期限延長",
        "ko": "제출 기한 연장",
    },

    # --- Handbook structure --------------------------------------------------
    "credit points": {
        "zh": "学分",
        "ja": "単位数",
        "ko": "학점",
    },
    "credit point": {
        "zh": "学分",
        "ja": "単位数",
        "ko": "학점",
    },
    # *Credit* is three different words here and only one of them is banking.
    # A bare "credit" is left out on purpose: on the finance units - credit
    # risk, credit scoring, consumer credit - 信贷 is right, and pinning the
    # word would break them. What is pinned is the phrases where it is not:
    # the exchange boilerplate that says 189 times over that fees and credit
    # are handled accurately, and the grade that sits between a pass and a
    # distinction.
    "fees and credit": {
        "zh": "学费与学分", "ja": "授業料と単位", "ko": "학비와 학점",
    },
    "academic credit": {
        "zh": "学分减免", "ja": "単位認定", "ko": "학점 인정",
    },
    "credit for prior learning": {
        "zh": "既往学习的学分减免", "ja": "既修学習の単位認定", "ko": "기존 학습 학점 인정",
    },
    "Pass with Credit": {
        "zh": "Pass with Credit（良好通过）",
        "ja": "Pass with Credit（良）",
        "ko": "Pass with Credit(양호)",
    },
    "High distinction": {
        "zh": "High distinction（最高优等）",
        "ja": "High distinction（最優秀）",
        "ko": "High distinction(최우수)",
    },
    "Distinction": {
        "zh": "Distinction（优等）",
        "ja": "Distinction（優）",
        "ko": "Distinction(우수)",
    },
    "credit card": {"zh": "信用卡", "ja": "クレジットカード", "ko": "신용카드"},
    "debit card": {"zh": "借记卡", "ja": "デビットカード", "ko": "체크카드"},
    "credit transfer": {
        "zh": "学分减免",
        "ja": "単位認定",
        "ko": "학점 인정",
    },
    "prerequisites": {
        "zh": "先修课程",
        "ja": "履修前提科目",
        "ko": "선수 과목",
    },
    "prerequisite": {
        "zh": "先修课程",
        "ja": "履修前提科目",
        "ko": "선수 과목",
    },
    "corequisite": {
        "zh": "同修课程",
        "ja": "同時履修科目",
        "ko": "동시 수강 과목",
    },
    "co-requisites": {
        "zh": "同修课程",
        "ja": "同時履修科目",
        "ko": "동시 수강 과목",
    },
    "co-requisite": {
        "zh": "同修课程",
        "ja": "同時履修科目",
        "ko": "동시 수강 과목",
    },
    "corequisites": {
        "zh": "同修课程",
        "ja": "同時履修科目",
        "ko": "동시 수강 과목",
    },
    "prohibition": {
        "zh": "互斥课程",
        "ja": "履修不可科目",
        "ko": "중복 수강 불가 과목",
    },
    "prohibitions": {
        "zh": "互斥课程",
        "ja": "履修不可科目",
        "ko": "중복 수강 불가 과목",
    },
    "enrolment rules": {
        "zh": "选课规则",
        "ja": "履修規則",
        "ko": "수강 규정",
    },
    "teaching period": {
        "zh": "开课学期",
        "ja": "開講期",
        "ko": "개설 학기",
    },
    "teaching periods": {
        "zh": "开课学期",
        "ja": "開講期",
        "ko": "개설 학기",
    },
    "offering": {
        "zh": "开课信息",
        "ja": "開講情報",
        "ko": "개설 정보",
    },
    "offerings": {
        "zh": "开课信息",
        "ja": "開講情報",
        "ko": "개설 정보",
    },
    "attendance mode": {
        "zh": "授课方式",
        "ja": "受講形態",
        "ko": "수업 방식",
    },
    "workload requirements": {
        "zh": "工作量要求",
        "ja": "学習時間の目安",
        "ko": "학습량 요건",
    },
    "workload": {
        "zh": "工作量",
        "ja": "学習時間",
        "ko": "학습량",
    },
    "learning outcomes": {
        "zh": "学习成果",
        "ja": "学習成果",
        "ko": "학습 성과",
    },
    "learning outcome": {
        "zh": "学习成果",
        "ja": "学習成果",
        "ko": "학습 성과",
    },
    "chief examiner": {
        "zh": "课程负责人",
        "ja": "科目責任者",
        "ko": "과목 책임자",
    },
    "handbook": {
        "zh": "Handbook",
        "ja": "Handbook",
        "ko": "Handbook",
    },
    "unit code": {
        "zh": "课程代码",
        "ja": "科目コード",
        "ko": "과목 코드",
    },
    "units": {
        "zh": "课程",
        "ja": "科目",
        "ko": "과목",
    },
    "unit": {
        "zh": "课程",
        "ja": "科目",
        "ko": "과목",
    },
    "course": {
        "zh": "学位课程",
        "ja": "コース（学位課程）",
        "ko": "학위 과정",
    },
    "courses": {
        "zh": "学位课程",
        "ja": "コース（学位課程）",
        "ko": "학위 과정",
    },
    "elective": {
        "zh": "选修课",
        "ja": "選択科目",
        "ko": "선택 과목",
    },
    "core unit": {
        "zh": "必修课程",
        "ja": "必修科目",
        "ko": "필수 과목",
    },
    "specialisation": {
        "zh": "专业方向",
        "ja": "専攻分野",
        "ko": "전공 분야",
    },
    "area of study": {
        "zh": "学习方向",
        "ja": "学習領域",
        "ko": "학습 영역",
    },
    "areas of study": {
        "zh": "学习方向",
        "ja": "学習領域",
        "ko": "학습 영역",
    },

    # --- enrolment and admin -------------------------------------------------
    "enrolment": {
        "zh": "选课注册",
        "ja": "履修登録",
        "ko": "수강 신청",
    },
    "enrol": {
        "zh": "选课注册",
        "ja": "履修登録する",
        "ko": "수강 신청하다",
    },
    # Longer first, or the hyphen lets *enrolment* match inside *Re-enrolment*
    # and WES's own menu came out as 选课注册/Re-选课注册.
    "re-enrolment": {
        "zh": "重新注册",
        "ja": "再履修登録",
        "ko": "재등록",
    },
    "re-enrol": {
        "zh": "重新注册",
        "ja": "再履修登録",
        "ko": "재등록",
    },
    "cross-institutional study": {
        "zh": "跨校修读", "ja": "他大学での履修", "ko": "타 대학 수강",
    },
    "academic transcript": {
        "zh": "成绩单",
        "ja": "成績証明書",
        "ko": "성적 증명서",
    },
    "transcript": {
        "zh": "成绩单",
        "ja": "成績証明書",
        "ko": "성적 증명서",
    },
    "graduation": {
        "zh": "毕业",
        "ja": "卒業",
        "ko": "졸업",
    },
    "timetable": {
        "zh": "课表",
        "ja": "時間割",
        "ko": "시간표",
    },
    "Allocate+": {
        "zh": "Allocate+（选课系统）",
        "ja": "Allocate+（時間割システム）",
        "ko": "Allocate+(수강 시스템)",
    },
    "WES": {
        "zh": "WES（学生系统）",
        "ja": "WES（学生システム）",
        "ko": "WES(학생 시스템)",
    },
    "Moodle": {
        "zh": "Moodle",
        "ja": "Moodle",
        "ko": "Moodle",
    },
    # Monash's own name for where the rules live. Left to itself the model
    # reads "bank" as the financial kind and renders it 政策银行.
    "policy bank": {
        "zh": "政策库（policy bank）",
        "ja": "ポリシーバンク（policy bank）",
        "ko": "정책 모음(policy bank)",
    },
    "policies and procedures": {
        "zh": "政策与流程",
        "ja": "ポリシーと手続き",
        "ko": "정책 및 절차",
    },

    # --- international students ---------------------------------------------
    "student visa": {
        "zh": "学生签证",
        "ja": "学生ビザ",
        "ko": "학생 비자",
    },
    "Confirmation of Enrolment": {
        "zh": "入学确认书（CoE）", "ja": "在学証明（CoE）", "ko": "입학 확인서(CoE)",
    },
    "CoE": {
        "zh": "CoE（入学确认书）",
        "ja": "CoE（在学証明）",
        "ko": "CoE(입학 확인서)",
    },
    "Overseas Student Health Cover": {
        "zh": "留学生医疗保险（OSHC）",
        "ja": "留学生健康保険（OSHC）",
        "ko": "유학생 의료보험(OSHC)",
    },
    "OSHC": {
        "zh": "OSHC（留学生医疗保险）",
        "ja": "OSHC（留学生健康保険）",
        "ko": "OSHC(유학생 의료보험)",
    },
    "full-time study load": {
        "zh": "全日制学习负荷",
        "ja": "フルタイムの履修量",
        "ko": "전일제 수강 부담",
    },

    # --- Monash Malaysia -----------------------------------------------------
    #
    # Malaysia's own vocabulary for the right to stay, which is not Australia's.
    # A student pass is issued by the Immigration Department through EMGS and
    # arrives as an eVAL; none of those words appear on the Australian pages,
    # and "student visa" does not appear on the Malaysian ones. Each keeps its
    # English, because it is what is written on the document the student holds
    # and on the portal they have to log into.
    "Electronic Visa Approval Letter": {
        "zh": "电子签证批准函（eVAL）",
        "ja": "電子ビザ承認レター（eVAL）",
        "ko": "전자 비자 승인서(eVAL)",
    },
    "student pass": {"zh": "学生准证（student pass）", "ja": "学生パス（student pass）",
                     "ko": "학생 패스(student pass)"},
    "Student Pass": {"zh": "学生准证（Student Pass）", "ja": "学生パス（Student Pass）",
                     "ko": "학생 패스(Student Pass)"},
    "Special Pass": {"zh": "特别准证（Special Pass）", "ja": "特別パス（Special Pass）",
                     "ko": "특별 패스(Special Pass)"},
    "Immigration Department of Malaysia": {
        "zh": "马来西亚移民局", "ja": "マレーシア移民局", "ko": "말레이시아 이민국",
    },
    "EMGS": {"zh": "EMGS", "ja": "EMGS", "ko": "EMGS"},
    "eVAL": {"zh": "eVAL", "ja": "eVAL", "ko": "eVAL"},
    "MPass": {"zh": "MPass", "ja": "MPass", "ko": "MPass"},
    "Release Letter": {"zh": "放行信（Release Letter）", "ja": "リリースレター（Release Letter）",
                       "ko": "릴리스 레터(Release Letter)"},
    "medical screening": {"zh": "体检", "ja": "健康診断", "ko": "건강검진"},

    # The OSHC page is about the insurance a student visa is conditional on,
    # and unaided it was the worst page on the site. The insurer's name was
    # transliterated three different ways and none of them is a company a
    # student can find: "Allianz Care Australia Policy Wording Documents"
    # came back as 澳大利亚爱护组织 (an Australian caring organisation) and
    # "Once you've purchased your Allianz Care Australia OSHC policy" as
    # 澳洲爱心 (Australian loving heart). The name is kept, like Monash's own.
    "Allianz Care Australia": {
        "zh": "Allianz Care Australia", "ja": "Allianz Care Australia",
        "ko": "Allianz Care Australia",
    },
    "Allianz Care": {
        "zh": "Allianz Care", "ja": "Allianz Care", "ko": "Allianz Care",
    },
    # An insurance *policy* is a 保单, not a 政策 - the model chose the
    # government kind on every occurrence, on the page that tells a student
    # what their cover pays for. Longest form first, as always.
    "policy wording": {
        "zh": "保单条款", "ja": "保険約款", "ko": "보험 약관",
    },
    "OSHC policy": {
        "zh": "OSHC（留学生医疗保险）保单",
        "ja": "OSHC（留学生健康保険）の保険",
        "ko": "OSHC(유학생 의료보험) 보험",
    },
    "extras policy": {
        "zh": "附加保障保单", "ja": "追加保障の保険", "ko": "부가 보장 보험",
    },
    "health cover": {
        "zh": "医疗保险保障", "ja": "医療保険", "ko": "의료보험 보장",
    },
    "your cover": {
        # "get the most from your cover" came back as 你的封面 - a book cover.
        "zh": "你的保险保障", "ja": "あなたの保障", "ko": "보장 내용",
    },
    # The extras a policy does not pay for, and the model's readings of them:
    # *chiropractic* became 脊髓灰质炎 (poliomyelitis), *osteopathy* 骨病 (bone
    # disease) and *optical* 光学 (the physics).
    "chiropractic": {
        "zh": "脊椎按摩治疗", "ja": "カイロプラクティック", "ko": "척추 교정 치료",
    },
    "osteopathy": {
        "zh": "整骨治疗", "ja": "オステオパシー", "ko": "정골 치료",
    },
    "optical": {
        "zh": "验光配镜", "ja": "眼鏡・検眼", "ko": "안경·검안",
    },
    "international student": {
        "zh": "国际学生",
        "ja": "留学生",
        "ko": "유학생",
    },
    "domestic student": {
        "zh": "本地学生",
        "ja": "国内学生",
        "ko": "자국 학생",
    },

    # A degree is *by coursework* or *by research*, and the pair decides which
    # rules a student is under. "a coursework student at Monash University"
    # came back as 教职员工 - a member of staff.
    "coursework students": {
        "zh": "授课型学生",
        "ja": "コースワークの学生",
        "ko": "코스워크 학생",
    },
    "coursework student": {
        "zh": "授课型学生",
        "ja": "コースワークの学生",
        "ko": "코스워크 학생",
    },
    "by coursework": {
        "zh": "授课型",
        "ja": "コースワーク型",
        "ko": "코스워크형",
    },
    "by research": {
        "zh": "研究型",
        "ja": "研究型",
        "ko": "연구형",
    },

    # --- what a student does at a desk ---------------------------------------
    # All four came off the key dates page, where the model had a label and no
    # sentence to read it in: *course transfer* became 学位课程转账 (a bank
    # transfer), *change of preference* became 更改优惠 (a change of discount),
    # *faculty* became 教职员工 (the teaching staff) and "How to apply" became
    # 如何适用 (how it is applicable).
    "course transfers": {
        "zh": "转学位课程",
        "ja": "コース変更",
        "ko": "학위 과정 변경",
    },
    "course transfer": {
        "zh": "转学位课程",
        "ja": "コース変更",
        "ko": "학위 과정 변경",
    },
    "change of preference": {
        "zh": "更改志愿",
        "ja": "志望変更",
        "ko": "지망 변경",
    },
    "How to apply": {
        "zh": "如何申请",
        "ja": "申請方法",
        "ko": "신청 방법",
    },
    "faculties": {
        "zh": "学院",
        "ja": "学部",
        "ko": "단과대학",
    },
    "faculty": {
        "zh": "学院",
        "ja": "学部",
        "ko": "단과대학",
    },

    # --- the university's own names ------------------------------------------
    # Left to itself the model reads "Monash" as *money*. Monash Abroad, the
    # office a student goes to about exchange, was published as 国外货币
    # (foreign currency) and the unit code MON1001 as 货币1001. Where it does
    # not do that it transliterates - 莫纳什 - which no reviewed translation on
    # this site has ever used and which cannot be matched against the address
    # on the student's own email. So the name is kept and the bracket says what
    # it is, the way census date and WES already do: a student has to be able
    # to match what they read here against the office they walk into. "Monash"
    # on its own is left alone - a gloss on every occurrence would be noise.
    "Monash Abroad": {
        "zh": "Monash Abroad（海外学习与交换）",
        "ja": "Monash Abroad（海外留学・交換留学）",
        "ko": "Monash Abroad(해외 유학·교환)",
    },
    "Monash Connect": {
        "zh": "Monash Connect（学生服务中心）",
        "ja": "Monash Connect（学生サービス窓口）",
        "ko": "Monash Connect(학생 서비스 센터)",
    },
    "Monash College": {
        "zh": "Monash College（预科学院）",
        "ja": "Monash College（進学準備カレッジ）",
        "ko": "Monash College(예비 과정 칼리지)",
    },
    "Monash Online": {
        "zh": "Monash Online（在线）",
        "ja": "Monash Online（オンライン）",
        "ko": "Monash Online(온라인)",
    },
    "Monash Health": {
        "zh": "Monash Health（医疗服务机构）",
        "ja": "Monash Health（医療機関）",
        "ko": "Monash Health(의료 기관)",
    },
    "Monash Indonesia": {
        "zh": "Monash Indonesia（印尼校区）",
        "ja": "Monash Indonesia（インドネシアキャンパス）",
        "ko": "Monash Indonesia(인도네시아 캠퍼스)",
    },
    "Monash Malaysia": {
        "zh": "Monash Malaysia（马来西亚校区）",
        "ja": "Monash Malaysia（マレーシアキャンパス）",
        "ko": "Monash Malaysia(말레이시아 캠퍼스)",
    },
    "Monash Prato": {
        "zh": "Monash Prato（意大利普拉托校区）",
        "ja": "Monash Prato（イタリア・プラートキャンパス）",
        "ko": "Monash Prato(이탈리아 프라토 캠퍼스)",
    },
    "Monash": {
        "zh": "Monash",
        "ja": "Monash",
        "ko": "Monash",
    },
    "Monash University": {
        "zh": "Monash 大学",
        "ja": "Monash 大学",
        "ko": "Monash 대학교",
    },

    # --- the faculties -------------------------------------------------------
    # Table labels on the dates pages, where the model has a name and no
    # sentence to put it in: "Faculty of Law" came back as 法学院： with the
    # colon copied off "School of", and "Faculty of Information Technology"
    # was split down the middle into 学院：信息技术.
    "Faculty of Art, Design and Architecture": {
        "zh": "艺术、设计与建筑学院",
        "ja": "芸術・デザイン・建築学部",
        "ko": "예술·디자인·건축대학",
    },
    "Faculty of Medicine, Nursing and Health Sciences": {
        "zh": "医学、护理与健康科学学院",
        "ja": "医学・看護・健康科学部",
        "ko": "의학·간호·보건과학대학",
    },
    "Faculty of Pharmacy and Pharmaceutical Sciences": {
        "zh": "药学与制药科学学院",
        "ja": "薬学・薬科学部",
        "ko": "약학·제약과학대학",
    },
    "Faculty of Information Technology": {
        "zh": "信息技术学院",
        "ja": "情報技術学部",
        "ko": "정보기술대학",
    },
    "Faculty of Business and Economics": {
        "zh": "商学与经济学院",
        "ja": "ビジネス・経済学部",
        "ko": "경영·경제대학",
    },
    "Faculty of Engineering": {
        "zh": "工程学院",
        "ja": "工学部",
        "ko": "공과대학",
    },
    "Faculty of Education": {
        "zh": "教育学院",
        "ja": "教育学部",
        "ko": "교육대학",
    },
    "Faculty of Science": {
        "zh": "理学院",
        "ja": "理学部",
        "ko": "이과대학",
    },
    "Faculty of Arts": {
        "zh": "文学院",
        "ja": "文学部",
        "ko": "인문대학",
    },
    "Faculty of Law": {
        "zh": "法学院",
        "ja": "法学部",
        "ko": "법과대학",
    },
    "Faculty of IT": {
        "zh": "信息技术学院（IT）",
        "ja": "情報技術学部（IT）",
        "ko": "정보기술대학(IT)",
    },

    # --- the period a date belongs to ----------------------------------------
    # The same periods ENUMS pins as whole field values, pinned again as
    # substrings: on the dates pages they arrive inside a label - "Trimester 1
    # (Faculty of Law units only)" - and the model, with nothing else to go
    # on, read Trimester 1 as 三月一日 (the first of March) and Semester 2 as
    # 学士2 (a bachelor's degree).
    "Semester 1": {
        "zh": "第一学期",
        "ja": "第1学期",
        "ko": "1학기",
    },
    "Semester 2": {
        "zh": "第二学期",
        "ja": "第2学期",
        "ko": "2학기",
    },
    "semester one": {
        "zh": "第一学期",
        "ja": "第1学期",
        "ko": "1학기",
    },
    "semester two": {
        "zh": "第二学期",
        "ja": "第2学期",
        "ko": "2학기",
    },
    "Trimester 1": {
        "zh": "第 1 学段",
        "ja": "第1トライメスター",
        "ko": "1트라이메스터",
    },
    "Trimester 2": {
        "zh": "第 2 学段",
        "ja": "第2トライメスター",
        "ko": "2트라이메스터",
    },
    "Trimester 3": {
        "zh": "第 3 学段",
        "ja": "第3トライメスター",
        "ko": "3트라이메스터",
    },
    "Term 1": {
        "zh": "第 1 学季",
        "ja": "第1ターム",
        "ko": "1학기(term)",
    },
    "Term 2": {
        "zh": "第 2 学季",
        "ja": "第2ターム",
        "ko": "2학기(term)",
    },
    "Term 3": {
        "zh": "第 3 学季",
        "ja": "第3ターム",
        "ko": "3학기(term)",
    },
    "Term 4": {
        "zh": "第 4 学季",
        "ja": "第4ターム",
        "ko": "4학기(term)",
    },
    "Teaching period 1": {
        "zh": "教学期 1",
        "ja": "開講期 1",
        "ko": "학기 1",
    },
    "Teaching period 2": {
        "zh": "教学期 2",
        "ja": "開講期 2",
        "ko": "학기 2",
    },
    "Teaching period 3": {
        "zh": "教学期 3",
        "ja": "開講期 3",
        "ko": "학기 3",
    },
    "Teaching period 4": {
        "zh": "教学期 4",
        "ja": "開講期 4",
        "ko": "학기 4",
    },
    "Teaching period 5": {
        "zh": "教学期 5",
        "ja": "開講期 5",
        "ko": "학기 5",
    },
    "Teaching period 6": {
        "zh": "教学期 6",
        "ja": "開講期 6",
        "ko": "학기 6",
    },

    # --- campuses and periods (enumerable, so pin them exactly) --------------
    "Clayton": {
        "zh": "Clayton 校区",
        "ja": "Clayton キャンパス",
        "ko": "Clayton 캠퍼스",
    },
    "Caulfield": {
        "zh": "Caulfield 校区",
        "ja": "Caulfield キャンパス",
        "ko": "Caulfield 캠퍼스",
    },
    "Peninsula": {
        "zh": "Peninsula 校区",
        "ja": "Peninsula キャンパス",
        "ko": "Peninsula 캠퍼스",
    },
    "Parkville": {
        "zh": "Parkville 校区",
        "ja": "Parkville キャンパス",
        "ko": "Parkville 캠퍼스",
    },
    "Malaysia": {
        "zh": "马来西亚校区",
        "ja": "マレーシアキャンパス",
        "ko": "말레이시아 캠퍼스",
    },
    "Suzhou": {
        "zh": "苏州校区",
        "ja": "蘇州キャンパス",
        "ko": "쑤저우 캠퍼스",
    },
    "First semester": {
        "zh": "第一学期",
        "ja": "第1学期",
        "ko": "1학기",
    },
    "Second semester": {
        "zh": "第二学期",
        "ja": "第2学期",
        "ko": "2학기",
    },
    "Full year": {
        "zh": "全学年",
        "ja": "通年",
        "ko": "연간",
    },
    # The dates pages name teaching periods in forms the Handbook does not use -
    # lower case, hyphenated, or an intake month - and a period name left in
    # English on the page that says when withdrawing stops being free is the one
    # word the reader needed.
    "and associated teaching periods": {"zh": "及相关开课学期", "ja": "および関連する教育期間",
                                        "ko": "및 관련 교육 기간"},
    "Faculty of Law units only": {"zh": "仅限法学院课程", "ja": "法学部ユニットのみ",
                                  "ko": "법학부 과목만"},
    "Except Faculty of Law units": {"zh": "法学院课程除外", "ja": "法学部ユニットを除く",
                                    "ko": "법학부 과목 제외"},
    "Except JD Law units": {"zh": "JD 法学课程除外", "ja": "JD法学ユニットを除く",
                            "ko": "JD 법학 과목 제외"},
    "JD Law units only": {"zh": "仅限 JD 法学课程", "ja": "JD法学ユニットのみ",
                          "ko": "JD 법학 과목만"},
    "October intake – Malaysia": {
        "zh": "10 月入学（马来西亚）",
        "ja": "10月入学（マレーシア）",
        "ko": "10월 입학(말레이시아)",
    },
    "November intake – Australia": {
        "zh": "11 月入学（澳大利亚）",
        "ja": "11月入学（オーストラリア）",
        "ko": "11월 입학(호주)",
    },
    "November intake (Australia)": {
        "zh": "11 月入学（澳大利亚）",
        "ja": "11月入学（オーストラリア）",
        "ko": "11월 입학(호주)",
    },
    "October intake (Malaysia)": {
        "zh": "10 月入学（马来西亚）",
        "ja": "10月入学（マレーシア）",
        "ko": "10월 입학(말레이시아)",
    },
    "Monash Indonesia term 5": {"zh": "Monash 印尼校区第 5 学季",
                                "ja": "Monash インドネシア校 第5ターム",
                                "ko": "Monash 인도네시아 5학기"},
    "Term 5": {"zh": "第 5 学季", "ja": "第5ターム", "ko": "5학기"},
    "term 5": {"zh": "第 5 学季", "ja": "第5ターム", "ko": "5학기"},
    "Australia Day": {"zh": "澳大利亚国庆日", "ja": "オーストラリア・デー", "ko": "호주의 날"},
    "Anzac Day": {"zh": "澳新军团日", "ja": "アンザック・デー", "ko": "안작 데이"},
    "Boxing Day": {"zh": "节礼日", "ja": "ボクシング・デー", "ko": "박싱 데이"},
    "Christmas Day": {"zh": "圣诞节", "ja": "クリスマス", "ko": "크리스마스"},
    "Christmas Eve": {"zh": "平安夜", "ja": "クリスマスイブ", "ko": "크리스마스 이브"},
    "New Year's Day": {"zh": "元旦", "ja": "元日", "ko": "새해 첫날"},
    "New Year's Eve": {"zh": "除夕", "ja": "大晦日", "ko": "섣달그믐"},
    "Easter Monday": {"zh": "复活节星期一", "ja": "イースターマンデー", "ko": "부활절 월요일"},
    "Easter Tuesday": {"zh": "复活节星期二", "ja": "イースターチューズデー", "ko": "부활절 화요일"},
    "Easter Saturday": {"zh": "复活节星期六", "ja": "イースターサタデー", "ko": "부활절 토요일"},
    "Easter Sunday": {"zh": "复活节星期日", "ja": "イースターサンデー", "ko": "부활절 일요일"},
    "Good Friday": {"zh": "耶稣受难日", "ja": "聖金曜日", "ko": "성금요일"},
    "Grand Final Friday": {
        "zh": "总决赛星期五",
        "ja": "グランドファイナル・フライデー",
        "ko": "그랜드 파이널 금요일",
    },
    "Labour Day": {"zh": "劳动节", "ja": "レイバー・デー", "ko": "노동절"},
    "Queen's Birthday": {"zh": "女王诞辰日", "ja": "女王誕生日", "ko": "여왕 탄신일"},
    "King's Birthday": {"zh": "国王诞辰日", "ja": "国王誕生日", "ko": "국왕 탄신일"},
    "Melbourne Cup Day": {
        "zh": "墨尔本杯赛马日",
        "ja": "メルボルンカップ・デー",
        "ko": "멜버른컵 데이",
    },
    "Public holiday": {"zh": "公共假日", "ja": "祝日", "ko": "공휴일"},
    "no replacement holiday": {"zh": "不另行补假", "ja": "振替休日なし", "ko": "대체 휴일 없음"},
    "MBA 1": {"zh": "MBA 1", "ja": "MBA 1", "ko": "MBA 1"},
    "MBA 2": {"zh": "MBA 2", "ja": "MBA 2", "ko": "MBA 2"},
    "Full-year extended": {"zh": "全学年（延长）", "ja": "通年（延長）", "ko": "연간(연장)"},
    "Full-year": {"zh": "全学年", "ja": "通年", "ko": "연간"},
    "extended": {"zh": "延长", "ja": "延長", "ko": "연장"},
    "November intake": {"zh": "11 月入学", "ja": "11月入学", "ko": "11월 입학"},
    "October intake": {"zh": "10 月入学", "ja": "10月入学", "ko": "10월 입학"},
    "full-year extended": {"zh": "全学年（延长）", "ja": "通年（延長）", "ko": "연간(연장)"},
    "full-year": {"zh": "全学年", "ja": "通年", "ko": "연간"},
    "summer A": {"zh": "夏季学期 A", "ja": "サマーセメスター A", "ko": "여름 학기 A"},
    "summer B": {"zh": "夏季学期 B", "ja": "サマーセメスター B", "ko": "여름 학기 B"},
    "Summer A": {"zh": "夏季学期 A", "ja": "サマーセメスター A", "ko": "여름 학기 A"},
    "Summer B": {"zh": "夏季学期 B", "ja": "サマーセメスター B", "ko": "여름 학기 B"},
    "Research Q1": {"zh": "研究季度 1", "ja": "研究四半期 1", "ko": "연구 분기 1"},
    "Research Q2": {"zh": "研究季度 2", "ja": "研究四半期 2", "ko": "연구 분기 2"},
    "Research Q3": {"zh": "研究季度 3", "ja": "研究四半期 3", "ko": "연구 분기 3"},
    "Research Q4": {"zh": "研究季度 4", "ja": "研究四半期 4", "ko": "연구 분기 4"},
    "Winter teaching period": {
        "zh": "冬季开课学期",
        "ja": "冬期の教育期間",
        "ko": "겨울 교육 기간",
    },
    "northern": {"zh": "北半球", "ja": "北半球", "ko": "북반구"},
    "swot vac": {"zh": "swot vac（复习周）", "ja": "swot vac（試験前復習期間）",
                 "ko": "swot vac(시험 전 복습 기간)"},
    "December round": {"zh": "12 月批次", "ja": "12月ラウンド", "ko": "12월 라운드"},
    "October round": {"zh": "10 月批次", "ja": "10月ラウンド", "ko": "10월 라운드"},
    "Australia": {"zh": "澳大利亚", "ja": "オーストラリア", "ko": "호주"},
    "Summer semester": {
        "zh": "夏季学期",
        "ja": "サマーセメスター",
        "ko": "여름 학기",
    },
    "Winter semester": {
        "zh": "冬季学期",
        "ja": "ウィンターセメスター",
        "ko": "겨울 학기",
    },
    "On-campus": {
        "zh": "校内授课",
        "ja": "対面授業",
        "ko": "대면 수업",
    },
    "Off-campus": {
        "zh": "校外授课",
        "ja": "遠隔授業",
        "ko": "원격 수업",
    },

    # --- the words that make a unit title ------------------------------------
    "programming paradigms": {
        "zh": "编程范式",
        "ja": "プログラミングパラダイム",
        "ko": "프로그래밍 패러다임",
    },
    "paradigms": {
        "zh": "范式",
        "ja": "パラダイム",
        "ko": "패러다임",
    },
    "data structures": {
        "zh": "数据结构",
        "ja": "データ構造",
        "ko": "자료 구조",
    },
    "algorithms": {
        "zh": "算法",
        "ja": "アルゴリズム",
        "ko": "알고리즘",
    },
    "databases": {
        "zh": "数据库",
        "ja": "データベース",
        "ko": "데이터베이스",
    },
    "machine learning": {
        "zh": "机器学习",
        "ja": "機械学習",
        "ko": "기계 학습",
    },
    "artificial intelligence": {
        "zh": "人工智能",
        "ja": "人工知能",
        "ko": "인공지능",
    },
    "software engineering": {
        "zh": "软件工程",
        "ja": "ソフトウェア工学",
        "ko": "소프트웨어 공학",
    },
    "computer science": {
        "zh": "计算机科学",
        "ja": "コンピュータサイエンス",
        "ko": "컴퓨터 과학",
    },
    "cyber security": {
        "zh": "网络安全",
        "ja": "サイバーセキュリティ",
        "ko": "사이버 보안",
    },
    "financial accounting": {
        "zh": "财务会计",
        "ja": "財務会計",
        "ko": "재무회계",
    },
    "management accounting": {
        "zh": "管理会计",
        "ja": "管理会計",
        "ko": "관리회계",
    },
    "accounting": {
        "zh": "会计",
        "ja": "会計",
        "ko": "회계",
    },
    "microeconomics": {
        "zh": "微观经济学",
        "ja": "ミクロ経済学",
        "ko": "미시경제학",
    },
    "macroeconomics": {
        "zh": "宏观经济学",
        "ja": "マクロ経済学",
        "ko": "거시경제학",
    },
    "econometrics": {
        "zh": "计量经济学",
        "ja": "計量経済学",
        "ko": "계량경제학",
    },
    "business finance": {
        "zh": "公司理财",
        "ja": "企業ファイナンス",
        "ko": "기업 재무",
    },
    "marketing": {
        "zh": "市场营销",
        "ja": "マーケティング",
        "ko": "마케팅",
    },
    "nursing": {
        "zh": "护理学",
        "ja": "看護学",
        "ko": "간호학",
    },
    "pharmacy": {
        "zh": "药学",
        "ja": "薬学",
        "ko": "약학",
    },
    "physiotherapy": {
        "zh": "物理治疗",
        "ja": "理学療法",
        "ko": "물리치료",
    },
    "radiography": {
        "zh": "放射医学影像",
        "ja": "放射線技術",
        "ko": "방사선학",
    },
    "biochemistry": {
        "zh": "生物化学",
        "ja": "生化学",
        "ko": "생화학",
    },
    "pharmacology": {
        "zh": "药理学",
        "ja": "薬理学",
        "ko": "약리학",
    },
    "physiology": {
        "zh": "生理学",
        "ja": "生理学",
        "ko": "생리학",
    },
    "anatomy": {
        "zh": "解剖学",
        "ja": "解剖学",
        "ko": "해부학",
    },
    "epidemiology": {
        "zh": "流行病学",
        "ja": "疫学",
        "ko": "역학",
    },
    "public health": {
        "zh": "公共卫生",
        "ja": "公衆衛生",
        "ko": "공중보건",
    },
    "civil engineering": {
        "zh": "土木工程",
        "ja": "土木工学",
        "ko": "토목공학",
    },
    "mechanical engineering": {
        "zh": "机械工程",
        "ja": "機械工学",
        "ko": "기계공학",
    },
    "chemical engineering": {
        "zh": "化学工程",
        "ja": "化学工学",
        "ko": "화학공학",
    },
    "electrical engineering": {
        "zh": "电气工程",
        "ja": "電気工学",
        "ko": "전기공학",
    },
    "engineering": {
        "zh": "工程",
        "ja": "工学",
        "ko": "공학",
    },
    "jurisprudence": {
        "zh": "法理学",
        "ja": "法理学",
        "ko": "법이학",
    },
    "criminology": {
        "zh": "犯罪学",
        "ja": "犯罪学",
        "ko": "범죄학",
    },
    "psychology": {
        "zh": "心理学",
        "ja": "心理学",
        "ko": "심리학",
    },
    "sociology": {
        "zh": "社会学",
        "ja": "社会学",
        "ko": "사회학",
    },
    "linguistics": {
        "zh": "语言学",
        "ja": "言語学",
        "ko": "언어학",
    },
    "architecture": {
        "zh": "建筑学",
        "ja": "建築学",
        "ko": "건축학",
    },
    "honours": {
        "zh": "荣誉学位",
        "ja": "オナーズ",
        "ko": "우등 학위",
    },
    "research project": {
        "zh": "研究项目",
        "ja": "研究プロジェクト",
        "ko": "연구 프로젝트",
    },
    "professional practice": {
        "zh": "专业实践",
        "ja": "専門実務",
        "ko": "전문 실무",
    },
    "clinical placement": {
        "zh": "临床实习",
        "ja": "臨床実習",
        "ko": "임상 실습",
    },
    "placement": {
        "zh": "实习",
        "ja": "実習",
        "ko": "실습",
    },
    "internship": {
        "zh": "实习",
        "ja": "インターンシップ",
        "ko": "인턴십",
    },
    "dissertation": {
        "zh": "学位论文",
        "ja": "学位論文",
        "ko": "학위 논문",
    },
    "thesis": {
        "zh": "学位论文",
        "ja": "学位論文",
        "ko": "학위 논문",
    },
    "seminar": {
        "zh": "研讨课",
        "ja": "セミナー",
        "ko": "세미나",
    },
    "workshop": {
        "zh": "工作坊",
        "ja": "ワークショップ",
        "ko": "워크숍",
    },
    "tutorial": {
        "zh": "辅导课",
        "ja": "チュートリアル",
        "ko": "튜토리얼",
    },
    "lecture": {
        "zh": "讲座课",
        "ja": "講義",
        "ko": "강의",
    },
    "applied session": {
        "zh": "实践课",
        "ja": "実習セッション",
        "ko": "실습 세션",
    },
    "applied sessions": {
        "zh": "实践课",
        "ja": "実習セッション",
        "ko": "실습 세션",
    },
    "laboratory": {
        "zh": "实验课",
        "ja": "実験",
        "ko": "실험",
    },
    "field trip": {
        "zh": "实地考察",
        "ja": "実地見学",
        "ko": "현장 학습",
    },
    "study abroad": {
        "zh": "海外学习",
        "ja": "海外留学",
        "ko": "해외 유학",
    },
    "podiatry": {
        "zh": "足病医学",
        "ja": "足病学",
        "ko": "발 의학",
    },
    "midwifery": {
        "zh": "助产学",
        "ja": "助産学",
        "ko": "조산학",
    },
    "paramedicine": {
        "zh": "院前急救医学",
        "ja": "救急救命学",
        "ko": "응급구조학",
    },
    "optometry": {
        "zh": "视光学",
        "ja": "検眼学",
        "ko": "검안학",
    },
    "dietetics": {
        "zh": "营养治疗学",
        "ja": "臨床栄養学",
        "ko": "임상영양학",
    },
    "nutrition": {
        "zh": "营养学",
        "ja": "栄養学",
        "ko": "영양학",
    },
    "occupational therapy": {
        "zh": "职业治疗",
        "ja": "作業療法",
        "ko": "작업치료",
    },
    "dentistry": {
        "zh": "牙医学",
        "ja": "歯学",
        "ko": "치의학",
    },
    "veterinary": {
        "zh": "兽医",
        "ja": "獣医学",
        "ko": "수의학",
    },
    "immunology": {
        "zh": "免疫学",
        "ja": "免疫学",
        "ko": "면역학",
    },
    "microbiology": {
        "zh": "微生物学",
        "ja": "微生物学",
        "ko": "미생물학",
    },
    "pathology": {
        "zh": "病理学",
        "ja": "病理学",
        "ko": "병리학",
    },
    "radiology": {
        "zh": "放射学",
        "ja": "放射線医学",
        "ko": "영상의학",
    },
    "obstetrics": {
        "zh": "产科学",
        "ja": "産科学",
        "ko": "산과학",
    },
    "paediatrics": {
        "zh": "儿科学",
        "ja": "小児科学",
        "ko": "소아과학",
    },
    "psychiatry": {
        "zh": "精神医学",
        "ja": "精神医学",
        "ko": "정신의학",
    },
    "biostatistics": {
        "zh": "生物统计学",
        "ja": "生物統計学",
        "ko": "생물통계학",
    },
    "genomics": {
        "zh": "基因组学",
        "ja": "ゲノミクス",
        "ko": "유전체학",
    },
    "neuroscience": {
        "zh": "神经科学",
        "ja": "神経科学",
        "ko": "신경과학",
    },
    "literature review": {
        "zh": "文献综述",
        "ja": "文献レビュー",
        "ko": "문헌 고찰",
    },
    "research methods": {
        "zh": "研究方法",
        "ja": "研究方法",
        "ko": "연구 방법",
    },
    "research methodology": {
        "zh": "研究方法论",
        "ja": "研究方法論",
        "ko": "연구 방법론",
    },
    "foundation practice": {
        "zh": "基础实践",
        "ja": "基礎実習",
        "ko": "기초 실습",
    },
    "foundations": {
        "zh": "基础",
        "ja": "基礎",
        "ko": "기초",
    },
    "fundamentals": {
        "zh": "基础",
        "ja": "基礎",
        "ko": "기초",
    },
    "principles": {
        "zh": "原理",
        "ja": "原理",
        "ko": "원리",
    },
    "introduction": {
        "zh": "导论",
        "ja": "入門",
        "ko": "입문",
    },
    "capstone": {
        "zh": "综合实践课程",
        "ja": "キャップストーン",
        "ko": "캡스톤",
    },
    "clinical practice": {
        "zh": "临床实践",
        "ja": "臨床実習",
        "ko": "임상 실습",
    },
    "advanced": {
        "zh": "高级",
        "ja": "上級",
        "ko": "고급",
    },
    "intermediate": {
        "zh": "中级",
        "ja": "中級",
        "ko": "중급",
    },
    "minor thesis": {
        "zh": "小型学位论文",
        "ja": "小論文",
        "ko": "소논문",
    },
    "special topic": {
        "zh": "专题",
        "ja": "特別研究",
        "ko": "특별 주제",
    },
    "industry project": {
        "zh": "产业项目",
        "ja": "産学プロジェクト",
        "ko": "산업 프로젝트",
    },
    "field work": {
        "zh": "田野调查",
        "ja": "フィールドワーク",
        "ko": "현장 조사",
    },
    "fieldwork": {
        "zh": "田野调查",
        "ja": "フィールドワーク",
        "ko": "현장 조사",
    },
    "study tour": {
        "zh": "海外研修",
        "ja": "研修旅行",
        "ko": "연수 여행",
    },
    "Japanese studies": {
        "zh": "日本研究",
        "ja": "日本研究",
        "ko": "일본학",
    },
    "Chinese studies": {
        "zh": "中国研究",
        "ja": "中国研究",
        "ko": "중국학",
    },
    "Korean studies": {
        "zh": "韩国研究",
        "ja": "韓国研究",
        "ko": "한국학",
    },
    "Indonesian studies": {
        "zh": "印尼研究",
        "ja": "インドネシア研究",
        "ko": "인도네시아학",
    },
    "French studies": {
        "zh": "法国研究",
        "ja": "フランス研究",
        "ko": "프랑스학",
    },
    "German studies": {
        "zh": "德国研究",
        "ja": "ドイツ研究",
        "ko": "독일학",
    },
    "Italian studies": {
        "zh": "意大利研究",
        "ja": "イタリア研究",
        "ko": "이탈리아학",
    },
    "Spanish studies": {
        "zh": "西班牙研究",
        "ja": "スペイン研究",
        "ko": "스페인학",
    },
    "Ukrainian studies": {
        "zh": "乌克兰研究",
        "ja": "ウクライナ研究",
        "ko": "우크라이나학",
    },
    "Jewish civilisation": {
        "zh": "犹太文明",
        "ja": "ユダヤ文明",
        "ko": "유대 문명",
    },
    "kanji": {
        "zh": "汉字",
        "ja": "漢字",
        "ko": "한자",
    },
    "Faculty of": {
        "zh": "学院：",
        "ja": "学部：",
        "ko": "학부:",
    },
    "Department of": {
        "zh": "系：",
        "ja": "学科：",
        "ko": "학과:",
    },
    "School of": {
        "zh": "学院：",
        "ja": "スクール：",
        "ko": "학부:",
    },
    "exchange": {
        "zh": "交换",
        "ja": "交換留学",
        "ko": "교환학생",
    },
}

# ---------------------------------------------------------------------------
# Whole field values, matched exactly rather than as substrings.
#
# The Handbook draws these from closed lists - eight levels, nineteen assessment
# types, forty campuses, forty-four teaching periods - and they are printed on
# every unit card and every unit page. There are only a couple of hundred of
# them in a year of data, so none of them has any business being guessed:
# unaided the model returns 锻炼 (physical exercise) for the assessment type
# *Exercise* and 阈值 (a numeric threshold) for the hurdle type *Threshold*.
#
# Names of institutions are deliberately left in English. "Walter and Eliza Hall
# Institute" is what is written on the building, and a student looking for it
# needs the name that is on the building.
ENUMS: dict[str, dict[str, str]] = {
    # --- level ---------------------------------------------------------------
    "Level 0": {"zh": "第 0 级", "ja": "レベル 0", "ko": "레벨 0"},
    "Level 1": {"zh": "第 1 级", "ja": "レベル 1", "ko": "레벨 1"},
    "Level 2": {"zh": "第 2 级", "ja": "レベル 2", "ko": "레벨 2"},
    "Level 3": {"zh": "第 3 级", "ja": "レベル 3", "ko": "레벨 3"},
    "Level 4": {"zh": "第 4 级", "ja": "レベル 4", "ko": "레벨 4"},
    "Level 5": {"zh": "第 5 级（研究生）", "ja": "レベル 5（大学院）", "ko": "레벨 5(대학원)"},
    "Level 6": {"zh": "第 6 级（研究生）", "ja": "レベル 6（大学院）", "ko": "레벨 6(대학원)"},
    "Level 9": {"zh": "第 9 级（研究）", "ja": "レベル 9（研究）", "ko": "레벨 9(연구)"},

    # --- assessment type -----------------------------------------------------
    "Examination": {"zh": "考试", "ja": "試験", "ko": "시험"},
    "Exam": {"zh": "考试", "ja": "試験", "ko": "시험"},
    "Quiz / Test": {"zh": "小测 / 测验", "ja": "小テスト", "ko": "퀴즈 / 테스트"},
    "Assignment": {"zh": "作业", "ja": "課題", "ko": "과제"},
    "Research assignment": {"zh": "研究作业", "ja": "研究課題", "ko": "연구 과제"},
    "Essay": {"zh": "论文写作", "ja": "エッセイ", "ko": "에세이"},
    "Report": {"zh": "报告", "ja": "レポート", "ko": "보고서"},
    "Project": {"zh": "项目作业", "ja": "プロジェクト", "ko": "프로젝트"},
    "Exercise": {"zh": "练习", "ja": "演習", "ko": "연습 과제"},
    "Presentation": {"zh": "口头报告", "ja": "プレゼンテーション", "ko": "발표"},
    "Performance": {"zh": "表演", "ja": "実演", "ko": "실연"},
    "Demonstration": {"zh": "操作演示", "ja": "実技デモ", "ko": "실기 시연"},
    "Portfolio": {"zh": "作品集", "ja": "ポートフォリオ", "ko": "포트폴리오"},
    "Folio": {"zh": "作品集", "ja": "作品集", "ko": "작품집"},
    "Artefact": {"zh": "作品成果", "ja": "制作物", "ko": "제작물"},
    "Attendance": {"zh": "出勤", "ja": "出席", "ko": "출석"},
    # *Written* and *Examination* are separate types on the same closed list -
    # 4,718 assessments against 1,311 - so 笔试 (a written *exam*) said something
    # the Handbook did not, on a site that also offers a has-an-exam filter.
    "Written": {"zh": "书面考核", "ja": "筆記", "ko": "필기"},
    "Work integrated": {"zh": "工作实践", "ja": "実務連携", "ko": "현장 연계"},
    "Other": {"zh": "其他", "ja": "その他", "ko": "기타"},

    # --- hurdle type ---------------------------------------------------------
    "Threshold": {"zh": "分数门槛", "ja": "最低到達点", "ko": "최저 점수 요건"},
    "Competency": {"zh": "能力达标", "ja": "能力要件", "ko": "역량 요건"},

    # --- teaching activity ---------------------------------------------------
    "Lectures": {"zh": "讲座课", "ja": "講義", "ko": "강의"},
    "Tutorials": {"zh": "辅导课", "ja": "チュートリアル", "ko": "튜토리얼"},
    "Workshops": {"zh": "工作坊", "ja": "ワークショップ", "ko": "워크숍"},
    "Seminars": {"zh": "研讨课", "ja": "セミナー", "ko": "세미나"},
    "Laboratories": {"zh": "实验课", "ja": "実験", "ko": "실험"},
    "Applied sessions": {"zh": "实践课", "ja": "実習セッション", "ko": "실습 세션"},
    "Practical activities": {"zh": "实操活动", "ja": "実技活動", "ko": "실기 활동"},
    "Studio activities": {"zh": "工作室课", "ja": "スタジオ活動", "ko": "스튜디오 활동"},
    "Assessments": {"zh": "考核", "ja": "評価", "ko": "평가"},

    # --- teaching period -----------------------------------------------------
    "First semester": {"zh": "第一学期", "ja": "第1学期", "ko": "1학기"},
    "Second semester": {"zh": "第二学期", "ja": "第2学期", "ko": "2학기"},
    "First semester (extended)": {
        "zh": "第一学期（延长）",
        "ja": "第1学期（延長）",
        "ko": "1학기(연장)",
    },
    "Second semester (extended)": {
        "zh": "第二学期（延长）",
        "ja": "第2学期（延長）",
        "ko": "2학기(연장)",
    },
    "First semester - alternate": {
        "zh": "第一学期（备选安排）",
        "ja": "第1学期（別日程）",
        "ko": "1학기(대체 일정)",
    },
    "Second semester - alternate": {
        "zh": "第二学期（备选安排）",
        "ja": "第2学期（別日程）",
        "ko": "2학기(대체 일정)",
    },
    "First semester (Northern)": {
        "zh": "第一学期（北半球）",
        "ja": "第1学期（北半球）",
        "ko": "1학기(북반구)",
    },
    "Second semester (Northern)": {
        "zh": "第二学期（北半球）",
        "ja": "第2学期（北半球）",
        "ko": "2학기(북반구)",
    },
    "First semester (Northern) - alternate": {
        "zh": "第一学期（北半球，备选安排）",
        "ja": "第1学期（北半球・別日程）",
        "ko": "1학기(북반구, 대체 일정)",
    },
    "Full year": {"zh": "全学年", "ja": "通年", "ko": "연간"},
    "Full year extended": {"zh": "全学年（延长）", "ja": "通年（延長）", "ko": "연간(연장)"},
    "Summer semester A": {"zh": "夏季学期 A", "ja": "サマーセメスター A", "ko": "여름 학기 A"},
    "Summer semester B": {"zh": "夏季学期 B", "ja": "サマーセメスター B", "ko": "여름 학기 B"},
    "Summer semester A - alternate": {
        "zh": "夏季学期 A（备选安排）",
        "ja": "サマーセメスター A（別日程）",
        "ko": "여름 학기 A(대체 일정)",
    },
    "Summer semester B - alternate": {
        "zh": "夏季学期 B（备选安排）",
        "ja": "サマーセメスター B（別日程）",
        "ko": "여름 학기 B(대체 일정)",
    },
    "Winter semester": {"zh": "冬季学期", "ja": "ウィンターセメスター", "ko": "겨울 학기"},
    "Winter semester - alternate": {
        "zh": "冬季学期（备选安排）",
        "ja": "ウィンターセメスター（別日程）",
        "ko": "겨울 학기(대체 일정)",
    },
    "November teaching period": {"zh": "11 月教学期", "ja": "11月開講期", "ko": "11월 학기"},
    "Teaching period 1": {"zh": "教学期 1", "ja": "開講期 1", "ko": "학기 1"},
    "Teaching period 2": {"zh": "教学期 2", "ja": "開講期 2", "ko": "학기 2"},
    "Teaching period 3": {"zh": "教学期 3", "ja": "開講期 3", "ko": "학기 3"},
    "Teaching period 4": {"zh": "教学期 4", "ja": "開講期 4", "ko": "학기 4"},
    "Teaching period 5": {"zh": "教学期 5", "ja": "開講期 5", "ko": "학기 5"},
    "Teaching period 6": {"zh": "教学期 6", "ja": "開講期 6", "ko": "학기 6"},
    "Term 1": {"zh": "第 1 学季", "ja": "第1タームト", "ko": "1학기(term)"},
    "Term 2": {"zh": "第 2 学季", "ja": "第2ターム", "ko": "2학기(term)"},
    "Term 3": {"zh": "第 3 学季", "ja": "第3ターム", "ko": "3학기(term)"},
    "Term 4": {"zh": "第 4 学季", "ja": "第4ターム", "ko": "4학기(term)"},
    "Trimester 1": {"zh": "第 1 学段", "ja": "第1トライメスター", "ko": "1트라이메스터"},
    "Trimester 2": {"zh": "第 2 学段", "ja": "第2トライメスター", "ko": "2트라이메스터"},
    "Trimester 3": {"zh": "第 3 学段", "ja": "第3トライメスター", "ko": "3트라이메스터"},
    "Research quarter 1": {"zh": "研究季度 1", "ja": "研究クォーター 1", "ko": "연구 분기 1"},
    "Research quarter 2": {"zh": "研究季度 2", "ja": "研究クォーター 2", "ko": "연구 분기 2"},
    "Research quarter 3": {"zh": "研究季度 3", "ja": "研究クォーター 3", "ko": "연구 분기 3"},
    "Research quarter 4": {"zh": "研究季度 4", "ja": "研究クォーター 4", "ko": "연구 분기 4"},

    # --- campus --------------------------------------------------------------
    "Clayton": {"zh": "Clayton 校区", "ja": "Clayton キャンパス", "ko": "Clayton 캠퍼스"},
    "Caulfield": {"zh": "Caulfield 校区", "ja": "Caulfield キャンパス", "ko": "Caulfield 캠퍼스"},
    "Peninsula": {"zh": "Peninsula 校区", "ja": "Peninsula キャンパス", "ko": "Peninsula 캠퍼스"},
    "Parkville": {"zh": "Parkville 校区", "ja": "Parkville キャンパス", "ko": "Parkville 캠퍼스"},
    "Malaysia": {"zh": "马来西亚校区", "ja": "マレーシアキャンパス", "ko": "말레이시아 캠퍼스"},
    "Malaysia (Off-shore)": {
        "zh": "马来西亚校区（境外授课）",
        "ja": "マレーシアキャンパス（海外実施）",
        "ko": "말레이시아 캠퍼스(해외 실시)",
    },
    "Malaysia (Other)": {
        "zh": "马来西亚（其他地点）",
        "ja": "マレーシア（その他）",
        "ko": "말레이시아(기타)",
    },
    "Suzhou": {"zh": "苏州校区", "ja": "蘇州キャンパス", "ko": "쑤저우 캠퍼스"},
    "Suzhou (SEU)": {"zh": "苏州（东南大学）", "ja": "蘇州（東南大学）", "ko": "쑤저우(둥난대)"},
    "Monash Online": {
        "zh": "Monash Online（在线）",
        "ja": "Monash Online（オンライン）",
        "ko": "Monash Online(온라인)",
    },
    "City (Melbourne)": {"zh": "墨尔本市区", "ja": "メルボルン市内", "ko": "멜버른 시티"},
    "Southbank": {"zh": "Southbank 校区", "ja": "Southbank キャンパス", "ko": "Southbank 캠퍼스"},
    "Overseas": {"zh": "海外", "ja": "海外", "ko": "해외"},
    "Australia (Other)": {
        "zh": "澳大利亚（其他地点）",
        "ja": "オーストラリア（その他）",
        "ko": "호주(기타)",
    },
    "Hong Kong": {"zh": "香港", "ja": "香港", "ko": "홍콩"},
    "Singapore": {"zh": "新加坡", "ja": "シンガポール", "ko": "싱가포르"},
    "Indonesia": {"zh": "印度尼西亚", "ja": "インドネシア", "ko": "인도네시아"},
    "Macau": {"zh": "澳门", "ja": "マカオ", "ko": "마카오"},
    "Prato": {"zh": "普拉托（意大利）", "ja": "プラート（イタリア）", "ko": "프라토(이탈리아)"},
    "Perth": {"zh": "珀斯", "ja": "パース", "ko": "퍼스"},
    "Bendigo": {"zh": "Bendigo", "ja": "Bendigo", "ko": "Bendigo"},
    "Gippsland": {"zh": "Gippsland", "ja": "Gippsland", "ko": "Gippsland"},
    "Mildura": {"zh": "Mildura", "ja": "Mildura", "ko": "Mildura"},
    "Warragul": {"zh": "Warragul", "ja": "Warragul", "ko": "Warragul"},
    "Box Hill": {"zh": "Box Hill", "ja": "Box Hill", "ko": "Box Hill"},
    "Notting Hill": {"zh": "Notting Hill", "ja": "Notting Hill", "ko": "Notting Hill"},
    "Moe": {"zh": "Moe", "ja": "Moe", "ko": "Moe"},

    # --- attendance mode -----------------------------------------------------
    "Teaching activities are on-campus (ON-CAMPUS)": {
        "zh": "校内授课（ON-CAMPUS）",
        "ja": "対面授業（ON-CAMPUS）",
        "ko": "대면 수업(ON-CAMPUS)",
    },
    "Teaching is all online (ONLINE)": {
        "zh": "全线上授课（ONLINE）",
        "ja": "全てオンライン授業（ONLINE）",
        "ko": "전면 온라인 수업(ONLINE)",
    },
    "Activities scheduled as a mix of on-campus and online activities (BLENDED)": {
        "zh": "线上线下混合授课（BLENDED）",
        "ja": "対面とオンラインの併用（BLENDED）",
        "ko": "대면·온라인 혼합 수업(BLENDED)",
    },
    "Some activities have a choice of on-campus or online teaching activities (FLEXIBLE)": {
        "zh": "部分课程可自选线上或校内（FLEXIBLE）",
        "ja": "一部は対面かオンラインを選択可（FLEXIBLE）",
        "ko": "일부 활동은 대면·온라인 선택 가능(FLEXIBLE)",
    },
    "Flexible (FLEXIBLE)": {
        "zh": "弹性授课（FLEXIBLE）",
        "ja": "フレキシブル（FLEXIBLE）",
        "ko": "유연 수업(FLEXIBLE)",
    },
    "Evening (EVENING)": {
        "zh": "晚间授课（EVENING）",
        "ja": "夜間授業（EVENING）",
        "ko": "야간 수업(EVENING)",
    },
    "Monash Online (MO)": {
        "zh": "Monash Online（MO）",
        "ja": "Monash Online（MO）",
        "ko": "Monash Online(MO)",
    },
    "Teaching activities are on-campus and held in the evening (ON-EV)": {
        "zh": "校内晚间授课（ON-EV）",
        "ja": "対面・夜間授業（ON-EV）",
        "ko": "대면 야간 수업(ON-EV)",
    },
    "Teaching activities are on-campus and in a block period (ON-BLK)": {
        "zh": "校内集中授课（ON-BLK）",
        "ja": "対面・集中授業（ON-BLK）",
        "ko": "대면 집중 수업(ON-BLK)",
    },
    "On-campus block of classes (BLOCK-ON)": {
        "zh": "校内集中授课（BLOCK-ON）",
        "ja": "対面・集中授業（BLOCK-ON）",
        "ko": "대면 집중 수업(BLOCK-ON)",
    },
    "Off-campus block of classes (BLOCK-OFF)": {
        "zh": "校外集中授课（BLOCK-OFF）",
        "ja": "学外・集中授業（BLOCK-OFF）",
        "ko": "교외 집중 수업(BLOCK-OFF)",
    },
    "Off-campus Day (DAY-OFF)": {
        "zh": "校外日间授课（DAY-OFF）",
        "ja": "学外・昼間授業（DAY-OFF）",
        "ko": "교외 주간 수업(DAY-OFF)",
    },
    "External Candidature (EXT-CAND)": {
        "zh": "校外研究生身份（EXT-CAND）",
        "ja": "学外在籍（EXT-CAND）",
        "ko": "교외 등록(EXT-CAND)",
    },
}


# Names a student meets in English everywhere else - on the official site, in
# the app's own navigation, printed on the building. Translating them would make
# the two impossible to match up, so these map to themselves on purpose.
KEEP_IN_ENGLISH = frozenset({
    "handbook", "Moodle",
    # The university's own name. It is on the student's enrolment email, on the
    # building and on every official page, and the model reads it as *money*.
    # The services that carry it - Monash Abroad, Monash Connect - keep the
    # English too, with a bracket saying what they are.
    "Monash",
    # The OSHC insurer, for the same reason: a student has to be able to match
    # the name here against the policy documents and the card in their wallet,
    # and every reading the model invented for it - 爱护组织, 爱心, 爱丽安兹 -
    # is a company that does not exist.
    "Allianz Care Australia", "Allianz Care",
    # Malaysia's own systems and bodies, named on the documents themselves.
    "EMGS", "eVAL", "MPass",
    # The Handbook's own labels for the MBA teaching periods. There is nothing
    # to translate in "MBA 1" and a rendering of it would not match Allocate+.
    "MBA 1", "MBA 2",
})


# Sorted longest-first so "weighted average mark" is matched before "mark".
# The terms that are allowed to stop a sentence being published.
#
# Every term here is substituted the same way. The difference is what happens
# when the substitution cannot be made - when the model rendered the term some
# third way in context and there is nothing to find and replace. For a term on
# this list the sentence keeps its English, because a student acting on a wrong
# census date or a reversed unit/course pays for it. For anything else the
# model's own wording stands: Moodle read as 面条 is embarrassing, and a page
# left in English because of it is worse.
#
# 159 sentences across the guides were being held back by a term off this list
# - results, teaching period, Moodle, enrolment - none of which decides
# anything a student spends money on.
CRITICAL: frozenset[str] = frozenset({
    # deadlines and money - the whole section
    "census date", "census dates", "withdraw", "withdrawal", "discontinue",
    "intermission", "tuition fees", "fee liability", "HECS-HELP", "FEE-HELP",
    "Commonwealth supported place",
    # what decides progression
    "weighted average mark", "WAM", "grade point average", "GPA",
    "hurdle requirement", "hurdle", "pass mark", "academic progress",
    "unsatisfactory progress", "exclusion", "academic integrity", "plagiarism",
    "collusion",
    # a second chance, or not
    "special consideration", "deferred assessment", "supplementary assessment",
    "final assessment", "extension",
    # the pair every general translator reverses, and what enrolment turns on
    "unit", "units", "course", "courses", "credit points", "credit point",
    "credit transfer", "prerequisites", "prerequisite", "corequisite",
    "prohibition", "prohibitions", "enrolment rules",
    # a visa depends on these being right
    "student visa", "Confirmation of Enrolment", "CoE",
    "Overseas Student Health Cover", "OSHC", "full-time study load",
    "international student", "domestic student",
})


def is_critical(written: str) -> bool:
    """Whether getting this term wrong is worse than leaving the page English."""
    canonical = _LOOKUP.get(written.lower())
    return canonical in CRITICAL


_SORTED = sorted(TERMS, key=lambda t: (-len(t), t))
_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(" + "|".join(re.escape(t) for t in _SORTED) + r")(?![A-Za-z0-9])",
    re.IGNORECASE,
)
_LOOKUP = {term.lower(): term for term in TERMS}

# Letter placeholders: the model rewrites digits (XX1XX came back as X22XX) but
# passes an unknown capitalised token through untouched.
_ALPHABET = "abcdefghijklmnopqrstuvwxyz"

# "Untouched" turned out to be a property of the particular token, not of
# invented tokens in general. Zqa survives most sentences and is transliterated
# in some - "What is Zqa?" came back as 什么是兹卡? - and reading the sentence
# does not tell you which. Measured over the 59 sentences that were actually
# failing on the live guides, with the token varied and nothing else:
#
#     #a#  32/59      <a>  28/59      Zqa  0/59 (this is the population it lost)
#     Qxa  30/59      Xya  20/59      a PUA character, or 〇a〇: 0/59
#
# No token carries them all, and the sentences each one loses are largely
# different sentences, so the caller works down this list until one comes back
# whole: 50 of the 59 are recovered that way. Zq stays at the front because
# every translation already stored was made with it and it is right about the
# other 99% of strings; the rest are in order of what they add after it.
MASKS: tuple[tuple[str, str], ...] = (
    ("Zq", ""),
    ("#", "#"),
    ("Qx", ""),
    ("<", ">"),
    ("Xy", ""),
)

_ANY_PLACEHOLDER = re.compile(
    "|".join(re.escape(pre) + "[a-z]+" + re.escape(suf) for pre, suf in MASKS)
)


def placeholder(index: int, mask: tuple[str, str] = MASKS[0]) -> str:
    """Zqa, Zqb, … Zqaa. Distinct, letters only, and not a real English word."""
    prefix, suffix = mask
    token = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        token = _ALPHABET[remainder] + token
    return prefix + token + suffix


def whole_value(text: str, locale: str) -> str | None:
    """The agreed translation of a complete field value, if there is one.

    Checked before anything else: these are closed lists, so an exact match is
    both safer and better than translating them as prose.
    """
    entry = ENUMS.get(text.strip())
    return entry.get(locale) if entry else None


# ---------------------------------------------------------------------------
# Values whose meaning is in their digits: dates, times of day, and codes.
#
# There is no grammar here for the model to contribute and everything to lose.
# On the census dates page "1 Aug 2024" was published as 2024年8月1日纽约 (New
# York), "1 Apr 2026" as 2026年4月1日（英语）, and "1 Jul – 30 Sep 2026" lost
# its start date altogether and became 2026年9月30日 - on the page that says
# when withdrawing stops being free. "before 5am" came back as 下午5点前,
# twelve hours out, and the unit code ATS1192 as 1192奥地利先令: ATS was the
# Austrian schilling, and the model would rather read a currency than a unit.
#
# So these are lifted out of the sentence the way a glossary term is, and put
# back either exactly as they arrived (a code) or in a form arithmetic decided
# (a date, a span of dates, a clock time). The model never sees one.

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
_MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"
_DASH = r"\s*[-–—]\s*"
# The census dates page writes the weekday in front of the date, and a weekday
# left outside the mask is a weekday handed to the model: "Sat 28 Feb 2026" kept
# its Sat and so the whole row stayed English. It is arithmetic like the rest -
# the day is already in the date, so nothing needs looking up.
_WEEKDAY = r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*\.?"

# The month has to be capitalised, so that "3 may be enough" stays a sentence
# and does not become the third of May.
#
# Three shapes, longest first, because the dates pages are mostly spans and a
# span matched as its end date alone is how "1 Jul – 30 Sep 2026" came to be
# published as a single day in September.
_SPAN = (                                        # 1 Jul – 30 Sep 2026
    rf"(?P<sday>\d{{1,2}})\s+(?P<smonth>{_MONTH})(?:\s+(?P<syear>\d{{4}}))?"
    rf"{_DASH}"
    rf"(?P<eday>\d{{1,2}})\s+(?P<emonth>{_MONTH})(?:\s+(?P<eyear>\d{{4}}))?"
)
_DAY_SPAN = (                                    # 3–7 Jun 2026
    rf"(?P<rday>\d{{1,2}}){_DASH}(?P<rlast>\d{{1,2}})\s+"
    rf"(?P<rmonth>{_MONTH})(?:\s+(?P<ryear>\d{{4}}))?"
)
_DATE = (                                        # Sat 28 Feb 2026
    rf"(?:(?P<wday>{_WEEKDAY})\s+)?"
    rf"(?P<day>\d{{1,2}})\s+(?P<month>{_MONTH})(?:\s+(?P<year>\d{{4}}))?"
)
# "11.55pm", "12.30am", "5am". Monash writes the minutes after a full stop.
_CLOCK = r"(?P<hour>\d{1,2})(?:[.:](?P<minute>\d{2}))?\s?(?P<half>[ap]m|[AP]M)"
# An email address. "servicedesk@Monash.edu" was published as
# 服务台@Monash.edu on the academic integrity page - the address a student is
# told to write to when they cannot finish the compulsory module, translated
# into an address that does not exist. There is no grammar in an address.
_EMAIL = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
# A unit code (ATS1192, MON1001), and the codes the dates pages hang off
# (S2-01, MO-TP1-01).
_UNIT_CODE = r"[A-Z]{2,4}\d{4}"
_PERIOD_CODE = r"[A-Z]{1,3}\d?-[A-Z0-9]{1,4}(?:-\d{1,2})?"

VERBATIM = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    + "|".join((_EMAIL, _SPAN, _DAY_SPAN, _DATE, _CLOCK, _UNIT_CODE, _PERIOD_CODE))
    + r")(?![A-Za-z0-9])"
)
_SPAN_ONLY = re.compile(rf"^{_SPAN}$")
_DAY_SPAN_ONLY = re.compile(rf"^{_DAY_SPAN}$")
_DATE_ONLY = re.compile(rf"^{_DATE}$")
_CLOCK_ONLY = re.compile(rf"^{_CLOCK}$")

# What separates the two ends of a span, once it is in the target language.
_TO = {"zh": "至", "ja": "〜", "ko": "~"}


def has_verbatim(text: str) -> bool:
    """Whether this string carries a date, a time or a code.

    The caller uses it to decide that a sentence is not worth a second attempt
    with nothing masked: unmasked is how "1 Aug 2024" acquired a New York.
    """
    return bool(VERBATIM.search(text))


def _written_date(day: int, month: int, year: str | None, locale: str) -> str:
    if locale == "ko":
        return f"{year}년 {month}월 {day}일" if year else f"{month}월 {day}일"
    return f"{year}年{month}月{day}日" if year else f"{month}月{day}日"


def _written_day(day: int, locale: str) -> str:
    return f"{day}일" if locale == "ko" else f"{day}日"


# Written after the date rather than before it, which is the order all three
# languages use.
_WEEKDAYS = {
    "mon": {"zh": "周一", "ja": "月", "ko": "월"},
    "tue": {"zh": "周二", "ja": "火", "ko": "화"},
    "wed": {"zh": "周三", "ja": "水", "ko": "수"},
    "thu": {"zh": "周四", "ja": "木", "ko": "목"},
    "fri": {"zh": "周五", "ja": "金", "ko": "금"},
    "sat": {"zh": "周六", "ja": "土", "ko": "토"},
    "sun": {"zh": "周日", "ja": "日", "ko": "일"},
}


def _written_weekday(written: str, locale: str) -> str:
    day = _WEEKDAYS[written.lower()[:3]][locale]
    return f"({day})" if locale == "ko" else f"（{day}）"


def _month_number(written: str) -> int:
    return _MONTHS[written.lower()[:3]]


def rendered_verbatim(value: str, locale: str) -> str:
    """What a date, span, time or code should read as. Arithmetic, not translation."""
    span = _SPAN_ONLY.match(value)
    if span:
        # One year written at the end covers both ends of the span, which is
        # how the Handbook and the dates pages write it.
        start_year = span["syear"] or span["eyear"]
        first = _written_date(
            int(span["sday"]), _month_number(span["smonth"]), start_year, locale
        )
        second = _written_date(
            int(span["eday"]), _month_number(span["emonth"]), span["eyear"], locale
        )
        if span["eyear"] and span["eyear"] == start_year and not span["syear"]:
            # Both ends in the same year: say the year once, at the front.
            second = _written_date(
                int(span["eday"]), _month_number(span["emonth"]), None, locale
            )
        return f"{first}{_TO[locale]}{second}"
    days = _DAY_SPAN_ONLY.match(value)
    if days:
        first = _written_date(
            int(days["rday"]), _month_number(days["rmonth"]), days["ryear"], locale
        )
        return f"{first}{_TO[locale]}{_written_day(int(days['rlast']), locale)}"
    date = _DATE_ONLY.match(value)
    if date:
        written = _written_date(
            int(date["day"]), _month_number(date["month"]), date["year"], locale
        )
        if date["wday"]:
            written += _written_weekday(date["wday"], locale)
        return written
    clock = _CLOCK_ONLY.match(value)
    if clock:
        # 24-hour, which all three languages write without an am or a pm to get
        # wrong: 11.55pm is 23:55 and 12.30am is 00:30.
        hour = int(clock["hour"]) % 12 + (12 if clock["half"].lower() == "pm" else 0)
        return f"{hour:02d}:{int(clock['minute'] or 0):02d}"
    return value  # a code, and the code is what a student matches against


def protect(
    text: str, locale: str, mask: tuple[str, str] = MASKS[0]
) -> tuple[str, list[str]]:
    """Replace every known term, date, time and code with a placeholder.

    Returns the masked text and the replacements, in placeholder order. The
    ``mask`` is the retry handle: the same sentence masked with a different
    token is a different problem to the model, and often an easier one.
    """
    replacements: list[str] = []

    def keep(match: re.Match[str]) -> str:
        replacements.append(rendered_verbatim(match.group(0), locale))
        return placeholder(len(replacements) - 1, mask)

    text = VERBATIM.sub(keep, text)

    def swap(match: re.Match[str]) -> str:
        canonical = _LOOKUP[match.group(1).lower()]
        translated = TERMS[canonical].get(locale)
        if not translated:
            return match.group(0)
        replacements.append(translated)
        return placeholder(len(replacements) - 1, mask)

    return _PATTERN.sub(swap, text), replacements


def terms_in(text: str, locale: str) -> list[tuple[str, str]]:
    """The reserved terms this string uses: (English as written, agreed wording).

    ``protect`` returns only the agreed side, which is all a placeholder needs.
    Repairing a translation needs the English too: to find what the model made
    of a term, you have to be able to ask it to translate that term.
    """
    found: list[tuple[str, str]] = []
    seen: set[str] = set()

    def note(match: re.Match[str]) -> str:
        written = match.group(1)
        agreed = TERMS[_LOOKUP[written.lower()]].get(locale)
        if agreed and written.lower() not in seen:
            seen.add(written.lower())
            found.append((written, agreed))
        return match.group(0)

    _PATTERN.sub(note, text)
    return found


def restore(
    text: str, replacements: list[str], mask: tuple[str, str] = MASKS[0]
) -> str:
    """Put the agreed wording back where the placeholders are.

    Longest placeholder first: without it ``Zqa`` matches inside ``Zqaa``.
    """
    for index in sorted(
        range(len(replacements)), key=lambda i: -len(placeholder(i, mask))
    ):
        text = text.replace(placeholder(index, mask), replacements[index])
    return text


def placeholders_survived(
    text: str, count: int, mask: tuple[str, str] = MASKS[0]
) -> bool:
    """Whether every placeholder made it through a translation intact.

    The model usually copies these tokens and occasionally transliterates one:
    "What is Zqa?" came back from a live page as 什么是兹卡?. Restoring cannot
    find a token that is no longer there, so the reader would be shown a
    nonsense word where a term should be. The caller keeps the English instead.
    """
    return all(placeholder(index, mask) in text for index in range(count))


def is_only_placeholders(text: str) -> bool:
    """True when nothing is left for the translator to do.

    A string that is entirely a known term - most unit titles, every campus
    name - must not be sent to the model: asked to translate the bare token
    ``Zqa`` it returns 兹卡.
    """
    return not re.search(r"[A-Za-z]", _ANY_PLACEHOLDER.sub("", text))

