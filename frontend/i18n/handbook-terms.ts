/**
 * Chinese, Japanese and Korean for the Handbook's own vocabulary.
 *
 * The Handbook writes its structured fields from closed lists, not free prose.
 * Across all 2,600 units in the 2026 Handbook there are 19 campuses, 43
 * teaching periods, 26 attendance modes, 10 assessment types, 9 activity types
 * and 73 faculties or schools — and that is the whole of it. A list that short
 * can be translated by hand, checked once, and then be right every time, which
 * is a different proposition from translating prose.
 *
 * So this file is a dictionary, not a translator. A value that is not in it
 * comes back in English rather than being guessed at: a wrong campus or a wrong
 * teaching period sends somebody to the wrong place on the wrong day, and
 * "Suzhou (SEU)" left in English costs a reader far less than a plausible
 * mistranslation of it.
 *
 * Two rules the entries follow:
 *
 * - **Keep the code.** Attendance modes and unit codes are what a student sees
 *   in WES and on their timetable, so the translation carries the original in
 *   brackets: "校内授课（ON-CAMPUS）" is matchable against the real system,
 *   "校内授课" is not.
 * - **Translate the word, not the meaning.** "Level 5" becomes "第 5 级", not
 *   "硕士课程". The Handbook says the first thing. The second is an inference,
 *   and it is wrong for some units.
 *
 * Faculty and school names are not here either. There are over a hundred of
 * them, and the API already has them in ENUMS in
 * backend/app/knowledge/glossary.py: it translates them on unit pages and sends
 * the same wording as `labels` with the unit filters, so there is one list.
 *
 * Long prose — a unit overview, a learning outcome, the body of an official
 * page — is not here and cannot be. That lives in the `content_translations`
 * table, one reviewed translation at a time.
 */
import type { LocaleCode } from './index'

export type TermKind =
  | 'campus'
  | 'period'
  | 'mode'
  | 'level'
  | 'faculty'
  | 'assessmentType'
  | 'hurdle'
  | 'requisiteType'
  | 'connector'
  | 'activityType'
  | 'duration'

type Dictionary = Record<string, string>

// --- campuses -------------------------------------------------------------

const zhCampus: Dictionary = {
  'Clayton': 'Clayton 校区',
  'Caulfield': 'Caulfield 校区',
  'Peninsula': 'Peninsula 校区',
  'Parkville': 'Parkville 校区',
  'Gippsland': 'Gippsland',
  'City (Melbourne)': '墨尔本市区',
  'Australia (Other)': '澳大利亚（其他地点）',
  'Malaysia': '马来西亚校区',
  'Malaysia (Other)': '马来西亚（其他地点）',
  'Indonesia': '印度尼西亚',
  'Singapore': '新加坡',
  'Hong Kong': '香港',
  'Prato': '普拉托（意大利）',
  'Suzhou (SEU)': '苏州（东南大学）',
  'Overseas': '海外',
  'Monash Online': 'Monash Online（在线）',
  'Monash Medical Centre': 'Monash Medical Centre（医疗中心）',
  'Monash Suzhou Research Institute': 'Monash 苏州研究院',
  'Monash Medical School - Alfred Hospital': 'Monash 医学院 · Alfred 医院'
}

// --- teaching periods -----------------------------------------------------

const zhPeriod: Dictionary = {
  'First semester': '第一学期',
  'Second semester': '第二学期',
  'Summer semester A': '夏季学期 A',
  'Summer semester B': '夏季学期 B',
  'Winter semester': '冬季学期',
  'Full year': '全学年',
  'Full year extended': '全学年（延长）',
  'First semester (extended)': '第一学期（延长）',
  'Second semester (extended)': '第二学期（延长）',
  // "Northern" is the northern-hemisphere calendar, used by the overseas and
  // Malaysia-linked offerings — not a campus called Northern.
  'First semester (Northern)': '第一学期（北半球）',
  'Second semester (Northern)': '第二学期（北半球）',
  'Term 1': '第 1 学季',
  'Term 2': '第 2 学季',
  'Term 3': '第 3 学季',
  'Term 4': '第 4 学季',
  'Trimester 1': '第 1 学段',
  'Trimester 2': '第 2 学段',
  'Trimester 3': '第 3 学段',
  'Teaching period 1': '教学期 1',
  'Teaching period 2': '教学期 2',
  'Teaching period 3': '教学期 3',
  'Teaching period 4': '教学期 4',
  'Teaching period 5': '教学期 5',
  'Teaching period 6': '教学期 6',
  'Research quarter 1': '研究季度 1',
  'Research quarter 2': '研究季度 2',
  'Research quarter 3': '研究季度 3',
  'Research quarter 4': '研究季度 4',
  'November teaching period': '11 月教学期',
  'October intake teaching period, Malaysia campus': '10 月入学教学期（马来西亚校区）',
  'Monash Indonesia semester 2': '印尼校区第二学期',
  'Monash Indonesia term 1': '印尼校区第 1 学季',
  'Monash Indonesia term 2': '印尼校区第 2 学季',
  'Monash Indonesia term 3': '印尼校区第 3 学季',
  'Monash Indonesia term 4': '印尼校区第 4 学季',
  'Monash Indonesia term 5': '印尼校区第 5 学季',
  'Monash Indonesia semester 1': '印尼校区第一学期'
}

// --- attendance modes -----------------------------------------------------
//
// Keyed on the bracketed code rather than the sentence in front of it. The code
// is what Monash's own systems use and it has been stable across Handbook
// years; the sentence has been reworded twice, and "Flexible (FLEXIBLE)" and
// "Some activities have a choice of on-campus or online teaching activities
// (FLEXIBLE)" are the same mode written two different ways in the same year.

const zhMode: Dictionary = {
  'ON-CAMPUS': '校内授课',
  'ON-BLK': '校内授课 · 集中授课时段',
  'ON-EV': '校内授课 · 晚间',
  'ON-EV-BLK': '校内授课 · 晚间 · 集中授课时段',
  'BLOCK-ON': '校内集中授课',
  'ONLINE': '全线上授课',
  'ONLINE-BLK': '线上授课 · 集中授课时段',
  'ONLINE-EV': '线上授课 · 晚间',
  'ONL-EV-BLK': '线上授课 · 晚间 · 集中授课时段',
  'MO': 'Monash Online · 全线上',
  'BLENDED': '线上线下混合',
  'BLD-BLK': '线上线下混合 · 集中授课时段',
  'BLD-EV': '线上线下混合 · 晚间',
  'BLD-BLK-EV': '线上线下混合 · 晚间 · 集中授课时段',
  'FLEXIBLE': '灵活模式：部分活动可自选线下或线上',
  'FLX-BLK': '灵活模式 · 集中授课时段',
  'FLX-EV': '灵活模式 · 晚间',
  'IMMERSIVE': '沉浸式：教学多在课堂与校园之外进行',
  'IMMERS-BLK': '沉浸式 · 集中授课时段',
  'BLOCK-OFF': '校外集中授课',
  'DAY-OFF': '校外日间授课',
  'EVENING': '晚间授课',
  'EXT-CAND': '校外候选人（不安排常规授课）',
  'ESP-EC': '拓展学习项目 · Enhancement Centre'
}

const MODE_CODE_RE = /\(([A-Z][A-Z0-9-]*)\)\s*$/

// --- everything else ------------------------------------------------------

const zhAssessmentType: Dictionary = {
  'Written': '书面考核',
  'Exercise': '练习',
  'Quiz / Test': '小测 / 测验',
  'Project': '项目作业',
  'Examination': '考试',
  'Presentation': '口头报告',
  'Demonstration': '操作演示',
  'Artefact': '作品成果',
  'Portfolio': '作品集',
  'Performance': '表演',
  'Work integrated': '工作实践',
  'Assignment': '作业',
  'Exam': '考试',
  'Research assignment': '研究作业',
  'Essay': '论文写作',
  'Report': '报告',
  'Folio': '作品集',
  'Attendance': '出勤',
  'Participation': '课堂参与',
  'Take home exam': '居家考试',
  'Thesis': '学位论文',
  'In class test': '课堂测验',
  'Other': '其他'
}

const zhHurdle: Dictionary = {
  // A hurdle is a component you must pass regardless of your total mark. The
  // two kinds differ in what "pass" means, so they are not merged.
  'Threshold': '分数门槛',
  'Competency': '能力达标'
}

const zhRequisiteType: Dictionary = {
  'prerequisite': '先修要求',
  'prerequisites': '先修要求',
  'corequisite': '同修要求',
  'corequisites': '同修要求',
  'prohibition': '互斥课程',
  'prohibitions': '互斥课程'
}

const zhConnector: Dictionary = { AND: '且', OR: '或' }

const zhActivityType: Dictionary = {
  'Lectures': '讲座课',
  'Tutorials': '辅导课',
  'Workshops': '工作坊',
  'Laboratories': '实验课',
  'Seminars': '研讨课',
  'Applied sessions': '实践课',
  'Studio activities': '工作室课',
  'Practical activities': '实操活动',
  'Assessments': '考核'
}

// --- Japanese and Korean ----------------------------------------------------
//
// The same closed lists. Campus, period, assessment and activity wording is
// copied from ENUMS in backend/app/knowledge/glossary.py, so a filter label and
// the value on a unit card agree; test_glossary.py checks that they do.

const jaCampus: Dictionary = {
  'Clayton': 'Clayton キャンパス',
  'Caulfield': 'Caulfield キャンパス',
  'Peninsula': 'Peninsula キャンパス',
  'Parkville': 'Parkville キャンパス',
  'Gippsland': 'Gippsland',
  'City (Melbourne)': 'メルボルン市内',
  'Australia (Other)': 'オーストラリア（その他）',
  'Malaysia': 'マレーシアキャンパス',
  'Malaysia (Other)': 'マレーシア（その他）',
  'Indonesia': 'インドネシア',
  'Singapore': 'シンガポール',
  'Hong Kong': '香港',
  'Prato': 'プラート（イタリア）',
  'Suzhou (SEU)': '蘇州（東南大学）',
  'Overseas': '海外',
  'Monash Online': 'Monash Online（オンライン）',
  'Monash Medical Centre': 'Monash Medical Centre（医療センター）',
  'Monash Suzhou Research Institute': 'Monash 蘇州研究院',
  'Monash Medical School - Alfred Hospital': 'Monash 医学部・Alfred 病院'
}

const koCampus: Dictionary = {
  'Clayton': 'Clayton 캠퍼스',
  'Caulfield': 'Caulfield 캠퍼스',
  'Peninsula': 'Peninsula 캠퍼스',
  'Parkville': 'Parkville 캠퍼스',
  'Gippsland': 'Gippsland',
  'City (Melbourne)': '멜버른 시티',
  'Australia (Other)': '호주(기타)',
  'Malaysia': '말레이시아 캠퍼스',
  'Malaysia (Other)': '말레이시아(기타)',
  'Indonesia': '인도네시아',
  'Singapore': '싱가포르',
  'Hong Kong': '홍콩',
  'Prato': '프라토(이탈리아)',
  'Suzhou (SEU)': '쑤저우(둥난대)',
  'Overseas': '해외',
  'Monash Online': 'Monash Online(온라인)',
  'Monash Medical Centre': 'Monash Medical Centre(의료 센터)',
  'Monash Suzhou Research Institute': 'Monash 쑤저우 연구원',
  'Monash Medical School - Alfred Hospital': 'Monash 의과대학 · Alfred 병원'
}

const jaPeriod: Dictionary = {
  'First semester': '第1学期',
  'Second semester': '第2学期',
  'Summer semester A': 'サマーセメスター A',
  'Summer semester B': 'サマーセメスター B',
  'Winter semester': 'ウィンターセメスター',
  'Full year': '通年',
  'Full year extended': '通年（延長）',
  'First semester (extended)': '第1学期（延長）',
  'Second semester (extended)': '第2学期（延長）',
  'First semester (Northern)': '第1学期（北半球）',
  'Second semester (Northern)': '第2学期（北半球）',
  'Term 1': '第1ターム',
  'Term 2': '第2ターム',
  'Term 3': '第3ターム',
  'Term 4': '第4ターム',
  'Trimester 1': '第1トライメスター',
  'Trimester 2': '第2トライメスター',
  'Trimester 3': '第3トライメスター',
  'Teaching period 1': '開講期 1',
  'Teaching period 2': '開講期 2',
  'Teaching period 3': '開講期 3',
  'Teaching period 4': '開講期 4',
  'Teaching period 5': '開講期 5',
  'Teaching period 6': '開講期 6',
  'Research quarter 1': '研究クォーター 1',
  'Research quarter 2': '研究クォーター 2',
  'Research quarter 3': '研究クォーター 3',
  'Research quarter 4': '研究クォーター 4',
  'November teaching period': '11月開講期',
  'October intake teaching period, Malaysia campus': '10月入学開講期（マレーシアキャンパス）',
  'Monash Indonesia semester 2': 'インドネシア校 第2学期',
  'Monash Indonesia term 1': 'インドネシア校 第1ターム',
  'Monash Indonesia term 2': 'インドネシア校 第2ターム',
  'Monash Indonesia term 3': 'インドネシア校 第3ターム',
  'Monash Indonesia term 4': 'インドネシア校 第4ターム',
  'Monash Indonesia term 5': 'インドネシア校 第5ターム',
  'Monash Indonesia semester 1': 'インドネシア校 第1学期'
}

const koPeriod: Dictionary = {
  'First semester': '1학기',
  'Second semester': '2학기',
  'Summer semester A': '여름 학기 A',
  'Summer semester B': '여름 학기 B',
  'Winter semester': '겨울 학기',
  'Full year': '연간',
  'Full year extended': '연간(연장)',
  'First semester (extended)': '1학기(연장)',
  'Second semester (extended)': '2학기(연장)',
  'First semester (Northern)': '1학기(북반구)',
  'Second semester (Northern)': '2학기(북반구)',
  'Term 1': '1텀',
  'Term 2': '2텀',
  'Term 3': '3텀',
  'Term 4': '4텀',
  'Trimester 1': '1트라이메스터',
  'Trimester 2': '2트라이메스터',
  'Trimester 3': '3트라이메스터',
  'Teaching period 1': '수업 기간 1',
  'Teaching period 2': '수업 기간 2',
  'Teaching period 3': '수업 기간 3',
  'Teaching period 4': '수업 기간 4',
  'Teaching period 5': '수업 기간 5',
  'Teaching period 6': '수업 기간 6',
  'Research quarter 1': '연구 분기 1',
  'Research quarter 2': '연구 분기 2',
  'Research quarter 3': '연구 분기 3',
  'Research quarter 4': '연구 분기 4',
  'November teaching period': '11월 학기',
  'October intake teaching period, Malaysia campus': '10월 입학 학기(말레이시아 캠퍼스)',
  'Monash Indonesia semester 2': '인도네시아 캠퍼스 2학기',
  'Monash Indonesia term 1': '인도네시아 캠퍼스 1텀',
  'Monash Indonesia term 2': '인도네시아 캠퍼스 2텀',
  'Monash Indonesia term 3': '인도네시아 캠퍼스 3텀',
  'Monash Indonesia term 4': '인도네시아 캠퍼스 4텀',
  'Monash Indonesia term 5': '인도네시아 캠퍼스 5텀',
  'Monash Indonesia semester 1': '인도네시아 캠퍼스 1학기'
}

const jaMode: Dictionary = {
  'ON-CAMPUS': '対面授業',
  'ON-BLK': '対面授業・集中講義',
  'ON-EV': '対面授業・夜間',
  'ON-EV-BLK': '対面授業・夜間・集中講義',
  'BLOCK-ON': '学内集中講義',
  'ONLINE': '全てオンライン授業',
  'ONLINE-BLK': 'オンライン授業・集中講義',
  'ONLINE-EV': 'オンライン授業・夜間',
  'ONL-EV-BLK': 'オンライン授業・夜間・集中講義',
  'MO': 'Monash Online・全てオンライン',
  'BLENDED': '対面とオンラインの併用',
  'BLD-BLK': '対面とオンラインの併用・集中講義',
  'BLD-EV': '対面とオンラインの併用・夜間',
  'BLD-BLK-EV': '対面とオンラインの併用・夜間・集中講義',
  'FLEXIBLE': 'フレキシブル：一部は対面かオンラインを選択可',
  'FLX-BLK': 'フレキシブル・集中講義',
  'FLX-EV': 'フレキシブル・夜間',
  'IMMERSIVE': '体験型：授業の多くは教室とキャンパスの外で実施',
  'IMMERS-BLK': '体験型・集中講義',
  'BLOCK-OFF': '学外集中講義',
  'DAY-OFF': '学外・昼間授業',
  'EVENING': '夜間授業',
  'EXT-CAND': '学外在籍（通常の授業なし）',
  'ESP-EC': '拡張学習プログラム・Enhancement Centre'
}

const koMode: Dictionary = {
  'ON-CAMPUS': '대면 수업',
  'ON-BLK': '대면 수업 · 집중 수업',
  'ON-EV': '대면 수업 · 야간',
  'ON-EV-BLK': '대면 수업 · 야간 · 집중 수업',
  'BLOCK-ON': '교내 집중 수업',
  'ONLINE': '전면 온라인 수업',
  'ONLINE-BLK': '온라인 수업 · 집중 수업',
  'ONLINE-EV': '온라인 수업 · 야간',
  'ONL-EV-BLK': '온라인 수업 · 야간 · 집중 수업',
  'MO': 'Monash Online · 전면 온라인',
  'BLENDED': '대면·온라인 혼합 수업',
  'BLD-BLK': '대면·온라인 혼합 · 집중 수업',
  'BLD-EV': '대면·온라인 혼합 · 야간',
  'BLD-BLK-EV': '대면·온라인 혼합 · 야간 · 집중 수업',
  'FLEXIBLE': '유연 수업: 일부 활동은 대면·온라인 선택 가능',
  'FLX-BLK': '유연 수업 · 집중 수업',
  'FLX-EV': '유연 수업 · 야간',
  'IMMERSIVE': '몰입형: 수업 대부분이 강의실과 캠퍼스 밖에서 진행',
  'IMMERS-BLK': '몰입형 · 집중 수업',
  'BLOCK-OFF': '교외 집중 수업',
  'DAY-OFF': '교외 주간 수업',
  'EVENING': '야간 수업',
  'EXT-CAND': '교외 등록(정규 수업 없음)',
  'ESP-EC': '심화 학습 프로그램 · Enhancement Centre'
}

const jaAssessmentType: Dictionary = {
  'Written': '筆記',
  'Exercise': '演習',
  'Quiz / Test': '小テスト',
  'Project': 'プロジェクト',
  'Examination': '試験',
  'Presentation': 'プレゼンテーション',
  'Demonstration': '実技デモ',
  'Artefact': '制作物',
  'Portfolio': 'ポートフォリオ',
  'Performance': '実演',
  'Work integrated': '実務連携',
  'Assignment': '課題',
  'Exam': '試験',
  'Research assignment': '研究課題',
  'Essay': 'エッセイ',
  'Report': 'レポート',
  'Folio': '作品集',
  'Attendance': '出席',
  'Participation': '授業参加',
  'Take home exam': '持ち帰り試験',
  'Thesis': '論文',
  'In class test': '授業内テスト',
  'Other': 'その他'
}

const koAssessmentType: Dictionary = {
  'Written': '필기',
  'Exercise': '연습 과제',
  'Quiz / Test': '퀴즈 / 테스트',
  'Project': '프로젝트',
  'Examination': '시험',
  'Presentation': '발표',
  'Demonstration': '실기 시연',
  'Artefact': '제작물',
  'Portfolio': '포트폴리오',
  'Performance': '실연',
  'Work integrated': '현장 연계',
  'Assignment': '과제',
  'Exam': '시험',
  'Research assignment': '연구 과제',
  'Essay': '에세이',
  'Report': '보고서',
  'Folio': '작품집',
  'Attendance': '출석',
  'Participation': '수업 참여',
  'Take home exam': '재택 시험',
  'Thesis': '학위 논문',
  'In class test': '수업 중 테스트',
  'Other': '기타'
}

const jaHurdle: Dictionary = { 'Threshold': '最低到達点', 'Competency': '能力要件' }
const koHurdle: Dictionary = { 'Threshold': '최저 점수 요건', 'Competency': '역량 요건' }

const jaRequisiteType: Dictionary = {
  'prerequisite': '履修前提科目',
  'prerequisites': '履修前提科目',
  'corequisite': '同時履修科目',
  'corequisites': '同時履修科目',
  'prohibition': '履修不可科目',
  'prohibitions': '履修不可科目'
}

const koRequisiteType: Dictionary = {
  'prerequisite': '선수 과목',
  'prerequisites': '선수 과목',
  'corequisite': '동시 수강 과목',
  'corequisites': '동시 수강 과목',
  'prohibition': '중복 수강 불가 과목',
  'prohibitions': '중복 수강 불가 과목'
}

const jaActivityType: Dictionary = {
  'Lectures': '講義',
  'Tutorials': 'チュートリアル',
  'Workshops': 'ワークショップ',
  'Laboratories': '実験',
  'Seminars': 'セミナー',
  'Applied sessions': '実習セッション',
  'Studio activities': 'スタジオ活動',
  'Practical activities': '実技活動',
  'Assessments': '評価'
}

const koActivityType: Dictionary = {
  'Lectures': '강의',
  'Tutorials': '튜토리얼',
  'Workshops': '워크숍',
  'Laboratories': '실험',
  'Seminars': '세미나',
  'Applied sessions': '실습 세션',
  'Studio activities': '스튜디오 활동',
  'Practical activities': '실기 활동',
  'Assessments': '평가'
}

const ZH: Record<TermKind, Dictionary> = {
  campus: zhCampus,
  period: zhPeriod,
  mode: zhMode,
  level: {},
  faculty: {},
  assessmentType: zhAssessmentType,
  hurdle: zhHurdle,
  requisiteType: zhRequisiteType,
  connector: zhConnector,
  activityType: zhActivityType,
  duration: {}
}

const JA: Record<TermKind, Dictionary> = {
  campus: jaCampus,
  period: jaPeriod,
  mode: jaMode,
  level: {},
  faculty: {},
  assessmentType: jaAssessmentType,
  hurdle: jaHurdle,
  requisiteType: jaRequisiteType,
  connector: { AND: 'かつ', OR: 'または' },
  activityType: jaActivityType,
  duration: {}
}

const KO: Record<TermKind, Dictionary> = {
  campus: koCampus,
  period: koPeriod,
  mode: koMode,
  level: {},
  faculty: {},
  assessmentType: koAssessmentType,
  hurdle: koHurdle,
  requisiteType: koRequisiteType,
  connector: { AND: '그리고', OR: '또는' },
  activityType: koActivityType,
  duration: {}
}

type Translated = Exclude<LocaleCode, 'en'>

const DICTIONARIES: Record<Translated, Record<TermKind, Dictionary>> = { zh: ZH, ja: JA, ko: KO }

/** The few things each language writes around a value rather than looking up. */
const FORMS: Record<Translated, {
  level: (n: string) => string
  hours: (n: string) => string
  mode: (text: string, code: string) => string
  range: string
  alternate: string
  numbered: (n: string, type: string) => string
}> = {
  zh: {
    level: n => `第 ${n} 级`,
    hours: n => `${n} 小时`,
    mode: (text, code) => `${text}（${code}）`,
    range: '至',
    alternate: '（备选安排）',
    numbered: (n, type) => `第 ${n} 项 · ${type}`
  },
  ja: {
    level: n => `レベル ${n}`,
    hours: n => `${n} 時間`,
    mode: (text, code) => `${text}（${code}）`,
    range: '〜',
    alternate: '（別日程）',
    numbered: (n, type) => `第${n}項・${type}`
  },
  ko: {
    level: n => `레벨 ${n}`,
    hours: n => `${n}시간`,
    mode: (text, code) => `${text}(${code})`,
    range: ' ~ ',
    alternate: '(대체 일정)',
    numbered: (n, type) => `${n}번 · ${type}`
  }
}

const HOURS_RE = /^(\d+(?:\.\d+)?)\s*hours?$/i
const LEVEL_RE = /^Level\s+(\d+)$/i
/** "Second semester to First semester", "Summer semester A to First semester". */
const RANGE_SEPARATOR = ' to '
/** A handful of periods carry this suffix; it means an alternative offering. */
const ALTERNATE_SUFFIX = ' - alternate'

/**
 * One Handbook value in the reader's language, or the value itself when there is no entry.
 *
 * Falling back to the source is the whole safety property here. A missing entry
 * shows English, which is mildly annoying; a guessed entry shows confident
 * text that is wrong, which is the thing this platform cannot afford.
 */
export function handbookTerm(
  kind: TermKind,
  value: string | null | undefined,
  locale: LocaleCode
): string | null {
  if (!value) return null
  const raw = value.trim()
  if (!raw) return null
  if (locale === 'en') return raw
  const dictionaries = DICTIONARIES[locale]
  const forms = FORMS[locale]

  if (kind === 'level') {
    const level = LEVEL_RE.exec(raw)
    return level ? forms.level(level[1]!) : raw
  }

  if (kind === 'duration') {
    // "24 hours" is the Handbook's own phrase for a weekly or total time.
    const hours = HOURS_RE.exec(raw)
    return hours ? forms.hours(hours[1]!) : raw
  }

  if (kind === 'mode') {
    const code = MODE_CODE_RE.exec(raw)?.[1]
    const translated = code ? dictionaries.mode[code] : undefined
    // The code stays visible: it is what appears in WES and on the timetable.
    return translated && code ? forms.mode(translated, code) : raw
  }

  if (kind === 'period') {
    return translatePeriod(raw, locale)
  }

  return dictionaries[kind][raw] ?? raw
}

function translatePeriod(raw: string, locale: Translated): string {
  const periods = DICTIONARIES[locale].period
  const forms = FORMS[locale]
  let suffix = ''
  let body = raw
  if (body.toLowerCase().endsWith(ALTERNATE_SUFFIX)) {
    body = body.slice(0, -ALTERNATE_SUFFIX.length)
    suffix = forms.alternate
  }

  const direct = periods[body]
  if (direct) return direct + suffix

  // "X to Y" spans two periods; both halves are in the dictionary even when the
  // pair is not, and there are more possible pairs than are worth listing.
  if (body.includes(RANGE_SEPARATOR)) {
    const parts = body.split(RANGE_SEPARATOR)
    const translated = parts.map(part => periods[part.trim()])
    if (translated.every(Boolean)) return translated.join(forms.range) + suffix
  }

  return raw
}

/**
 * The Handbook's own label for an assessment item, e.g. "1 - Project".
 *
 * The label is generated: a number, a dash, and the assessment type. When the
 * tail is a type the dictionary knows, the whole thing is worth translating:
 * leaving "1 - Project" beside a type column that already reads 项目 is the
 * kind of half-translation that looks like a bug.
 *
 * Anything else is a name a faculty wrote ("Weekly Quiz", "Theory test") and is
 * left exactly as it is. Those are per-unit prose, and prose is not this file's
 * business.
 */
const NUMBERED_ASSESSMENT_RE = /^(\d+)\s*[-–]\s*(.+)$/

export function assessmentName(
  value: string | null | undefined,
  locale: LocaleCode
): string | null {
  if (!value) return null
  const raw = value.trim()
  if (locale === 'en') return raw
  const types = DICTIONARIES[locale].assessmentType

  const numbered = NUMBERED_ASSESSMENT_RE.exec(raw)
  if (!numbered) return types[raw] ?? raw

  const type = types[numbered[2]!.trim()]
  return type ? FORMS[locale].numbered(numbered[1]!, type) : raw
}

/** Convenience for a list of values, dropping the ones that are empty. */
export function handbookTerms(
  kind: TermKind,
  values: (string | null | undefined)[],
  locale: LocaleCode
): string[] {
  return values.map(v => handbookTerm(kind, v, locale)).filter((v): v is string => !!v)
}
