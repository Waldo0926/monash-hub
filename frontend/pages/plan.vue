<script setup lang="ts">
import { CAMPUS_CHOICES } from '~/composables/useCampuses'
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
import { toCsv } from '~/utils/csv'
import { handbookYearFor } from '~/composables/useHandbookYear'
import { MAX_YEARS, OPTIONAL_PERIODS, type PlanEntry } from '~/composables/usePlan'

const { $t } = useNuxtApp()
const campusName = useCampusName()
const {
  plan, yearsList, slotEntries, add, remove, move, reset, addYear, removeYear, exported, imported,
  undo, redo, canUndo, canRedo, savedAt, library
} = usePlan()

/**
 * The slot the add-unit dialog was opened for. The dialog does its own search
 * and preview; this page only says where the unit goes and puts it there.
 */
const picking = ref<{ year: number; period: string } | null>(null)

function openPicker(year: number, period: string) {
  picking.value = { year, period }
}

function place(unitCode: string) {
  if (!picking.value) return
  add(unitCode, picking.value.year, picking.value.period)
}

// --- checking --------------------------------------------------------------

const report = ref<any>(null)
const checking = ref(false)
const checkError = ref('')
let checkTimer: ReturnType<typeof setTimeout> | undefined

async function check() {
  if (!plan.value.entries.length) {
    report.value = null
    return
  }
  checking.value = true
  checkError.value = ''
  try {
    report.value = await apiFetch<any>('/v1/plan/check', {
      method: 'POST',
      // No Handbook year: the API checks each unit against the Handbook of
      // the calendar year it is placed in, or the nearest loaded one when that
      // year's is not (a plan starting in 2025 reads 2026). Sending a start
      // year here used to force one Handbook onto the whole plan.
      body: {
        campus: plan.value.campus,
        entries: plan.value.entries
      }
    })
  } catch (caught) {
    // The report on screen is from before this change; say so rather than
    // let it pass for a verdict on the plan as it is now.
    checkError.value = apiErrorMessage(caught, $t)
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
      return $t('plan.issue.notInYear', { year: d.handbook_year ?? '' })
    // The API sends the Handbook's English names; the sentence around them is
    // already in the reader's language, so the names follow it.
    case 'not_offered_at_campus':
      return $t('plan.issue.notHere', {
        campus: campusName(d.campus),
        elsewhere: (d.elsewhere || []).map(campusName).join('、') || '—'
      })
    case 'not_offered_in_period':
      return (d.offered_in || []).length
        ? $t('plan.issue.notThen', { periods: (d.offered_in || []).map(shortPeriod).join('、') })
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

// Which Handbooks are loaded, for units and for degrees. A plan reads each year
// from that year's Handbook, and the degree's rules from the year the student
// started in, because that is the course version they are enrolled in. Left to
// the API's default both came from the site's current Handbook, 2027 from
// October 2026, which drops units like FIT1058 that are still taught in 2026.
const { data: unitYears } = await useApiFetch<any>('/v1/units/filters')
const { data: courseYears } = await useApiFetch<any>('/v1/courses/filters')
const unitHandbook = (year: number) => handbookYearFor(year, unitYears.value?.years)
const courseHandbook = computed(() => handbookYearFor(plan.value.startYear, courseYears.value?.years))

async function loadCourse() {
  if (!chosenCourse.value) {
    course.value = null
    return
  }
  const query = new URLSearchParams({
    campus: chosenCampus.value || '',
    locale: locale.value
  })
  if (courseHandbook.value) query.set('year', String(courseHandbook.value))
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
watch([chosenCourse, chosenCampus, locale, courseHandbook], loadCourse)

const { data: courseList } = await useLocalisedApiFetch<any>(
  () => {
    const params = new URLSearchParams({ limit: '200' })
    if (chosenCampus.value) params.set('campus', chosenCampus.value)
    if (courseHandbook.value) params.set('year', String(courseHandbook.value))
    return `/v1/courses?${params}`
  },
  { watch: [chosenCampus, courseHandbook] }
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
const requirements = computed(() => {
  if (!course.value?.containers) return null
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

  // Which part each planned unit counts towards, for the colour on its card.
  // Named parts first, in the order the degree lists them, then the free
  // elective part takes whatever is left - the same order the scoring above
  // uses, so a card never says "Part A" while the bar counted it under C.
  const partOf = new Map<string, number>()
  rows.forEach((row: any, index: number) => {
    if (row.free) return
    for (const code of row.claimed) if (!partOf.has(code)) partOf.set(code, index)
  })
  if (free.length) {
    const at = rows.indexOf(free[0])
    for (const code of planned.value) if (!partOf.has(code)) partOf.set(code, at)
  }

  return {
    partOf,
    rows: rows.map(({ claimed: _claimed, ...row }: any, index: number) => ({
      ...row,
      index,
      letter: partLetter(row.title, index),
      tone: partTone(row, index)
    }))
  }
})

/**
 * The short tag on a unit card. Handbook parts are titled "Part A. Foundation
 * studies", and the translated titles keep the letter at the front, so the
 * letter is read off the title; a degree whose parts are not lettered gets a
 * number instead.
 */
function partLetter(title: string, index: number): string {
  const match = /^(?:Part\s+)?([A-Z])(?=[\s.。:：]|$)/.exec((title || '').trim())
  return match?.[1] ?? String(index + 1)
}

/**
 * One of six colours. The free elective part is always the grey one: it is
 * "everything else", and giving it a loud colour made the electives look like
 * the most important units on the map.
 */
function partTone(row: any, index: number): number {
  return row.free ? 6 : (index % 5) + 1
}

/** The parts worth a row in the side panel. */
const progress = computed(() =>
  // A container with no credit points of its own and nothing planned in it is
  // a heading the Handbook uses to group rules ("Rules", 0). As a bar it was
  // an empty track with a 0 next to it, which tells the reader nothing.
  (requirements.value?.rows || []).filter((row: any) => row.required || row.planned)
)

function partFor(code: string) {
  const index = requirements.value?.partOf.get(code)
  return index === undefined ? null : requirements.value!.rows[index]
}

// --- export and import -----------------------------------------------------

const importError = ref('')

function download() {
  const blob = new Blob([exported()], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${fileStem()}.json`
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

// --- what the map shows on each card -----------------------------------------

/** The Handbook title, from the check, or from the degree when the check has not come back yet. */
function titleOf(code: string): string {
  return report.value?.unit_titles?.[code] || course.value?.units?.[code]?.title || ''
}

function worthOf(code: string): number {
  return Number(report.value?.unit_credit_points?.[code] ?? course.value?.units?.[code]?.credit_points ?? 0)
}

function pointsIn(entries: PlanEntry[]): number {
  return entries.reduce((sum, entry) => sum + worthOf(entry.unit_code), 0)
}

function yearPoints(year: number): number {
  return pointsIn(plan.value.entries.filter((e) => e.year === year))
}

function slotHasError(year: number, period: string): boolean {
  return slotEntries(year, period).some((entry) => entryIssues(entry).some((i) => i.severity === 'error'))
}

function cardState(entry: PlanEntry): '' | 'error' | 'warn' {
  const issues = entryIssues(entry)
  if (issues.some((i) => i.severity === 'error')) return 'error'
  return issues.length ? 'warn' : ''
}

/**
 * A full-time load is four units. Empty slots up to that are drawn so the row
 * reads as a semester; once it is full, adding a fifth moves to a small button
 * by the semester's name instead of a whole empty card on a row of its own.
 */
const LOAD = 4
function placeholders(year: number, period: string): number {
  return Math.max(0, LOAD - slotEntries(year, period).length)
}

// --- moving units ----------------------------------------------------------
//
// Two ways, because dragging only exists for a mouse. The "move to" menu on
// each card is a real <select>, so it works with a keyboard, a screen reader
// and a phone's own picker without any of the long-press code a touch drag
// would need.

const dragging = ref<PlanEntry | null>(null)
const dropTarget = ref('')

function slotKey(year: number, period: string) {
  return `${year}|${period}`
}

function onDragStart(entry: PlanEntry, event: DragEvent) {
  dragging.value = entry
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', entry.unit_code)
  }
}

function onDragOver(year: number, period: string) {
  if (dragging.value) dropTarget.value = slotKey(year, period)
}

function onDragLeave(event: DragEvent) {
  // dragleave fires when the pointer crosses into a child card too; only a
  // leave to somewhere outside the row clears the highlight.
  const row = event.currentTarget as Node
  if (!row.contains(event.relatedTarget as Node | null)) dropTarget.value = ''
}

function onDrop(year: number, period: string) {
  if (dragging.value) move(dragging.value, year, period)
  onDragEnd()
}

function onDragEnd() {
  dragging.value = null
  dropTarget.value = ''
}

function moveTo(entry: PlanEntry, event: Event) {
  const select = event.target as HTMLSelectElement
  const [year, ...rest] = select.value.split('|')
  if (year && rest.length) move(entry, Number(year), rest.join('|'))
  select.value = ''
}

// --- toolbar ---------------------------------------------------------------

function confirmReset() {
  // The only button on the page that cannot be put back by hand, so it asks.
  // Undo would also bring it back, but nobody looks for undo after "clear".
  if (!plan.value.entries.length || window.confirm($t('plan.resetConfirm'))) reset()
}

/**
 * The plan as a spreadsheet: one row per unit, in plan order. JSON is for
 * moving a plan between browsers; this is for an advisor's email or a print-out
 * you can annotate.
 */
function downloadCsv() {
  const order = (period: string) => {
    const at = plan.value.periods.indexOf(period)
    return at < 0 ? 99 : at
  }
  const rows = [...plan.value.entries]
    .sort((a, b) => a.year - b.year || order(a.teaching_period) - order(b.teaching_period))
    .map((entry) => [
      entry.year,
      shortPeriod(entry.teaching_period),
      entry.unit_code,
      titleOf(entry.unit_code),
      worthOf(entry.unit_code) || '',
      partFor(entry.unit_code)?.title || '',
      entryIssues(entry).map(issueText).join(' ')
    ])
  const head = ['year', 'teaching_period', 'unit_code', 'title', 'credit_points', 'counts_towards', 'issues']
  const blob = new Blob([toCsv([head, ...rows])], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${fileStem()}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

/** "monash-hub-plan-2026", or the plan's own name when it has one that survives as a file name. */
function fileStem(): string {
  const name = plan.value.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
  return name ? `monash-hub-${name}` : `monash-hub-plan-${plan.value.startYear}`
}

function print() {
  window.print()
}

/**
 * CSV, export, import and print live in one "More" menu: they are used once in
 * a while, and four buttons for them pushed undo and the teaching periods off
 * a phone's first screen. A <details> needs no script to open and works with
 * a keyboard; it is closed again after each action.
 */
const moreMenu = ref<HTMLDetailsElement | null>(null)
function fromMenu(action: (event?: any) => void) {
  return (event?: any) => {
    action(event)
    if (moreMenu.value) moreMenu.value.open = false
  }
}
function closeMoreOutside(event: MouseEvent) {
  if (moreMenu.value?.open && !moreMenu.value.contains(event.target as Node)) moreMenu.value.open = false
}
onMounted(() => document.addEventListener('click', closeMoreOutside))
onBeforeUnmount(() => document.removeEventListener('click', closeMoreOutside))

// The first step on an empty plan points at the degree box.
const degreeSelect = ref<HTMLSelectElement | null>(null)
function focusDegree() {
  degreeSelect.value?.focus()
}

/**
 * The verdict pill says how many problems there are; clicking it goes to the
 * first card that has one, so a student does not scan four years of cards
 * looking for the red one.
 */
function jumpToIssue() {
  const card = document.querySelector<HTMLElement>('.ucard--error, .ucard--warn')
  if (!card) return
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  card.scrollIntoView({ block: 'center', behavior: still ? 'auto' : 'smooth' })
  card.querySelector<HTMLElement>('.ucard-code')?.focus({ preventScroll: true })
}

/** Ctrl/Cmd+Z and Shift+Ctrl/Cmd+Z (or Ctrl+Y), except while typing in a field. */
function onKey(event: KeyboardEvent) {
  if (!(event.ctrlKey || event.metaKey)) return
  const target = event.target as HTMLElement | null
  if (target?.closest('input, textarea, select, [contenteditable="true"]')) return
  if (picking.value) return
  const key = event.key.toLowerCase()
  if (key === 'z' && !event.shiftKey) {
    event.preventDefault()
    undo()
  } else if ((key === 'z' && event.shiftKey) || key === 'y') {
    event.preventDefault()
    redo()
  }
}

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))

// --- summary ---------------------------------------------------------------

const plannedPoints = computed(() => report.value?.credit_points ?? 0)
const requiredPoints = computed(() => Number(course.value?.credit_points) || 0)
const ringValue = computed(() =>
  requiredPoints.value ? plannedPoints.value / requiredPoints.value : null
)
const percent = computed(() => Math.min(100, Math.round((ringValue.value ?? 0) * 100)))

/** "Saved on this device" plus the time, refreshed every half minute so "just now" ages. */
const now = ref(Date.now())
let clock: ReturnType<typeof setInterval> | undefined
onMounted(() => { clock = setInterval(() => (now.value = Date.now()), 30_000) })
onBeforeUnmount(() => clearInterval(clock))
const savedLabel = computed(() => {
  if (!savedAt.value) return ''
  const minutes = Math.floor((now.value - savedAt.value) / 60_000)
  if (minutes < 1) return $t('plan.savedJustNow')
  if (minutes < 60) return $t('plan.savedMinutes', { n: minutes })
  return $t('plan.saved')
})

const status = computed<'empty' | 'checking' | 'failed' | 'error' | 'warn' | 'ok'>(() => {
  if (!plan.value.entries.length) return 'empty'
  if (checking.value && !report.value) return 'checking'
  if (checkError.value) return 'failed'
  if (errorCount.value) return 'error'
  if (warningCount.value) return 'warn'
  return 'ok'
})

useSeoMeta({ title: () => $t('plan.title') })
</script>

<template>
  <div class="page">
    <header class="intro">
      <div class="intro-text">
        <h1>{{ $t('plan.title') }}</h1>
        <p class="lede">{{ $t('plan.lede') }}</p>
      </div>

      <div class="tools" role="toolbar" :aria-label="$t('plan.tools')">
        <div class="tool-group">
          <button
            class="tool tool--icon"
            type="button"
            :disabled="!canUndo"
            :title="$t('plan.undo')"
            :aria-label="$t('plan.undo')"
            @click="undo"
          ><PlanIcon name="undo" /></button>
          <button
            class="tool tool--icon"
            type="button"
            :disabled="!canRedo"
            :title="$t('plan.redo')"
            :aria-label="$t('plan.redo')"
            @click="redo"
          ><PlanIcon name="redo" /></button>
        </div>
        <div class="tool-group">
          <button
            class="tool"
            :class="{ 'tool--on': showOptional }"
            type="button"
            :aria-expanded="showOptional"
            @click="showOptional = !showOptional"
          ><PlanIcon name="calendar" />{{ $t('plan.periods') }}</button>
          <details ref="moreMenu" class="more">
            <summary class="tool">{{ $t('plan.more') }}<PlanIcon name="chevron-down" :size="14" /></summary>
            <div class="more-list">
              <button class="tool" type="button" @click="fromMenu(downloadCsv)()">
                <PlanIcon name="download" />CSV
              </button>
              <button class="tool" type="button" @click="fromMenu(download)()">
                <PlanIcon name="download" />{{ $t('plan.export') }}
              </button>
              <label class="tool file">
                <PlanIcon name="upload" />{{ $t('plan.import') }}
                <input type="file" accept="application/json" @change="fromMenu(upload)($event)" />
              </label>
              <button class="tool" type="button" @click="fromMenu(print)()">
                <PlanIcon name="print" />{{ $t('plan.print') }}
              </button>
            </div>
          </details>
        </div>
        <button class="tool tool--danger" type="button" @click="confirmReset">
          <PlanIcon name="trash" />{{ $t('plan.reset') }}
        </button>
      </div>
    </header>

    <p v-if="importError" class="banner banner--bad" role="alert">{{ importError }}</p>

    <div class="split">
      <section class="board" :aria-label="$t('plan.title')">
        <div class="board-head">
          <div class="plan-title">
            <input
              v-model.lazy.trim="plan.name"
              class="plan-name"
              type="text"
              maxlength="60"
              :placeholder="$t('plans.untitled')"
              :aria-label="$t('plans.name')"
            />
            <NuxtLink to="/plans" class="plan-all">
              {{ $t('plans.all', { n: library.plans.length }) }}
            </NuxtLink>
            <!-- Next to the name, so nobody takes the plan for something saved
                 to an account. The side panel says the same at length. -->
            <span class="local"><PlanIcon name="lock" :size="13" />{{ $t('plan.localOnly') }}</span>
          </div>
          <div class="settings">
            <label class="ctl">
              <span class="ctl-label">{{ $t('tree.campus') }}</span>
              <select v-model="plan.campus" class="ctl-input">
                <option v-for="choice in CAMPUS_CHOICES" :key="choice" :value="choice">{{ campusName(choice) }}</option>
                <option value="">{{ $t('tree.campusAny') }}</option>
              </select>
            </label>

            <label class="ctl ctl--wide">
              <span class="ctl-label">{{ $t('plan.course') }}</span>
              <select ref="degreeSelect" v-model="plan.courseCode" class="ctl-input">
                <option value="">{{ $t('plan.noCourse') }}</option>
                <option v-for="c in courseList?.results || []" :key="c.course_code" :value="c.course_code">
                  {{ c.course_code }} {{ c.title }}
                </option>
              </select>
              <span v-if="plan.courseCode && courseHandbook" class="ctl-note">
                {{ $t('plan.courseHandbook', { year: courseHandbook }) }}
              </span>
            </label>

            <label class="ctl ctl--narrow">
              <span class="ctl-label">{{ $t('plan.startYear') }}</span>
              <input v-model.number="plan.startYear" class="ctl-input" type="number" min="2020" max="2040" />
            </label>
          </div>

          <!-- The verdict on the whole plan, where the eye already is. The
               side panel has the numbers; this only says whether to look. -->
          <p class="pill-wrap" role="status" aria-live="polite">
            <button
              v-if="status === 'error' || status === 'warn'"
              class="pill pill--jump"
              :class="`pill--${status}`"
              type="button"
              :title="$t('plan.jumpToIssue')"
              @click="jumpToIssue"
            >
              <PlanIcon name="alert" :size="14" />
              {{ status === 'error' ? $t('plan.errors', { n: errorCount }) : $t('plan.warnings', { n: warningCount }) }}
              <span class="visually-hidden">. {{ $t('plan.jumpToIssue') }}</span>
            </button>
            <span v-else class="pill" :class="`pill--${status}`">
              <template v-if="status === 'empty'">{{ $t('plan.empty') }}</template>
              <template v-else-if="status === 'checking'"><PlanIcon name="spinner" :size="14" />{{ $t('plan.checking') }}</template>
              <template v-else-if="status === 'failed'"><PlanIcon name="alert" :size="14" />{{ $t('plan.checkFailed') }}</template>
              <template v-else><PlanIcon name="check" :size="14" />{{ $t('plan.allClear') }}</template>
            </span>
          </p>
        </div>

        <!-- An empty plan opens with what to do first, in order. It goes as
             soon as the first unit is on the map. -->
        <ol v-if="!plan.entries.length" class="start">
          <li>
            <span class="start-n">1</span>
            <span class="start-text">
              {{ $t('plan.start.degree') }}
              <button v-if="!plan.courseCode" type="button" class="start-link" @click="focusDegree">{{ $t('plan.start.pickDegree') }}</button>
            </span>
          </li>
          <li>
            <span class="start-n">2</span>
            <span class="start-text">{{ $t('plan.start.year') }}</span>
          </li>
          <li>
            <span class="start-n">3</span>
            <span class="start-text">{{ $t('plan.start.add') }}</span>
          </li>
        </ol>

        <div v-if="showOptional" class="periods">
          <span class="periods-label">{{ $t('plan.periodsHelp') }}</span>
          <button
            v-for="period in OPTIONAL_PERIODS"
            :key="period"
            class="chip"
            :class="{ 'chip--on': plan.periods.includes(period) }"
            type="button"
            :aria-pressed="plan.periods.includes(period)"
            @click="togglePeriod(period)"
          >{{ shortPeriod(period) }}</button>
        </div>

        <article v-for="(year, yearIndex) in yearsList" :key="year" class="year">
          <header class="year-bar">
            <h2 class="year-name">
              {{ $t('plan.yearNth', { n: yearIndex + 1 }) }}
              <span class="year-num">{{ year }}</span>
            </h2>
            <span v-if="yearPoints(year)" class="year-points">
              {{ $t('plan.cp', { n: yearPoints(year) }) }}
            </span>
            <button
              v-if="yearsList.length > 1"
              class="bar-btn"
              type="button"
              :title="$t('plan.removeYear')"
              :aria-label="`${$t('plan.removeYear')} ${year}`"
              @click="removeYear(year)"
            ><PlanIcon name="trash" :size="15" /></button>
          </header>

          <div
            v-for="period in plan.periods"
            :key="period"
            class="term"
            :class="{ 'term--target': dropTarget === slotKey(year, period) }"
            @dragover.prevent="onDragOver(year, period)"
            @dragleave="onDragLeave"
            @drop.prevent="onDrop(year, period)"
          >
            <div class="term-label">
              <h3 class="term-name">
                {{ shortPeriod(period) }}
                <span
                  v-if="slotHasError(year, period)"
                  class="term-dot"
                  :title="$t('plan.slotHasProblems')"
                ><span class="visually-hidden">{{ $t('plan.slotHasProblems') }}</span></span>
              </h3>
              <p class="term-meta">
                {{ $t(slotEntries(year, period).length === 1 ? 'plan.unitCountOne' : 'plan.unitCount', { n: slotEntries(year, period).length }) }}
                <template v-if="pointsIn(slotEntries(year, period))">
                  · {{ $t('plan.cp', { n: pointsIn(slotEntries(year, period)) }) }}
                </template>
              </p>
              <button
                v-if="!placeholders(year, period)"
                class="term-add"
                type="button"
                :aria-label="`${$t('plan.addUnit')}: ${shortPeriod(period)}, ${year}`"
                @click="openPicker(year, period)"
              ><PlanIcon name="plus" :size="13" />{{ $t('plan.addUnit') }}</button>
            </div>

            <ul class="cards">
              <li
                v-for="entry in slotEntries(year, period)"
                :key="entry.unit_code"
                class="ucard"
                :class="[
                  cardState(entry) && `ucard--${cardState(entry)}`,
                  partFor(entry.unit_code) && `tone-${partFor(entry.unit_code).tone}`,
                  { 'ucard--dragging': dragging === entry }
                ]"
                draggable="true"
                @dragstart="onDragStart(entry, $event)"
                @dragend="onDragEnd"
              >
                <div class="ucard-top">
                  <NuxtLink class="ucard-code" :to="`/units/${entry.unit_code}`">
                    {{ entry.unit_code }}
                  </NuxtLink>
                  <span class="ucard-tools">
                    <NuxtLink
                      class="mini"
                      :to="`/tree?unit=${entry.unit_code}&campus=${plan.campus}`"
                      :title="$t('courses.openTree')"
                      :aria-label="`${$t('courses.openTree')}: ${entry.unit_code}`"
                    ><PlanIcon name="tree" :size="14" /></NuxtLink>
                    <label class="mini mini--select" :title="$t('plan.moveTo')">
                      <PlanIcon name="move" :size="14" />
                      <span class="visually-hidden">{{ $t('plan.moveTo') }} {{ entry.unit_code }}</span>
                      <select @change="moveTo(entry, $event)">
                        <option value="" selected disabled>{{ $t('plan.moveTo') }}</option>
                        <optgroup
                          v-for="(y, yi) in yearsList"
                          :key="y"
                          :label="`${$t('plan.yearNth', { n: yi + 1 })} · ${y}`"
                        >
                          <option
                            v-for="p in plan.periods"
                            :key="p"
                            :value="slotKey(y, p)"
                            :disabled="y === entry.year && p === entry.teaching_period"
                          >{{ shortPeriod(p) }}, {{ y }}</option>
                        </optgroup>
                      </select>
                    </label>
                    <button
                      class="mini mini--remove"
                      type="button"
                      :title="$t('plan.removeUnit')"
                      :aria-label="`${$t('plan.removeUnit')}: ${entry.unit_code}`"
                      @click="remove(entry)"
                    ><PlanIcon name="close" :size="14" /></button>
                  </span>
                </div>
                <p v-if="titleOf(entry.unit_code)" class="ucard-title">{{ titleOf(entry.unit_code) }}</p>
                <ul v-if="entryIssues(entry).length" class="ucard-issues">
                  <li v-for="(issue, i) in entryIssues(entry)" :key="i">
                    <PlanIcon name="alert" :size="12" />{{ issueText(issue) }}
                  </li>
                </ul>
                <div class="ucard-foot">
                  <span v-if="worthOf(entry.unit_code)" class="ucard-cp">
                    {{ $t('plan.cp', { n: worthOf(entry.unit_code) }) }}
                  </span>
                  <span
                    v-if="partFor(entry.unit_code)"
                    class="ucard-part"
                    :title="partFor(entry.unit_code).title"
                  >{{ partFor(entry.unit_code).letter }}</span>
                </div>
              </li>

              <li v-for="n in placeholders(year, period)" :key="`slot-${n}`" class="slot-li" :class="{ 'slot-li--extra': n > 1 }">
                <button
                  class="slot"
                  type="button"
                  :aria-label="`${$t('plan.addUnit')}: ${shortPeriod(period)}, ${year}`"
                  @click="openPicker(year, period)"
                >
                  <PlanIcon name="plus" :size="18" />
                  <span v-if="n === 1" class="slot-text">{{ $t('plan.addUnit') }}</span>
                </button>
              </li>
            </ul>
          </div>
        </article>

        <button class="add-year" type="button" :disabled="yearsList.length >= MAX_YEARS" @click="addYear">
          <PlanIcon name="plus" />{{ $t('plan.addYear') }}
        </button>

        <p class="board-foot">
          <span class="hint">{{ $t('plan.dragHint') }}</span>
          <span v-if="savedLabel" class="saved"><PlanIcon name="check" :size="13" />{{ savedLabel }}</span>
        </p>
      </section>

      <aside class="side">
        <section class="panel panel--progress">
          <h2 class="panel-title">{{ $t('plan.summary') }}</h2>
          <PlanRing :value="ringValue">
            <template v-if="requiredPoints">
              <span class="ring-big">{{ percent }}<small>%</small></span>
              <span class="ring-small">{{ plannedPoints }} / {{ requiredPoints }} {{ $t('courses.creditPoints') }}</span>
            </template>
            <template v-else>
              <span class="ring-big">{{ plannedPoints }}</span>
              <span class="ring-small">{{ $t('courses.creditPoints') }}</span>
            </template>
          </PlanRing>
          <p v-if="!requiredPoints" class="panel-note">{{ $t('plan.pickDegree') }}</p>
          <p v-else-if="course?.title" class="panel-note">{{ course.course_code }} {{ course.title }}</p>

          <dl class="stats">
            <div>
              <dt>{{ $t('plan.stat.units') }}</dt>
              <dd>{{ plan.entries.length }}</dd>
            </div>
            <div :class="{ 'stat--bad': errorCount }">
              <dt>{{ $t('plan.stat.errors') }}</dt>
              <dd>{{ errorCount }}</dd>
            </div>
            <div :class="{ 'stat--warn': warningCount }">
              <dt>{{ $t('plan.stat.warnings') }}</dt>
              <dd>{{ warningCount }}</dd>
            </div>
          </dl>
          <p v-if="checkError" class="tiny bad-text" role="alert">{{ checkError }}</p>
        </section>

        <section v-if="progress.length" class="panel">
          <h2 class="panel-title">{{ $t('plan.progress') }}</h2>
          <ul class="parts">
            <li v-for="row in progress" :key="row.title" :class="`tone-${row.tone}`">
              <div class="part-line">
                <span class="part-tag">{{ row.letter }}</span>
                <span class="part-name">{{ row.title }}</span>
                <span class="part-num">{{ row.planned }}<template v-if="row.required"> / {{ row.required }}</template></span>
              </div>
              <div class="part-bar">
                <span
                  class="part-fill"
                  :style="{ width: `${row.required ? Math.min(100, (row.planned / row.required) * 100) : 0}%` }"
                />
              </div>
              <!-- Which specialisation the points came from. A part that asks
                   for one of four is answered by naming the one, not by a
                   number that could have come from any of them. -->
              <p v-if="row.via" class="part-note">{{ $t('plan.via', { name: row.via }) }}</p>
              <!-- And for a free elective part, why units it never lists are
                   counted towards it. -->
              <p v-else-if="row.free && row.count" class="part-note">
                {{ $t('plan.freeElective', { n: row.count }) }}
              </p>
            </li>
          </ul>
        </section>

        <section class="panel panel--quiet">
          <PlanIcon name="lock" :size="15" />
          <p>{{ $t('plan.privacy') }}</p>
        </section>
      </aside>
    </div>

    <UnitPicker
      v-if="picking"
      :year="picking.year"
      :handbook-year="unitHandbook(picking.year)"
      :period="picking.period"
      :campus="plan.campus"
      :entries="plan.entries"
      :describe="issueText"
      :period-name="shortPeriod"
      @add="place"
      @close="picking = null"
    />
  </div>
</template>

<style scoped>
.page { max-width: 1400px; margin: 0 auto; padding: var(--s5) var(--s5) var(--s7); }

/* --- heading and toolbar --------------------------------------------------- */

.intro {
  display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between;
  gap: var(--s4); margin-bottom: var(--s4);
}
.intro-text { min-width: 0; flex: 1 1 420px; }
.intro h1 { margin: 0 0 var(--s1); }
.lede { color: var(--muted); margin: 0; max-width: var(--measure-lede); font-size: 0.95rem; }

.tools { display: flex; flex-wrap: wrap; gap: var(--s2); align-items: center; }
.tool-group {
  display: inline-flex; background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 2px; box-shadow: var(--shadow-sm);
}
.tool {
  display: inline-flex; align-items: center; gap: 6px;
  min-height: 34px; padding: 0 10px; border: 0; border-radius: 6px;
  background: none; color: var(--text); font: inherit; font-size: 0.85rem; font-weight: 500;
  cursor: pointer; white-space: nowrap;
}
.tool:hover:not(:disabled) { background: var(--surface-2); }
.tool:disabled { color: var(--muted-2); cursor: default; }
.tool--icon { padding: 0 8px; }
.tool--on { background: var(--blue-50); color: var(--brand-700); }
.tool--danger {
  border: 1px solid var(--border); background: var(--surface); box-shadow: var(--shadow-sm);
  min-height: 40px; color: var(--muted);
}
.tool--danger:hover { color: var(--danger); border-color: #f1c4c4; background: var(--danger-bg) !important; }
.file { position: relative; overflow: hidden; }
.file input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
.more { position: relative; }
.more > summary { list-style: none; }
.more > summary::-webkit-details-marker { display: none; }
.more[open] > summary { background: var(--surface-2); }
.more-list {
  position: absolute; right: 0; top: calc(100% + 6px); z-index: 20;
  display: grid; min-width: 150px; padding: 4px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm);
  box-shadow: var(--shadow);
}
.more-list .tool { justify-content: flex-start; width: 100%; }

.banner { margin: 0 0 var(--s3); padding: var(--s2) var(--s3); border-radius: var(--radius-sm); font-size: 0.85rem; }
.banner--bad { background: var(--danger-bg); color: var(--danger); }

.split { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: var(--s4); align-items: start; }

/* --- the board --------------------------------------------------------------- */

.board {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
  box-shadow: var(--shadow); overflow: hidden;
}

.board-head {
  display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between;
  gap: var(--s3); padding: var(--s4) var(--s5);
}
.plan-title { display: flex; align-items: center; gap: var(--s3); flex-basis: 100%; min-width: 0; }
/* The name is an input that looks like a heading until you touch it. */
.plan-name {
  flex: 1; min-width: 0; margin-left: -8px; padding: 2px 8px;
  border: 1px solid transparent; border-radius: 6px; background: none;
  font: 600 1.15rem var(--font); color: var(--text);
}
.plan-name::placeholder { color: var(--text); }
.plan-name:hover { border-color: var(--border); }
.plan-name:focus { border-color: var(--brand); outline: none; box-shadow: 0 0 0 3px var(--blue-50); }
.plan-all { flex: none; font-size: 0.82rem; font-weight: 500; }
.local {
  display: inline-flex; flex: none; align-items: center; gap: 4px;
  color: var(--muted); font-size: 0.78rem; white-space: nowrap;
}
/* Named tracks plus min-width: 0. The degree <select> holds 200 long titles,
   which gives it a max-content width in the thousands of pixels; without the
   minmax(0, ...) that width decides the layout instead of the screen. */
.settings {
  display: grid; grid-template-columns: minmax(0, 190px) minmax(0, 1fr) 96px;
  gap: var(--s3); flex: 1 1 560px; min-width: 0;
}
.ctl { display: grid; gap: 4px; min-width: 0; }
.ctl-label {
  font-size: 0.7rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
  color: var(--muted);
}
.ctl-input {
  width: 100%; min-width: 0; height: 40px; padding: 0 var(--s3);
  border: 1px solid var(--border-strong); border-radius: var(--radius-sm);
  background-color: var(--surface); color: var(--text); font: inherit; font-size: 0.9rem;
}
select.ctl-input {
  appearance: none; -webkit-appearance: none; padding-right: 32px;
  text-overflow: ellipsis;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2356667a' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 12px center;
}
.ctl-input:hover { border-color: var(--muted-2); }
.ctl-note { color: var(--muted-2); font-size: 0.74rem; }

.pill {
  display: inline-flex; align-items: center; gap: 6px; margin: 0;
  min-height: 32px; padding: 0 12px; border-radius: var(--radius-pill);
  font-size: 0.82rem; font-weight: 600; white-space: nowrap;
  border: 1px solid var(--border); color: var(--muted); background: var(--surface-2);
}
.pill--ok { color: var(--success); background: var(--success-bg); border-color: #b7e4d0; }
.pill--error, .pill--failed { color: var(--danger); background: var(--danger-bg); border-color: #f1c4c4; }
.pill--warn { color: var(--warning); background: var(--warning-bg); border-color: #f5dcae; }
.pill-wrap { margin: 0; }
.pill--jump { font: inherit; font-size: 0.82rem; font-weight: 600; cursor: pointer; }
.pill--jump:hover { text-decoration: underline; }

.start {
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s3);
  margin: 0; padding: var(--s4) var(--s5); list-style: none;
  background: var(--blue-50); border-top: 1px solid var(--border);
}
.start li { display: flex; gap: var(--s3); align-items: flex-start; font-size: 0.86rem; line-height: 1.55; }
.start-n {
  display: grid; flex: none; place-items: center; width: 24px; height: 24px;
  border-radius: 50%; background: var(--brand); color: var(--text-inverse);
  font-size: 0.78rem; font-weight: 600;
}
.start-text:lang(ko) { word-break: keep-all; }
.start-link {
  padding: 0; border: 0; background: none; color: var(--brand-700);
  font: inherit; font-weight: 600; text-decoration: underline; cursor: pointer;
}

.periods {
  display: flex; flex-wrap: wrap; gap: var(--s2); align-items: center;
  padding: var(--s3) var(--s5); background: var(--surface-2); border-top: 1px solid var(--border);
}
.periods-label { font-size: 0.8rem; color: var(--muted); }
.chip {
  border: 1px solid var(--border-strong); background: var(--surface); color: var(--text);
  border-radius: var(--radius-pill); padding: 4px 12px; font: inherit;
  font-size: 0.8rem; cursor: pointer;
}
.chip--on { background: var(--ink); color: var(--text-inverse); border-color: var(--ink); }

/* One dark bar per year. It is the only dark block on the page, which is the
   point: it is what the eye uses to find "third year" in a long plan. */
.year-bar {
  display: flex; align-items: center; gap: var(--s3);
  padding: 10px var(--s5); background: var(--ink); color: var(--text-inverse);
}
.year-name {
  margin: 0; font-family: var(--font); font-size: 0.82rem; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase; color: inherit;
}
.year-num { margin-left: 6px; font-family: var(--font-mono); font-weight: 400; letter-spacing: 0; opacity: 0.6; }
.year-points { margin-left: auto; font-size: 0.78rem; opacity: 0.7; }
.bar-btn {
  display: inline-grid; place-items: center; width: 30px; height: 30px; margin-right: -6px;
  border: 0; border-radius: 6px; background: none; color: inherit; opacity: 0.6; cursor: pointer;
}
.year-points + .bar-btn { margin-left: 0; }
.year-name + .bar-btn { margin-left: auto; }
.bar-btn:hover { opacity: 1; background: rgba(255, 255, 255, 0.1); }

.term {
  display: grid; grid-template-columns: 156px minmax(0, 1fr);
  border-top: 1px solid var(--border); transition: background 0.12s;
}
.year-bar + .term { border-top: 0; }
.term--target { background: var(--blue-50); box-shadow: inset 0 0 0 2px var(--brand); }

.term-label {
  padding: var(--s4) var(--s4) var(--s4) var(--s5);
  border-right: 1px solid var(--border); background: #fafbfc;
}
.term-name {
  display: flex; align-items: center; gap: 6px;
  margin: 0; font-family: var(--font); font-size: 0.88rem; font-weight: 600;
}
.term-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--danger); }
.term-meta { margin: 2px 0 0; font-size: 0.76rem; color: var(--muted); }
.term-add {
  display: inline-flex; align-items: center; gap: 4px; margin-top: var(--s2);
  padding: 3px 8px 3px 6px; border: 1px dashed var(--border-strong); border-radius: 6px;
  background: var(--surface); color: var(--muted); font: inherit; font-size: 0.74rem; cursor: pointer;
}
.term-add:hover { border-color: var(--brand); color: var(--brand); }

.cards {
  list-style: none; margin: 0; padding: var(--s3);
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px;
}

/* --- unit cards ---------------------------------------------------------------
 * The colour stripe says which part of the degree the unit counts towards,
 * matching the bars in the side panel. The letter in the corner says the same
 * thing in text, so the colour is never the only signal. */

.ucard {
  --tone: var(--border-strong);
  --tone-bg: var(--surface-2);
  position: relative; display: flex; flex-direction: column;
  min-height: 104px; padding: 10px 10px 10px 16px;
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm); cursor: grab;
  transition: box-shadow 0.15s, border-color 0.15s, transform 0.15s;
}
.ucard::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 5px;
  border-radius: var(--radius-sm) 0 0 var(--radius-sm); background: var(--tone);
}
.ucard:hover { border-color: var(--border-strong); box-shadow: var(--shadow); }
.ucard:active { cursor: grabbing; }
.ucard--dragging { opacity: 0.45; }
.ucard--error { border-color: var(--danger); box-shadow: 0 0 0 1px var(--danger) inset; }
.ucard--warn { border-color: #e9b866; }

.ucard-top { display: flex; align-items: center; gap: 4px; }
.ucard-code {
  font: 600 0.86rem var(--font-mono); letter-spacing: 0.01em; color: var(--navy);
  text-decoration: none;
}
.ucard-code:hover { color: var(--brand); text-decoration: underline; }
.ucard-tools { margin-left: auto; display: inline-flex; gap: 0; margin-right: -4px; }
.mini {
  position: relative; display: inline-grid; place-items: center;
  width: 26px; height: 26px; border: 0; border-radius: 6px; background: none;
  color: var(--muted-2); cursor: pointer; text-decoration: none;
}
.mini:hover, .mini:focus-within { background: var(--surface-2); color: var(--text); }
.mini--remove:hover { color: var(--danger); background: var(--danger-bg); }
/* The move menu is a real <select> laid over the icon, so the browser draws
   the list - a native picker on a phone, a keyboard-usable one on a laptop. */
.mini--select select {
  position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer;
  font-size: 16px;
}
/* On a mouse, the tools only show for the card under the pointer, so a full
   grid reads as units rather than as forty little buttons. */
@media (hover: hover) {
  .ucard-tools { opacity: 0; transition: opacity 0.12s; }
  .ucard:hover .ucard-tools, .ucard:focus-within .ucard-tools { opacity: 1; }
}

.ucard-title {
  margin: 2px 0 0; font-size: 0.78rem; line-height: 1.35; color: var(--muted);
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.ucard-issues { list-style: none; margin: 8px 0 0; padding: 0; display: grid; gap: 4px; }
.ucard-issues li {
  display: flex; gap: 5px; align-items: flex-start;
  padding: 5px 7px; border-radius: 6px; font-size: 0.72rem; line-height: 1.35;
  background: var(--danger-bg); color: var(--danger);
}
.ucard-issues li :deep(svg) { margin-top: 2px; }
.ucard--warn .ucard-issues li { background: var(--warning-bg); color: var(--warning); }
.ucard-foot { display: flex; align-items: center; gap: var(--s2); margin-top: auto; padding-top: 8px; }
.ucard-cp { font-size: 0.72rem; color: var(--muted); }
.ucard-part {
  margin-left: auto; min-width: 20px; padding: 1px 6px; border-radius: 4px; text-align: center;
  font-size: 0.7rem; font-weight: 700; color: var(--tone); background: var(--tone-bg);
}

.slot-li { display: flex; }
.slot {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  min-height: 104px; border: 1.5px dashed var(--border-strong); border-radius: var(--radius-sm);
  background: none; color: var(--muted); font: inherit; cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
}
.slot-li--extra .slot { border-color: var(--border); color: var(--muted-2); }
.slot:hover, .slot-li--extra .slot:hover { border-color: var(--brand); color: var(--brand); background: var(--blue-50); }
.slot-text { font-size: 0.78rem; font-weight: 500; }

.add-year {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  width: calc(100% - 2 * var(--s5)); margin: var(--s4) var(--s5) 0; min-height: 48px;
  border: 1.5px dashed var(--border-strong); border-radius: var(--radius-sm);
  background: none; color: var(--muted); font: inherit; font-size: 0.88rem; font-weight: 500; cursor: pointer;
}
.add-year:hover:not(:disabled) { border-color: var(--brand); color: var(--brand); background: var(--blue-50); }
.add-year:disabled { opacity: 0.5; cursor: default; }

.board-foot {
  display: flex; flex-wrap: wrap; justify-content: space-between; gap: var(--s2);
  margin: 0; padding: var(--s3) var(--s5) var(--s4); font-size: 0.76rem; color: var(--muted-2);
}
.saved { display: inline-flex; align-items: center; gap: 4px; color: var(--success); }
@media (hover: none) {
  .hint { visibility: hidden; }
  /* The unit page links to the tree already; on a phone the card keeps only
     the two tools that change the plan. */
  .ucard-tools .mini:first-child { display: none; }
}

/* --- part colours -------------------------------------------------------------- */

.tone-1 { --tone: var(--part-1); --tone-bg: var(--part-1-bg); }
.tone-2 { --tone: var(--part-2); --tone-bg: var(--part-2-bg); }
.tone-3 { --tone: var(--part-3); --tone-bg: var(--part-3-bg); }
.tone-4 { --tone: var(--part-4); --tone-bg: var(--part-4-bg); }
.tone-5 { --tone: var(--part-5); --tone-bg: var(--part-5-bg); }
.tone-6 { --tone: var(--part-6); --tone-bg: var(--part-6-bg); }

/* --- side panel ----------------------------------------------------------------- */

.side { display: grid; gap: var(--s3); position: sticky; top: calc(var(--header-h) + var(--s3)); }
.panel {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
  padding: var(--s4) var(--s5); box-shadow: var(--shadow-sm);
}
.panel-title {
  margin: 0 0 var(--s3); font-family: var(--font); font-size: 0.72rem; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted);
}
.panel--progress { display: flex; flex-direction: column; align-items: center; text-align: center; }
.panel--progress .panel-title { align-self: flex-start; }
.ring-big { font-size: 2.2rem; font-weight: 700; line-height: 1; letter-spacing: -0.02em; color: var(--text); }
.ring-big small { font-size: 1rem; font-weight: 600; margin-left: 1px; color: var(--muted); }
.ring-small { margin-top: 6px; font-size: 0.76rem; color: var(--muted); }
.panel-note { margin: var(--s3) 0 0; font-size: 0.8rem; color: var(--muted); text-wrap: balance; }

.stats {
  display: grid; grid-template-columns: repeat(3, 1fr); width: 100%;
  margin: var(--s4) 0 0; padding-top: var(--s3); border-top: 1px solid var(--border);
}
.stats div + div { border-left: 1px solid var(--border); }
.stats dt { font-size: 0.7rem; color: var(--muted); }
.stats dd { margin: 0; font-size: 1.2rem; font-weight: 700; color: var(--text); }
.stat--bad dd { color: var(--danger); }
.stat--warn dd { color: var(--warning); }
.bad-text { margin: var(--s2) 0 0; color: var(--danger); }

.parts { list-style: none; margin: 0; padding: 0; display: grid; gap: 14px; }
.part-line { display: flex; gap: var(--s2); align-items: center; margin-bottom: 6px; }
.part-tag {
  flex: none; min-width: 20px; padding: 1px 5px; border-radius: 4px; text-align: center;
  font-size: 0.7rem; font-weight: 700; color: var(--tone); background: var(--tone-bg);
}
.part-name { flex: 1; min-width: 0; font-size: 0.82rem; line-height: 1.3; }
.part-num { font: 500 0.76rem var(--font-mono); color: var(--muted); white-space: nowrap; }
.part-bar { height: 6px; background: var(--surface-2); border-radius: var(--radius-pill); overflow: hidden; }
.part-fill { display: block; height: 100%; background: var(--tone); border-radius: inherit; transition: width 0.4s ease; }
.part-note { margin: 4px 0 0; font-size: 0.74rem; color: var(--muted); }

.panel--quiet {
  display: flex; gap: var(--s2); align-items: flex-start; background: var(--surface-2);
  box-shadow: none; color: var(--muted);
}
.panel--quiet p { margin: 0; font-size: 0.76rem; line-height: 1.5; }
.panel--quiet :deep(svg) { margin-top: 2px; }

/* --- narrower screens ------------------------------------------------------------ */

@media (max-width: 1180px) {
  .split { grid-template-columns: minmax(0, 1fr); }
  .side { position: static; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: start; }
  .panel--quiet { grid-column: 1 / -1; }
}

@media (max-width: 760px) {
  .page { padding: var(--s4) var(--s4) var(--s6); }
  /* With the occasional tools in "More" the rest fit on one row, and the row
     must not scroll: a scrolling row would clip the menu that opens from it. */
  .tools { width: 100%; }
  .tool-group, .tool--danger { flex: none; }
  .tool--danger { margin-left: auto; }
  .board { border-radius: var(--radius); margin: 0 calc(-1 * var(--s2)); }
  .board-head { padding: var(--s4); }
  .settings { grid-template-columns: minmax(0, 1fr) 96px; flex-basis: 100%; }
  .ctl--wide { grid-column: 1 / -1; grid-row: 1; }
  .periods { padding: var(--s3) var(--s4); }
  .plan-title { flex-wrap: wrap; row-gap: var(--s1); }
  .start { grid-template-columns: minmax(0, 1fr); padding: var(--s4); }
  .year-bar { padding: 10px var(--s4); }
  .term { grid-template-columns: minmax(0, 1fr); }
  .term-label {
    display: flex; align-items: baseline; justify-content: space-between; gap: var(--s2);
    padding: 10px var(--s4) 0; border-right: 0; background: none;
  }
  .term-meta { margin: 0 0 0 auto; }
  .term-add { margin-top: 0; }
  .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); padding: var(--s2) var(--s4) var(--s4); gap: var(--s2); }
  .slot-li--extra { display: none; }
  .slot, .ucard { min-height: 92px; }
  .add-year { width: calc(100% - 2 * var(--s4)); margin: var(--s4) var(--s4) 0; }
  .board-foot { padding: var(--s3) var(--s4) var(--s4); }
  .side { grid-template-columns: minmax(0, 1fr); }
}

/* --- print ----------------------------------------------------------------------
 * The board and the totals, nothing that only makes sense on a screen. A year
 * stays on one page where it fits, so a printed plan never splits Semester 1
 * from its own heading. */
@media print {
  .page { max-width: none; padding: 0; }
  .tools, .periods, .slot-li, .add-year, .board-foot, .ucard-tools, .term-add, .panel--quiet, .lede, .start, .local { display: none !important; }
  .split { grid-template-columns: minmax(0, 1fr); }
  .board, .panel { box-shadow: none; border-color: #c9d2dc; }
  .board-head { padding: 8px 12px; }
  .ctl-input { border: 0; padding: 0; height: auto; background-image: none; }
  .plan-all { display: none; }
  .year { break-inside: avoid; }
  .year-bar { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  .ucard, .ucard::before, .ucard-part, .part-fill, .part-tag { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  .ucard { min-height: 0; break-inside: avoid; }
  .side { position: static; grid-template-columns: 1fr 2fr; break-inside: avoid; }
}
</style>
