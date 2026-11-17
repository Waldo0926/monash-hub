<script setup lang="ts">
/**
 * Finding a free elective by what students ask about it: is there an exam,
 * does it need a prerequisite, is it taught at my campus.
 *
 * The four exam colours are the unit cards' own (utils/examStatus.ts), worked
 * out from the Handbook's assessment table. Below them, two switches for "no
 * prerequisite listed" and first-year units, then a dozen undergraduate units
 * that fit, taking turns between faculties, and a link to all of them.
 *
 * Everything here is a Handbook filter, never a recommendation, and whether a
 * unit counts towards a degree is that degree's rule, so the page says both.
 * The campus is the home page's cookie; the rest is in the address.
 */
const config = useRuntimeConfig()
const route = useRoute()
const router = useRouter()
const { locale } = useLocale()
const { $t } = useNuxtApp()

const campus = useCookie<'malaysia' | 'australia'>('mh_home_campus', {
  default: () => 'malaysia',
  maxAge: 60 * 60 * 24 * 365,
  sameSite: 'lax',
  path: '/'
})
if (campus.value !== 'malaysia' && campus.value !== 'australia') campus.value = 'malaysia'

const COPY = {
  en: {
    title: 'Find an elective',
    lead: 'Filter units at your campus by exam and prerequisite.',
    switcher: 'Campus',
    campus: { malaysia: 'Malaysia', australia: 'Australia' },
    statusGroup: 'Exam',
    noPrereq: 'No prerequisite listed',
    level1: 'First year only',
    found: '{n} units',
    scope: { malaysia: 'Undergraduate units at the Malaysia campus', australia: 'Undergraduate units at the Australian campuses' },
    seeAll: 'See all {n}',
    openList: 'Open the unit list',
    empty: 'No unit at this campus fits all of this.',
    failed: 'These units could not be loaded. The full list may still work.',
    notesTitle: 'Before you enrol',
    notes: [
      'The colours come from the assessment items in the Handbook. "Not listed" means the Handbook does not list one, and the unit page has the details.',
      'Whether a unit counts as a free elective depends on your course. Check your course page or progression map, and ask your faculty when unsure.',
      'Open a unit to see when it runs at your campus and what students rated it.'
    ],
    course: 'Find your course',
    all: 'All units'
  },
  zh: {
    title: '找选修课',
    lead: '按有没有考试、要不要先修课，筛出你校区开的课',
    switcher: '校区',
    campus: { malaysia: '马来西亚', australia: '澳大利亚' },
    statusGroup: '考试',
    noPrereq: '无需先修课',
    level1: '只看一年级',
    found: '{n} 门',
    scope: { malaysia: '马来西亚校区的本科课', australia: '澳大利亚校区的本科课' },
    seeAll: '查看全部 {n} 门',
    openList: '进课程列表',
    empty: '这个校区没有同时符合这些条件的课',
    failed: '课程暂时加载不出来，可以直接进课程列表看',
    notesTitle: '选课之前',
    notes: [
      '颜色是按Handbook的考核项目分的，“没列”只表示Handbook没写，具体以课程页面为准',
      '一门课能不能算自由选修学分，要看你自己的学位要求，先查学位页面或course progression map，拿不准就问学院',
      '点进课程可以看它在你的校区哪个学期开、同学打了多少分'
    ],
    course: '查我的学位',
    all: '全部课程'
  }
}
const c = computed(() => (locale.value === 'zh' ? COPY.zh : COPY.en))

const AUSTRALIA = ['Clayton', 'Caulfield', 'Peninsula', 'Parkville']
const UNDERGRAD = ['Level 1', 'Level 2', 'Level 3']
const SAMPLE = 12

const status = computed<ExamStatus>(() =>
  (EXAM_STATUSES as readonly string[]).includes(route.query.status as string) ? (route.query.status as ExamStatus) : 'none'
)
const noPrereq = computed(() => route.query.prereq === '1')
const level1 = computed(() => route.query.level1 === '1')

function set(key: 'status' | 'prereq' | 'level1', value: string | undefined) {
  router.replace({ query: { ...route.query, show: undefined, [key]: value } })
}
const pick = (value: ExamStatus) => set('status', value === 'none' ? undefined : value)
const toggle = (key: 'prereq' | 'level1', on: boolean) => set(key, on ? undefined : '1')

type Query = Record<string, string | string[]>
// Everything except the exam colour: the counts beside the colours use this.
const base = computed<Query>(() => ({
  campus: campus.value === 'malaysia' ? ['Malaysia'] : AUSTRALIA,
  level: level1.value ? ['Level 1'] : UNDERGRAD,
  ...(noPrereq.value ? { no_prereq: 'true' } : {})
}))
const chosen = computed<Query>(() => ({ ...base.value, exam_status: status.value }))

function path(endpoint: string, query: Query, extra: Record<string, string> = {}) {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(query)) {
    for (const item of Array.isArray(value) ? value : [value]) params.append(key, item)
  }
  for (const [key, value] of Object.entries(extra)) params.set(key, value)
  return `${endpoint}?${params.toString()}`
}

// One request for all four counts, on the client so the page is there first.
const { data: facets } = useApiFetch<any>(() => path('/v1/units/facets', base.value), {
  watch: [base], server: false, lazy: true
})
const count = (value: ExamStatus) => facets.value?.counts?.exam_status?.[value] as number | undefined

const { data: sample, pending, error } = useLocalisedApiFetch<any>(
  () => path('/v1/units', chosen.value, { sort: 'mixed', limit: String(SAMPLE) }),
  { watch: [chosen], server: false, lazy: true }
)
const units = computed(() => (sample.value?.results || []) as any[])
const total = computed(() => sample.value?.total as number | undefined)
const listLink = computed(() => ({ path: '/units', query: chosen.value }))

useSeoMeta({
  title: () => c.value.title,
  description: () => c.value.lead
})
useHead({ link: [{ rel: 'canonical', href: `${config.public.siteUrl}/electives` }] })
</script>

<template>
  <div class="container electives-page">
    <header class="head">
      <div class="intro">
        <h1>{{ c.title }}</h1>
        <p class="lead">{{ c.lead }}</p>
      </div>
      <div class="seg" role="group" :aria-label="c.switcher">
        <button
          v-for="option in (['malaysia', 'australia'] as const)"
          :key="option"
          type="button"
          :aria-pressed="campus === option"
          @click="campus = option"
        >
          {{ c.campus[option] }}
        </button>
      </div>
    </header>

    <div class="panel">
      <div class="statuses" role="group" :aria-label="c.statusGroup">
        <button
          v-for="value in EXAM_STATUSES"
          :key="value"
          type="button"
          class="status"
          :class="`status--${value}`"
          :aria-pressed="status === value"
          :title="$t(`units.statusHint.${value}`)"
          @click="pick(value)"
        >
          <span class="dot" aria-hidden="true" />
          <span class="label">{{ $t(`units.status.${value}`) }}</span>
          <span v-if="count(value) !== undefined" class="n mono">{{ count(value) }}</span>
        </button>
      </div>
      <p class="hint small">{{ $t(`units.statusHint.${status}`) }}</p>
      <div class="switches">
        <button type="button" class="switch" :aria-pressed="noPrereq" @click="toggle('prereq', noPrereq)">
          <span class="box" aria-hidden="true" />{{ c.noPrereq }}
        </button>
        <button type="button" class="switch" :aria-pressed="level1" @click="toggle('level1', level1)">
          <span class="box" aria-hidden="true" />{{ c.level1 }}
        </button>
      </div>
    </div>

    <section class="sample" aria-labelledby="sample-title">
      <div class="sample-head">
        <h2 id="sample-title">
          {{ $t(`units.status.${status}`) }}
          <span v-if="total !== undefined" class="total">{{ c.found.replace('{n}', String(total)) }}</span>
        </h2>
        <p class="small muted">{{ c.scope[campus] }}</p>
      </div>

      <div v-if="pending && !units.length" class="grid" aria-busy="true">
        <div v-for="n in 6" :key="n" class="card placeholder"><Skeleton :lines="3" /></div>
      </div>
      <p v-else-if="error" class="state small muted" role="status">{{ c.failed }}</p>
      <p v-else-if="!units.length" class="state small muted" role="status">{{ c.empty }}</p>
      <div v-else class="grid">
        <UnitCard v-for="unit in units" :key="unit.unit_code" :unit="unit" />
      </div>

      <div v-if="units.length" class="more">
        <NuxtLink class="btn" :to="listLink">
          {{ total !== undefined ? c.seeAll.replace('{n}', String(total)) : c.openList }} <span aria-hidden="true">→</span>
        </NuxtLink>
      </div>
    </section>

    <section class="notes" aria-labelledby="notes-title">
      <h2 id="notes-title">{{ c.notesTitle }}</h2>
      <ul>
        <li v-for="note in c.notes" :key="note">{{ note }}</li>
      </ul>
      <div class="links">
        <NuxtLink class="btn btn--ghost btn--small" to="/courses">{{ c.course }} <span aria-hidden="true">→</span></NuxtLink>
        <NuxtLink class="btn btn--ghost btn--small" to="/units">{{ c.all }} <span aria-hidden="true">→</span></NuxtLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.electives-page { padding-block: var(--s6) var(--s8); }

.head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--s5);
  margin-bottom: var(--s5);
}
.intro { min-width: 0; }
.head h1 { margin: 0 0 var(--s2); }
.lead { margin: 0; color: var(--muted); }

.seg {
  flex: none;
  display: inline-flex;
  padding: 3px;
  border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  background: var(--surface);
}
.seg button {
  min-height: 34px;
  padding: 0 var(--s4);
  border: 0;
  border-radius: var(--radius-pill);
  background: none;
  color: var(--muted);
  font: inherit;
  font-size: 0.92rem;
  cursor: pointer;
}
.seg button[aria-pressed='true'] { background: var(--ink); color: var(--text-inverse); }

.panel {
  padding: var(--s4);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow-sm);
}
.statuses { display: flex; flex-wrap: wrap; gap: var(--s2); }
.status {
  display: inline-flex;
  align-items: center;
  gap: var(--s2);
  min-height: 40px;
  padding: 0 var(--s4);
  border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  background: var(--surface-2);
  color: var(--text);
  font: inherit;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background-color 0.15s, border-color 0.15s;
}
.status:hover { border-color: var(--border-strong); }
.status:focus-visible, .switch:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }
.status .dot { width: 9px; height: 9px; border-radius: 50%; }
.status .n { font-size: 0.8rem; color: var(--muted); }
.status--none .dot { background: var(--success); }
.status--quiz .dot { background: var(--warning); }
.status--exam .dot { background: var(--danger); }
.status--unknown .dot { background: var(--muted-2); }
.status[aria-pressed='true'] { font-weight: 600; }
.status--none[aria-pressed='true'] { background: var(--success-bg); border-color: var(--success); color: var(--success); }
.status--quiz[aria-pressed='true'] { background: var(--warning-bg); border-color: var(--warning); color: var(--warning); }
.status--exam[aria-pressed='true'] { background: var(--danger-bg); border-color: var(--danger); color: var(--danger); }
.status--unknown[aria-pressed='true'] { background: var(--surface-2); border-color: var(--muted); color: var(--text); }
.status[aria-pressed='true'] .n { color: inherit; }

.hint { margin: var(--s3) 0 0; color: var(--muted); }

.switches {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s2) var(--s5);
  margin-top: var(--s3);
  padding-top: var(--s3);
  border-top: 1px solid var(--border);
}
.switch {
  display: inline-flex;
  align-items: center;
  gap: var(--s2);
  min-height: 36px;
  padding: 0;
  border: 0;
  background: none;
  color: var(--text);
  font: inherit;
  font-size: 0.95rem;
  cursor: pointer;
}
.switch .box {
  width: 18px;
  height: 18px;
  border: 1.5px solid var(--border-strong);
  border-radius: 5px;
  background: var(--surface);
}
.switch[aria-pressed='true'] .box {
  border-color: var(--brand);
  background: var(--brand) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath d='M3.5 8.5l3 3 6-7' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center / 14px no-repeat;
}

.sample { margin-top: var(--s6); }
.sample-head { margin-bottom: var(--s4); }
.sample-head h2 { display: flex; align-items: baseline; gap: var(--s3); margin: 0 0 var(--s1); font-size: 1.2rem; }
.sample-head .total { font-family: var(--font); font-size: 0.95rem; font-weight: 500; color: var(--muted); }
.sample-head p { margin: 0; }

.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s3); }
.placeholder { padding: var(--s4); min-height: 150px; }
.state { padding: var(--s5); border: 1px dashed var(--border-strong); border-radius: var(--radius); text-align: center; }
.more { display: flex; justify-content: center; margin-top: var(--s5); }

.notes {
  margin-top: var(--s7);
  padding: var(--s5);
  border-radius: var(--radius);
  background: var(--surface-2);
}
.notes h2 { margin: 0 0 var(--s3); font-size: 1.05rem; }
.notes ul { margin: 0; padding-left: 1.2em; }
.notes li { margin-bottom: var(--s2); max-width: 52em; font-size: 0.94rem; }
.links { display: flex; flex-wrap: wrap; gap: var(--s3); margin-top: var(--s4); }

@media (max-width: 1000px) {
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .head { flex-direction: column; align-items: flex-start; gap: var(--s4); }
  .panel { padding: var(--s3); }
  /* Four colours in two rows of two on a phone, the same width each. */
  .statuses { display: grid; grid-template-columns: 1fr 1fr; }
  .status { justify-content: flex-start; padding: 0 var(--s3); }
  .status .n { margin-left: auto; }
  .grid { grid-template-columns: 1fr; }
  .grid > :nth-child(n + 7) { display: none; }
  .more .btn { width: 100%; }
}
</style>
