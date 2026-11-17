<script setup lang="ts">
/**
 * Ways in to the unit list for someone choosing a free elective.
 *
 * Students ask the same three things about an elective: is there an exam,
 * does it need a prerequisite, and is it taught at my campus. The unit list
 * already filters on all three; this page is the shortcut, with the number of
 * units behind each link so nobody opens an empty list.
 *
 * Everything here is a Handbook filter, never a recommendation. "No exam
 * listed" and "no prerequisite listed" are what the Handbook says, and whether
 * a unit counts towards a degree is that degree's rule, so the page says both.
 *
 * The campus choice is the home page's cookie, so switching on one switches
 * the other.
 */
const config = useRuntimeConfig()
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
    lead: 'Shortcuts into the unit list for the questions people ask about electives: is there an exam, does it need a prerequisite, is it taught at my campus.',
    switcher: 'Campus',
    campus: { malaysia: 'Malaysia', australia: 'Australia' },
    byNeed: 'By what you need',
    byFaculty: 'No exam listed, by faculty',
    units: '{n} units',
    presets: {
      noExam: ['No exam listed', 'No assessment item in the Handbook is called an exam or examination. Final and mid-semester exams both count as exams; quizzes and tests do not'],
      noPrereq: ['No prerequisite listed', 'The Handbook lists no prerequisite, so no earlier unit is asked for'],
      both: ['No exam and no prerequisite listed', 'Both of the above'],
      level1: ['Level 1, no prerequisite listed', 'First-year units anyone can start with']
    },
    notesTitle: 'Before you enrol',
    notes: [
      'These are Handbook filters. "Not listed" means the Handbook does not list one; there may still be an in-semester test or an entry requirement written elsewhere on the unit page.',
      'Whether a unit counts as a free elective depends on your course. Check the course page or your course progression map, and ask your faculty when unsure.',
      'Open the unit to see when it is taught at your campus, its assessment and what students have rated it.'
    ],
    course: 'Find your course',
    all: 'All units',
    failed: 'The counts could not be loaded. The links still work.'
  },
  zh: {
    title: '找选修课',
    lead: '选选修课最常问的几件事：有没有考试、要不要先修课、自己校区开不开，这里是直接进课程列表的快捷入口',
    switcher: '校区',
    campus: { malaysia: '马来西亚', australia: '澳大利亚' },
    byNeed: '按需要找',
    byFaculty: '按学院看没列出考试的课',
    units: '{n} 门',
    presets: {
      noExam: ['没列出考试', 'Handbook的考核项目里没有叫exam或examination的，期末考和期中考都算考试，quiz和test不算'],
      noPrereq: ['没列出先修课', 'Handbook没有列出先修课，不要求先读别的课'],
      both: ['没列出考试，也没列出先修课', '同时满足上面两条'],
      level1: ['Level 1，没列出先修课', '一年级的课，谁都可以从这里开始']
    },
    notesTitle: '选课之前',
    notes: [
      '这些都是按Handbook筛出来的，“没列出”只表示Handbook没有写，学期中可能还有测验，课程页面别处也可能写了其他修读要求',
      '一门课能不能算自由选修学分，要看你自己的学位要求，先查学位页面或者course progression map，拿不准就问学院',
      '点进课程可以看它在你的校区哪个学期开、考核怎么算、同学打了多少分'
    ],
    course: '查我的学位',
    all: '全部课程',
    failed: '数量暂时加载不出来，链接可以照常点'
  }
}
const c = computed(() => (locale.value === 'zh' ? COPY.zh : COPY.en))

const AUSTRALIA = ['Clayton', 'Caulfield', 'Peninsula', 'Parkville']
const campuses = computed(() => (campus.value === 'malaysia' ? ['Malaysia'] : AUSTRALIA))

type Query = Record<string, string | string[]>
const PRESETS: { key: keyof typeof COPY.en.presets; query: Query }[] = [
  { key: 'noExam', query: { has_exam: 'false' } },
  { key: 'noPrereq', query: { no_prereq: 'true' } },
  { key: 'both', query: { has_exam: 'false', no_prereq: 'true' } },
  { key: 'level1', query: { level: 'Level 1', no_prereq: 'true' } }
]

const withCampus = (query: Query): Query => ({ campus: campuses.value, ...query })

function apiPath(query: Query) {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(withCampus(query))) {
    for (const item of Array.isArray(value) ? value : [value]) params.append(key, item)
  }
  params.set('limit', '1')
  return `/v1/units?${params.toString()}`
}

// One small request per card for its total. On the client and lazy, so the
// page and its links are there before any number is.
const totals = PRESETS.map(preset =>
  useApiFetch<any>(() => apiPath(preset.query), { watch: [campus], server: false, lazy: true })
)
const total = (index: number) => totals[index]?.data.value?.total as number | undefined
const failed = computed(() => totals.some(fetch => fetch.error.value))

// The faculties that teach a unit with no exam listed at this campus, and how many.
const facetPath = computed(() => {
  const params = new URLSearchParams({ has_exam: 'false' })
  for (const item of campuses.value) params.append('campus', item)
  return `/v1/units/facets?${params.toString()}`
})
const { data: facets } = useApiFetch<any>(() => facetPath.value, { watch: [campus], server: false, lazy: true })
// The faculty names in the reader's language, as the unit list labels them.
const { data: meta } = useLocalisedApiFetch<any>('/v1/units/filters', { server: false, lazy: true })
const { $term } = useNuxtApp()
const faculties = computed(() =>
  Object.entries((facets.value?.counts?.faculty || {}) as Record<string, number>)
    .filter(([, count]) => count > 0)
    .sort((a, b) => b[1] - a[1])
    .map(([name, count]) => ({ name, count, label: meta.value?.labels?.[name] || $term('faculty', name) || name }))
)

useSeoMeta({
  title: () => c.value.title,
  description: () => c.value.lead
})
useHead({ link: [{ rel: 'canonical', href: `${config.public.siteUrl}/electives` }] })
</script>

<template>
  <div class="container electives-page">
    <header class="head">
      <h1>{{ c.title }}</h1>
      <p class="lead">{{ c.lead }}</p>
    </header>

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

    <section aria-labelledby="by-need">
      <h2 id="by-need">{{ c.byNeed }}</h2>
      <ul class="presets">
        <li v-for="(preset, index) in PRESETS" :key="preset.key">
          <NuxtLink :to="{ path: '/units', query: withCampus(preset.query) }" class="card preset">
            <span class="name">{{ c.presets[preset.key][0] }}</span>
            <span class="why small muted">{{ c.presets[preset.key][1] }}</span>
            <span v-if="total(index) !== undefined" class="count mono small">
              {{ c.units.replace('{n}', String(total(index))) }}
            </span>
          </NuxtLink>
        </li>
      </ul>
      <p v-if="failed" class="small muted" role="status">{{ c.failed }}</p>
    </section>

    <section v-if="faculties.length" aria-labelledby="by-faculty">
      <h2 id="by-faculty">{{ c.byFaculty }}</h2>
      <ul class="faculties">
        <li v-for="faculty in faculties" :key="faculty.name">
          <NuxtLink
            :to="{ path: '/units', query: withCampus({ has_exam: 'false', faculty: faculty.name }) }"
            class="faculty"
          >
            <span>{{ faculty.label }}</span>
            <span class="mono small muted">{{ faculty.count }}</span>
          </NuxtLink>
        </li>
      </ul>
    </section>

    <section class="notes" aria-labelledby="notes-title">
      <h2 id="notes-title">{{ c.notesTitle }}</h2>
      <ul>
        <li v-for="note in c.notes" :key="note">{{ note }}</li>
      </ul>
      <p class="links small">
        <NuxtLink to="/courses">{{ c.course }} →</NuxtLink>
        <NuxtLink to="/units">{{ c.all }} →</NuxtLink>
      </p>
    </section>
  </div>
</template>

<style scoped>
.electives-page { padding-block: var(--s6) var(--s8); }
.head h1 { margin: 0 0 var(--s3); }
.lead { max-width: 40em; margin: 0 0 var(--s5); color: var(--muted); }
h2 { margin: var(--s6) 0 var(--s3); font-size: var(--fs-lg, 1.125rem); }

.seg { display: inline-flex; padding: 2px; border: 1px solid var(--border-strong); border-radius: var(--radius-pill); }
.seg button {
  min-height: 36px;
  padding: 0 var(--s4);
  border: 0;
  border-radius: var(--radius-pill);
  background: none;
  color: inherit;
  font: inherit;
  cursor: pointer;
}
.seg button[aria-pressed='true'] { background: var(--ink); color: var(--text-inverse); }

.presets, .faculties { display: grid; gap: var(--s3); margin: 0; padding: 0; list-style: none; }
.presets { grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); }
.preset { display: flex; flex-direction: column; gap: var(--s1); height: 100%; color: inherit; text-decoration: none; }
.preset:hover .name, .preset:focus-visible .name { text-decoration: underline; }
.preset .name { font-weight: 600; }
.preset .count { margin-top: auto; padding-top: var(--s2); }

.faculties { grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); }
.faculty {
  display: flex;
  justify-content: space-between;
  gap: var(--s3);
  min-height: 44px;
  align-items: center;
  padding: var(--s2) var(--s3);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: inherit;
  text-decoration: none;
}
.faculty:hover, .faculty:focus-visible { border-color: var(--border-strong); }

.notes ul { margin: 0; padding-left: 1.2em; }
.notes li { margin-bottom: var(--s2); max-width: 46em; }
.links { display: flex; flex-wrap: wrap; gap: var(--s4); margin-top: var(--s4); }
</style>
