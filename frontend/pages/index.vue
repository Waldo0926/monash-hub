<script setup lang="ts">
/**
 * Home: a search box and eight entries, with the next dates at the student's
 * campus and the systems people log into beside them. Under that, the guides
 * for this part of the semester, the 马莫百科 block, and one unit per faculty.
 *
 * For a signed-in reader it also carries the notification list, because the
 * point of being told your question was answered is that you see it without
 * going looking for it.
 *
 * The campus switch (Malaysia / Australia) drives the key dates, the season
 * guides, the systems and the example units. The Handbook has different units
 * at each campus - Business at Malaysia is ACW/MKW, at Clayton ACC/MKC - so one
 * list could not be right for both.
 */
import { MONASH_SYSTEMS } from '~/data/systems'
import type { KeyDates } from '~/utils/keyDates'
import { SEASON_GUIDES, SEASON_LIMIT, pickSeason } from '~/utils/season'

const config = useRuntimeConfig()
const { $t } = useNuxtApp()
const { locale } = useLocale()
const { withYear } = useHandbookYear()
const query = ref('')

const campus = useCookie<'malaysia' | 'australia'>('mh_home_campus', {
  default: () => 'malaysia',
  maxAge: 60 * 60 * 24 * 365,
  sameSite: 'lax',
  path: '/'
})
if (campus.value !== 'malaysia' && campus.value !== 'australia') campus.value = 'malaysia'

// One unit per faculty when nobody has searched for one there yet.
const EXAMPLES: Record<string, { code: string; area: Record<'en' | 'zh', string> }[]> = {
  malaysia: [
    { code: 'FIT1045', area: { en: 'Information Technology', zh: '信息技术' } },
    { code: 'MKW1120', area: { en: 'Business', zh: '商学' } },
    { code: 'ENG1011', area: { en: 'Engineering', zh: '工程' } },
    { code: 'AMU1010', area: { en: 'Arts and Media', zh: '文学与传媒' } },
    { code: 'SCI1020', area: { en: 'Science', zh: '理学' } },
    { code: 'PSY1011', area: { en: 'Psychology', zh: '心理学' } },
    { code: 'BPS1011', area: { en: 'Pharmacy', zh: '药学' } },
    { code: 'NUT1021', area: { en: 'Health Sciences', zh: '健康科学' } }
  ],
  australia: [
    { code: 'FIT1045', area: { en: 'Information Technology', zh: '信息技术' } },
    { code: 'MKC1200', area: { en: 'Business', zh: '商学' } },
    { code: 'ENG1011', area: { en: 'Engineering', zh: '工程' } },
    { code: 'ATS1125', area: { en: 'Arts and Media', zh: '文学与传媒' } },
    { code: 'SCI1020', area: { en: 'Science', zh: '理学' } },
    { code: 'PSY1011', area: { en: 'Psychology', zh: '心理学' } },
    { code: 'LAW1111', area: { en: 'Law', zh: '法学' } },
    { code: 'MED1100', area: { en: 'Medicine', zh: '医学' } }
  ]
}
const examples = computed(() => EXAMPLES[campus.value]!)

const AUSTRALIA = new Set(['Clayton', 'Caulfield', 'Peninsula', 'Parkville'])
const atCampus = (campusRaw: string | null | undefined) =>
  campus.value === 'malaysia' ? campusRaw === 'Malaysia' : AUSTRALIA.has(campusRaw ?? '')

// The dates use the same path as KeyDatesCard, so both read one fetch.
const datesFetch = useLocalisedApiFetch<KeyDates>(
  () => `/v1/key-dates?campus=${campus.value}&limit=8`,
  { watch: [campus] }
)
const popularFetch = useApiFetch<any>('/v1/search/popular?limit=20')
const [{ data: dates }, { data: searched }] = await Promise.all([datesFetch, popularFetch])

const season = computed(() => (dates.value ? pickSeason(dates.value.items, dates.value.today) : 'term'))
const seasonSlugs = computed(() => SEASON_GUIDES[campus.value][season.value].join(','))

const CODE = /^(?:[A-Z]{3}\d{4}|[A-Z]\d{4})$/
const UNIT_CODE = /^[A-Z]{3}\d{4}$/
const searchedTerms = computed(() => ((searched.value?.terms ?? []) as { label: string }[]).map(t => t.label))
const hotCodes = computed(() => searchedTerms.value.filter(t => UNIT_CODE.test(t)))
// The API takes at most 20 codes; the examples go first so they always load.
const unitCodes = computed(() =>
  [...new Set([...examples.value.map(e => e.code), ...hotCodes.value])].slice(0, 20).join(',')
)

const unitsFetch = useLocalisedApiFetch<any>(() => `/v1/units?codes=${unitCodes.value}`, { watch: [campus, unitCodes] })
const guidesFetch = useLocalisedApiFetch<any>(() => `/v1/guides?slugs=${seasonSlugs.value}`, { watch: [seasonSlugs] })
const [{ data: units }, { data: guides }] = await Promise.all([unitsFetch, guidesFetch])

const seasonGuides = computed(() => (guides.value?.results ?? []).slice(0, SEASON_LIMIT))

// Each faculty row shows the most searched unit from that faculty taught at
// this campus, or the fixed example when there is none. A searched unit that is
// already another row's example is left where it is.
const unitRows = computed(() => {
  const byCode = new Map<string, any>((units.value?.results ?? []).map((u: any) => [u.unit_code, u]))
  const exampleCodes = new Set(examples.value.map(e => e.code))
  const hot = hotCodes.value
    .filter(code => !exampleCodes.has(code))
    .map(code => byCode.get(code))
    .filter((u: any) => u && u.offerings.some((o: any) => atCampus(o.campus_raw)))
  const taken = new Set<string>()
  return examples.value.flatMap(({ code, area }) => {
    const example = byCode.get(code)
    if (!example) return []
    const swap = hot.find((u: any) => u.faculty_raw === example.faculty_raw && !taken.has(u.unit_code))
    const unit = swap ?? example
    taken.add(unit.unit_code)
    return [{ unit, area: locale.value === 'zh' ? area.zh : area.en }]
  })
})

const PERIOD_ORDER = ['S1', 'S2', 'SA', 'SB', 'W', 'OCT', 'FY']
function periodsHere(unit: any): string[] {
  const shorts = unit.offerings
    .filter((o: any) => atCampus(o.campus_raw))
    .map((o: any) => o.short)
    .filter((s: string | null) => s && /^[A-Z]{1,3}\d{0,2}$/.test(s))
  const rank = (s: string) => (PERIOD_ORDER.includes(s) ? PERIOD_ORDER.indexOf(s) : PERIOD_ORDER.length)
  return [...new Set<string>(shorts)].sort((a, b) => rank(a) - rank(b) || a.localeCompare(b))
}

const COPY = {
  en: {
    hero: 'Find units, check policies, plan your degree',
    description: 'Monash units, degrees, official guides and planning tools, read from the Handbook and monash.edu.',
    placeholder: 'FIT2004, special consideration, census date…',
    popular: 'Try',
    unitsTitle: 'Units across the faculties',
    exam: 'exam',
    noExam: 'no exam',
    cp: 'cp',
    assessments: 'assessments'
  },
  zh: {
    hero: '查课程、查政策、排选课',
    description: 'Monash 的课程、学位、官方指南和选课工具，数据来自 Handbook 和 Monash 官网。',
    placeholder: 'FIT2004、特殊考虑、census date…',
    popular: '试试搜',
    unitsTitle: '各学院的课程',
    exam: '有考试',
    noExam: '无考试',
    cp: '学分',
    assessments: '项考核'
  }
}
const c = computed(() => (locale.value === 'zh' ? COPY.zh : COPY.en))

const ENTRIES = [
  { to: '/units', key: 'units', icon: 'book' },
  { to: '/courses', key: 'courses', icon: 'degree' },
  { to: '/plan', key: 'plan', icon: 'columns' },
  { to: '/tree', key: 'tree', icon: 'tree' },
  { to: '/marks', key: 'marks', icon: 'percent' },
  { to: '/guides', key: 'guides', icon: 'page' },
  { to: '/community', key: 'community', icon: 'chat' },
  { to: '/fees', key: 'fees', icon: 'calendar' }
]

// One phrase per line under each entry title.
const hintLines = (key: string) => $t(`home.toolHint.${key}`).split(/[、，]|, /).map(l => l.trim()).filter(Boolean)

const systems = computed(() =>
  campus.value === 'malaysia' ? MONASH_SYSTEMS : MONASH_SYSTEMS.filter(s => s.appliesTo === 'all')
)

const exampleTerms = computed(() => [
  { query: 'C2001', text: 'C2001', code: true },
  { query: 'FIT2102', text: 'FIT2102', code: true },
  { query: 'Special consideration', text: locale.value === 'zh' ? '特殊考虑' : 'Special consideration' },
  { query: 'WAM', text: 'WAM/GPA' },
  { query: 'Student visa', text: locale.value === 'zh' ? '学生签证' : 'Student visa' },
  { query: 'Exchange', text: locale.value === 'zh' ? '交换' : 'Exchange' }
])
// Three real terms read as a list; one or two read as an oddity.
const liveTerms = computed(() => searchedTerms.value.length >= 3)
const popularTerms = computed(() =>
  liveTerms.value
    ? searchedTerms.value.slice(0, 6).map(label => ({ query: label, text: label, code: CODE.test(label) }))
    : exampleTerms.value
)
const popularLabel = computed(() => (liveTerms.value ? $t('home.searchedLately') : c.value.popular))

function search(value: string) {
  if (value) navigateTo({ path: '/search', query: { q: value } })
}

useSeoMeta({
  title: () => $t('home.title'),
  description: () => c.value.description,
  ogTitle: 'Monash Hub',
  ogDescription: () => c.value.description,
  ogUrl: config.public.siteUrl
})
useHead({ link: [{ rel: 'canonical', href: config.public.siteUrl }] })
</script>

<template>
  <div class="container">
    <p v-if="$route.query.closed" class="closed-note small" role="status">
      {{ $t('profile.close.done') }}
    </p>

    <section class="hero">
      <div class="hero-main">
        <h1>{{ c.hero }}</h1>
        <SearchInput v-model="query" big autofocus :placeholder="c.placeholder" @submit="search" />
        <p class="often tiny">
          <span class="muted">{{ popularLabel }}</span>
          <button
            v-for="term in popularTerms"
            :key="term.query"
            class="term"
            :class="{ mono: term.code }"
            @click="search(term.query)"
          >
            {{ term.text }}
          </button>
        </p>
        <nav class="tools" :aria-label="$t('nav.tools')">
          <NuxtLink v-for="item in ENTRIES" :key="item.to" :to="item.to" class="tool">
            <span class="tool-icon"><PlanIcon :name="item.icon" :size="26" /></span>
            <span class="tool-text">
              <b>{{ $t(`nav.${item.key}`) }}</b>
              <span class="tool-hint">
                <span v-for="line in hintLines(item.key)" :key="line">{{ line }}</span>
              </span>
            </span>
          </NuxtLink>
        </nav>
      </div>
      <div class="hero-side">
        <KeyDatesCard v-model:campus="campus" :show-sources="false" />
        <section class="systems-box" aria-labelledby="systems-title">
          <h2 id="systems-title">{{ $t('home.systems') }}</h2>
          <ul class="systems">
            <li v-for="s in systems" :key="s.url">
              <a :href="s.url" target="_blank" rel="noopener external">
                {{ s.name }}<PlanIcon name="external" :size="13" />
              </a>
            </li>
          </ul>
        </section>
      </div>
    </section>

    <NotificationPanel class="notifications" />

    <section v-if="seasonGuides.length" class="sec sec--season" aria-labelledby="season-title">
      <div class="sec-head">
        <h2 id="season-title">{{ $t(`home.season.${season}`) }}</h2>
        <NuxtLink to="/guides" class="more small">{{ $t('home.allGuides') }}</NuxtLink>
      </div>
      <ul class="guides">
        <li v-for="page in seasonGuides" :key="page.slug">
          <NuxtLink :to="`/guides/${page.slug}`">
            <span class="gt">{{ page.title }}</span>
            <span class="gm tiny muted">{{ $t(`category.${page.category}`) }}</span>
          </NuxtLink>
        </li>
      </ul>
    </section>

    <MamoIntro class="mamo-block" />

    <section class="sec" aria-labelledby="units-title">
      <div class="sec-head">
        <h2 id="units-title">{{ c.unitsTitle }}</h2>
        <NuxtLink to="/units" class="more small">{{ $t('home.allUnits') }}</NuxtLink>
      </div>
      <ul v-if="unitRows.length" class="units">
        <li v-for="{ unit, area } in unitRows" :key="unit.unit_code" class="unit">
          <NuxtLink
            :to="{ path: '/units', query: { faculty: unit.faculty_raw } }"
            class="area small"
            :title="$t('home.facultyUnits', { faculty: unit.faculty || area })"
          >
            {{ area }}
          </NuxtLink>
          <NuxtLink :to="withYear(`/units/${unit.unit_code}`)" class="unit-link">
            <span class="code mono">{{ unit.unit_code }}</span>
            <span class="title">{{ unit.title }}</span>
            <span class="periods">
              <span v-for="p in periodsHere(unit)" :key="p" class="tag mono">{{ p }}</span>
            </span>
            <span class="meta tiny muted">
              {{ unit.credit_points }} {{ c.cp }} · {{ unit.assessment_count }} {{ c.assessments }}
              <template v-if="unit.has_exam === true"> · <b>{{ c.exam }}</b></template>
              <template v-else-if="unit.has_exam === false"> · {{ c.noExam }}</template>
            </span>
          </NuxtLink>
        </li>
      </ul>
      <EmptyState v-else :title="$t('home.noUnits')" :hint="$t('home.noUnitsHint')" />
    </section>
  </div>
</template>

<style scoped>
.closed-note {
  margin: var(--s4) 0 0; padding: var(--s3) var(--s4);
  border-radius: var(--radius-sm); background: var(--success-bg); color: var(--success);
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr);
  gap: clamp(32px, 5vw, 72px);
  align-items: stretch;
  padding-block: clamp(16px, 4vw, 48px) var(--s6);
}
/* Both columns end on the same line: the entry tiles and the systems box take
   up whatever height the other column leaves. */
.hero-main { display: flex; flex-direction: column; }
.hero h1 {
  margin: 0 0 var(--s5);
  font-size: clamp(1.9rem, 1.2rem + 2.4vw, 2.9rem);
  line-height: 1.16;
  letter-spacing: -0.02em;
}
.often { display: flex; flex-wrap: wrap; align-items: center; gap: var(--s1) var(--s4); margin: var(--s3) 0 0; }
.term {
  padding: 0;
  border: 0;
  border-bottom: 1px solid var(--border-strong);
  background: none;
  color: var(--muted);
  font: inherit;
  font-size: 0.875rem;
  cursor: pointer;
}
.term:hover { color: var(--brand); border-color: var(--brand); }

.notifications { margin-bottom: var(--s6); }

.sec { padding-block: var(--s6) var(--s7); border-top: 1px solid var(--border); }
.sec--season { padding-top: var(--s4); border-top: 0; }
.sec h2 { margin: 0 0 var(--s4); }
.sec-head { display: flex; align-items: baseline; justify-content: space-between; gap: var(--s4); flex-wrap: wrap; margin-bottom: var(--s4); }
.sec-head h2 { margin: 0; }
.more { color: var(--brand); white-space: nowrap; }

.tools {
  flex: 1 1 auto;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  grid-auto-rows: 1fr;
  gap: var(--s2);
  margin-top: var(--s6);
}
.tool {
  display: grid;
  justify-items: center;
  align-content: start;
  row-gap: var(--s3);
  padding: var(--s6) var(--s3) var(--s5);
  text-align: center;
  border-radius: 12px;
  background: var(--surface-2);
  color: inherit;
  transition: background-color 0.15s;
}
.tool:hover { background: var(--blue-50); text-decoration: none; }
.tool:hover b { color: var(--brand-700); }
.tool-icon {
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: var(--surface);
  color: var(--brand);
  box-shadow: var(--shadow-sm), 0 0 0 1px var(--border);
}
.tool-text { display: grid; gap: 4px; }
.tool b { font-size: 1.05rem; font-weight: 600; line-height: 1.3; }
.tool-hint { display: grid; color: var(--muted); font-size: 0.85rem; line-height: 1.5; }

.guides { margin: 0; padding: 0; list-style: none; border-top: 1px solid var(--ink); }
.guides li { border-bottom: 1px solid var(--border); }
.guides a { display: flex; align-items: baseline; justify-content: space-between; gap: var(--s4); padding: var(--s3) 0; color: inherit; }
.guides a:hover { text-decoration: none; }
.guides a:hover .gt { color: var(--brand); }
.gt { font-weight: 500; }
.gm { white-space: nowrap; }

.hero-side { display: grid; grid-template-rows: auto 1fr; gap: var(--s4); }
.systems-box {
  padding: var(--s4) var(--s5);
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--surface);
}
.systems-box h2 { margin: 0 0 var(--s3); font-family: var(--font); font-size: 0.95rem; font-weight: 600; }
.systems { display: flex; flex-wrap: wrap; gap: var(--s2); margin: 0; padding: 0; list-style: none; }
.systems a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 34px;
  padding: 0 var(--s3);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  color: var(--text);
  font-size: 0.875rem;
}
.systems a:hover { border-color: var(--brand); color: var(--brand); text-decoration: none; }
.systems a .icon { color: var(--muted-2); }

.mamo-block { margin-bottom: var(--s7); }

.units { margin: 0; padding: 0; list-style: none; border-top: 1px solid var(--ink); }
.unit {
  display: grid;
  grid-template-columns: 9em minmax(0, 1fr);
  gap: var(--s4);
  align-items: baseline;
  border-bottom: 1px solid var(--border);
}
.area { padding: 14px 0; color: var(--muted); }
.area:hover { color: var(--brand); }
.unit-link {
  display: grid;
  grid-template-columns: 6.5em minmax(0, 1fr) minmax(0, 9em) 14em;
  gap: var(--s4);
  align-items: baseline;
  padding: 14px 0;
  color: inherit;
}
.unit-link:hover { text-decoration: none; background: linear-gradient(90deg, var(--blue-50), transparent 70%); }
.unit-link:hover .title { color: var(--brand-700); }
.code { color: var(--brand-700); font-weight: 500; }
.title { font-weight: 500; }
.periods { display: flex; flex-wrap: wrap; gap: var(--s1); }
.tag { padding: 1px 8px; border-radius: var(--radius-pill); background: var(--blue-50); color: var(--brand-700); font-size: 0.75rem; white-space: nowrap; }
.meta { text-align: right; font-variant-numeric: tabular-nums; }
.meta b { color: var(--soon); font-weight: 500; }

@media (max-width: 1040px) {
  .unit-link { grid-template-columns: 6.5em minmax(0, 1fr) auto; }
  .meta { display: none; }
}
@media (max-width: 860px) {
  .hero { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .tools { gap: var(--s4) var(--s2); margin-top: var(--s5); }
  .tool {
    align-content: start;
    row-gap: 6px;
    padding: 0;
    background: none;
    text-align: center;
  }
  .tool:hover { background: none; }
  .tool-icon { width: 48px; height: 48px; border-radius: 14px; background: var(--surface-2); box-shadow: none; }
  .tool:hover .tool-icon { background: var(--blue-50); }
  .tool b { font-size: 0.8rem; font-weight: 500; }
  .tool-hint { display: none; }
  .unit { grid-template-columns: 1fr; gap: 0; }
  .area { padding: var(--s3) 0 0; }
  .unit-link { grid-template-columns: auto minmax(0, 1fr); gap: 2px var(--s3); padding-top: 2px; }
  .title { grid-column: 1 / -1; grid-row: 2; }
  .periods { grid-column: 2; grid-row: 1; justify-content: flex-end; }
  .guides a { flex-direction: column; gap: 2px; }
  .systems-box { padding: var(--s4); }
}
@media (prefers-reduced-motion: reduce) {
  .tool { transition: none; }
}
</style>
