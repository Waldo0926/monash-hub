<script setup lang="ts">
/**
 * Ways in to the unit list for someone choosing a free elective.
 *
 * Students ask the same three things about an elective: is there an exam,
 * does it need a prerequisite, and is it taught at my campus. Pick one of the
 * four conditions and the page shows a dozen units that fit, from different
 * faculties, with a link to the full list behind it.
 *
 * Everything here is a Handbook filter, never a recommendation. "No exam
 * listed" and "no prerequisite listed" are what the Handbook says, and whether
 * a unit counts towards a degree is that degree's rule, so the page says both.
 *
 * The campus choice is the home page's cookie, so switching on one switches
 * the other. The chosen condition is in the address (?show=), so a link to
 * this page can open on it.
 */
const config = useRuntimeConfig()
const route = useRoute()
const router = useRouter()
const { locale } = useLocale()

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
    conditions: 'Conditions',
    presets: {
      noExam: ['No exam listed', 'Final and mid-semester exams both count, quizzes and tests do not'],
      noPrereq: ['No prerequisite listed', 'No earlier unit is asked for'],
      both: ['Neither listed', 'No exam and no prerequisite listed'],
      level1: ['First-year starters', 'Level 1 with no prerequisite listed']
    },
    sample: 'A few to start with',
    taught: { malaysia: 'Undergraduate units taught at the Malaysia campus', australia: 'Undergraduate units taught at an Australian campus' },
    seeAll: 'See all {n}',
    openList: 'Open the unit list',
    empty: 'No unit at this campus fits this condition.',
    failed: 'These units could not be loaded. The full list may still work.',
    notesTitle: 'Before you enrol',
    notes: [
      '"Not listed" means the Handbook does not list one. There may still be an in-semester test, or an entry requirement written elsewhere on the unit page.',
      'Whether a unit counts as a free elective depends on your course. Check your course page or progression map, and ask your faculty when unsure.',
      'Open a unit to see when it runs at your campus, how it is assessed and what students rated it.'
    ],
    course: 'Find your course',
    all: 'All units'
  },
  zh: {
    title: '找选修课',
    lead: '按有没有考试、要不要先修课，筛出你校区开的课',
    switcher: '校区',
    campus: { malaysia: '马来西亚', australia: '澳大利亚' },
    conditions: '条件',
    presets: {
      noExam: ['没列出考试', '期末、期中都算考试，quiz和test不算'],
      noPrereq: ['没列出先修课', '不要求先读过别的课'],
      both: ['两样都没列出', '没列出考试，也没列出先修课'],
      level1: ['一年级入门', 'Level 1，没列出先修课']
    },
    sample: '先看这几门',
    taught: { malaysia: '马来西亚校区开的本科课', australia: '澳大利亚校区开的本科课' },
    seeAll: '查看全部 {n} 门',
    openList: '进课程列表',
    empty: '这个校区没有符合这个条件的课',
    failed: '课程暂时加载不出来，可以直接进课程列表看',
    notesTitle: '选课之前',
    notes: [
      '“没列出”只表示Handbook没写，学期中可能还有测验，课程页面别处也可能写了其他修读要求',
      '一门课能不能算自由选修学分，要看你自己的学位要求，先查学位页面或course progression map，拿不准就问学院',
      '点进课程可以看它在你的校区哪个学期开、考核怎么算、同学打了多少分'
    ],
    course: '查我的学位',
    all: '全部课程'
  }
}
const c = computed(() => (locale.value === 'zh' ? COPY.zh : COPY.en))

const AUSTRALIA = ['Clayton', 'Caulfield', 'Peninsula', 'Parkville']
const campuses = computed(() => (campus.value === 'malaysia' ? ['Malaysia'] : AUSTRALIA))

type Query = Record<string, string | string[]>
type Key = keyof typeof COPY.en.presets
const PRESETS: { key: Key; query: Query }[] = [
  { key: 'noExam', query: { has_exam: 'false' } },
  { key: 'noPrereq', query: { no_prereq: 'true' } },
  { key: 'both', query: { has_exam: 'false', no_prereq: 'true' } },
  { key: 'level1', query: { level: 'Level 1', no_prereq: 'true' } }
]
const SAMPLE = 12

const active = computed<Key>(() =>
  PRESETS.some(p => p.key === route.query.show) ? (route.query.show as Key) : 'noExam'
)
const activePreset = computed(() => PRESETS.find(p => p.key === active.value)!)
function choose(key: Key) {
  router.replace({ query: { ...route.query, show: key === 'noExam' ? undefined : key } })
}

const withCampus = (query: Query): Query => ({ campus: campuses.value, ...query })
const listLink = (query: Query) => ({ path: '/units', query: withCampus(query) })

function apiPath(query: Query, extra: Record<string, string>) {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(withCampus(query))) {
    for (const item of Array.isArray(value) ? value : [value]) params.append(key, item)
  }
  for (const [key, value] of Object.entries(extra)) params.set(key, value)
  return `/v1/units?${params.toString()}`
}

// One small request per condition for its total. On the client and lazy, so
// the page and its links are there before any number is.
const totals = PRESETS.map(preset =>
  useApiFetch<any>(() => apiPath(preset.query, { limit: '1' }), { watch: [campus], server: false, lazy: true })
)
const total = (key: Key) => totals[PRESETS.findIndex(p => p.key === key)]?.data.value?.total as number | undefined

// The sample: a dozen units of the chosen condition, taking turns between
// faculties so it is not twelve units from one subject.
// Only undergraduate levels here: a Level 5 unit is no one's free elective.
// "See all" still opens the whole condition.
const UNDERGRAD = ['Level 1', 'Level 2', 'Level 3']
const sampleQuery = computed<Query>(() => ({ level: UNDERGRAD, ...activePreset.value.query }))
const samplePath = computed(() => apiPath(sampleQuery.value, { sort: 'mixed', limit: String(SAMPLE) }))
const { data: sample, pending, error } = useLocalisedApiFetch<any>(() => samplePath.value, {
  watch: [samplePath],
  server: false,
  lazy: true
})
const units = computed(() => (sample.value?.results || []) as any[])
const activeTotal = computed(() => total(active.value))

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

    <div class="conditions" role="group" :aria-label="c.conditions">
      <button
        v-for="preset in PRESETS"
        :key="preset.key"
        type="button"
        class="condition"
        :aria-pressed="active === preset.key"
        @click="choose(preset.key)"
      >
        <span class="name">{{ c.presets[preset.key][0] }}</span>
        <span class="count mono">
          <template v-if="total(preset.key) !== undefined">{{ total(preset.key) }}</template>
          <span v-else class="count-wait" aria-hidden="true" />
        </span>
        <span class="hint">{{ c.presets[preset.key][1] }}</span>
      </button>
    </div>

    <section class="sample" aria-labelledby="sample-title">
      <div class="sample-head">
        <div>
          <h2 id="sample-title">{{ c.presets[active][0] }} · {{ c.sample }}</h2>
          <p class="small muted">{{ c.taught[campus] }}</p>
        </div>
        <NuxtLink class="btn btn--ghost btn--small" :to="listLink(activePreset.query)">
          {{ activeTotal !== undefined ? c.seeAll.replace('{n}', String(activeTotal)) : c.openList }}
          <span aria-hidden="true">→</span>
        </NuxtLink>
      </div>

      <div v-if="pending && !units.length" class="grid" aria-busy="true">
        <div v-for="n in 6" :key="n" class="card placeholder"><Skeleton :lines="3" /></div>
      </div>
      <p v-else-if="error" class="state small muted" role="status">{{ c.failed }}</p>
      <p v-else-if="!units.length" class="state small muted" role="status">{{ c.empty }}</p>
      <div v-else class="grid">
        <UnitCard v-for="unit in units" :key="unit.unit_code" :unit="unit" />
      </div>

      <div v-if="activeTotal && units.length" class="more">
        <NuxtLink class="btn" :to="listLink(activePreset.query)">
          {{ c.seeAll.replace('{n}', String(activeTotal)) }} <span aria-hidden="true">→</span>
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

.conditions {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--s3);
}
.condition {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  grid-template-areas: 'name count' 'hint hint';
  align-content: start;
  gap: var(--s1) var(--s3);
  padding: var(--s4);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow-sm);
  color: var(--text);
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s, background-color 0.15s;
}
.condition:hover { border-color: var(--border-strong); }
.condition:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }
.condition[aria-pressed='true'] { border-color: var(--brand); background: var(--blue-50); }
.condition .name { grid-area: name; font-weight: 600; }
.condition[aria-pressed='true'] .name { color: var(--brand-700); }
.condition .count { grid-area: count; font-size: 0.92rem; color: var(--muted); }
.condition[aria-pressed='true'] .count { color: var(--brand-700); }
.count-wait {
  display: inline-block;
  width: 2.2em;
  height: 0.9em;
  border-radius: var(--radius-sm);
  background: var(--surface-2);
  vertical-align: middle;
}
.condition .hint { grid-area: hint; font-size: 0.84rem; line-height: 1.45; color: var(--muted); }

.sample { margin-top: var(--s6); }
.sample-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--s4);
  margin-bottom: var(--s4);
}
.sample-head h2 { margin: 0 0 var(--s1); font-size: 1.2rem; }
.sample-head p { margin: 0; }
.sample-head .btn { flex: none; }

.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s3); }
.grid :deep(.unit) { height: 100%; }
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
.notes ul { margin: 0; padding-left: 1.2em; color: var(--text); }
.notes li { margin-bottom: var(--s2); max-width: 52em; font-size: 0.94rem; }
.links { display: flex; flex-wrap: wrap; gap: var(--s3); margin-top: var(--s4); }

@media (max-width: 1000px) {
  .conditions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .head { flex-direction: column; align-items: flex-start; gap: var(--s4); }
  .grid { grid-template-columns: 1fr; }
  /* Six is enough on a phone; the button below opens the rest. */
  .grid > :nth-child(n + 7) { display: none; }
  .sample-head { flex-direction: column; align-items: flex-start; gap: var(--s3); }
  .condition { padding: var(--s3); }
}
</style>
