<script setup lang="ts">
/**
 * Unit detail - the first page that shows what the product is for. Everything
 * on it is a parsed Handbook field, with the source and the check date in
 * view, plus the zero-AI ask box and any related community threads.
 *
 * The page is long, so it opens with the four facts most students came for
 * (credit points, when it runs at their campus, whether there is an exam,
 * level), every card has an icon to find it by, and the contents on the
 * right follow the scroll.
 */
const route = useRoute()
const config = useRuntimeConfig()
const { $t, $term } = useNuxtApp() as any
const { locale } = useLocale()
const campusName = useCampusName()
const code = computed(() => String(route.params.code).toUpperCase())

const { year, withYear, setYear } = useHandbookYear()
const { data: unit, error } = await useLocalisedApiFetch<any>(
  () => withYear(`/v1/units/${code.value}`),
  { watch: [year] }
)
useErrorStatus(error)

/** The newest year that lists the unit is the default, so choosing it clears `?year=`. */
function pickYear(y: number) {
  setYear(y === unit.value?.available_years?.[0] ? null : y)
}
const { data: discussions } = await useApiFetch<any>(
  () => `/v1/community/posts?unit_code=${code.value}&limit=5`
)
// Student ratings, averages only. The ratings section fetches its own list
// and says when it changed, so the header and the questions below follow.
const { data: ratings, refresh: refreshRatings } = await useApiFetch<any>(
  () => `/v1/reviews/units/${code.value}?limit=0`
)
const rating = computed(() => (ratings.value?.summary?.count ? ratings.value.summary : null))

// The campus the reader planned for, so "not taught at Malaysia" means their
// campus. A reader with no plan gets the default, Malaysia.
const { plan } = usePlan()
const campus = computed(() => plan.value.campus || 'Malaysia')

// Shared with the After list below: the same path is the same cache entry,
// so this is one request, not two.
const { data: unlocks } = await useLocalisedApiFetch<any>(
  () => `/v1/units/${code.value}/unlocks?year=${unit.value?.academic_year ?? ''}&campus=${campus.value}`,
  { watch: [() => unit.value?.academic_year, campus] }
)

// --- ask ---------------------------------------------------------------------

const question = ref('')
const answer = ref<any>(null)
const asking = ref(false)
const askError = ref('')

async function ask(text?: string) {
  const q = (text ?? question.value).trim()
  if (!q) return
  question.value = q
  asking.value = true
  askError.value = ''
  try {
    // The page's unit and year go with the question. Without them "How good is
    // this unit?" reached the router with no code in it, and a question asked
    // on the 2025 page was answered from the current Handbook.
    answer.value = await apiFetch<any>(`/v1/ask?locale=${locale.value}`, {
      method: 'POST',
      body: { query: q, unit_code: code.value, year: unit.value?.academic_year }
    })
  } catch (caught) {
    askError.value = apiErrorMessage(caught, $t)
  } finally {
    asking.value = false
  }
}

const suggestions = computed(() => [
  $t('unit.suggestExam', { code: code.value }),
  $t('unit.suggestPrereq', { code: code.value }),
  $t('unit.suggestMalaysia', { code: code.value })
])

// --- facts -------------------------------------------------------------------

const PERIOD_ORDER = ['S1', 'S2', 'SA', 'SB', 'W', 'FY', 'OCT']

/** "Semester 1" for S1, through the planner's own labels. */
function periodLabel(short: string, fallback: string): string {
  const full: Record<string, string> = {
    S1: 'First semester', S2: 'Second semester', SA: 'Summer semester A',
    SB: 'Summer semester B', W: 'Winter semester', FY: 'Full year',
    OCT: 'October intake teaching period, Malaysia campus'
  }
  const key = full[short] ? `plan.period.${full[short]}` : ''
  const label = key ? $t(key) : ''
  return label && label !== key ? label : fallback
}

/** The periods the unit runs in at one campus, or everywhere when none is given. */
function periodsAt(where: string | null): string[] {
  const seen = new Map<string, string>()
  for (const o of unit.value?.offerings || []) {
    if (where && o.campus_raw !== where) continue
    const short = o.short || o.teaching_period_raw
    if (!seen.has(short)) seen.set(short, periodLabel(short, o.teaching_period))
  }
  return [...seen.entries()]
    .sort((a, b) => (PERIOD_ORDER.indexOf(a[0]) + 99) % 99 - (PERIOD_ORDER.indexOf(b[0]) + 99) % 99)
    .map(([, label]) => label)
}

const periodsHere = computed(() => periodsAt(campus.value))
const assessmentCount = computed(() => unit.value?.assessments?.length ?? 0)

/** The workload statement's total, when it states one ("144 hours per semester"). */
const totalHours = computed(() => {
  const match = /(\d{2,3})\s*hours?/i.exec(unit.value?.workload_requirements || '')
  return match ? Number(match[1]) : null
})

// --- assessment --------------------------------------------------------------

/** Brand blue at falling strength, so neighbouring segments stay apart. */
const SEGMENT_SHADES = ['var(--brand)', 'var(--navy)', '#4f97c9', '#9cc3df', '#2c6f9e', '#c9dceb']

const assessmentRows = computed(() =>
  (unit.value?.assessments || []).map((item: any, i: number) => {
    const weight = Number(String(item.weight ?? '').replace('%', ''))
    return { ...item, weightNumber: Number.isFinite(weight) && weight > 0 ? weight : null, shade: SEGMENT_SHADES[i % SEGMENT_SHADES.length] }
  })
)
const weightTotal = computed(() =>
  assessmentRows.value.reduce((sum: number, row: any) => sum + (row.weightNumber || 0), 0)
)

// --- offerings ---------------------------------------------------------------

/** Offerings grouped by teaching period, the reader's campus first in each group. */
const offeringGroups = computed(() => {
  const groups = new Map<string, any[]>()
  for (const o of unit.value?.offerings || []) {
    const key = o.teaching_period || ''
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(o)
  }
  return [...groups.entries()].map(([period, rows]) => ({
    period,
    rows: [...rows].sort((a, b) => Number(b.campus_raw === campus.value) - Number(a.campus_raw === campus.value))
  }))
})

// --- requisites ---------------------------------------------------------------

const requisitesByType = computed(() => {
  const groups: Record<string, any[]> = {}
  for (const group of unit.value?.requisites || []) {
    ;(groups[group.requisite_type] ||= []).push(group)
  }
  return groups
})

/** Every unit code a set of rules names, nested groups included. */
function codesIn(groups: any[]): string[] {
  const out: string[] = []
  const walk = (rule: any) => {
    for (const item of rule.items || []) if (item.code && !out.includes(item.code)) out.push(item.code)
    for (const child of rule.groups || []) walk(child)
  }
  groups.forEach(walk)
  return out
}

// --- resources ---------------------------------------------------------------

// Stops at full-width punctuation too, which a translated line puts right after a link.
const URL_RE = /(https?:\/\/[^\s)（）"'，。、；]+)/g

/** "Recommended resources" in the reader's language, or as published. */
function resourceLabel(type: string): string {
  const key = `unit.res.${type}`
  const label = $t(key)
  return label === key ? type : label
}

/** A reading-list line split into text and links, so the links can be links. */
function linkify(text: string): { text: string; href?: string }[] {
  return text.split(URL_RE).filter(Boolean).map((part) =>
    /^https?:\/\//.test(part) ? { text: part, href: part } : { text: part }
  )
}

// --- common questions ------------------------------------------------------------

/**
 * The questions students search for about a unit, answered from the fields on
 * this page. Nothing here is a judgement of ours: "is it hard" is answered by
 * saying we do not rate units, and pointing at the workload and at students.
 */
const faq = computed(() => {
  const u = unit.value
  if (!u) return []
  const c = u.unit_code
  const y = u.academic_year
  const items: { q: string; a: string }[] = []

  const prereqs = codesIn(Object.entries(requisitesByType.value)
    .filter(([type]) => /prereq/i.test(type)).flatMap(([, groups]) => groups))
  items.push({
    q: $t('faq.prereqQ', { code: c }),
    a: prereqs.length
      ? $t('faq.prereqSome', { code: c, year: y, units: prereqs.join(', ') })
      : $t('faq.prereqNone', { code: c, year: y })
  })

  const next = unlocks.value?.units || []
  if (unlocks.value) {
    items.push({
      q: $t('faq.afterQ', { code: c }),
      a: next.length
        ? $t('faq.afterSome', {
          code: c,
          count: next.length,
          units: next.slice(0, 6).map((n: any) => n.unit_code).join(', ')
        }) + (unlocks.value.total_downstream > next.length ? ` ${$t('unlocks.leadsOn', { total: unlocks.value.total_downstream })}` : '')
        : $t('unlocks.none', { code: c, year: y })
    })
  }

  const everywhere = periodsAt(null)
  const campuses = [...new Set((u.offerings || []).map((o: any) => o.campus))]
  items.push({
    q: $t('faq.whenQ', { code: c }),
    a: everywhere.length
      ? $t('faq.whenSome', { code: c, year: y, periods: everywhere.join(', '), campuses: campuses.join(', ') })
      : $t('unit.noOfferingsPublished')
  })

  items.push({
    q: $t('faq.examQ', { code: c }),
    a: u.has_exam === true
      ? $t('faq.examYes', { code: c, year: y, count: assessmentCount.value })
      : u.has_exam === false
        ? $t('faq.examNo', { code: c, year: y, count: assessmentCount.value })
        : $t('faq.examUnknown', { code: c, year: y })
  })

  const said = discussions.value?.total ?? discussions.value?.results?.length ?? 0
  const difficulty = rating.value?.dimensions?.difficulty
  items.push({
    q: $t('faq.hardQ', { code: c }),
    a: [
      $t('faq.hardIntro'),
      difficulty?.count
        ? $t(difficulty.count === 1 ? 'faq.hardRatedOne' : 'faq.hardRated', {
          score: Number(difficulty.average).toFixed(1), count: difficulty.count
        })
        : '',
      totalHours.value ? $t('faq.hardHours', { hours: totalHours.value }) : '',
      said ? $t('faq.hardCommunity', { count: said }) : $t('faq.hardNoCommunity')
    ].filter(Boolean).join(' ')
  })

  if (u.areas?.length) {
    items.push({
      q: $t('faq.areasQ', { code: c }),
      a: $t('faq.areasSome', { code: c, areas: u.areas.map((a: any) => a.title).join(', ') })
    })
  }
  return items
})

// --- contents ------------------------------------------------------------------

const sections = computed(() => {
  const u = unit.value
  if (!u) return []
  return [
    u.overview && { id: 'overview', label: $t('unit.overview') },
    { id: 'offerings', label: $t('unit.offerings') },
    { id: 'assessment', label: $t('unit.assessment') },
    { id: 'requisites', label: $t('unit.requisites') },
    u.learning_outcomes?.length && { id: 'outcomes', label: $t('unit.outcomes') },
    { id: 'workload', label: $t('unit.workload') },
    u.learning_resources?.length && { id: 'resources', label: $t('unit.resources') },
    u.areas?.length && { id: 'fits', label: $t('unit.whereItFits') },
    { id: 'reviews', label: $t('reviews.title') },
    { id: 'faq', label: $t('unit.commonQuestions') },
    { id: 'details', label: $t('unit.moreDetails') },
    { id: 'ask', label: $t('unit.askAbout', { code: u.unit_code }) },
    { id: 'community', label: $t('nav.community') }
  ].filter(Boolean) as { id: string; label: string }[]
})

/** The section being read, for the contents on the right to mark. */
const current = ref('')
let observer: IntersectionObserver | null = null
function watchSections() {
  observer?.disconnect()
  if (typeof IntersectionObserver === 'undefined') return
  observer = new IntersectionObserver((entries) => {
    const visible = entries.filter((e) => e.isIntersecting)
      .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
    if (visible[0]) current.value = visible[0].target.id
  }, { rootMargin: '-80px 0px -60% 0px' })
  for (const s of sections.value) {
    const el = document.getElementById(s.id)
    if (el) observer.observe(el)
  }
}
onMounted(() => nextTick(watchSections))
watch(() => sections.value.map((s) => s.id).join(), () => nextTick(watchSections))
onBeforeUnmount(() => observer?.disconnect())

// --- head ---------------------------------------------------------------------

useSeoMeta({
  title: () => (unit.value ? `${unit.value.unit_code} ${unit.value.title}` : 'Unit'),
  description: () =>
    unit.value
      ? `${unit.value.unit_code} ${unit.value.title}: assessment, requisites, offerings and workload from the ${unit.value.academic_year} Monash Handbook.`
      : undefined,
  ogTitle: () => (unit.value ? `${unit.value.unit_code} · ${unit.value.title}` : undefined)
})
useHead(() => ({
  // No canonical for a page that is not there: it would tell the crawler this
  // is the real address of nothing.
  link: unit.value ? [{ rel: 'canonical', href: `${config.public.siteUrl}/units/${code.value}` }] : [],
  // The common questions as structured data, so a search result can show
  // them. Every answer is the same sentence the page shows.
  script: faq.value.length
    ? [{
        type: 'application/ld+json',
        innerHTML: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'FAQPage',
          mainEntity: faq.value.map((item) => ({
            '@type': 'Question',
            name: item.q,
            acceptedAnswer: { '@type': 'Answer', text: item.a }
          }))
        })
      }]
    : []
}))
</script>

<template>
  <div class="container">
    <ErrorState v-if="error" :error="error" />

    <article v-else-if="unit" class="unit">
      <YearNotice v-if="unit.not_in_year" :code="unit.unit_code" :year="unit.academic_year" :missing="unit.not_in_year" />
      <TeachOutNotice v-if="unit.teach_out" :entries="unit.teach_out.entries" :sources="unit.teach_out.sources" :pages="unit.teach_out.pages" :campus="campus" />
      <p v-if="unit.is_active === false" class="withdrawn small" role="status">
        {{ $t('handbook.withdrawn', { code: unit.unit_code, year: unit.academic_year }) }}
      </p>
      <header class="head card">
        <div class="head-top">
          <div>
            <p class="tiny muted">
              <NuxtLink to="/units">{{ $t('nav.units') }}</NuxtLink> / {{ unit.unit_code }}
            </p>
            <h1><span class="mono">{{ unit.unit_code }}</span> · {{ unit.title }}</h1>
          </div>
          <SourceBadge kind="handbook" />
        </div>

        <dl class="facts">
          <div class="fact">
            <dt>{{ $t('unit.factCredit') }}</dt>
            <dd v-if="unit.credit_points">{{ unit.credit_points }}</dd>
            <dd v-else class="fact-muted">{{ $t('unit.notStated') }}</dd>
          </div>
          <div class="fact">
            <dt>{{ $t('unit.factOffered', { campus: campusName(campus) }) }}</dt>
            <dd v-if="periodsHere.length">{{ periodsHere.join(', ') }}</dd>
            <dd v-else class="fact-warn">{{ $t('unit.factNotHere') }}</dd>
          </div>
          <div class="fact">
            <dt>{{ $t('unit.factAssessment') }}</dt>
            <dd v-if="unit.has_exam === true">{{ $t('unit.factExam', { count: assessmentCount }) }}</dd>
            <dd v-else-if="unit.has_exam === false">{{ $t('unit.factNoExam', { count: assessmentCount }) }}</dd>
            <dd v-else class="fact-muted">{{ $t('unit.factUnknown') }}</dd>
          </div>
          <div class="fact">
            <dt>{{ $t('unit.factLevel') }}</dt>
            <dd v-if="unit.level">{{ $term('level', unit.level) }}</dd>
            <dd v-else class="fact-muted">{{ $t('unit.notStated') }}</dd>
          </div>
        </dl>

        <div class="head-foot">
          <p class="chips">
            <span class="chip">{{ $t('unit.handbookYear', { year: unit.academic_year }) }}</span>
            <span v-if="unit.faculty" class="chip">{{ $term('faculty', unit.faculty) }}</span>
            <a v-if="rating" href="#reviews" class="chip chip--rating">
              <StarRating :value="rating.average" size="sm" />
              <strong>{{ Number(rating.average).toFixed(1) }}</strong>
              <span>{{ rating.count === 1 ? $t('reviews.countOne') : $t('reviews.count', { count: rating.count }) }}</span>
              <span class="chip-source">{{ $t('badge.community') }}</span>
            </a>
          </p>
          <div class="head-meta">
            <LastChecked :value="unit.last_checked" />
            <YearPicker
              v-if="(unit.available_years || []).length > 1"
              :model-value="unit.academic_year"
              :years="unit.available_years"
              @update:model-value="pickYear"
            />
          </div>
        </div>
      </header>

      <div class="body">
        <div class="content stack">
          <section v-if="unit.overview" id="overview" class="card section">
            <SectionHead icon="overview" :title="$t('unit.overview')" />
            <TranslationNotice
              v-if="unit.translation"
              :translation="unit.translation"
              :source-url="unit.source_url"
              class="mb"
            />
            <p class="pre measure">{{ unit.overview }}</p>
          </section>

          <section id="offerings" class="card section">
            <SectionHead icon="offerings" :title="$t('unit.offeringsIn', { year: unit.academic_year })" />
            <div v-if="offeringGroups.length" class="scroll-x">
              <table class="offer-table">
                <thead>
                  <tr>
                    <th>{{ $t('unit.colPeriod') }}</th>
                    <th>{{ $t('unit.colCampus') }}</th>
                    <th>{{ $t('unit.colMode') }}</th>
                  </tr>
                </thead>
                <tbody v-for="group in offeringGroups" :key="group.period">
                  <tr v-for="(o, i) in group.rows" :key="i" :class="{ here: o.campus_raw === campus }">
                    <th v-if="i === 0" scope="rowgroup" :rowspan="group.rows.length" class="period">
                      {{ $term('period', group.period) || group.period }}
                    </th>
                    <td>{{ $term('campus', o.campus) || o.campus }}</td>
                    <td class="muted">{{ $term('mode', o.attendance_mode) || o.attendance_mode }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="muted small">{{ $t('unit.noOfferingsPublished') }}</p>
          </section>

          <section id="assessment" class="card section">
            <SectionHead icon="assessment" :title="$t('unit.assessment')" />
            <p class="verdict small">
              <template v-if="unit.has_exam === true">{{ $t('unit.examYes') }}</template>
              <template v-else-if="unit.has_exam === false">{{ $t('unit.examNo') }}</template>
              <template v-else>{{ $t('unit.examUnknown') }}</template>
            </p>
            <template v-if="assessmentRows.length">
              <div v-if="weightTotal" class="weight-bar" role="img" :aria-label="$t('unit.weightBar')">
                <span
                  v-for="row in assessmentRows.filter((r: any) => r.weightNumber)"
                  :key="row.number"
                  class="segment"
                  :style="{ flexGrow: row.weightNumber, background: row.shade }"
                />
                <span v-if="weightTotal < 100" class="segment segment--rest" :style="{ flexGrow: 100 - weightTotal }" />
              </div>
              <ol class="assess-list">
                <li v-for="row in assessmentRows" :key="row.number" class="assess">
                  <span class="dot" :style="{ background: row.weightNumber ? row.shade : 'transparent' }" />
                  <div class="assess-main">
                    <p class="assess-name">{{ $assessmentName(row.name) }}</p>
                    <p class="assess-meta">
                      <span v-if="row.type">{{ $term('assessmentType', row.type) }}</span>
                      <span v-if="row.hurdle" class="hurdle">{{ $term('hurdle', row.hurdle) }}</span>
                    </p>
                  </div>
                  <span class="assess-weight">{{ row.weightNumber ? `${row.weightNumber}%` : '' }}</span>
                </li>
              </ol>
            </template>
            <p v-if="unit.assessment_summary" class="small pre muted">{{ unit.assessment_summary }}</p>
            <p v-if="unit.assessment_static_text" class="tiny muted pre">{{ unit.assessment_static_text }}</p>
          </section>

          <section id="requisites" class="card section">
            <SectionHead icon="requisites" :title="$t('unit.requisites')" />
            <div class="before-after">
              <div>
                <h3 class="side-label">{{ $t('unlocks.before', { code: unit.unit_code }) }}</h3>
                <template v-if="unit.requisites.length">
                  <div v-for="(groups, type) in requisitesByType" :key="type" class="req">
                    <h4 class="req-type">{{ $term('requisiteType', String(type)) }}</h4>
                    <RequisiteRule
                      v-for="(group, gi) in groups"
                      :key="gi"
                      :rule="group"
                      class="req-group"
                    />
                  </div>
                </template>
                <p v-else class="muted small">{{ $t('unit.noRequisites') }}</p>
              </div>
              <div>
                <h3 class="side-label">{{ $t('unlocks.after', { code: unit.unit_code }) }}</h3>
                <UnitUnlocks :code="unit.unit_code" :year="unit.academic_year" :campus="campus" />
              </div>
            </div>
          </section>

          <section v-if="unit.learning_outcomes.length" id="outcomes" class="card section">
            <SectionHead icon="outcomes" :title="$t('unit.outcomes')" />
            <ol class="outcomes measure">
              <li v-for="outcome in unit.learning_outcomes" :key="outcome.code">
                {{ outcome.description }}
              </li>
            </ol>
          </section>

          <section id="workload" class="card section">
            <SectionHead icon="workload" :title="$t('unit.workloadTeaching')" />
            <div v-if="unit.activities.length || totalHours" class="tiles">
              <div v-if="totalHours" class="tile tile--strong">
                <span class="tile-label">{{ $t('unit.totalHours') }}</span>
                <span class="tile-value">{{ $t('unit.hours', { hours: totalHours }) }}</span>
              </div>
              <div v-for="(activity, i) in unit.activities" :key="i" class="tile">
                <span class="tile-label">{{ $term('activityType', activity.activity_type) }}</span>
                <span class="tile-value">{{ $term('duration', activity.name) || $t('unit.notStated') }}</span>
              </div>
            </div>
            <p v-if="unit.teaching_approach" class="pre small measure">{{ unit.teaching_approach }}</p>
            <p v-if="unit.workload_requirements" class="pre muted small measure">{{ unit.workload_requirements }}</p>
            <p v-if="!unit.workload_requirements && !unit.activities.length" class="muted small">
              {{ $t('unit.noWorkload') }}
            </p>
          </section>

          <section v-if="unit.learning_resources?.length" id="resources" class="card section">
            <SectionHead icon="resources" :title="$t('unit.resources')" />
            <div v-for="group in unit.learning_resources" :key="group.type" class="res-group">
              <h3 class="side-label">{{ resourceLabel(group.type) }}</h3>
              <ul class="res-list measure">
                <li v-for="(item, i) in group.items" :key="i">
                  <template v-for="(part, pi) in linkify(item)" :key="pi">
                    <a v-if="part.href" :href="part.href" rel="noopener nofollow external" target="_blank">{{ part.text }}</a>
                    <template v-else>{{ part.text }}</template>
                  </template>
                </li>
              </ul>
            </div>
            <p class="tiny muted">{{ $t('unit.resourcesNote') }}</p>
          </section>

          <section v-if="unit.areas?.length" id="fits" class="card section">
            <SectionHead icon="fits" :title="$t('unit.whereItFits')" />
            <p class="small">{{ $t(unit.areas.length === 1 ? 'unit.fitsIntroOne' : 'unit.fitsIntro', { code: unit.unit_code, count: unit.areas.length, year: unit.academic_year }) }}</p>
            <div class="fits">
              <NuxtLink
                v-for="area in unit.areas"
                :key="area.aos_code"
                class="fit"
                :to="`/courses/aos/${area.aos_code}?year=${unit.academic_year}`"
              >
                <span class="fit-top">
                  <span class="mono fit-code">{{ area.aos_code }}</span>
                  <span v-if="area.aos_type" class="fit-type">{{ area.aos_type }}</span>
                </span>
                <span class="fit-title">{{ area.title }}</span>
                <span v-if="area.parts.length" class="fit-parts">{{ area.parts.join(', ') }}</span>
              </NuxtLink>
            </div>
          </section>

          <UnitReviews :code="unit.unit_code" :campus="campus" @changed="refreshRatings" />

          <section id="faq" class="card section">
            <SectionHead icon="faq" :title="$t('unit.commonQuestions')" />
            <div class="faq">
              <div v-for="item in faq" :key="item.q" class="qa">
                <h3>{{ item.q }}</h3>
                <p>{{ item.a }}</p>
              </div>
            </div>
          </section>

          <section id="details" class="card section">
            <SectionHead icon="details" :title="$t('unit.moreDetails')" />
            <dl class="details">
              <div v-if="unit.credit_points"><dt>{{ $t('unit.factCredit') }}</dt><dd>{{ unit.credit_points }}</dd></div>
              <div v-if="unit.level"><dt>{{ $t('unit.factLevel') }}</dt><dd>{{ $term('level', unit.level) }}</dd></div>
              <div v-if="unit.faculty"><dt>{{ $t('unit.faculty') }}</dt><dd>{{ $term('faculty', unit.faculty) }}</dd></div>
              <div v-if="unit.school"><dt>{{ $t('unit.school') }}</dt><dd>{{ unit.school }}</dd></div>
              <div v-if="unit.sca_band"><dt>{{ $t('unit.scaBand') }}</dt><dd>{{ $t('unit.band', { band: unit.sca_band }) }}</dd></div>
              <div>
                <dt>{{ $t('unit.studyAbroad') }}</dt>
                <dd>
                  {{ unit.study_abroad === true ? $t('unit.available') : unit.study_abroad === false ? $t('unit.notAvailable') : $t('unit.notStated') }}
                </dd>
              </div>
              <div v-if="unit.handbook_version"><dt>{{ $t('unit.version') }}</dt><dd>{{ unit.handbook_version }}</dd></div>
              <div v-if="(unit.available_years || []).length > 1" class="years-row">
                <dt>{{ $t('unit.handbookYears') }}</dt>
                <dd class="years">
                  <template v-for="y in [...unit.available_years].sort()" :key="y">
                    <strong v-if="y === unit.academic_year">{{ y }}</strong>
                    <a v-else href="#" @click.prevent="pickYear(y)">{{ y }}</a>
                  </template>
                </dd>
              </div>
            </dl>
          </section>

          <section id="ask" class="card section ask">
            <SectionHead icon="ask" :title="$t('unit.askAbout', { code: unit.unit_code })" />
            <p class="tiny muted">{{ $t('unit.askHint') }}</p>
            <SearchInput
              v-model="question"
              :placeholder="$t('unit.askPlaceholder', { code: unit.unit_code })"
              @submit="ask"
            />
            <p class="suggestions tiny">
              <button v-for="s in suggestions" :key="s" class="chip-btn" @click="ask(s)">{{ s }}</button>
            </p>
            <Skeleton v-if="asking" :lines="3" />
            <p v-else-if="askError" class="tiny bad-text" role="alert">{{ askError }}</p>
            <AnswerBlocks
              v-else-if="answer"
              :answer="answer"
              :suggest="!answer.answer_type?.startsWith('handbook')"
              class="answer"
              @ask="ask"
            />
          </section>

          <section id="community" class="card section">
            <SectionHead icon="community" :title="$t('unit.discussionsAbout', { code: unit.unit_code })">
              <SourceBadge kind="community" />
            </SectionHead>
            <p class="tiny muted">{{ $t('unit.discussionsNote') }}</p>
            <div v-if="discussions?.results?.length" class="grid">
              <PostCard v-for="post in discussions.results" :key="post.id" :post="post" />
            </div>
            <EmptyState
              v-else
              :title="$t('unit.noDiscussions')"
              :hint="$t('unit.noDiscussionsHint')"
            >
              <NuxtLink :to="`/community?unit=${unit.unit_code}`" class="btn">
                {{ $t('unit.startDiscussion') }}
              </NuxtLink>
            </EmptyState>
          </section>
        </div>

        <aside class="side">
          <nav class="toc" :aria-label="$t('unit.onThisPage')">
            <h2 class="toc-title">{{ $t('unit.onThisPage') }}</h2>
            <a
              v-for="s in sections"
              :key="s.id"
              :href="`#${s.id}`"
              :class="{ on: current === s.id }"
              :aria-current="current === s.id ? 'location' : undefined"
            >{{ s.label }}</a>
          </nav>
          <div class="card section">
            <h2 class="small">{{ $t('unit.officialSource') }}</h2>
            <p class="small">
              <a :href="unit.source_url" rel="noopener external" target="_blank">
                Monash Handbook {{ unit.academic_year }} ↗
              </a>
            </p>
            <LastChecked :value="unit.last_checked" />
            <p class="tiny muted">
              {{ $t('unit.handbookVersion', { version: unit.handbook_version || $t('unit.notStated') }) }}
              {{ $t('unit.moodleNote') }}
            </p>
          </div>
        </aside>
      </div>
    </article>
  </div>
</template>

<style scoped>
.withdrawn {
  margin: 0 0 var(--s3); padding: var(--s3) var(--s4); border-radius: var(--radius-sm);
  background: var(--warning-bg); color: var(--warning);
}
.mb { margin-bottom: var(--s5); }
.measure { max-width: var(--measure); }

/* Header ---------------------------------------------------------------------- */
.head { padding: var(--s5); margin-bottom: var(--s5); }
.head-top { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--s4); }
.head h1 { margin-bottom: var(--s4); }
.facts {
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: var(--s3);
  margin: 0 0 var(--s4);
}
.fact {
  padding: var(--s3) var(--s4); border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--surface-2);
}
.fact dt { font-size: 0.75rem; color: var(--muted); margin-bottom: 2px; }
.fact dd { margin: 0; font-weight: 600; font-size: 1.02rem; }
.fact-warn { color: var(--warning); }
.fact-muted { color: var(--muted); font-weight: 500 !important; }
.head-foot { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: var(--s3); }
.head-meta { display: flex; flex-wrap: wrap; align-items: center; gap: var(--s4); }
.chips { display: flex; flex-wrap: wrap; gap: var(--s2); margin: 0; }
.chip { padding: 2px 10px; border-radius: var(--radius-pill); background: var(--surface-2); font-size: 0.78rem; }
/* The student rating sits with the chips but is told apart from the Handbook
   ones by its border and its own "Community" label. */
.chip--rating {
  display: inline-flex; align-items: center; gap: 6px; color: var(--text);
  background: var(--surface); border: 1px solid var(--border-strong);
}
.chip--rating:hover { text-decoration: none; border-color: var(--badge-community); }
.chip-source { color: var(--badge-community); font-weight: 600; }

/* Layout ------------------------------------------------------------------------ */
.body { display: grid; grid-template-columns: minmax(0, 1fr) 240px; gap: var(--s5); align-items: start; }
/* A grid item defaults to min-width:auto, so a wide table inside .scroll-x
   stretches its own column instead of scrolling, and the whole page ends up
   scrolling sideways on a phone. This is the line that keeps the scroll inside
   the table where it belongs. */
.body > * { min-width: 0; }
.section { padding: var(--s5); }
.pre { white-space: pre-line; }
.side-label {
  font-family: var(--font); font-size: 0.75rem; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--muted); margin-bottom: var(--s3);
}

/* Offerings ---------------------------------------------------------------------- */
.offer-table { width: 100%; border-collapse: collapse; font-size: 0.93rem; }
.offer-table thead th {
  text-align: left; font-size: 0.8rem; font-weight: 600; color: var(--muted);
  padding: var(--s2) var(--s3); background: var(--surface-2);
}
.offer-table td, .offer-table .period { padding: var(--s2) var(--s3); border-top: 1px solid var(--border); text-align: left; vertical-align: top; }
/* The period is a row header, not a column header: no caps, no shading. */
.offer-table tbody th.period {
  font-weight: 600; font-size: inherit; color: var(--text); background: none;
  text-transform: none; letter-spacing: normal; border-bottom: 0;
}
.offer-table { border-bottom: 1px solid var(--border); }
.offer-table tr.here td { background: var(--blue-50); }

/* Assessment ---------------------------------------------------------------------- */
.verdict {
  padding: var(--s3) var(--s4);
  border-left: 3px solid var(--blue);
  background: var(--blue-50);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.weight-bar {
  display: flex; gap: 2px; height: 12px; margin: var(--s4) 0 var(--s3);
  border-radius: var(--radius-pill); overflow: hidden;
}
.segment { flex-basis: 0; min-width: 4px; }
.segment--rest { background: var(--surface-2); }
.assess-list { list-style: none; margin: 0 0 var(--s4); padding: 0; }
.assess {
  display: grid; grid-template-columns: 12px minmax(0, 1fr) auto; gap: var(--s3); align-items: start;
  padding: var(--s3) 0; border-bottom: 1px solid var(--border);
}
.dot { width: 10px; height: 10px; border-radius: 50%; margin-top: 7px; border: 1.5px solid var(--border-strong); }
.assess-name { margin: 0; font-weight: 500; }
.assess-meta { margin: 2px 0 0; display: flex; flex-wrap: wrap; gap: var(--s2); align-items: center; font-size: 0.82rem; color: var(--muted); }
.hurdle { padding: 0 8px; border-radius: 4px; background: var(--warning-bg); color: var(--warning); font-weight: 600; }
.assess-weight { font-weight: 600; font-variant-numeric: tabular-nums; }

/* Requisites ---------------------------------------------------------------------- */
.before-after { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--s6); }
.req + .req { margin-top: var(--s5); }
.req-type { text-transform: capitalize; }
.req-group ul { margin: var(--s2) 0; padding-left: var(--s5); }
.outcomes { padding-left: var(--s5); }
.outcomes li + li { margin-top: var(--s2); }

/* Workload ---------------------------------------------------------------------- */
.tiles { display: flex; flex-wrap: wrap; gap: var(--s3); margin-bottom: var(--s4); }
.tile {
  display: grid; gap: 2px; padding: var(--s3) var(--s4); min-width: 140px;
  border: 1px solid var(--border); border-radius: var(--radius-sm);
}
.tile--strong { background: var(--blue-50); border-color: transparent; }
.tile-label { font-size: 0.78rem; color: var(--muted); }
.tile-value { font-weight: 600; }

/* Resources, fits, FAQ, details ---------------------------------------------------- */
.res-group + .res-group { margin-top: var(--s4); }
.res-list { margin: 0 0 var(--s3); padding-left: var(--s5); }
.res-list li + li { margin-top: var(--s2); }
.res-list a { overflow-wrap: anywhere; text-decoration: underline; text-underline-offset: 2px; }
.fits { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: var(--s3); }
.fit {
  display: grid; gap: var(--s1); padding: var(--s3) var(--s4); color: var(--text);
  border: 1px solid var(--border); border-radius: var(--radius-sm);
}
.fit:hover { border-color: var(--brand); text-decoration: none; }
.fit-top { display: flex; justify-content: space-between; gap: var(--s2); font-size: 0.75rem; color: var(--muted); }
.fit-code { font-weight: 600; color: var(--navy); }
.fit-title { font-weight: 600; }
.fit-parts { font-size: 0.8rem; color: var(--muted); }
.faq { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--s5) var(--s6); }
.qa h3 { font-family: var(--font); font-size: 0.98rem; margin-bottom: var(--s1); }
.qa p { margin: 0; color: var(--muted); font-size: 0.93rem; }
.details { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: var(--s6); margin: 0; }
.details > div {
  display: flex; justify-content: space-between; gap: var(--s3);
  padding: var(--s2) 0; border-bottom: 1px solid var(--border); font-size: 0.93rem;
}
.details dt { color: var(--muted); }
.details dd { margin: 0; text-align: right; font-weight: 500; }
.years { display: flex; flex-wrap: wrap; gap: var(--s2); justify-content: flex-end; }

/* Ask, community ------------------------------------------------------------------- */
.suggestions { display: flex; flex-wrap: wrap; gap: var(--s2); margin: var(--s3) 0; }
.chip-btn {
  padding: 4px 12px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  background: var(--surface);
  font: inherit;
  font-size: 0.78rem;
  cursor: pointer;
}
.chip-btn:hover { background: var(--surface-2); }
.answer { margin-top: var(--s4); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--s3); }

/* Contents ------------------------------------------------------------------------- */
.side { position: sticky; top: calc(var(--header-h) + var(--s4)); display: grid; gap: var(--s4); }
.toc { display: grid; border-left: 1px solid var(--border); }
.toc-title {
  font-family: var(--font); font-size: 0.75rem; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--muted); margin: 0 0 var(--s2) var(--s4);
}
.toc a {
  padding: 5px var(--s4); margin-left: -1px; border-left: 2px solid transparent;
  color: var(--muted); font-size: 0.9rem;
}
.toc a:hover { color: var(--text); text-decoration: none; }
.toc a.on { color: var(--text); font-weight: 600; border-left-color: var(--text); }

@media (max-width: 1000px) {
  .facts { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 900px) {
  .body { grid-template-columns: 1fr; }
  .side { position: static; }
  .toc { display: none; }
  .before-after, .faq, .details { grid-template-columns: 1fr; gap: var(--s5); }
  .details { gap: 0; }
}
@media (max-width: 600px) {
  .head, .section { padding: var(--s4); }
}
</style>
