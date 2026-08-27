/**
 * Chinese for the Handbook's own vocabulary.
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
  'Monash Medical Centre': '莫纳什医疗中心',
  'Monash Suzhou Research Institute': '莫纳什苏州研究院',
  'Monash Medical School - Alfred Hospital': '莫纳什医学院 · 阿尔弗雷德医院'
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
  'Monash Indonesia semester 2': '莫纳什印尼第二学期',
  'Monash Indonesia term 1': '莫纳什印尼第 1 学段',
  'Monash Indonesia term 2': '莫纳什印尼第 2 学段',
  'Monash Indonesia term 3': '莫纳什印尼第 3 学段',
  'Monash Indonesia term 4': '莫纳什印尼第 4 学段'
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
  'Performance': '表演'
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

const zhFaculty: Dictionary = {
  'Faculty of Arts': '文学院',
  'Faculty of Art, Design and Architecture': '艺术、设计与建筑学院',
  'Faculty of Business and Economics': '商学与经济学院',
  'Faculty of Education': '教育学院',
  'Faculty of Engineering': '工程学院',
  'Faculty of Information Technology': '信息技术学院',
  'Faculty of Pharmacy and Pharmaceutical Sciences': '药学与制药科学学院',
  'Faculty of Science': '理学院',
  'Department of Accounting': '会计系',
  'Department of Architecture': '建筑系',
  'Department of Banking and Finance': '银行与金融系',
  'Department of Business Law and Taxation': '商法与税法系',
  'Department of Chemical and Biological Engineering': '化学与生物工程系',
  'Department of Civil and Environmental Engineering': '土木与环境工程系',
  'Department of Design': '设计系',
  'Department of Econometrics and Business Statistics': '计量经济与商业统计系',
  'Department of Economics': '经济学系',
  'Department of Electrical and Computer Systems Engineering': '电气与计算机系统工程系',
  'Department of Fine Art': '美术系',
  'Department of Management': '管理系',
  'Department of Marketing': '市场营销系',
  'Department of Materials Science and Engineering': '材料科学与工程系',
  'Department of Obstetrics and Gynaecology': '妇产科学系',
  'Department of Tourism': '旅游系',
  'School of Biological Sciences': '生物科学学院',
  'School of Biomedical Sciences': '生物医学科学学院',
  'School of Chemistry': '化学学院',
  'School of Clinical Sciences at Monash Health': '莫纳什健康临床科学学院',
  'School of Earth, Atmosphere and Environment': '地球、大气与环境学院',
  'School of Languages, Literatures, Cultures and Linguistics': '语言、文学、文化与语言学学院',
  'School of Media, Film and Journalism': '媒体、电影与新闻学院',
  'School of Philosophical, Historical and Indigenous Studies': '哲学、历史与原住民研究学院',
  'School of Physics and Astronomy': '物理与天文学院',
  'School of Primary & Allied Health Care': '初级与联合医疗保健学院',
  'School of Social Sciences': '社会科学学院',
  'Sir Zelman Cowen School of Music and Performance': 'Zelman Cowen 音乐与表演学院',
  'Eastern Health Clinical School': '东部健康临床学院',
  'Malaysia Business Law & Taxation': '马来西亚校区商法与税法',
  'Malaysia School of Arts and Social Sciences': '马来西亚校区文学与社会科学学院',
  'Malaysia School of Engineering': '马来西亚校区工程学院',
  'Malaysia School of Science': '马来西亚校区理学院',
  'Monash Business School GEMBA': '莫纳什商学院 GEMBA',
  'Monash Business School of Executive Education': '莫纳什商学院高管教育',
  'Monash Bioethics Centre': '莫纳什生物伦理中心',
  'Monash Centre for Financial Studies': '莫纳什金融研究中心',
  'Monash Indigenous Studies Centre': '莫纳什原住民研究中心',
  'Monash Sustainable Development Institute': '莫纳什可持续发展研究院',
  'Australian Centre for Jewish Civilisation': '澳大利亚犹太文明研究中心',
  'Australian Regenerative Medicine Institute': '澳大利亚再生医学研究所',
  'Centre for Health Economics': '健康经济学研究中心',
  'Victorian Heart Institute (VHI)': '维多利亚心脏研究所（VHI）',
  'Anthropology': '人类学',
  'Archaeology and Ancient History': '考古学与古代史',
  'Chinese Studies': '汉学研究',
  'Communications': '传播学',
  'Criminology': '犯罪学',
  'Critical Performance Studies': '批判表演研究',
  'European Languages': '欧洲语言',
  'Film, Screen and Culture': '电影、影像与文化',
  'History': '历史学',
  'Human Geography Anthropology & Development Studies': '人文地理、人类学与发展研究',
  'Indonesian Studies': '印尼研究',
  'Intercultural Studies': '跨文化研究',
  'Japanese Studies': '日本研究',
  'Journalism': '新闻学',
  'Korean Studies': '韩国研究',
  'Linguistics': '语言学',
  'Literary Studies': '文学研究',
  'Media': '媒体研究',
  'Philosophy': '哲学',
  'Politics and International Relations': '政治学与国际关系',
  'Sociology': '社会学',
  'Translation Studies': '翻译研究'
}

const ZH: Record<TermKind, Dictionary> = {
  campus: zhCampus,
  period: zhPeriod,
  mode: zhMode,
  level: {},
  faculty: zhFaculty,
  assessmentType: zhAssessmentType,
  hurdle: zhHurdle,
  requisiteType: zhRequisiteType,
  connector: zhConnector,
  activityType: zhActivityType
}

const LEVEL_RE = /^Level\s+(\d+)$/i
/** "Second semester to First semester", "Summer semester A to First semester". */
const RANGE_SEPARATOR = ' to '
/** A handful of periods carry this suffix; it means an alternative offering. */
const ALTERNATE_SUFFIX = ' - alternate'

/**
 * Chinese for one Handbook value, or the value itself when there is no entry.
 *
 * Falling back to the source is the whole safety property here. A missing entry
 * shows English, which is mildly annoying; a guessed entry shows confident
 * Chinese that is wrong, which is the thing this platform cannot afford.
 */
export function handbookTerm(
  kind: TermKind,
  value: string | null | undefined,
  locale: LocaleCode
): string | null {
  if (!value) return null
  const raw = value.trim()
  if (!raw) return null
  if (locale !== 'zh') return raw

  if (kind === 'level') {
    const level = LEVEL_RE.exec(raw)
    return level ? `第 ${level[1]} 级` : raw
  }

  if (kind === 'mode') {
    const code = MODE_CODE_RE.exec(raw)?.[1]
    const translated = code ? zhMode[code] : undefined
    // The code stays visible: it is what appears in WES and on the timetable.
    return translated ? `${translated}（${code}）` : raw
  }

  if (kind === 'period') {
    return translatePeriod(raw)
  }

  return ZH[kind][raw] ?? raw
}

function translatePeriod(raw: string): string {
  let suffix = ''
  let body = raw
  if (body.toLowerCase().endsWith(ALTERNATE_SUFFIX)) {
    body = body.slice(0, -ALTERNATE_SUFFIX.length)
    suffix = '（替代开课）'
  }

  const direct = zhPeriod[body]
  if (direct) return direct + suffix

  // "X to Y" spans two periods; both halves are in the dictionary even when the
  // pair is not, and there are more possible pairs than are worth listing.
  if (body.includes(RANGE_SEPARATOR)) {
    const parts = body.split(RANGE_SEPARATOR)
    const translated = parts.map(part => zhPeriod[part.trim()])
    if (translated.every(Boolean)) return translated.join(' 至 ') + suffix
  }

  return raw
}

/**
 * The Handbook's own label for an assessment item, e.g. "1 - Project".
 *
 * The label is generated: a number, a dash, and the assessment type. When the
 * tail is a type the dictionary knows, the whole thing is worth translating —
 * leaving "1 - Project" beside a 类型 column that already reads 项目 is the
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
  if (locale !== 'zh') return raw

  const numbered = NUMBERED_ASSESSMENT_RE.exec(raw)
  if (!numbered) return zhAssessmentType[raw] ?? raw

  const type = zhAssessmentType[numbered[2]!.trim()]
  return type ? `第 ${numbered[1]} 项 · ${type}` : raw
}

/** Convenience for a list of values, dropping the ones that are empty. */
export function handbookTerms(
  kind: TermKind,
  values: (string | null | undefined)[],
  locale: LocaleCode
): string[] {
  return values.map(v => handbookTerm(kind, v, locale)).filter((v): v is string => !!v)
}
