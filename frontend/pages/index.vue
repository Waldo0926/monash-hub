<script setup lang="ts">
/**
 * Home answers three questions above the fold and nothing else: what is this,
 * where do I search, and what is coming up for me. Everything below is a way
 * in: the eight tools, one example unit per faculty, the guides most used at
 * this point in the semester, and the community.
 *
 * For a signed-in reader it also carries the notification list, because the
 * point of being told your question was answered is that you see it without
 * going looking for it.
 *
 * The campus switch (Malaysia / Australia) drives both the key dates and the
 * example units. Exchange students go the other way, and the Handbook has
 * different units at each campus - Business at Malaysia is ACW/MKW, at Clayton
 * ACC/MKC - so one list could not be right for both.
 */
const config = useRuntimeConfig()
const { $t, $term } = useNuxtApp()
const { locale } = useLocale()
const { withYear } = useHandbookYear()
const query = ref('')
const sectionItems = useSectionNavigation()

const campus = useCookie<'malaysia' | 'australia'>('mh_home_campus', {
  default: () => 'malaysia',
  maxAge: 60 * 60 * 24 * 365,
  sameSite: 'lax',
  path: '/'
})
if (campus.value !== 'malaysia' && campus.value !== 'australia') campus.value = 'malaysia'

// One example unit per faculty. Not "most searched": there is not yet enough
// traffic for that to mean anything, and a ranking built on the founder's own
// testing would show one faculty to everyone.
const EXAMPLES: Record<string, { code: string; area: { en: string; zh: string } }[]> = {
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

const { data: units } = await useLocalisedApiFetch<any>(
  () => `/v1/units?codes=${examples.value.map(e => e.code).join(',')}`,
  { watch: [campus] }
)
// The pages students open at this point in the semester, named rather than
// searched for: a category query returns whatever sorts first.
const GUIDE_SLUGS = {
  malaysia: [
    'malaysia-special-consideration', 'supporting-documents', 'final-assessment-dates',
    'dates-timetables-start-times', 'results-release', 'malaysia-frequent-asked-questions-faq-exam-results'
  ],
  australia: [
    'special-consideration', 'supporting-documents', 'final-assessment-dates',
    'dates-timetables-start-times', 'results-release', 'extensions-special-consideration-spec-con-extensio'
  ]
}
const { data: guides } = await useLocalisedApiFetch<any>(
  () => `/v1/guides?slugs=${GUIDE_SLUGS[campus.value].join(',')}`,
  { watch: [campus] }
)
const { data: posts } = await useApiFetch<any>('/v1/community/posts?limit=4')

const unitRows = computed(() => {
  const byCode = new Map<string, any>((units.value?.results ?? []).map((u: any) => [u.unit_code, u]))
  return examples.value.flatMap(({ code, area }) => {
    const unit = byCode.get(code)
    return unit ? [{ unit, area: locale.value === 'zh' ? area.zh : area.en }] : []
  })
})
function campusesOf(unit: any): string[] {
  return [...new Set<string>(unit.offerings.map((o: any) => o.campus))].filter(Boolean)
}

// The home copy is deliberately concrete. English and Chinese are the two
// actively maintained marketing copies; the other locales keep the interface
// translations that already existed and fall back to English for the rest.
const COPY = {
  en: {
    eyebrow: 'Student-run · not affiliated with Monash',
    heroBefore: 'Units and policies, with the ',
    heroEm: 'source',
    heroAfter: ' attached.',
    lead: 'Handbook units, official Monash pages and student experience, kept apart. Every entry says where it came from and when it was last checked.',
    placeholder: 'FIT2004, special consideration, census date…',
    popular: 'Often searched',
    startHere: 'Start here',
    unitsTitle: 'Units across the faculties',
    unitsLead: 'One unit from each, as a way in. Search covers every unit in the Handbook.',
    exam: 'exam',
    noExam: 'no exam',
    cp: 'cp',
    assessments: 'assessments',
    guidesTitle: 'Assessment and results',
    guidesLead: 'Extensions, special consideration, exam timetables and results.',
    checked: 'checked',
    community: 'Community',
    communityLead: 'Ask what official pages cannot answer: workload, exams, which units pair well.',
    ask: 'Ask a question',
    trust: [
      ['Weekly', 'Every unit and degree re-synced from handbook.monash.edu'],
      ['Every 6 hours', 'Official Monash pages checked for changes'],
      ['2025–2027', 'Three Handbook years, so you can check by your intake year'],
      ['4 languages', '中文 · English · 日本語 · 한국어']
    ],
    hints: {
      '/units': 'Assessment, requisites, where and when it runs',
      '/guides': 'Special consideration, census dates, visas',
      '/tree': 'What a unit needs first, and what it unlocks',
      '/plan': 'Lay out semesters, checked against each year’s Handbook',
      '/courses': 'Structure, core units and majors',
      '/marks': 'Type marks in, or read them from a transcript screenshot',
      '/community': 'Ask, and hear from students who took it',
      '/mamo': 'Life and admin at the Malaysia campus'
    } as Record<string, string>
  },
  zh: {
    eyebrow: '学生自建 · 非 Monash 官方',
    heroBefore: '查课程、查政策，每条都有',
    heroEm: '出处',
    heroAfter: '。',
    lead: 'Handbook 课程、Monash 官方页面和同学的经验分开放。每条信息都写明来自哪里、最后什么时候核对过。',
    placeholder: 'FIT2004、特殊考虑、census date…',
    popular: '常搜',
    startHere: '从这里开始',
    unitsTitle: '各学院的课程',
    unitsLead: '每个学院放一门，当作入口。搜索能查 Handbook 里的全部课程。',
    exam: '有考试',
    noExam: '无考试',
    cp: '学分',
    assessments: '项考核',
    guidesTitle: '考核与成绩',
    guidesLead: '延期、特殊考虑、考试时间表和成绩。',
    checked: '核对于',
    community: '社区',
    communityLead: '官方页面答不了的，在这里问同学：学习负担、考试、哪些课搭着上。',
    ask: '提一个问题',
    trust: [
      ['每周', '从 handbook.monash.edu 同步全部课程和学位'],
      ['每 6 小时', '核对一次 Monash 官方页面有没有改动'],
      ['2025–2027', '三年 Handbook 都在，按入学年份查'],
      ['4 种语言', '中文 · English · 日本語 · 한국어']
    ],
    hints: {
      '/units': '考核方式、先修要求、哪个校区哪学期开',
      '/guides': '特殊考虑、Census date、学生签证',
      '/tree': '一门课要先修什么，修完能解锁什么',
      '/plan': '按学期排课，按当年 Handbook 检查先修',
      '/courses': '学位结构、必修课和专业方向',
      '/marks': '手动输入，或上传成绩单截图识别',
      '/community': '提问，看同学怎么说',
      '/mamo': '马来西亚校区的生活和办事'
    } as Record<string, string>
  }
}
const c = computed(() => (locale.value === 'zh' ? COPY.zh : COPY.en))
const marketing = computed(() => locale.value === 'en' || locale.value === 'zh')

const ORDER = ['/units', '/guides', '/tree', '/plan', '/courses', '/marks', '/community', '/mamo']
const directory = computed(() =>
  ORDER.flatMap(to => {
    const item = sectionItems.value.find(i => i.to === to)
    return item ? [{ ...item, hint: c.value.hints[to] }] : []
  })
)

const popularTerms = computed(() =>
  [
    { query: 'C2001', text: 'C2001', code: true },
    { query: 'FIT2102', text: 'FIT2102', code: true },
    { query: 'Special consideration', text: locale.value === 'zh' ? '特殊考虑' : 'Special consideration' },
    { query: 'WAM', text: 'WAM/GPA' },
    { query: 'Student visa', text: locale.value === 'zh' ? '学生签证' : 'Student visa' },
    { query: 'Exchange', text: locale.value === 'zh' ? '交换' : 'Exchange' }
  ]
)

const searchPlaceholder = computed(() => (marketing.value ? c.value.placeholder : $t('search.placeholder')))

function search(value: string) {
  if (value) navigateTo({ path: '/search', query: { q: value } })
}

function shortDate(iso: string | null): string {
  if (!iso) return ''
  const [, m, d] = iso.slice(0, 10).split('-').map(Number) as [number, number, number]
  const en = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return locale.value === 'zh' ? `${m}月${d}日` : `${d} ${en[m - 1]}`
}

useSeoMeta({
  title: () => $t('home.title'),
  description: () => (marketing.value ? c.value.lead : $t('home.lead')),
  ogTitle: 'Monash Hub',
  ogDescription: () => (marketing.value ? c.value.lead : $t('home.lead')),
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
        <p class="eyebrow">{{ marketing ? c.eyebrow : $t('footer.about') }}</p>
        <h1>
          <template v-if="marketing">{{ c.heroBefore }}<em>{{ c.heroEm }}</em>{{ c.heroAfter }}</template>
          <template v-else>{{ $t('home.hero') }}</template>
        </h1>
        <p class="lead">{{ marketing ? c.lead : $t('home.lead') }}</p>
        <SearchInput v-model="query" big autofocus :placeholder="searchPlaceholder" @submit="search" />
        <p class="often tiny">
          <span class="muted">{{ marketing ? c.popular : $t('home.trending') }}</span>
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
      </div>
      <KeyDatesCard v-model:campus="campus" />
    </section>

    <NotificationPanel class="notifications" />

    <ul v-if="marketing" class="trust" aria-label="Data freshness">
      <li v-for="[figure, text] in c.trust" :key="figure">
        <b>{{ figure }}</b>
        <span class="small">{{ text }}</span>
      </li>
    </ul>

    <section class="sec" aria-labelledby="start-title">
      <h2 id="start-title">{{ marketing ? c.startHere : $t('home.moreTools') }}</h2>
      <nav class="dir">
        <NuxtLink v-for="item in directory" :key="item.to" :to="item.to">
          <strong>{{ item.label }}</strong>
          <span v-if="marketing" class="small">{{ item.hint }}</span>
        </NuxtLink>
      </nav>
    </section>

    <section class="sec" aria-labelledby="units-title">
      <div class="sec-head">
        <div>
          <h2 id="units-title">{{ marketing ? c.unitsTitle : $t('home.unitsInIndex') }}</h2>
          <p v-if="marketing" class="small muted">{{ c.unitsLead }}</p>
        </div>
        <NuxtLink to="/units" class="more small">{{ $t('home.allUnits') }}</NuxtLink>
      </div>
      <div v-if="unitRows.length" class="units">
        <NuxtLink
          v-for="{ unit, area } in unitRows"
          :key="unit.unit_code"
          :to="withYear(`/units/${unit.unit_code}`)"
          class="unit"
        >
          <span class="area tiny muted">{{ area }}</span>
          <span class="code mono">{{ unit.unit_code }}</span>
          <span class="title">{{ unit.title }}</span>
          <span class="campuses">
            <span v-for="name in campusesOf(unit).slice(0, 3)" :key="name" class="tag">{{ $term('campus', name) }}</span>
            <span v-if="campusesOf(unit).length > 3" class="tag">+{{ campusesOf(unit).length - 3 }}</span>
          </span>
          <span class="meta tiny muted">
            {{ unit.credit_points }} {{ marketing ? c.cp : $t('units.creditPoints') }} ·
            {{ unit.assessment_count }} {{ marketing ? c.assessments : $t('units.assessmentItems') }}
            <template v-if="unit.has_exam === true"> · <b>{{ marketing ? c.exam : $t('units.examListed') }}</b></template>
            <template v-else-if="unit.has_exam === false"> · {{ marketing ? c.noExam : $t('units.noExamListed') }}</template>
          </span>
        </NuxtLink>
      </div>
      <EmptyState v-else :title="$t('home.noUnits')" :hint="$t('home.noUnitsHint')" />
    </section>

    <div class="sec split">
      <section aria-labelledby="guides-title">
        <div class="sec-head">
          <div>
            <h2 id="guides-title">{{ marketing ? c.guidesTitle : $t('home.officialGuides') }}</h2>
            <p v-if="marketing" class="small muted">{{ c.guidesLead }}</p>
          </div>
          <NuxtLink to="/guides" class="more small">{{ $t('home.allGuides') }}</NuxtLink>
        </div>
        <ul class="guides">
          <li v-for="page in guides?.results || []" :key="page.slug">
            <NuxtLink :to="`/guides/${page.slug}`">
              <span class="gt">{{ page.title }}</span>
              <span class="gm tiny muted">
                {{ $t(`category.${page.category}`) }} ·
                <CampusNotice :applies-to="page.applies_to" compact />
              </span>
              <span class="gd tiny muted mono">{{ marketing ? c.checked : '' }} {{ shortDate(page.last_checked) }}</span>
            </NuxtLink>
          </li>
        </ul>
      </section>

      <!-- Always rendered, empty or not. An empty forum that says nothing looks
           broken; an empty forum that asks for the first question is an invitation. -->
      <section aria-labelledby="community-title">
        <div class="sec-head">
          <h2 id="community-title">{{ marketing ? c.community : $t('home.latestDiscussions') }}</h2>
          <NuxtLink to="/community" class="more small">{{ $t('home.allDiscussions') }}</NuxtLink>
        </div>
        <div class="ask">
          <ul v-if="posts?.results?.length" class="posts">
            <li v-for="post in posts.results" :key="post.id">
              <NuxtLink :to="`/community/post/${post.id}`">
                <span class="gt">{{ post.title }}</span>
                <span class="gm tiny muted">{{ post.author || '—' }}</span>
              </NuxtLink>
            </li>
          </ul>
          <p class="small muted">{{ marketing ? c.communityLead : $t('home.communityEmptyHint') }}</p>
          <NuxtLink to="/community" class="btn btn--small">{{ marketing ? c.ask : $t('community.ask') }}</NuxtLink>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.closed-note {
  margin: var(--s4) 0 0; padding: var(--s3) var(--s4);
  border-radius: var(--radius-sm); background: var(--success-bg); color: var(--success);
}

/* Search leads on the left; the dates sit beside it, because "what is due next"
   is the second thing a student opens the site for. */
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr);
  gap: clamp(32px, 5vw, 72px);
  align-items: start;
  padding-block: clamp(16px, 4vw, 48px) clamp(32px, 5vw, 56px);
}
.eyebrow { margin: 0 0 var(--s4); color: var(--muted-2); font-size: 0.8rem; letter-spacing: 0.04em; }
.hero h1 {
  margin: 0 0 var(--s4);
  font-size: clamp(2.1rem, 1.3rem + 2.8vw, 3.3rem);
  line-height: 1.14;
  letter-spacing: -0.02em;
}
.hero h1 em { font-style: normal; color: var(--brand); }
.lead { max-width: 34em; margin: 0 0 var(--s5); color: var(--muted); font-size: 1.05rem; }
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

.trust {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--s5) var(--s6);
  margin: 0;
  padding: 0 0 var(--s7);
  list-style: none;
}
.trust li { display: grid; gap: var(--s1); align-content: start; }
.trust b { font-family: var(--font-display); font-size: 1.3rem; font-weight: 600; letter-spacing: -0.01em; }
.trust span { color: var(--muted); }

.sec { padding-block: var(--s6) var(--s7); border-top: 1px solid var(--border); }
.sec h2 { margin: 0 0 var(--s4); }
.sec-head { display: flex; align-items: baseline; justify-content: space-between; gap: var(--s4); flex-wrap: wrap; margin-bottom: var(--s4); }
.sec-head h2 { margin: 0; }
.sec-head p { margin: var(--s1) 0 0; }
.more { color: var(--brand); white-space: nowrap; }

/* The eight tools as a ruled index rather than eight boxes. The first rule is
   ink and the rest are hairlines, so the list reads as one object. */
.dir { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); column-gap: var(--s6); }
.dir a { display: block; padding: var(--s4) 0 var(--s5); border-top: 1px solid var(--border); color: inherit; }
.dir a:nth-child(-n + 4) { border-top-color: var(--ink); }
.dir a:hover { text-decoration: none; }
.dir strong { display: flex; align-items: center; gap: var(--s2); font-weight: 600; }
.dir strong::after { content: '→'; color: var(--brand); font-weight: 400; opacity: 0; transform: translateX(-4px); transition: opacity 0.15s, transform 0.15s; }
.dir a:hover strong::after { opacity: 1; transform: none; }
.dir span { display: block; margin-top: var(--s1); color: var(--muted); line-height: 1.5; }

.units { border-top: 1px solid var(--ink); }
.unit {
  display: grid;
  grid-template-columns: 9em 6.5em minmax(0, 1fr) minmax(0, 14em) 14em;
  gap: var(--s4);
  align-items: baseline;
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
  color: inherit;
}
.unit:hover { text-decoration: none; background: linear-gradient(90deg, var(--blue-50), transparent 70%); }
.code { color: var(--brand-700); font-weight: 500; }
.title { font-weight: 500; }
.campuses { display: flex; flex-wrap: wrap; gap: var(--s1); }
.tag { padding: 1px 8px; border-radius: var(--radius-pill); background: var(--blue-50); color: var(--brand-700); font-size: 0.75rem; white-space: nowrap; }
.meta { text-align: right; font-variant-numeric: tabular-nums; }
.meta b { color: var(--soon); font-weight: 500; }

.split { display: grid; grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr); gap: var(--s7); }
.guides, .posts { margin: 0; padding: 0; list-style: none; }
.guides { border-top: 1px solid var(--ink); }
.guides li { border-bottom: 1px solid var(--border); }
.guides a, .posts a { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 2px var(--s4); padding: var(--s3) 0; color: inherit; }
.guides a:hover, .posts a:hover { text-decoration: none; }
.guides a:hover .gt, .posts a:hover .gt { color: var(--brand); }
.gt { font-weight: 500; }
.gm { grid-column: 1; }
.gd { grid-column: 2; grid-row: 1 / span 2; align-self: center; text-align: right; white-space: nowrap; }
.ask { padding-top: var(--s4); border-top: 1px solid var(--ink); }
.posts { margin-bottom: var(--s4); }
.posts li { border-bottom: 1px solid var(--border); }
.ask > p { margin: 0 0 var(--s4); }

@media (max-width: 1040px) {
  .unit { grid-template-columns: 8em 6.5em minmax(0, 1fr) auto; }
  .meta { display: none; }
}
@media (max-width: 860px) {
  .hero { grid-template-columns: 1fr; }
  .trust { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .dir { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .dir a:nth-child(-n + 4) { border-top-color: var(--border); }
  .dir a:nth-child(-n + 2) { border-top-color: var(--ink); }
  .split { grid-template-columns: 1fr; gap: var(--s6); }
}
@media (max-width: 560px) {
  .dir { grid-template-columns: 1fr; }
  .dir a:nth-child(2) { border-top-color: var(--border); }
  .unit { grid-template-columns: 1fr auto; gap: 2px var(--s3); }
  .area { grid-column: 2; grid-row: 1; text-align: right; }
  .code { grid-column: 1; grid-row: 1; }
  .title { grid-column: 1 / -1; grid-row: 2; }
  .campuses { grid-column: 1 / -1; }
}
@media (prefers-reduced-motion: reduce) {
  .dir strong::after { transition: none; }
}
</style>
