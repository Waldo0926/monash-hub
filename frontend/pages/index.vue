<script setup lang="ts">
/**
 * Home answers four questions above the fold: what is this, where do I search,
 * what else can I do here, and what is coming up for me. Everything below is a
 * way in: one example unit per faculty, the guides most used at this point in
 * the semester, and the community.
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
const EXAMPLES: Record<string, { code: string; area: Record<'en' | 'zh' | 'ja' | 'ko', string> }[]> = {
  malaysia: [
    { code: 'FIT1045', area: { en: 'Information Technology', zh: '信息技术', ja: '情報技術', ko: '정보기술' } },
    { code: 'MKW1120', area: { en: 'Business', zh: '商学', ja: 'ビジネス', ko: '경영학' } },
    { code: 'ENG1011', area: { en: 'Engineering', zh: '工程', ja: '工学', ko: '공학' } },
    { code: 'AMU1010', area: { en: 'Arts and Media', zh: '文学与传媒', ja: '人文・メディア', ko: '인문·미디어' } },
    { code: 'SCI1020', area: { en: 'Science', zh: '理学', ja: '理学', ko: '이학' } },
    { code: 'PSY1011', area: { en: 'Psychology', zh: '心理学', ja: '心理学', ko: '심리학' } },
    { code: 'BPS1011', area: { en: 'Pharmacy', zh: '药学', ja: '薬学', ko: '약학' } },
    { code: 'NUT1021', area: { en: 'Health Sciences', zh: '健康科学', ja: '健康科学', ko: '보건과학' } }
  ],
  australia: [
    { code: 'FIT1045', area: { en: 'Information Technology', zh: '信息技术', ja: '情報技術', ko: '정보기술' } },
    { code: 'MKC1200', area: { en: 'Business', zh: '商学', ja: 'ビジネス', ko: '경영학' } },
    { code: 'ENG1011', area: { en: 'Engineering', zh: '工程', ja: '工学', ko: '공학' } },
    { code: 'ATS1125', area: { en: 'Arts and Media', zh: '文学与传媒', ja: '人文・メディア', ko: '인문·미디어' } },
    { code: 'SCI1020', area: { en: 'Science', zh: '理学', ja: '理学', ko: '이학' } },
    { code: 'PSY1011', area: { en: 'Psychology', zh: '心理学', ja: '心理学', ko: '심리학' } },
    { code: 'LAW1111', area: { en: 'Law', zh: '法学', ja: '法学', ko: '법학' } },
    { code: 'MED1100', area: { en: 'Medicine', zh: '医学', ja: '医学', ko: '의학' } }
  ]
}
const examples = computed(() => EXAMPLES[campus.value]!)

// The three home-page fetches are independent, so they run together; one
// after another they added up on every server render.
const unitsFetch = useLocalisedApiFetch<any>(
  () => `/v1/units?codes=${examples.value.map(e => e.code).join(',')}`,
  { watch: [campus] }
)
// The pages students open at this point in the semester, named rather than
// searched for: a category query returns whatever sorts first.
const GUIDE_SLUGS = {
  malaysia: [
    'special-consideration', 'supporting-documents', 'final-assessment-dates',
    'dates-timetables-start-times', 'results-release', 'malaysia-frequent-asked-questions-faq-exam-results'
  ],
  australia: [
    'special-consideration', 'supporting-documents', 'final-assessment-dates',
    'dates-timetables-start-times', 'results-release', 'extensions-special-consideration-spec-con-extensio'
  ]
}
const guidesFetch = useLocalisedApiFetch<any>(
  () => `/v1/guides?slugs=${GUIDE_SLUGS[campus.value].join(',')}`,
  { watch: [campus] }
)
const postsFetch = useApiFetch<any>('/v1/community/posts?limit=4')
const [{ data: units }, { data: guides }, { data: posts }] = await Promise.all([
  unitsFetch, guidesFetch, postsFetch
])

const unitRows = computed(() => {
  const byCode = new Map<string, any>((units.value?.results ?? []).map((u: any) => [u.unit_code, u]))
  return examples.value.flatMap(({ code, area }) => {
    const unit = byCode.get(code)
    return unit ? [{ unit, area: area[locale.value as keyof typeof area] ?? area.en }] : []
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
    ]
  },
  zh: {
    eyebrow: '学生自建 · 非 Monash 官方',
    heroBefore: '查课程、查政策，每条都有',
    heroEm: '出处',
    heroAfter: '。',
    lead: 'Handbook 课程、Monash 官方页面和同学的经验分开放。每条信息都写明来自哪里、最后什么时候核对过。',
    placeholder: 'FIT2004、特殊考虑、census date…',
    popular: '常搜',
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
    ]
  }
}
const c = computed(() => (locale.value === 'zh' ? COPY.zh : COPY.en))
const marketing = computed(() => locale.value === 'en' || locale.value === 'zh')

// The eight tools sit under the search box, so a first visit sees what the site
// does without scrolling past the dates. Labels come from the header navigation;
// the icons are the line set the header and the plan page already use.
const TOOLS = [
  { to: '/units', key: 'units', icon: 'book' },
  { to: '/guides', key: 'guides', icon: 'page' },
  { to: '/tree', key: 'tree', icon: 'tree' },
  { to: '/plan', key: 'plan', icon: 'columns' },
  { to: '/courses', key: 'courses', icon: 'degree' },
  { to: '/marks', key: 'marks', icon: 'percent' },
  { to: '/community', key: 'community', icon: 'chat' },
  { to: '/mamo', key: 'mamo', icon: 'pin' }
]
const directory = computed(() =>
  TOOLS.flatMap(({ to, key, icon }) => {
    const item = sectionItems.value.find(i => i.to === to)
    return item ? [{ to, icon, label: item.label, hint: $t(`home.toolHint.${key}`) }] : []
  })
)

// The query stays English, which is what the official pages are indexed by.
const POPULAR = {
  consideration: { en: 'Special consideration', zh: '特殊考虑', ja: '特別配慮', ko: '특별 고려' },
  visa: { en: 'Student visa', zh: '学生签证', ja: '学生ビザ', ko: '학생 비자' },
  exchange: { en: 'Exchange', zh: '交换', ja: '交換留学', ko: '교환학생' }
}
const lang = () => (['zh', 'ja', 'ko'].includes(locale.value) ? locale.value : 'en') as keyof typeof POPULAR.visa

const popularTerms = computed(() =>
  [
    { query: 'C2001', text: 'C2001', code: true },
    { query: 'FIT2102', text: 'FIT2102', code: true },
    { query: 'Special consideration', text: POPULAR.consideration[lang()] },
    { query: 'WAM', text: 'WAM/GPA' },
    { query: 'Student visa', text: POPULAR.visa[lang()] },
    { query: 'Exchange', text: POPULAR.exchange[lang()] }
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
  if (locale.value === 'ko') return `${m}월 ${d}일`
  return locale.value === 'zh' || locale.value === 'ja' ? `${m}月${d}日` : `${d} ${en[m - 1]}`
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
        <nav class="tools" aria-labelledby="tools-title">
          <h2 id="tools-title" class="tools-title">{{ $t('home.startHere') }}</h2>
          <NuxtLink v-for="item in directory" :key="item.to" :to="item.to" class="tool">
            <span class="tool-icon"><PlanIcon :name="item.icon" :size="20" /></span>
            <span class="tool-text">
              <b>{{ item.label }}</b>
              <span class="tool-hint">{{ item.hint }}</span>
            </span>
          </NuxtLink>
        </nav>
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

/* The eight tools as soft tiles on the same light grey as the header tray: two
   columns beside the dates, an app-style grid of four on a phone. The icon sits
   on a small white chip, like the raised sign-in piece in the header. */
.tools {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--s2);
  margin-top: var(--s5);
}
.tools-title {
  grid-column: 1 / -1;
  margin: 0 0 var(--s1);
  color: var(--muted-2);
  font-family: var(--font);
  font-size: 0.8rem;
  font-weight: 400;
  letter-spacing: 0.04em;
}
.tool {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  column-gap: var(--s3);
  align-items: center;
  padding: var(--s2) var(--s3);
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
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--surface);
  color: var(--brand);
  box-shadow: var(--shadow-sm), 0 0 0 1px var(--border);
}
.tool-text { display: grid; gap: 1px; }
.tool b { font-size: 0.95rem; font-weight: 600; line-height: 1.3; }
.tool-hint { color: var(--muted); font-size: 0.8rem; line-height: 1.4; }
/* Korean wraps between words, not inside them. */
.tool-hint:lang(ko) { word-break: keep-all; }

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
  .tools { margin-top: var(--s5); }
  .split { grid-template-columns: 1fr; gap: var(--s6); }
}
@media (max-width: 560px) {
  .tools { grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--s3) var(--s2); }
  .tool {
    grid-template-columns: 1fr;
    justify-items: center;
    align-content: start;
    row-gap: 6px;
    padding: 0;
    background: none;
    text-align: center;
  }
  .tool:hover { background: none; }
  .tool-icon { width: 48px; height: 48px; border-radius: 14px; background: var(--surface-2); box-shadow: none; }
  .tool:hover .tool-icon { background: var(--blue-50); }
  .tool b { font-size: 0.75rem; font-weight: 500; }
  .tool-hint { display: none; }
  .unit { grid-template-columns: 1fr auto; gap: 2px var(--s3); }
  .area { grid-column: 2; grid-row: 1; text-align: right; }
  .code { grid-column: 1; grid-row: 1; }
  .title { grid-column: 1 / -1; grid-row: 2; }
  .campuses { grid-column: 1 / -1; }
}
@media (prefers-reduced-motion: reduce) {
  .tool { transition: none; }
}
</style>
