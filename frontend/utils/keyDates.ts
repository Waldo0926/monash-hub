/**
 * Wording and date formatting for the key dates, shared by the home-page card
 * and the /dates page so the two always say the same thing.
 *
 * Every date comes from /v1/key-dates, which reads the official date pages; only
 * the labels are written here. Holiday names are a closed list per language: a
 * name that is not in it is shown in the source's own English.
 */
export type KeyDate = {
  date: string
  end: string | null
  kind: string
  period: string | null
  name: string | null
  /** "17:00", only where the official page prints a time. */
  time?: string | null
  source: string
}
export type KeyDates = {
  campus: string
  today: string
  items: KeyDate[]
  sources: Record<string, { title: string; url: string; last_checked: string | null }>
}

export const KEY_DATE_TEXT = {
  en: {
    title: 'Key dates',
    campus: { malaysia: 'Malaysia', australia: 'Australia' },
    kind: {
      census: 'Census date',
      withdraw: 'Last day to withdraw, or Withdrawn Fail applies',
      teaching_end: 'Teaching ends, last day to withdraw',
      swot_vac: 'Swot vac',
      exams: 'Final assessments',
      results: 'Results released',
      holiday: 'University closed',
      allocate_pref_open: 'Allocate+ preference entry opens',
      allocate_pref_close: 'Allocate+ preference entry closes',
      allocate_adjust_open: 'Allocate+ timetable adjustment opens',
      allocate_adjust_close: 'Allocate+ timetable adjustment closes',
      wes_open: 'WES opens for first enrolment'
    } as Record<string, string>,
    period: { 'S1-01': 'Semester 1', 'S2-01': 'Semester 2', 'OCT-MY-01': 'October intake' } as Record<string, string>,
    today: 'today',
    inDays: (n: number) => (n === 1 ? 'tomorrow' : `in ${n} days`),
    daysAway: (n: number) => (n === 1 ? 'day away' : 'days away'),
    underway: 'underway',
    source: 'Source',
    checked: 'checked',
    empty: 'Dates are not available right now. The official pages are linked below.',
    switcher: 'Campus',
    viewAll: 'All key dates',
    pageTitle: 'Key dates',
    pageLead: 'Census, withdrawal, Allocate+ timetable, WES enrolment, swot vac, exam and results dates for the main teaching periods, and the days the university is closed. Read from the official Monash date pages.',
    periods: { malaysia: 'Semester 1, Semester 2 and the October intake', australia: 'Semester 1 and Semester 2' },
    periodsLabel: 'Teaching periods shown: ',
    otherPeriods: 'Summer, winter, Monash Online and other teaching periods are on the official pages below.',
    showHolidays: 'Show days the university is closed',
    month: (y: number, m: number) => `${['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][m - 1]} ${y}`,
    count: (n: number) => `${n} upcoming`
  },
  zh: {
    title: '重要日期',
    campus: { malaysia: '马来西亚', australia: '澳洲' },
    kind: {
      census: 'Census date（学籍统计日）',
      withdraw: '退课最后一天，之后记 Withdrawn Fail',
      teaching_end: '教学结束，最后退课日',
      swot_vac: '复习周 Swot vac',
      exams: '期末考核',
      results: '公布成绩',
      holiday: '学校休息',
      allocate_pref_open: 'Allocate+ 开始填上课时间偏好',
      allocate_pref_close: 'Allocate+ 填时间偏好截止',
      allocate_adjust_open: 'Allocate+ 开放调整课表',
      allocate_adjust_close: 'Allocate+ 调整课表截止',
      wes_open: 'WES 开放选课（新生首次选课）'
    } as Record<string, string>,
    period: { 'S1-01': '第一学期', 'S2-01': '第二学期', 'OCT-MY-01': '十月入学' } as Record<string, string>,
    today: '今天',
    inDays: (n: number) => (n === 1 ? '明天' : `${n} 天后`),
    daysAway: () => '天后',
    underway: '进行中',
    source: '来源',
    checked: '核对于',
    empty: '暂时取不到日期，下面是官方页面的链接。',
    switcher: '校区',
    viewAll: '查看全部日期',
    pageTitle: '重要日期',
    pageLead: '主要教学期的 Census、退课、Allocate+ 排课、WES 选课、复习周、考试和公布成绩日期，以及学校休息日。全部从 Monash 官方日期页面读取。',
    periods: { malaysia: '第一学期、第二学期、十月入学', australia: '第一学期、第二学期' },
    periodsLabel: '列出的教学期：',
    otherPeriods: '夏季、冬季、Monash Online 等其他教学期请看下面的官方页面。',
    showHolidays: '显示学校休息日',
    month: (y: number, m: number) => `${y}年${m}月`,
    count: (n: number) => `接下来 ${n} 项`
  },
  ja: {
    title: '重要な日程',
    campus: { malaysia: 'マレーシア', australia: 'オーストラリア' },
    kind: {
      census: 'Census date（在籍確定日）',
      withdraw: '履修取消の最終日、以降は Withdrawn Fail',
      teaching_end: '授業終了、履修取消の最終日',
      swot_vac: '試験準備期間 Swot vac',
      exams: '期末評価',
      results: '成績発表',
      holiday: '大学休業日',
      allocate_pref_open: 'Allocate+ 希望時間の登録開始',
      allocate_pref_close: 'Allocate+ 希望時間の登録締切',
      allocate_adjust_open: 'Allocate+ 時間割の調整開始',
      allocate_adjust_close: 'Allocate+ 時間割の調整締切',
      wes_open: 'WES 履修登録開始（初回登録）'
    } as Record<string, string>,
    period: { 'S1-01': '第1学期', 'S2-01': '第2学期', 'OCT-MY-01': '10月入学' } as Record<string, string>,
    today: '今日',
    inDays: (n: number) => (n === 1 ? '明日' : `${n} 日後`),
    daysAway: () => '日後',
    underway: '実施中',
    source: '出典',
    checked: '確認日',
    empty: '日程を取得できません。下に公式ページのリンクがあります。',
    switcher: 'キャンパス',
    viewAll: 'すべての日程',
    pageTitle: '重要な日程',
    pageLead: '主な学期の Census、履修取消、Allocate+ の時間割、WES の履修登録、試験準備期間、試験、成績発表の日程と大学休業日です。Monash の公式日程ページから読み取っています。',
    periods: { malaysia: '第1学期、第2学期、10月入学', australia: '第1学期、第2学期' },
    periodsLabel: '表示している学期：',
    otherPeriods: '夏期、冬期、Monash Online などほかの学期は下の公式ページを見てください。',
    showHolidays: '大学休業日も表示',
    month: (y: number, m: number) => `${y}年${m}月`,
    count: (n: number) => `今後 ${n} 件`
  },
  ko: {
    title: '주요 일정',
    campus: { malaysia: '말레이시아', australia: '호주' },
    kind: {
      census: 'Census date(등록 확정일)',
      withdraw: '수강 철회 마감일, 이후에는 Withdrawn Fail',
      teaching_end: '수업 종료, 수강 철회 마감일',
      swot_vac: '시험 준비 기간 Swot vac',
      exams: '기말 평가',
      results: '성적 발표',
      holiday: '대학 휴무일',
      allocate_pref_open: 'Allocate+ 선호 시간 입력 시작',
      allocate_pref_close: 'Allocate+ 선호 시간 입력 마감',
      allocate_adjust_open: 'Allocate+ 시간표 조정 시작',
      allocate_adjust_close: 'Allocate+ 시간표 조정 마감',
      wes_open: 'WES 수강 신청 시작(첫 등록)'
    } as Record<string, string>,
    period: { 'S1-01': '1학기', 'S2-01': '2학기', 'OCT-MY-01': '10월 입학' } as Record<string, string>,
    today: '오늘',
    inDays: (n: number) => (n === 1 ? '내일' : `${n}일 후`),
    daysAway: () => '일 후',
    underway: '진행 중',
    source: '출처',
    checked: '확인일',
    empty: '지금은 일정을 불러올 수 없습니다. 아래에 공식 페이지 링크가 있습니다.',
    switcher: '캠퍼스',
    viewAll: '전체 일정',
    pageTitle: '주요 일정',
    pageLead: '주요 학기의 Census, 수강 철회, Allocate+ 시간표, WES 수강 신청, 시험 준비 기간, 시험, 성적 발표 일정과 대학 휴무일입니다. Monash 공식 일정 페이지에서 읽어 옵니다.',
    periods: { malaysia: '1학기, 2학기, 10월 입학', australia: '1학기, 2학기' },
    periodsLabel: '표시하는 학기: ',
    otherPeriods: '하계, 동계, Monash Online 등 다른 학기는 아래 공식 페이지를 확인하세요.',
    showHolidays: '대학 휴무일도 표시',
    month: (y: number, m: number) => `${y}년 ${m}월`,
    count: (n: number) => `앞으로 ${n}건`
  }
}
export type KeyDateLang = keyof typeof KEY_DATE_TEXT

// Closed list. A holiday name that is not here is shown in the source's own
// English rather than approximated.
const HOLIDAYS_ZH: [RegExp, string][] = [
  [/silver jubilee/i, '雪兰莪苏丹登基银禧'],
  [/birthday of the sultan/i, '雪兰莪苏丹诞辰'],
  [/deepavali/i, '屠妖节 Deepavali'],
  [/christmas/i, '圣诞节'],
  [/boxing day/i, '节礼日'],
  [/new year's day/i, '元旦'],
  [/chinese new year/i, '农历新年'],
  [/thaipusam/i, '大宝森节'],
  [/nuzul/i, '古兰经降示日'],
  [/aidilfitri/i, '开斋节'],
  [/hari raya haji/i, '哈芝节'],
  [/labour day/i, '劳动节'],
  [/wesak/i, '卫塞节'],
  [/king's birthday/i, '最高元首诞辰'],
  [/awal muharram/i, '回历新年'],
  [/prophet muhammad/i, '先知穆罕默德诞辰'],
  [/national day/i, '国庆日'],
  [/malaysia day/i, '马来西亚日'],
  [/good friday/i, '耶稣受难日'],
  [/easter/i, '复活节'],
  [/anzac/i, 'Anzac Day'],
  [/grand final/i, 'AFL 总决赛前一天']
]

const HOLIDAYS_JA: [RegExp, string][] = [
  [/silver jubilee/i, 'セランゴール州スルタン即位25周年'],
  [/birthday of the sultan/i, 'セランゴール州スルタン誕生日'],
  [/deepavali/i, 'ディパバリ Deepavali'],
  [/christmas/i, 'クリスマス'],
  [/boxing day/i, 'ボクシング・デー'],
  [/new year's day/i, '元日'],
  [/chinese new year/i, '旧正月'],
  [/thaipusam/i, 'タイプーサム'],
  [/nuzul/i, 'ヌズル・アル＝クルアーン'],
  [/aidilfitri/i, 'ハリラヤ・プアサ'],
  [/hari raya haji/i, 'ハリラヤ・ハジ'],
  [/labour day/i, 'メーデー'],
  [/wesak/i, 'ウェサック・デー'],
  [/king's birthday/i, '国王誕生日'],
  [/awal muharram/i, 'イスラム暦新年'],
  [/prophet muhammad/i, '預言者ムハンマド生誕祭'],
  [/national day/i, '独立記念日'],
  [/malaysia day/i, 'マレーシア・デー'],
  [/good friday/i, '聖金曜日'],
  [/easter/i, 'イースター'],
  [/anzac/i, 'Anzac Day'],
  [/grand final/i, 'AFL グランドファイナル前日']
]
const HOLIDAYS_KO: [RegExp, string][] = [
  [/silver jubilee/i, '슬랑오르 술탄 즉위 25주년'],
  [/birthday of the sultan/i, '슬랑오르 술탄 탄신일'],
  [/deepavali/i, '디파발리 Deepavali'],
  [/christmas/i, '크리스마스'],
  [/boxing day/i, '박싱 데이'],
  [/new year's day/i, '신정'],
  [/chinese new year/i, '설날'],
  [/thaipusam/i, '타이푸삼'],
  [/nuzul/i, '쿠란 계시일'],
  [/aidilfitri/i, '하리 라야 푸아사'],
  [/hari raya haji/i, '하리 라야 하지'],
  [/labour day/i, '노동절'],
  [/wesak/i, '웨삭 데이'],
  [/king's birthday/i, '국왕 탄신일'],
  [/awal muharram/i, '이슬람력 새해'],
  [/prophet muhammad/i, '예언자 무함마드 탄신일'],
  [/national day/i, '독립기념일'],
  [/malaysia day/i, '말레이시아의 날'],
  [/good friday/i, '성금요일'],
  [/easter/i, '부활절'],
  [/anzac/i, 'Anzac Day'],
  [/grand final/i, 'AFL 그랜드 파이널 전날']
]
const HOLIDAYS: Partial<Record<KeyDateLang, [RegExp, string][]>> = { zh: HOLIDAYS_ZH, ja: HOLIDAYS_JA, ko: HOLIDAYS_KO }

export function keyDateLabel(item: KeyDate, lang: KeyDateLang): { main: string; sub: string | null } {
  const t = KEY_DATE_TEXT[lang]
  if (item.kind === 'holiday') {
    const name = item.name || ''
    const names = HOLIDAYS[lang]
    if (names) {
      const hit = names.find(([re]) => re.test(name))
      return { main: hit ? hit[1] : name, sub: hit ? name : null }
    }
    return { main: name, sub: null }
  }
  const period = item.period ? (t.period[item.period] ?? item.period) : ''
  // The time goes beside the period rather than the date, so the date column
  // keeps its width.
  const sub = [period, item.time].filter(Boolean).join(' · ')
  return { main: t.kind[item.kind] ?? item.kind, sub: sub || null }
}

export const MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
export function parts(iso: string) {
  const [y, m, d] = iso.split('-').map(Number) as [number, number, number]
  return { y, m, d }
}
export function dayNumber(iso: string) {
  const p = parts(iso)
  return Date.UTC(p.y, p.m - 1, p.d) / 86_400_000
}
/** `today` decides whether the year is printed: only dates outside it carry one. */
export function keyDateRange(item: KeyDate, lang: KeyDateLang, today: string | undefined): string {
  const a = parts(item.date)
  const b = item.end ? parts(item.end) : null
  const thisYear = parts(today ?? item.date).y
  const withYear = a.y !== thisYear || (b !== null && b.y !== thisYear)
  if (lang === 'zh' || lang === 'ja') {
    const yr = (p: typeof a) => (withYear ? `${p.y}年` : '')
    if (!b) return `${yr(a)}${a.m}月${a.d}日`
    if (a.m === b.m && a.y === b.y) return `${yr(a)}${a.m}月${a.d}–${b.d}日`
    return `${yr(a)}${a.m}月${a.d}日–${yr(b)}${b.m}月${b.d}日`
  }
  if (lang === 'ko') {
    const yr = (p: typeof a) => (withYear ? `${p.y}년 ` : '')
    if (!b) return `${yr(a)}${a.m}월 ${a.d}일`
    if (a.m === b.m && a.y === b.y) return `${yr(a)}${a.m}월 ${a.d}–${b.d}일`
    return `${yr(a)}${a.m}월 ${a.d}일 – ${yr(b)}${b.m}월 ${b.d}일`
  }
  const yr = (p: typeof a) => (withYear ? ` ${p.y}` : '')
  if (!b) return `${a.d} ${MONTHS_EN[a.m - 1]}${yr(a)}`
  if (a.m === b.m && a.y === b.y) return `${a.d}–${b.d} ${MONTHS_EN[a.m - 1]}${yr(a)}`
  return `${a.d} ${MONTHS_EN[a.m - 1]}${yr(a)} – ${b.d} ${MONTHS_EN[b.m - 1]}${yr(b)}`
}

/** The most recent check across the source pages, as a short date. */
export function checkedOnLabel(
  sources: { last_checked: string | null }[], lang: KeyDateLang
): string {
  const times = sources.map(s => s.last_checked).filter(Boolean) as string[]
  if (!times.length) return ''
  const p = parts(times.sort().at(-1)!.slice(0, 10))
  if (lang === 'ko') return `${p.m}월 ${p.d}일`
  return lang === 'en' ? `${p.d} ${MONTHS_EN[p.m - 1]}` : `${p.m}月${p.d}日`
}
