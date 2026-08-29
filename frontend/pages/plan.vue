<script setup lang="ts">
/**
 * The course map.
 *
 * A grid of years and teaching periods that you drop units into, checked
 * against the Handbook every time it changes. Writing down twelve units in
 * four semesters is something a student can do on paper; what they cannot do
 * on paper is verify that each one is taught at their campus in the semester
 * they put it in, and that everything it requires sits somewhere earlier.
 *
 * The plan lives in this browser. Nothing is uploaded except the plan itself,
 * at the moment it is checked, and nothing is stored on the server - which is
 * why there is no sign-in on this page and why there is an export button.
 */
import { OPTIONAL_PERIODS, type PlanEntry } from '~/composables/usePlan'

const { $t } = useNuxtApp()
const {
  plan, yearsList, slotEntries, add, remove, reset, addYear, removeYear, exported, imported
} = usePlan()

const picking = ref<{ year: number; period: string } | null>(null)
const query = ref('')
const results = ref<any[]>([])
const searching = ref(false)

async function search() {
  const term = query.value.trim()
  if (term.length < 2) {
    results.value = []
    return
  }
  searching.value = true
  try {
    const params = new URLSearchParams({ q: term, limit: '12' })
    if (plan.value.campus) params.set('campus', plan.value.campus)
    const body = await apiFetch<any>(`/v1/units?${params.toString()}`)
    results.value = body.results || []
  } finally {
    searching.value = false
  }
}

let searchTimer: ReturnType<typeof setTimeout> | undefined
watch(query, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(search, 220)
})

/**
 * Opening the picker and then having to click the field it just opened is one
 * click too many when you are placing thirty units.
 */
const pickerInput = ref<HTMLInputElement | HTMLInputElement[] | null>(null)
function openPicker(year: number, period: string) {
  picking.value = { year, period }
  query.value = ''
  results.value = []
  nextTick(() => {
    const field = Array.isArray(pickerInput.value) ? pickerInput.value[0] : pickerInput.value
    field?.focus()
  })
}

function place(unitCode: string) {
  if (!picking.value) return
  add(unitCode, picking.value.year, picking.value.period)
  query.value = ''
  results.value = []
}

// --- checking --------------------------------------------------------------

const report = ref<any>(null)
const checking = ref(false)
let checkTimer: ReturnType<typeof setTimeout> | undefined

async function check() {
  if (!plan.value.entries.length) {
    report.value = null
    return
  }
  checking.value = true
  try {
    report.value = await apiFetch<any>('/v1/plan/check', {
      method: 'POST',
      body: {
        year: plan.value.startYear,
        campus: plan.value.campus,
        entries: plan.value.entries
      }
    })
  } finally {
    checking.value = false
  }
}

watch(
  () => JSON.stringify([plan.value.entries, plan.value.campus]),
  () => {
    clearTimeout(checkTimer)
    checkTimer = setTimeout(check, 350)
  },
  { immediate: true }
)

/** Issues keyed by the unit and slot they belong to, for the card to read. */
const issuesFor = computed(() => {
  const map = new Map<string, any[]>()
  for (const issue of report.value?.issues || []) {
    const key = `${issue.unit_code}|${issue.year}|${issue.teaching_period}`
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(issue)
  }
  return map
})

function entryIssues(entry: PlanEntry) {
  return issuesFor.value.get(`${entry.unit_code}|${entry.year}|${entry.teaching_period}`) || []
}

const errorCount = computed(
  () => (report.value?.issues || []).filter((i: any) => i.severity === 'error').length
)
const warningCount = computed(
  () => (report.value?.issues || []).filter((i: any) => i.severity === 'warning').length
)

/** The message for one finding, with the codes it names spelled out. */
/**
 * A requisite rule, written out.
 *
 * The rule nests, and the flat `any_of` / `all_of` summaries the API sends
 * alongside it only describe the outermost group. FIT2004 asks for one of
 * FIT1008/FIT1054/FIT2085 *and* one of MAT1830/FIT1058, so its outer group is
 * an AND holding two ORs and naming no units of its own - both summaries came
 * back empty and the student was told "需要先修完 。" with nothing after it.
 *
 * The nesting is the rule, so it is read rather than flattened: flattening
 * would list five units and imply all five were needed.
 */
function describeRule(rule: any): string {
  if (!rule) return ''
  const parts = [
    ...(rule.codes || []),
    ...(rule.groups || []).map((child: any) => describeRule(child))
  ].filter(Boolean)
  if (!parts.length) return ''
  if (parts.length === 1) return parts[0]
  const joined = parts.join(rule.connector === 'OR' ? ' / ' : $t('plan.rule.and'))
  // Bracketed so "one of these and one of those" cannot be read as one list.
  return rule.connector === 'OR' ? `（${joined}）` : joined
}

function issueText(issue: any): string {
  const d = issue.detail || {}
  switch (issue.kind) {
    case 'not_in_year':
      return $t('plan.issue.notInYear')
    case 'not_offered_at_campus':
      return $t('plan.issue.notHere', {
        campus: d.campus,
        elsewhere: (d.elsewhere || []).join('、') || '—'
      })
    case 'not_offered_in_period':
      return (d.offered_in || []).length
        ? $t('plan.issue.notThen', { periods: (d.offered_in || []).join('、') })
        : $t('plan.issue.notThenAtAll')
    case 'missing_prerequisite': {
      if (d.any_of?.length) return $t('plan.issue.needAny', { units: d.any_of.join(' / ') })
      const units = d.all_of?.length ? d.all_of.join('、') : describeRule(d.rule)
      return units ? $t('plan.issue.needAll', { units }) : $t('plan.issue.needUnknown')
    }
    case 'missing_corequisite': {
      const flat = [...(d.any_of || []), ...(d.all_of || [])]
      const units = flat.length ? flat.join('、') : describeRule(d.rule)
      return units ? $t('plan.issue.needWith', { units }) : $t('plan.issue.needUnknown')
    }
    case 'prohibited_with':
      return $t('plan.issue.prohibited', { units: (d.units || []).join('、') })
    case 'duplicate':
      return $t('plan.issue.duplicate')
    default:
      return issue.kind
  }
}

// --- progress --------------------------------------------------------------

const chosenCourse = computed(() => plan.value.courseCode)
const chosenCampus = computed(() => plan.value.campus)

/**
 * The chosen degree, fetched in the browser rather than on the server.
 *
 * Which degree to fetch comes out of localStorage, so the server cannot know
 * it: rendering this page on the server asked the API for the empty path and
 * got the API's own index document back, and that answer - not the degree -
 * was what the page then held. The symptom was the whole "against your degree"
 * card silently missing on a reload of /plan, while reaching the same page by
 * clicking a link showed it, because then setup ran with localStorage already
 * read. Client-only data belongs in a client-only fetch.
 */
const { locale } = useLocale()
const course = ref<any>(null)

async function loadCourse() {
  if (!chosenCourse.value) {
    course.value = null
    return
  }
  const query = new URLSearchParams({
    campus: chosenCampus.value || '',
    locale: locale.value
  })
  try {
    course.value = await apiFetch<any>(
      `/v1/courses/${encodeURIComponent(chosenCourse.value)}?${query}`
    )
  } catch {
    // A degree that has since been withdrawn, or the API being down. The
    // planner still checks units; it just cannot draw the bars.
    course.value = null
  }
}

onMounted(loadCourse)
watch([chosenCourse, chosenCampus, locale], loadCourse)

const { data: courseList } = await useLocalisedApiFetch<any>(
  () => `/v1/courses?limit=200${chosenCampus.value ? `&campus=${chosenCampus.value}` : ''}`,
  { watch: [chosenCampus] }
)

const planned = computed(() => new Set(plan.value.entries.map((e) => e.unit_code)))

const AOS_TYPES = ['specialisation', 'major', 'minor']

/**
 * Credit points planned against each top-level requirement group.
 *
 * Two kinds of requirement, and conflating them is what made "Part C.
 * Specialist studies" read 0/36 for a student who had planned the whole thing.
 *
 * Most parts list **units**, and those are simply matched against the plan.
 * Part C lists **specialisations** - four of them, each 36 points, of which the
 * student does one. So its units cannot be summed: adding all four would report
 * 144/36. The part is credited with its best-matching specialisation instead,
 * and the matched one is named, because "36/36 via Algorithms and software"
 * tells the student something "36/36" does not.
 */
const progress = computed(() => {
  if (!course.value?.containers) return []
  const facts = course.value.units || {}
  const aosUnits = new Map<string, string[]>(
    (course.value.areas_of_study || []).map((a: any) => [a.code, a.unit_codes || []])
  )
  const aosTitle = new Map<string, string>(
    (course.value.areas_of_study || []).map((a: any) => [a.code, a.title])
  )

  const unitsIn = (node: any): string[] => [
    ...(node.items || []).filter((i: any) => i.type === 'unit').map((i: any) => i.code),
    ...(node.containers || []).flatMap(unitsIn)
  ]
  const choicesIn = (node: any): string[] => [
    ...(node.items || [])
      .filter((i: any) => AOS_TYPES.includes(i.type))
      .map((i: any) => i.code),
    ...(node.containers || []).flatMap(choicesIn)
  ]
  // What a unit is worth. The course endpoint describes the units the degree
  // names; the checker describes the units actually in the plan. A free
  // elective is credited with units in the second set and not the first, so
  // both are needed - reading only the first scored two planned units as 6
  // credit points instead of 12.
  const worth = (code: string) =>
    Number(facts[code]?.credit_points ?? report.value?.unit_credit_points?.[code] ?? 0)

  const score = (codes: string[]) => {
    const done = codes.filter((c) => planned.value.has(c))
    return { count: done.length, points: done.reduce((sum, c) => sum + worth(c), 0) }
  }

  const rows = course.value.containers.map((node: any) => {
    const direct = score(unitsIn(node))
    let points = direct.points
    let count = direct.count
    let via: string | null = null
    const claimed = new Set(unitsIn(node).filter((c) => planned.value.has(c)))

    const choices = choicesIn(node)
    if (choices.length) {
      let best = { points: 0, count: 0, code: '' }
      for (const code of choices) {
        const scored = score(aosUnits.get(code) || [])
        if (scored.points > best.points) best = { ...scored, code }
      }
      points += best.points
      count += best.count
      // Only worth naming once the student has actually started one.
      if (best.code && best.points > 0) via = aosTitle.get(best.code) || best.code
      for (const code of aosUnits.get(best.code) || []) {
        if (planned.value.has(code)) claimed.add(code)
      }
    }

    return {
      title: node.title,
      required: node.credit_points,
      planned: points,
      count,
      via,
      free: !!node.free_elective,
      claimed
    }
  })

  // A free elective part is not a list to match against - it is "anything else
  // you take". So it is credited with the units no other part has claimed,
  // which is what the Handbook means by the words and what a student sees when
  // they look at their own plan. Without this, a plan holding FIT1056 and
  // FIT1061 - real units, in no other part - reported Part E as 0/48.
  //
  // The parts that name their units are scored first, above, so a unit only
  // falls through to here once nothing else has taken it.
  const spoken = new Set<string>()
  for (const row of rows) {
    if (!row.free) for (const code of row.claimed) spoken.add(code)
  }
  const free = rows.filter((row: any) => row.free)
  if (free.length) {
    const leftover = [...planned.value].filter((code) => !spoken.has(code))
    // No degree in the catalogue has two of these - 55 have one, 448 have
    // none, measured over all 503. The loop still guards the case: splitting
    // leftovers between two free parts would be a guess, so the first is
    // credited and any other keeps whatever it lists. Under-reporting beats
    // counting a unit twice.
    const first = free[0]
    const points = leftover.reduce((sum, c) => sum + worth(c), 0)
    // Capped: a student with 60 points spare has not completed 60/48 of a part.
    first.planned = first.required ? Math.min(points, first.required) : points
    first.count = leftover.length
    // The number no longer came from the best-matching minor, so the line
    // naming that minor would be describing a different figure.
    first.via = null
  }

  return rows.map(({ claimed: _claimed, ...row }: any) => row)
})

// --- export and import -----------------------------------------------------

const importError = ref('')

function download() {
  const blob = new Blob([exported()], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `monash-hub-plan-${plan.value.startYear}.json`
  link.click()
  URL.revokeObjectURL(url)
}

function upload(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    const failure = imported(String(reader.result))
    importError.value = failure ? $t(failure) : ''
  }
  reader.readAsText(file)
}

const showOptional = ref(false)
function togglePeriod(period: string) {
  const at = plan.value.periods.indexOf(period)
  if (at >= 0) {
    plan.value.periods.splice(at, 1)
    plan.value.entries = plan.value.entries.filter((e) => e.teaching_period !== period)
  } else {
    plan.value.periods.push(period)
  }
}

function shortPeriod(period: string): string {
  const key = `plan.period.${period}`
  const label = $t(key)
  return label === key ? period : label
}

useHead({ title: $t('plan.title') })
</script>

<template>
  <div class="page">
    <header class="intro">
      <h1>{{ $t('plan.title') }}</h1>
      <p class="lede">{{ $t('plan.lede') }}</p>
    </header>

    <div class="toolbar">
      <label class="field">
        <span>{{ $t('tree.campus') }}</span>
        <select v-model="plan.campus" class="input">
          <option value="Malaysia">{{ $t('tree.campusMalaysia') }}</option>
          <option value="Clayton">Clayton</option>
          <option value="">{{ $t('tree.campusAny') }}</option>
        </select>
      </label>

      <label class="field">
        <span>{{ $t('plan.course') }}</span>
        <select v-model="plan.courseCode" class="input">
          <option value="">{{ $t('plan.noCourse') }}</option>
          <option v-for="c in courseList?.results || []" :key="c.course_code" :value="c.course_code">
            {{ c.course_code }} {{ c.title }}
          </option>
        </select>
      </label>

      <label class="field field--narrow">
        <span>{{ $t('plan.startYear') }}</span>
        <input v-model.number="plan.startYear" class="input" type="number" min="2020" max="2040" />
      </label>

      <div class="actions">
        <button class="btn btn--ghost btn--small" type="button" @click="addYear">
          {{ $t('plan.addYear') }}
        </button>
        <button class="btn btn--ghost btn--small" type="button" @click="showOptional = !showOptional">
          {{ $t('plan.periods') }}
        </button>
        <button class="btn btn--ghost btn--small" type="button" @click="download">
          {{ $t('plan.export') }}
        </button>
        <label class="btn btn--ghost btn--small file">
          {{ $t('plan.import') }}
          <input type="file" accept="application/json" @change="upload" />
        </label>
        <button class="btn btn--ghost btn--small" type="button" @click="reset">
          {{ $t('plan.reset') }}
        </button>
      </div>
    </div>

    <div v-if="showOptional" class="periods">
      <span class="periods-label">{{ $t('plan.periodsHelp') }}</span>
      <button
        v-for="period in OPTIONAL_PERIODS"
        :key="period"
        class="chip"
        :class="{ 'chip--on': plan.periods.includes(period) }"
        type="button"
        @click="togglePeriod(period)"
      >{{ shortPeriod(period) }}</button>
    </div>

    <p v-if="importError" class="warn">{{ importError }}</p>

    <div class="split">
      <section class="grid">
        <article v-for="year in yearsList" :key="year" class="year">
          <header class="year-head">
            <h2>{{ $t('plan.yearLabel', { year }) }}</h2>
            <button
              v-if="yearsList.length > 1"
              class="drop"
              type="button"
              :aria-label="$t('plan.removeYear')"
              @click="removeYear(year)"
            >×</button>
          </header>

          <div v-for="period in plan.periods" :key="period" class="slot">
            <div class="slot-head">
              <span class="slot-name">{{ shortPeriod(period) }}</span>
              <span class="slot-count">
                {{ slotEntries(year, period).length }}
              </span>
            </div>

            <ul class="units">
              <li
                v-for="entry in slotEntries(year, period)"
                :key="entry.unit_code"
                class="unit"
                :class="{
                  'unit--error': entryIssues(entry).some((i) => i.severity === 'error'),
                  'unit--warn': entryIssues(entry).every((i) => i.severity === 'warning')
                    && entryIssues(entry).length > 0
                }"
              >
                <div class="unit-line">
                  <NuxtLink class="unit-code" :to="`/units/${entry.unit_code}`">
                    {{ entry.unit_code }}
                  </NuxtLink>
                  <NuxtLink
                    class="unit-tree"
                    :to="`/tree?unit=${entry.unit_code}&campus=${plan.campus}`"
                    :title="$t('courses.openTree')"
                  >⤳</NuxtLink>
                  <button
                    class="drop"
                    type="button"
                    :aria-label="$t('plan.removeUnit')"
                    @click="remove(entry)"
                  >×</button>
                </div>
                <p v-for="(issue, i) in entryIssues(entry)" :key="i" class="issue">
                  {{ issueText(issue) }}
                </p>
              </li>
            </ul>

            <div v-if="picking?.year === year && picking?.period === period" class="picker">
              <input
                ref="pickerInput"
                v-model="query"
                class="input"
                :placeholder="$t('plan.searchPlaceholder')"
                autocomplete="off"
                @keydown.esc="picking = null"
              />
              <ul v-if="results.length" class="results">
                <li v-for="unit in results" :key="unit.unit_code">
                  <button type="button" @click="place(unit.unit_code)">
                    <span class="unit-code">{{ unit.unit_code }}</span>
                    <span class="result-title">{{ unit.title }}</span>
                  </button>
                </li>
              </ul>
              <p v-else-if="query.length >= 2 && !searching" class="muted">
                {{ $t('plan.noMatches') }}
              </p>
              <button class="btn btn--ghost btn--small" type="button" @click="picking = null">
                {{ $t('plan.done') }}
              </button>
            </div>
            <button
              v-else
              class="add"
              type="button"
              @click="openPicker(year, period)"
            >+ {{ $t('plan.addUnit') }}</button>
          </div>
        </article>
      </section>

      <aside class="panel">
        <section class="card">
          <h2>{{ $t('plan.summary') }}</h2>
          <p class="totals">
            <strong>{{ report?.credit_points ?? 0 }}</strong>
            <span v-if="course?.credit_points"> / {{ course.credit_points }}</span>
            {{ $t('courses.creditPoints') }}
          </p>
          <p v-if="checking" class="muted">{{ $t('plan.checking') }}</p>
          <p v-else-if="!plan.entries.length" class="muted">{{ $t('plan.empty') }}</p>
          <p v-else-if="!errorCount && !warningCount" class="ok">{{ $t('plan.allClear') }}</p>
          <template v-else>
            <p v-if="errorCount" class="warn">{{ $t('plan.errors', { n: errorCount }) }}</p>
            <p v-if="warningCount" class="note">{{ $t('plan.warnings', { n: warningCount }) }}</p>
          </template>
        </section>

        <section v-if="progress.length" class="card">
          <h2>{{ $t('plan.progress') }}</h2>
          <ul class="bars">
            <li v-for="row in progress" :key="row.title">
              <div class="bar-line">
                <span class="bar-name">{{ row.title }}</span>
                <span class="bar-num">{{ row.planned }}<template v-if="row.required">/{{ row.required }}</template></span>
              </div>
              <div class="bar">
                <span
                  class="bar-fill"
                  :style="{ width: `${row.required ? Math.min(100, (row.planned / row.required) * 100) : 0}%` }"
                />
              </div>
              <!-- Which specialisation the points came from. A part that asks
                   for one of four is answered by naming the one, not by a
                   number that could have come from any of them. -->
              <p v-if="row.via" class="tiny muted via">{{ $t('plan.via', { name: row.via }) }}</p>
              <!-- And for a free elective part, why units it never lists are
                   counted towards it. -->
              <p v-else-if="row.free && row.count" class="tiny muted via">
                {{ $t('plan.freeElective', { n: row.count }) }}
              </p>
            </li>
          </ul>
        </section>

        <section class="card note-card">
          <p>{{ $t('plan.privacy') }}</p>
        </section>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: var(--container); margin: 0 auto; padding: var(--s5) var(--s4) var(--s7); }
.intro h1 { margin: 0 0 var(--s2); }
.lede { color: var(--muted); margin: 0 0 var(--s5); max-width: var(--measure-lede); }

/* Grid, not flex-wrap.
 *
 * As a flex row every field took a whole line to itself, so the four controls
 * stacked into four rows on a 1440px screen. The cause was the course <select>:
 * 200 options with long titles give it a max-content width in the thousands of
 * pixels, and `max-width` on the .input constrained the select without ever
 * constraining the .field wrapping it. Named tracks plus `min-width: 0` are
 * what stop a wide option list from deciding the layout. */
.toolbar {
  display: grid;
  grid-template-columns: minmax(0, 200px) minmax(0, 1fr) 110px auto;
  gap: var(--s3); align-items: end;
  padding: var(--s3); background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); margin-bottom: var(--s3);
}
.field { display: grid; gap: var(--s1); font-size: 0.8rem; color: var(--muted); min-width: 0; }
.field--narrow { max-width: 110px; }
.input {
  padding: var(--s2) var(--s3); border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm); font: inherit; background: var(--surface); color: var(--text);
  width: 100%; min-width: 0;
}
.actions { display: flex; flex-wrap: wrap; gap: var(--s2); justify-self: end; }

/* The five buttons need ~375px; below this the row cannot hold them as well. */
@media (max-width: 1100px) {
  .toolbar { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) 110px; }
  .actions { grid-column: 1 / -1; justify-self: start; }
}
@media (max-width: 620px) {
  .toolbar { grid-template-columns: 1fr; }
  .field--narrow { max-width: none; }
}
.file { position: relative; overflow: hidden; cursor: pointer; }
.file input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }

.periods { display: flex; flex-wrap: wrap; gap: var(--s2); align-items: center; margin-bottom: var(--s3); }
.periods-label { font-size: 0.8rem; color: var(--muted); }
.chip {
  border: 1px solid var(--border-strong); background: var(--surface); color: var(--text);
  border-radius: var(--radius-pill); padding: var(--s1) var(--s3); font: inherit;
  font-size: 0.8rem; cursor: pointer;
}
.chip--on { background: var(--navy); color: var(--text-inverse); border-color: var(--navy); }

.split { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: var(--s4); align-items: start; }
.grid { display: grid; gap: var(--s3); }

.year { border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); }
.year-head {
  display: flex; align-items: center; gap: var(--s2);
  padding: var(--s3) var(--s4); border-bottom: 1px solid var(--border);
}
.year-head h2 { margin: 0; font-size: 0.95rem; }
.drop {
  margin-left: auto; border: 0; background: none; color: var(--muted);
  font-size: 1.1rem; line-height: 1; cursor: pointer; padding: 0 var(--s1);
}
.drop:hover { color: var(--danger); }

.slot { padding: var(--s3) var(--s4); border-top: 1px solid var(--border); }
.slot:first-of-type { border-top: 0; }
.slot-head { display: flex; gap: var(--s2); align-items: baseline; margin-bottom: var(--s2); }
.slot-name { font-size: 0.8rem; font-weight: 600; color: var(--muted); }
.slot-count { font-size: 0.75rem; color: var(--muted); }

.units { list-style: none; margin: 0 0 var(--s2); padding: 0; display: grid; gap: var(--s2); }
.unit {
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  padding: var(--s2) var(--s3); background: var(--surface);
}
.unit--error { border-color: var(--danger); background: var(--danger-bg); }
.unit--warn { border-color: #fcd9a4; background: var(--warning-bg); }
.unit-line { display: flex; align-items: center; gap: var(--s2); }
.unit-code { font: 600 0.82rem var(--font-mono); color: var(--navy); text-decoration: none; }
.unit-tree { color: var(--muted); text-decoration: none; }
.unit-tree:hover { color: var(--blue); }
.issue { margin: var(--s1) 0 0; font-size: 0.78rem; color: var(--danger); }
.unit--warn .issue { color: var(--warning); }

.add {
  width: 100%; border: 1px dashed var(--border-strong); background: none;
  border-radius: var(--radius-sm); padding: var(--s2); cursor: pointer;
  font: inherit; font-size: 0.82rem; color: var(--muted);
}
.add:hover { border-color: var(--blue); color: var(--blue); }

.picker { display: grid; gap: var(--s2); }
.picker .input { max-width: none; }
.results { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; max-height: 220px; overflow-y: auto; }
.results button {
  display: flex; gap: var(--s2); width: 100%; text-align: left; border: 0;
  background: none; padding: var(--s2); border-radius: var(--radius-sm);
  cursor: pointer; font: inherit; color: var(--text);
}
.results button:hover { background: var(--blue-50); }
.result-title { font-size: 0.85rem; color: var(--muted); }

.panel { display: grid; gap: var(--s3); position: sticky; top: calc(var(--header-h) + var(--s3)); }
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: var(--s4);
}
.card h2 { margin: 0 0 var(--s2); font-size: 0.95rem; }
.totals { margin: 0 0 var(--s2); font-size: 0.9rem; color: var(--muted); }
.totals strong { font-size: 1.4rem; color: var(--text); }
.ok { margin: 0; color: var(--success); font-size: 0.85rem; }
.warn { margin: 0 0 var(--s1); color: var(--danger); font-size: 0.85rem; }
.note { margin: 0; color: var(--warning); font-size: 0.85rem; }
.muted { margin: 0; color: var(--muted); font-size: 0.85rem; }
.note-card p { margin: 0; font-size: 0.78rem; color: var(--muted); }

.bars { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--s3); }
.bar-line { display: flex; gap: var(--s2); align-items: baseline; margin-bottom: var(--s1); }
.via { margin: var(--s1) 0 0; }
.bar-name { font-size: 0.8rem; flex: 1; }
.bar-num { font-size: 0.75rem; color: var(--muted); white-space: nowrap; }
.bar { height: 6px; background: var(--surface-2); border-radius: var(--radius-pill); overflow: hidden; }
.bar-fill { display: block; height: 100%; background: var(--blue); }

@media (max-width: 900px) {
  .split { grid-template-columns: minmax(0, 1fr); }
  .panel { position: static; }
  .actions { margin-left: 0; }
}
</style>
