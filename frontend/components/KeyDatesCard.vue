<script setup lang="ts">
/**
 * What is coming up at the student's campus: census and withdrawal deadlines,
 * the end of teaching, swot vac, exams, results and public holidays.
 *
 * Every row comes from /v1/key-dates, which reads the official date pages the
 * index already holds. Nothing here is typed in by hand except the wording, and
 * the card says which pages the dates came from and when they were checked -
 * a deadline without a source is a rumour.
 *
 * Days remaining are counted from the date the API reports for the campus, not
 * from the browser's clock, so the server and the client render the same number
 * and a student abroad sees the campus's today.
 */
type KeyDate = {
  date: string
  end: string | null
  kind: string
  period: string | null
  name: string | null
  source: string
}
type KeyDates = {
  campus: string
  today: string
  items: KeyDate[]
  sources: Record<string, { title: string; url: string; last_checked: string | null }>
}

const campus = defineModel<'malaysia' | 'australia'>('campus', { required: true })
const { locale } = useLocale()
const lang = computed(() => (['zh', 'ja', 'ko'].includes(locale.value) ? locale.value : 'en') as Lang)

// The source titles come back in the page's language, so the fetch carries it.
const { data, error } = await useLocalisedApiFetch<KeyDates>(
  () => `/v1/key-dates?campus=${campus.value}&limit=6`,
  { watch: [campus] }
)

const TEXT = {
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
      holiday: 'University closed'
    } as Record<string, string>,
    period: { 'S1-01': 'Semester 1', 'S2-01': 'Semester 2', 'OCT-MY-01': 'October intake' } as Record<string, string>,
    today: 'today',
    inDays: (n: number) => (n === 1 ? 'tomorrow' : `in ${n} days`),
    daysAway: (n: number) => (n === 1 ? 'day away' : 'days away'),
    underway: 'underway',
    source: 'Source',
    checked: 'checked',
    empty: 'Dates are not available right now. The official pages are linked below.',
    switcher: 'Campus'
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
      holiday: '学校休息'
    } as Record<string, string>,
    period: { 'S1-01': '第一学期', 'S2-01': '第二学期', 'OCT-MY-01': '十月入学' } as Record<string, string>,
    today: '今天',
    inDays: (n: number) => (n === 1 ? '明天' : `${n} 天后`),
    daysAway: () => '天后',
    underway: '进行中',
    source: '来源',
    checked: '核对于',
    empty: '暂时取不到日期，下面是官方页面的链接。',
    switcher: '校区'
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
      holiday: '大学休業日'
    } as Record<string, string>,
    period: { 'S1-01': '第1学期', 'S2-01': '第2学期', 'OCT-MY-01': '10月入学' } as Record<string, string>,
    today: '今日',
    inDays: (n: number) => (n === 1 ? '明日' : `${n} 日後`),
    daysAway: () => '日後',
    underway: '実施中',
    source: '出典',
    checked: '確認日',
    empty: '日程を取得できません。下に公式ページのリンクがあります。',
    switcher: 'キャンパス'
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
      holiday: '대학 휴무일'
    } as Record<string, string>,
    period: { 'S1-01': '1학기', 'S2-01': '2학기', 'OCT-MY-01': '10월 입학' } as Record<string, string>,
    today: '오늘',
    inDays: (n: number) => (n === 1 ? '내일' : `${n}일 후`),
    daysAway: () => '일 후',
    underway: '진행 중',
    source: '출처',
    checked: '확인일',
    empty: '지금은 일정을 불러올 수 없습니다. 아래에 공식 페이지 링크가 있습니다.',
    switcher: '캠퍼스'
  }
}
type Lang = keyof typeof TEXT
const t = computed(() => TEXT[lang.value])

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
const HOLIDAYS: Partial<Record<Lang, [RegExp, string][]>> = { zh: HOLIDAYS_ZH, ja: HOLIDAYS_JA, ko: HOLIDAYS_KO }

function label(item: KeyDate): { main: string; sub: string | null } {
  if (item.kind === 'holiday') {
    const name = item.name || ''
    const names = HOLIDAYS[lang.value]
    if (names) {
      const hit = names.find(([re]) => re.test(name))
      return { main: hit ? hit[1] : name, sub: hit ? name : null }
    }
    return { main: name, sub: null }
  }
  const period = item.period ? (t.value.period[item.period] ?? item.period) : ''
  return { main: t.value.kind[item.kind] ?? item.kind, sub: period || null }
}

const MONTHS_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
function parts(iso: string) {
  const [y, m, d] = iso.split('-').map(Number) as [number, number, number]
  return { y, m, d }
}
function day(iso: string) {
  const p = parts(iso)
  return Date.UTC(p.y, p.m - 1, p.d) / 86_400_000
}
function range(item: KeyDate): string {
  const a = parts(item.date)
  const b = item.end ? parts(item.end) : null
  const thisYear = parts(data.value?.today ?? item.date).y
  const withYear = a.y !== thisYear || (b !== null && b.y !== thisYear)
  if (lang.value === 'zh' || lang.value === 'ja') {
    const yr = (p: typeof a) => (withYear ? `${p.y}年` : '')
    if (!b) return `${yr(a)}${a.m}月${a.d}日`
    if (a.m === b.m && a.y === b.y) return `${yr(a)}${a.m}月${a.d}–${b.d}日`
    return `${yr(a)}${a.m}月${a.d}日–${yr(b)}${b.m}月${b.d}日`
  }
  if (lang.value === 'ko') {
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
function when(item: KeyDate): string {
  const today = day(data.value!.today)
  if (day(item.date) <= today) return t.value.underway
  const n = day(item.date) - today
  return t.value.inDays(n)
}

const rows = computed(() =>
  (data.value?.items ?? []).map(item => ({ item, ...label(item), range: range(item), when: when(item) }))
)
const next = computed(() => {
  const first = data.value?.items[0]
  if (!first) return null
  const today = day(data.value!.today)
  const n = day(first.date) - today
  return { n: Math.max(n, 0), underway: n <= 0, ...label(first), range: range(first) }
})

const sources = computed(() => Object.values(data.value?.sources ?? {}))
const checkedOn = computed(() => {
  const times = sources.value.map(s => s.last_checked).filter(Boolean) as string[]
  if (!times.length) return ''
  const latest = times.sort().at(-1)!.slice(0, 10)
  const p = parts(latest)
  if (lang.value === 'ko') return `${p.m}월 ${p.d}일`
  return lang.value === 'en' ? `${p.d} ${MONTHS_EN[p.m - 1]}` : `${p.m}月${p.d}日`
})

const options = ['malaysia', 'australia'] as const
</script>

<template>
  <aside class="dates" aria-labelledby="dates-title">
    <div class="head">
      <h2 id="dates-title">{{ t.title }}</h2>
      <div class="seg" role="group" :aria-label="t.switcher">
        <button
          v-for="option in options"
          :key="option"
          type="button"
          :aria-pressed="campus === option"
          @click="campus = option"
        >
          {{ t.campus[option] }}
        </button>
      </div>
    </div>

    <template v-if="next && !error">
      <p class="count">
        <b v-if="!next.underway">{{ next.n }}</b>
        <span class="count-text">
          <template v-if="next.underway">{{ t.underway }}</template>
          <template v-else>{{ t.daysAway(next.n) }}</template>
          <small>{{ next.main }}<template v-if="next.sub"> · {{ next.sub }}</template></small>
        </span>
      </p>

      <ol class="list">
        <li v-for="(row, i) in rows" :key="`${row.item.date}-${row.item.kind}-${row.item.period}-${row.item.name}`" :class="{ first: i === 0 }">
          <span class="d mono">{{ row.range }}</span>
          <span class="what">
            {{ row.main }}
            <small v-if="row.sub">{{ row.sub }}</small>
          </span>
          <span class="when">{{ row.when }}</span>
        </li>
      </ol>
    </template>
    <p v-else class="muted small empty">{{ t.empty }}</p>

    <p class="src tiny muted">
      <template v-if="sources.length">{{ t.source }}:
        <template v-for="(s, i) in sources" :key="s.url">
          <a :href="s.url" rel="noopener external" target="_blank">{{ s.title }}</a><template v-if="i < sources.length - 1"> · </template>
        </template>
        <template v-if="checkedOn"> · {{ t.checked }} {{ checkedOn }}</template>
      </template>
    </p>
  </aside>
</template>

<style scoped>
.dates {
  padding: var(--s5) var(--s5) var(--s4);
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--surface);
}
.head { display: flex; align-items: center; justify-content: space-between; gap: var(--s3); flex-wrap: wrap; }
.head h2 { margin: 0; font-family: var(--font); font-size: 0.95rem; font-weight: 600; }
.seg { display: inline-flex; padding: 2px; border: 1px solid var(--border-strong); border-radius: var(--radius-pill); }
.seg button {
  min-height: 28px;
  padding: 0 var(--s3);
  border: 0;
  border-radius: var(--radius-pill);
  background: none;
  color: var(--muted);
  font: inherit;
  font-size: 0.8rem;
  cursor: pointer;
}
.seg button[aria-pressed='true'] { background: var(--ink); color: var(--text-inverse); }

.count { display: flex; align-items: baseline; gap: var(--s3); margin: var(--s4) 0 var(--s3); }
.count b {
  font-family: var(--font-display);
  font-size: 3.2rem;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.03em;
  font-variant-numeric: tabular-nums;
}
.count-text { display: grid; color: var(--muted); }
.count-text small { color: var(--text); font-size: 0.9rem; font-weight: 500; }

.list { list-style: none; margin: 0; padding: 0; }
.list li {
  display: grid;
  grid-template-columns: 7.6em minmax(0, 1fr) auto;
  gap: var(--s3);
  align-items: baseline;
  padding: 10px 0;
  border-top: 1px solid var(--border);
  font-size: 0.92rem;
}
.d { color: var(--muted); font-size: 0.8rem; font-variant-numeric: tabular-nums; }
.what small { display: block; color: var(--muted-2); font-size: 0.78rem; }
.when { color: var(--muted-2); font-size: 0.78rem; white-space: nowrap; font-variant-numeric: tabular-nums; }
.list li.first .what { font-weight: 600; }
.list li.first .when { color: var(--soon); font-weight: 500; }

.empty { margin: var(--s4) 0 0; }
.src { margin: var(--s3) 0 0; }
.src a { color: inherit; border-bottom: 1px solid var(--border-strong); }
.src a:hover { color: var(--text); text-decoration: none; }

@media (max-width: 520px) {
  .dates { padding: var(--s4); }
  .list li { grid-template-columns: 1fr auto; row-gap: 0; }
  .d { grid-column: 1; }
  .when { grid-column: 2; grid-row: 1; }
  .what { grid-column: 1 / -1; }
}
</style>
