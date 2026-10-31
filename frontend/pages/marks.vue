<script setup lang="ts">
/**
 * WAM and GPA: what they are, what yours is, and what you need next semester.
 *
 * Three things a generic calculator on the internet cannot do, and they are the
 * reason this page exists rather than a link to one:
 *
 * 1. **It knows the units.** Type FIT1008 and the credit points and level that
 *    decide the weighting come out of the Handbook, not out of the student's
 *    memory. Getting the level wrong is the single commonest way a homemade
 *    calculation goes wrong, because Level 1 units count half.
 * 2. **It knows which campus you are at.** Malaysia scores on CGPA, where a
 *    Credit is 2.85 rather than 2.0. One table for both campuses is simply
 *    wrong for half the people reading.
 * 3. **It answers the question actually being asked**, which is not "what was
 *    my average" but "what do I need this semester".
 *
 * The marks never leave the browser. The server supplies the scoring tables and
 * the unit weights; the arithmetic runs here, and the entries are kept in
 * localStorage on this device only.
 *
 * The layout follows the course map: the units on the left, grouped by level
 * because the level is what sets the weight, and the totals in a panel on the
 * right that stays on screen while the marks are typed. On a phone the panel
 * drops below the list, so a slim bar at the bottom carries the two numbers
 * instead.
 */
import {
  AUSTRALIA,
  MALAYSIA,
  applyGpa,
  applyWam,
  countable,
  gradeForMark,
  markNeeded,
  parsePastedResults,
  resolveGrade,
  type MarkEntry,
  type MarksReference
} from '~/utils/marks'

const { $t } = useNuxtApp()

const { data: reference } = await useApiFetch<MarksReference>('/v1/marks/reference')

const STORAGE_KEY = 'mh_marks'
const scale = ref<string>(MALAYSIA)
const entries = ref<MarkEntry[]>([])
const pasted = ref('')
const showImport = ref(false)
const lookupNote = ref('')
let nextId = 1

/** A row nobody has typed anything into. The old page saved four of these. */
function isBlank(entry: MarkEntry): boolean {
  return !entry.unitCode?.trim() && entry.mark === null && !entry.grade && entry.creditPoints === null
}

onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')
    if (saved?.entries?.length) {
      entries.value = (saved.entries as MarkEntry[])
        .filter(e => !isBlank(e))
        // The grade used to be a free text box, so "hd" and "" are both in
        // people's saved data. The picker needs the code or null.
        .map(e => ({ ...e, grade: e.grade?.trim() ? e.grade.trim().toUpperCase() : null }))
      nextId = Math.max(0, ...saved.entries.map((e: MarkEntry) => e.id)) + 1
    }
    if (saved?.scale) scale.value = saved.scale
  } catch {
    // A corrupt or unreadable store is not worth an error on screen; the page
    // simply starts empty.
  }
})

watch([entries, scale], () => {
  if (!import.meta.client) return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ entries: entries.value, scale: scale.value }))
  } catch { /* private mode, or the quota is full */ }
}, { deep: true })

// --- the Handbook lookup ----------------------------------------------------

interface LookupResult {
  academic_year: number
  results: { unit_code: string; title: string; credit_points: number | null; level: number | null }[]
  missing: string[]
}

async function fetchUnits(codes: string[]): Promise<LookupResult | null> {
  const params = new URLSearchParams({ codes: codes.join(',') })
  try {
    return await apiFetch<LookupResult>(`/v1/marks/units?${params.toString()}`)
  } catch {
    lookupNote.value = $t('marks.lookupFailed')
    return null
  }
}

function noteMissing(result: LookupResult) {
  if (result.missing.length) {
    lookupNote.value = $t('marks.notFound', {
      year: result.academic_year,
      codes: result.missing.join(', ')
    })
  }
}

/** Fill in credit points and level from the Handbook for whatever is typed. */
async function lookup(codes: string[]) {
  const wanted = [...new Set(codes.map(c => c.trim().toUpperCase()).filter(Boolean))]
  if (!wanted.length) return
  lookupNote.value = ''
  const result = await fetchUnits(wanted)
  if (!result) return
  const byCode = new Map(result.results.map(u => [u.unit_code, u]))
  for (const entry of entries.value) {
    const found = byCode.get(entry.unitCode.trim().toUpperCase())
    if (!found) continue
    entry.title = found.title
    if (found.credit_points !== null) entry.creditPoints = found.credit_points
    if (found.level !== null) entry.level = found.level
  }
  noteMissing(result)
}

function onCodeEntered(entry: MarkEntry) {
  if (entry.unitCode.trim()) lookup([entry.unitCode])
}

// --- adding a unit ----------------------------------------------------------
//
// One line at the foot of the list instead of four empty rows. The Handbook is
// asked before the row is added, so the unit lands straight in its level group
// rather than appearing under "Level not set" and jumping a moment later.
const draftCode = ref('')
const draftMark = ref<number | null>(null)
const adding = ref(false)
const draftInput = ref<HTMLInputElement | null>(null)

async function addDraft() {
  const code = draftCode.value.trim().toUpperCase()
  if (!code || adding.value) return
  adding.value = true
  lookupNote.value = ''
  const result = await fetchUnits([code])
  const found = result?.results.find(u => u.unit_code === code)
  entries.value.push({
    id: nextId++,
    unitCode: code,
    title: found?.title ?? null,
    creditPoints: found?.credit_points ?? null,
    level: found?.level ?? null,
    mark: typeof draftMark.value === 'number' && !Number.isNaN(draftMark.value) ? draftMark.value : null,
    grade: null
  })
  if (result) noteMissing(result)
  draftCode.value = ''
  draftMark.value = null
  adding.value = false
  await nextTick()
  draftInput.value?.focus()
}

// --- removing, with a way back ------------------------------------------------
//
// Clearing used to wipe the list with no way back. Rather than ask first, it
// now happens at once and offers to undo, which is quicker for the student who
// meant it and still safe for the one who did not.
const undoState = ref<{ snapshot: MarkEntry[]; message: string } | null>(null)

function removeRow(entry: MarkEntry) {
  undoState.value = {
    snapshot: entries.value.map(e => ({ ...e })),
    message: $t('marks.removed', { code: entry.unitCode || '?' })
  }
  entries.value = entries.value.filter(e => e.id !== entry.id)
}

function clearAll() {
  if (!entries.value.length) return
  undoState.value = {
    snapshot: entries.value.map(e => ({ ...e })),
    message: $t('marks.cleared', { n: entries.value.length })
  }
  entries.value = []
  pasted.value = ''
  lookupNote.value = ''
}

function undo() {
  if (!undoState.value) return
  entries.value = undoState.value.snapshot
  undoState.value = null
}

// --- reading a screenshot -------------------------------------------------
//
// The least accurate of the three ways in, and the one students reach for
// first. It runs entirely in the browser, so the screenshot of somebody's
// transcript is not uploaded anywhere, and whatever it reads lands in the
// editable table rather than straight into a total.
const ocr = useOcr()

async function onScreenshot(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const text = await ocr.recognise(file)
  // Clear the input so choosing the same file twice still fires a change.
  input.value = ''
  if (!text.trim()) {
    if (!ocr.error.value) lookupNote.value = $t('marks.ocrNothing')
    return
  }
  pasted.value = text
  applyPaste()
  lookupNote.value = $t('marks.ocrCheck')
}

function applyPaste() {
  const rows = parsePastedResults(pasted.value)
  if (!rows.length) {
    lookupNote.value = $t('marks.pasteNothing')
    return
  }
  const existing = new Set(entries.value.map(e => e.unitCode.trim().toUpperCase()).filter(Boolean))
  for (const row of rows) {
    if (existing.has(row.unitCode)) continue
    entries.value.push({
      id: nextId++,
      unitCode: row.unitCode,
      title: null,
      creditPoints: row.creditPoints,
      level: null,
      mark: row.mark,
      grade: row.grade
    })
  }
  showImport.value = false
  pasted.value = ''
  lookup(rows.map(r => r.unitCode))
}

// --- the totals ---------------------------------------------------------------

const counted = computed(() =>
  reference.value ? countable(entries.value, reference.value) : []
)
const countedIds = computed(() => new Set(counted.value.map(e => e.id)))
const countedPoints = computed(() =>
  counted.value.reduce((sum, e) => sum + (e.creditPoints ?? 0), 0)
)
const uncounted = computed(() => entries.value.length - counted.value.length)
const wamValue = computed(() =>
  reference.value ? applyWam(entries.value, reference.value) : null
)
const gpaValue = computed(() =>
  reference.value ? applyGpa(entries.value, reference.value, scale.value) : null
)
const gpaLabel = computed(() => (scale.value === MALAYSIA ? 'CGPA' : 'GPA'))
const wamGrade = computed(() =>
  wamValue.value !== null && reference.value ? gradeForMark(wamValue.value, reference.value) : null
)

/** How many of each grade, in the order the scale runs, for the bar under the ring. */
const gradeMix = computed(() => {
  if (!reference.value) return []
  const counts = new Map<string, number>()
  for (const entry of counted.value) {
    const grade = resolveGrade(entry, reference.value)!
    counts.set(grade, (counts.get(grade) ?? 0) + 1)
  }
  return Object.keys(reference.value.grade_names)
    .filter(code => counts.has(code))
    .map(code => ({ code, n: counts.get(code)!, share: counts.get(code)! / counted.value.length }))
})

function gradeOf(entry: MarkEntry): string | null {
  return reference.value ? resolveGrade(entry, reference.value) : null
}

/** What the grade chip says: the grade picked by hand, or the one the mark gives. */
function chipOf(entry: MarkEntry): string | null {
  return entry.grade?.trim() ? entry.grade.trim().toUpperCase() : gradeOf(entry)
}

/**
 * One colour family per grade. Pass and up go from blue to green, the fails are
 * red, and a grade that counts for neither average is grey. The code is always
 * printed too, so the colour never carries the grade on its own.
 */
function toneOf(code: string | null): string {
  if (!code) return 'none'
  if (['HD', 'D', 'C', 'P'].includes(code)) return code.toLowerCase()
  if (code === 'NP') return 'np'
  if (['N', 'NH', 'WN'].includes(code)) return 'fail'
  return 'muted'
}

// --- grouped by level ---------------------------------------------------------

interface Group {
  key: string
  level: number | null
  weight: number
  entries: MarkEntry[]
  wam: number | null
}

const groups = computed<Group[]>(() => {
  const byLevel = new Map<number | null, MarkEntry[]>()
  for (const entry of entries.value) {
    const level = typeof entry.level === 'number' && !Number.isNaN(entry.level) ? entry.level : null
    if (!byLevel.has(level)) byLevel.set(level, [])
    byLevel.get(level)!.push(entry)
  }
  const ref = reference.value
  return [...byLevel.entries()]
    // Levels in order, and "not set" last, where the unfinished rows belong.
    .sort(([a], [b]) => (a === null ? 1 : b === null ? -1 : a - b))
    .map(([level, list]) => ({
      key: String(level),
      level,
      weight: ref ? (level === 1 ? ref.level_weights.first_year : ref.level_weights.other) : 1,
      entries: list,
      wam: ref ? applyWam(list, ref) : null
    }))
})

// --- the projection -------------------------------------------------------
const target = ref(70)
// Level 1 units count at a lower weight than the rest, so a semester that mixes
// them (FIT1045 next to FIT2004 and FIT3155) is entered as two counts. Levels 2
// and up share one weight, so they need no further split.
const plannedFirstYear = ref(0)
const plannedLater = ref(4)
const plannedCredit = ref(6)

const plannedWeight = computed(() => {
  if (!reference.value) return 0
  const { first_year, other } = reference.value.level_weights
  const count = (n: number) => (Number.isFinite(n) && n > 0 ? n : 0)
  const credit = count(plannedCredit.value)
  return credit * (count(plannedFirstYear.value) * first_year + count(plannedLater.value) * other)
})

const needed = computed(() =>
  reference.value
    ? markNeeded(entries.value, plannedWeight.value, target.value, reference.value)
    : null
)
const neededGrade = computed(() => {
  if (needed.value === null || !reference.value) return null
  if (needed.value < 0 || needed.value > 100) return null
  return gradeForMark(needed.value, reference.value)
})

const gradeRows = computed(() => {
  if (!reference.value) return []
  return Object.keys(reference.value.grade_names).map(code => ({
    code,
    name: reference.value!.grade_names[code],
    au: reference.value!.grade_points[AUSTRALIA]?.[code],
    my: reference.value!.grade_points[MALAYSIA]?.[code],
    floor: reference.value!.grade_bands.find(b => b.grade === code)?.floor
  }))
})

function fmt(value: number | null, digits = 2): string {
  return value === null || Number.isNaN(value) ? '—' : value.toFixed(digits)
}

// --- the bar at the bottom of a phone -------------------------------------------
//
// Shown only while the summary panel is off screen, so the numbers are never
// on the page twice.
const summaryEl = ref<HTMLElement | null>(null)
const summaryVisible = ref(true)
let observer: IntersectionObserver | undefined
onMounted(() => {
  if (!summaryEl.value || typeof IntersectionObserver === 'undefined') return
  observer = new IntersectionObserver(([entry]) => { summaryVisible.value = !!entry?.isIntersecting })
  observer.observe(summaryEl.value)
})
onBeforeUnmount(() => observer?.disconnect())

useSeoMeta({
  title: () => $t('marks.metaTitle'),
  description: () => $t('marks.metaDescription')
})
</script>

<template>
  <div class="page">
    <header class="intro">
      <div class="intro-text">
        <h1>{{ $t('marks.title') }}</h1>
        <p class="lede">{{ $t('marks.lede') }}</p>
      </div>
      <div class="tools">
        <button
          class="tool tool--primary"
          type="button"
          :aria-expanded="showImport"
          @click="showImport = !showImport"
        ><PlanIcon name="upload" />{{ $t('marks.import') }}</button>
        <button class="tool tool--danger" type="button" :disabled="!entries.length" @click="clearAll">
          <PlanIcon name="trash" />{{ $t('marks.clear') }}
        </button>
      </div>
    </header>

    <div class="split">
      <section class="board" :aria-label="$t('marks.yourUnits')">
        <div class="board-head">
          <div>
            <h2 class="board-title">{{ $t('marks.yourUnits') }}</h2>
            <p class="board-meta">{{ $t('marks.unitsMeta', { n: entries.length, cp: countedPoints }) }}</p>
          </div>
          <div class="segmented" role="radiogroup" :aria-label="$t('marks.scale')">
            <button
              v-for="option in [MALAYSIA, AUSTRALIA]"
              :key="option"
              type="button"
              role="radio"
              class="seg"
              :class="{ 'seg--on': scale === option }"
              :aria-checked="scale === option"
              @click="scale = option"
            >{{ option === MALAYSIA ? $t('marks.scaleMalaysia') : $t('marks.scaleAustralia') }}</button>
          </div>
        </div>

        <div v-if="showImport" class="import">
          <div class="import-head">
            <h3>{{ $t('marks.importTitle') }}</h3>
            <button class="mini" type="button" :aria-label="$t('marks.cancel')" @click="showImport = false">
              <PlanIcon name="close" />
            </button>
          </div>
          <p class="import-help">{{ $t('marks.pasteHelp') }}</p>
          <textarea
            v-model="pasted"
            class="paste-box"
            rows="5"
            :placeholder="$t('marks.pastePlaceholder')"
          />
          <div class="import-actions">
            <button class="btn btn--small" type="button" :disabled="!pasted.trim()" @click="applyPaste">
              {{ $t('marks.pasteApply') }}
            </button>
            <label class="btn btn--ghost btn--small file">
              {{ $t('marks.screenshot') }}
              <input type="file" accept="image/*" @change="onScreenshot">
            </label>
          </div>
          <p
            v-if="ocr.stage.value === 'loading' || ocr.stage.value === 'recognising'"
            class="banner banner--info"
            role="status"
          >
            <PlanIcon name="spinner" :size="14" />
            {{ ocr.stage.value === 'loading' ? $t('marks.ocrLoading') : $t('marks.ocrReading') }}
            <span v-if="ocr.progress.value !== null">{{ Math.round(ocr.progress.value * 100) }}%</span>
          </p>
          <p v-if="ocr.error.value" class="banner banner--bad" role="alert">{{ $t('marks.ocrFailed') }}</p>
        </div>

        <div v-if="lookupNote || undoState" class="notes" aria-live="polite">
          <p v-if="undoState" class="banner banner--quiet">
            <span>{{ undoState.message }}</span>
            <button class="link-btn" type="button" @click="undo">
              <PlanIcon name="undo" :size="14" />{{ $t('marks.undo') }}
            </button>
          </p>
          <p v-if="lookupNote" class="banner banner--warn">
            <PlanIcon name="alert" :size="14" />{{ lookupNote }}
          </p>
        </div>

        <div v-if="entries.length" class="cols" aria-hidden="true">
          <span>{{ $t('marks.colGrade') }}</span>
          <span>{{ $t('marks.colUnit') }}</span>
          <span>{{ $t('marks.colMark') }}</span>
          <span>{{ $t('marks.colCredit') }}</span>
          <span>{{ $t('marks.colLevel') }}</span>
          <span />
        </div>

        <section v-for="group in groups" :key="group.key" class="group">
          <div class="group-bar">
            <h3 class="group-name">
              {{ group.level === null ? $t('marks.levelUnset') : $t('marks.level', { n: group.level }) }}
            </h3>
            <span class="group-weight">{{ $t('marks.levelWeight', { w: group.weight }) }}</span>
            <span v-if="group.wam !== null" class="group-avg">{{ $t('marks.groupAverage', { wam: fmt(group.wam, 1) }) }}</span>
          </div>
          <ul class="rows">
            <li
              v-for="entry in group.entries"
              :key="entry.id"
              class="row"
              :class="{ 'row--off': !countedIds.has(entry.id) }"
            >
              <label class="grade" :title="entry.grade ? '' : $t('marks.gradeAuto')">
                <span class="chip" :class="[`chip--${toneOf(chipOf(entry))}`, { 'chip--manual': !!entry.grade }]">
                  {{ chipOf(entry) || '—' }}
                </span>
                <select v-model="entry.grade" :aria-label="`${entry.unitCode} ${$t('marks.colGrade')}`">
                  <option :value="null">{{ $t('marks.gradeAuto') }}{{ gradeOf({ ...entry, grade: null }) ? ` (${gradeOf({ ...entry, grade: null })})` : '' }}</option>
                  <option v-for="code in Object.keys(reference?.grade_names || {})" :key="code" :value="code">
                    {{ code }} · {{ reference?.grade_names[code] }}
                  </option>
                  <optgroup :label="$t('marks.notCounted')">
                    <option v-for="code in reference?.excluded_grades || []" :key="code" :value="code">{{ code }}</option>
                  </optgroup>
                </select>
              </label>

              <div class="unit">
                <input
                  v-model="entry.unitCode"
                  class="code-input"
                  :aria-label="$t('marks.colUnit')"
                  :placeholder="$t('marks.unitPlaceholder')"
                  @change="onCodeEntered(entry)"
                >
                <p class="unit-title">
                  <span v-if="entry.title">{{ entry.title }}</span>
                  <span v-if="!countedIds.has(entry.id)" class="tag">{{ $t('marks.notCounted') }}</span>
                </p>
              </div>

              <label class="num num--mark">
                <span class="num-label">{{ $t('marks.colMark') }}</span>
                <input v-model.number="entry.mark" type="number" min="0" max="100" step="0.01" inputmode="decimal" placeholder="—">
              </label>
              <label class="num">
                <span class="num-label">{{ $t('marks.colCredit') }}</span>
                <input v-model.number="entry.creditPoints" type="number" min="0" step="1" inputmode="numeric" placeholder="—">
              </label>
              <label class="num">
                <span class="num-label">{{ $t('marks.colLevel') }}</span>
                <input v-model.number="entry.level" type="number" min="0" max="9" inputmode="numeric" placeholder="—">
              </label>

              <button class="mini mini--remove" type="button" :aria-label="$t('marks.colRemove')" @click="removeRow(entry)">
                <PlanIcon name="close" :size="15" />
              </button>
            </li>
          </ul>
        </section>

        <div v-if="!entries.length" class="empty">
          <p>{{ $t('marks.empty') }}</p>
          <button v-if="!showImport" class="btn btn--ghost btn--small" type="button" @click="showImport = true">
            <PlanIcon name="upload" :size="14" />{{ $t('marks.paste') }}
          </button>
        </div>

        <form class="composer" @submit.prevent="addDraft">
          <PlanIcon name="plus" class="composer-icon" />
          <input
            ref="draftInput"
            v-model="draftCode"
            class="composer-code"
            :aria-label="$t('marks.colUnit')"
            :placeholder="$t('marks.addPlaceholder')"
            autocapitalize="characters"
            autocomplete="off"
            spellcheck="false"
          >
          <input
            v-model.number="draftMark"
            class="composer-mark"
            type="number"
            min="0"
            max="100"
            step="0.01"
            inputmode="decimal"
            :aria-label="$t('marks.colMark')"
            :placeholder="$t('marks.colMark')"
          >
          <button class="btn btn--small" type="submit" :disabled="!draftCode.trim() || adding">
            <PlanIcon v-if="adding" name="spinner" :size="14" />{{ $t('marks.add') }}
          </button>
        </form>
      </section>

      <aside class="side">
        <section ref="summaryEl" class="panel panel--summary">
          <h2 class="panel-title">{{ $t('plan.summary') }}</h2>
          <PlanRing :value="wamValue === null ? null : wamValue / 100" :size="176">
            <span class="ring-big">{{ fmt(wamValue, 3) }}</span>
            <span class="ring-small">WAM</span>
          </PlanRing>
          <p v-if="wamGrade" class="ring-grade">
            <span class="chip" :class="`chip--${toneOf(wamGrade)}`">{{ wamGrade }}</span>
            {{ reference?.grade_names[wamGrade] }}
          </p>
          <p v-else class="panel-note">{{ $t('marks.wamHow') }}</p>

          <dl class="stats">
            <div>
              <dt>{{ gpaLabel }}</dt>
              <dd>{{ fmt(gpaValue, 3) }}<small v-if="gpaValue !== null"> / 4</small></dd>
            </div>
            <div>
              <dt>{{ $t('marks.counted') }}</dt>
              <dd>{{ counted.length }}</dd>
            </div>
            <div>
              <dt>{{ $t('courses.creditPoints') }}</dt>
              <dd>{{ countedPoints }}</dd>
            </div>
          </dl>

          <div v-if="gradeMix.length" class="mix">
            <p class="mix-title">{{ $t('marks.gradeMix') }}</p>
            <div class="mix-bar">
              <span
                v-for="g in gradeMix"
                :key="g.code"
                class="mix-seg"
                :class="`seg-${toneOf(g.code)}`"
                :style="{ width: `${g.share * 100}%` }"
              />
            </div>
            <ul class="mix-legend">
              <li v-for="g in gradeMix" :key="g.code">
                <span class="dot" :class="`seg-${toneOf(g.code)}`" />{{ g.code }} <b>{{ g.n }}</b>
              </li>
            </ul>
          </div>

          <p v-if="uncounted" class="panel-warn">
            <PlanIcon name="alert" :size="14" />{{ $t('marks.notCountedNote', { n: uncounted }) }}
          </p>
        </section>

        <section class="panel">
          <h2 class="panel-title">{{ $t('marks.projection') }}</h2>
          <p class="panel-help">{{ $t('marks.projectionHelp') }}</p>
          <div class="projection">
            <label class="ctl ctl--wide">
              <span class="ctl-label">{{ $t('marks.targetWam') }}</span>
              <input v-model.number="target" class="ctl-input" type="number" min="0" max="100" inputmode="decimal">
            </label>
            <label class="ctl">
              <span class="ctl-label">{{ $t('marks.plannedFirstYear') }}</span>
              <input v-model.number="plannedFirstYear" class="ctl-input" type="number" min="0" max="12" inputmode="numeric">
            </label>
            <label class="ctl">
              <span class="ctl-label">{{ $t('marks.plannedLater') }}</span>
              <input v-model.number="plannedLater" class="ctl-input" type="number" min="0" max="12" inputmode="numeric">
            </label>
            <label class="ctl">
              <span class="ctl-label">{{ $t('marks.plannedCredit') }}</span>
              <input v-model.number="plannedCredit" class="ctl-input" type="number" min="1" max="48" inputmode="numeric">
            </label>
          </div>

          <div v-if="needed !== null && needed > 0 && needed <= 100" class="verdict">
            <p class="verdict-num">
              {{ fmt(needed, 1) }}
              <span v-if="neededGrade" class="chip" :class="`chip--${toneOf(neededGrade)}`">{{ neededGrade }}</span>
            </p>
            <p class="verdict-text">{{ $t('marks.needEach', { need: fmt(needed, 1), target }) }}</p>
          </div>
          <p v-else-if="needed === null" class="verdict-line">{{ $t('marks.needNothing') }}</p>
          <p v-else-if="needed > 100" class="verdict-line verdict-line--warn">
            {{ $t('marks.needImpossible', { target, need: fmt(needed, 1) }) }}
          </p>
          <p v-else class="verdict-line verdict-line--good">{{ $t('marks.needSecured', { target }) }}</p>
        </section>

        <section class="panel panel--quiet">
          <PlanIcon name="lock" :size="15" />
          <p>{{ $t('marks.privacy') }}</p>
        </section>
      </aside>
    </div>

    <section class="rules">
      <h2>{{ $t('marks.rules') }}</h2>
      <div class="rules-grid">
        <div class="panel">
          <h3 class="panel-title">{{ $t('marks.rulesGrades') }}</h3>
          <table class="grades">
            <thead>
              <tr>
                <th scope="col">{{ $t('marks.colGrade') }}</th>
                <th scope="col" class="numcol">{{ $t('marks.colMark') }}</th>
                <th scope="col" class="numcol">{{ $t('marks.colGpaAu') }}</th>
                <th scope="col" class="numcol">{{ $t('marks.colGpaMy') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in gradeRows" :key="row.code">
                <td>
                  <span class="chip" :class="`chip--${toneOf(row.code)}`">{{ row.code }}</span>
                  {{ row.name }}
                </td>
                <td class="numcol">{{ row.floor === undefined ? '' : `${row.floor}+` }}</td>
                <td class="numcol" :class="{ 'on-scale': scale === AUSTRALIA }">{{ row.au?.toFixed(2) }}</td>
                <td class="numcol" :class="{ 'on-scale': scale === MALAYSIA }">{{ row.my?.toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="panel">
          <h3 class="panel-title">{{ $t('marks.rulesWeights') }}</h3>
          <p class="small">{{ $t('marks.rulesWeightsBody') }}</p>

          <h3 class="panel-title panel-title--gap">{{ $t('marks.rulesGotchas') }}</h3>
          <ul class="gotchas small">
            <li>{{ $t('marks.gotchaFail') }}</li>
            <li>{{ $t('marks.gotchaWithdrawn') }}</li>
            <li>{{ $t('marks.gotchaLevel') }}</li>
            <li>{{ $t('marks.gotchaRounding') }}</li>
            <li v-if="reference">
              {{ $t('marks.gotchaExcluded', { codes: reference.excluded_grades.join(', ') }) }}
            </li>
          </ul>

          <p v-if="reference" class="links small">
            <a :href="reference.sources.wam" rel="noopener external" target="_blank">{{ $t('marks.sourceWam') }}</a>
            <a :href="reference.sources.gpa" rel="noopener external" target="_blank">{{ $t('marks.sourceGpa') }}</a>
            <NuxtLink :to="reference.guides.wam">{{ $t('marks.guideWam') }}</NuxtLink>
            <NuxtLink :to="reference.guides.gpa">{{ $t('marks.guideGpa') }}</NuxtLink>
          </p>
        </div>
      </div>
    </section>

    <div v-if="!summaryVisible && counted.length" class="dock" aria-hidden="true">
      <span><small>WAM</small>{{ fmt(wamValue, 3) }}</span>
      <span><small>{{ gpaLabel }}</small>{{ fmt(gpaValue, 3) }}</span>
      <span><small>{{ $t('courses.creditPoints') }}</small>{{ countedPoints }}</span>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: 1280px; margin: 0 auto; padding: var(--s5) var(--s5) var(--s7); }

/* --- heading and tools ------------------------------------------------------- */

.intro {
  display: flex; flex-wrap: wrap; align-items: flex-end; justify-content: space-between;
  gap: var(--s4); margin-bottom: var(--s4);
}
.intro-text { min-width: 0; flex: 1 1 420px; }
.intro h1 { margin: 0 0 var(--s1); }
.lede { color: var(--muted); margin: 0; max-width: var(--measure-lede); font-size: 0.95rem; }

.tools { display: flex; gap: var(--s2); }
.tool {
  display: inline-flex; align-items: center; gap: 6px;
  min-height: 40px; padding: 0 14px; border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--surface); color: var(--text); box-shadow: var(--shadow-sm);
  font: inherit; font-size: 0.88rem; font-weight: 500; cursor: pointer; white-space: nowrap;
}
.tool:hover:not(:disabled) { background: var(--surface-2); }
.tool:disabled { color: var(--muted-2); cursor: default; box-shadow: none; }
.tool--primary { background: var(--ink); border-color: var(--ink); color: var(--text-inverse); }
.tool--primary:hover:not(:disabled) { background: var(--ink-700); }
.tool--danger { color: var(--muted); }
.tool--danger:hover:not(:disabled) { color: var(--danger); border-color: #f1c4c4; background: var(--danger-bg); }

.split { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: var(--s4); align-items: start; }

/* --- the board ----------------------------------------------------------------- */

.board {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
  box-shadow: var(--shadow); overflow: hidden;
}
.board-head {
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  gap: var(--s3); padding: var(--s4) var(--s5);
}
.board-title { margin: 0; font: 600 1.15rem var(--font); }
.board-meta { margin: 2px 0 0; font-size: 0.8rem; color: var(--muted); }

/* Two campuses, so two buttons side by side rather than a drop-down that hides
   the other choice. */
.segmented {
  display: inline-flex; padding: 3px; gap: 2px;
  background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-pill);
}
.seg {
  min-height: 32px; padding: 0 14px; border: 0; border-radius: var(--radius-pill);
  background: none; color: var(--muted); font: inherit; font-size: 0.84rem; font-weight: 500;
  cursor: pointer; white-space: nowrap;
}
.seg:hover { color: var(--text); }
.seg--on { background: var(--surface); color: var(--text); box-shadow: 0 1px 3px rgba(12, 27, 42, 0.12); }

.import {
  display: grid; gap: var(--s3); padding: var(--s4) var(--s5);
  background: var(--surface-2); border-top: 1px solid var(--border);
}
.import-head { display: flex; align-items: center; justify-content: space-between; }
.import h3 { margin: 0; font: 600 0.95rem var(--font); }
.import-help { margin: 0; font-size: 0.84rem; color: var(--muted); }
.paste-box {
  width: 100%; padding: var(--s3); border: 1px solid var(--border-strong); border-radius: var(--radius-sm);
  background: var(--surface); color: var(--text); font: 0.85rem/1.5 var(--font-mono); resize: vertical;
}
.paste-box:focus { border-color: var(--brand); outline: none; box-shadow: 0 0 0 3px var(--blue-50); }
.import-actions { display: flex; flex-wrap: wrap; gap: var(--s2); }
.import-actions .btn:disabled { opacity: 0.45; cursor: default; }
/* The file input is the button; the real control is unusable and every browser
   styles it differently. */
.file { position: relative; overflow: hidden; cursor: pointer; }
.file input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }

.notes { display: grid; gap: var(--s2); padding: 0 var(--s5) var(--s3); }
.import + .notes { padding-top: var(--s3); }
.banner {
  display: flex; align-items: center; gap: var(--s2); margin: 0;
  padding: var(--s2) var(--s3); border-radius: var(--radius-sm); font-size: 0.84rem;
}
.banner :deep(svg) { flex: none; }
.banner--warn { background: var(--warning-bg); color: var(--warning); }
.banner--bad { background: var(--danger-bg); color: var(--danger); }
.banner--info { background: var(--blue-50); color: var(--brand-700); }
.banner--quiet { justify-content: space-between; background: var(--surface-2); color: var(--muted); }
.link-btn {
  display: inline-flex; align-items: center; gap: 4px; border: 0; background: none; padding: 0;
  color: var(--brand); font: inherit; font-weight: 600; cursor: pointer;
}

/* --- the rows ------------------------------------------------------------------- */

/* One grid for the header and every row, so the columns line up without a
   <table> and the row can still turn into a card on a phone. */
.cols, .row {
  display: grid; align-items: center; gap: var(--s3);
  grid-template-columns: 48px minmax(0, 1fr) 92px 72px 64px 28px;
}
.cols {
  align-items: end; padding: var(--s2) var(--s5); border-top: 1px solid var(--border);
  font-size: 0.7rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted);
}

.group-bar {
  display: flex; align-items: baseline; gap: var(--s3);
  padding: 10px var(--s5); background: var(--surface-2);
  border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
}
.group-name { margin: 0; font: 600 0.88rem var(--font); }
.group-weight { font-size: 0.78rem; color: var(--muted); }
.group-avg { margin-left: auto; font: 500 0.8rem var(--font-mono); color: var(--text); }

.rows { list-style: none; margin: 0; padding: 0; }
.row { padding: 10px var(--s5); transition: background 0.12s; }
.row + .row { border-top: 1px solid var(--border); }
.row:hover, .row:focus-within { background: #fafbfd; }

.grade { position: relative; display: inline-flex; cursor: pointer; }
.grade select {
  position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer; font-size: 16px;
}
.chip {
  display: inline-grid; place-items: center; min-width: 40px; height: 28px; padding: 0 8px;
  border-radius: 7px; font: 700 0.8rem var(--font-mono); letter-spacing: 0.02em;
  color: var(--tone, var(--muted)); background: var(--tone-bg, var(--surface-2));
}
.ring-grade .chip, .verdict .chip, .grades .chip { min-width: 34px; height: 24px; font-size: 0.74rem; }
.grade .chip { position: relative; transition: box-shadow 0.12s; }
.grade:hover .chip, .grade:focus-within .chip { box-shadow: 0 0 0 2px var(--border-strong); }
/* A grade picked by hand rather than worked out from the mark gets a corner
   dot, so a WN typed in last year is not mistaken for a calculated one. */
.chip--manual::after {
  content: ''; position: absolute; top: -3px; right: -3px;
  width: 8px; height: 8px; border-radius: 50%; background: var(--tone, var(--muted)); border: 2px solid var(--surface);
}
.chip--none { background: none; border: 1.5px dashed var(--border-strong); color: var(--muted-2); }

.chip--hd, .seg-hd { --tone: var(--part-3); --tone-bg: var(--part-3-bg); }
.chip--d, .seg-d { --tone: var(--part-1); --tone-bg: var(--part-1-bg); }
.chip--c, .seg-c { --tone: var(--part-2); --tone-bg: var(--part-2-bg); }
.chip--p, .seg-p { --tone: var(--success); --tone-bg: var(--success-bg); }
.chip--np, .seg-np { --tone: var(--warning); --tone-bg: var(--warning-bg); }
.chip--fail, .seg-fail { --tone: var(--danger); --tone-bg: var(--danger-bg); }
.chip--muted, .seg-muted { --tone: var(--part-6); --tone-bg: var(--part-6-bg); }

.unit { min-width: 0; }
/* Looks like text until it is touched, the way the plan name does. */
.code-input {
  width: 100%; max-width: 160px; margin-left: -7px; padding: 2px 6px;
  border: 1px solid transparent; border-radius: 6px; background: none;
  font: 600 0.95rem var(--font-mono); color: var(--text); text-transform: uppercase;
}
.code-input:hover { border-color: var(--border); }
.code-input:focus { border-color: var(--brand); outline: none; box-shadow: 0 0 0 3px var(--blue-50); background: var(--surface); }
.unit-title {
  display: flex; flex-wrap: wrap; align-items: center; gap: 6px;
  margin: 1px 0 0; font-size: 0.78rem; line-height: 1.35; color: var(--muted);
}
.unit-title:empty { display: none; }
.tag {
  padding: 0 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600;
  background: var(--warning-bg); color: var(--warning);
}

.num { display: block; }
.num-label { display: none; }
.num input {
  width: 100%; height: 36px; padding: 0 10px;
  border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface);
  color: var(--text); font: 500 0.92rem var(--font-mono); text-align: right;
  -moz-appearance: textfield;
}
.num input::-webkit-outer-spin-button, .num input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.num input:hover { border-color: var(--border-strong); }
.num input:focus { border-color: var(--brand); outline: none; box-shadow: 0 0 0 3px var(--blue-50); }
.num--mark input { font-weight: 700; font-size: 1rem; border-color: var(--border-strong); }
.row--off .chip { opacity: 0.8; }

.mini {
  display: inline-grid; place-items: center; width: 28px; height: 28px; border: 0; border-radius: 6px;
  background: none; color: var(--muted-2); cursor: pointer;
}
.mini:hover { background: var(--surface-2); color: var(--text); }
.mini--remove:hover { color: var(--danger); background: var(--danger-bg); }
@media (hover: hover) {
  .mini--remove { opacity: 0; transition: opacity 0.12s; }
  .row:hover .mini--remove, .row:focus-within .mini--remove { opacity: 1; }
}

.empty {
  display: grid; justify-items: center; gap: var(--s3); padding: var(--s7) var(--s5) var(--s5);
  border-top: 1px solid var(--border); text-align: center; color: var(--muted); font-size: 0.9rem;
}
.empty p { margin: 0; max-width: 34em; }
.empty .btn { display: inline-flex; gap: 6px; align-items: center; }

/* The add line: the one place a new unit comes from. */
.composer {
  display: flex; align-items: center; gap: var(--s2);
  padding: var(--s3) var(--s5) var(--s4); border-top: 1px solid var(--border);
}
.composer-icon { color: var(--muted-2); }
.composer input {
  height: 40px; padding: 0 var(--s3); min-width: 0;
  border: 1.5px dashed var(--border-strong); border-radius: var(--radius-sm); background: none;
  color: var(--text); font: 500 0.92rem var(--font-mono);
}
.composer input:focus { border-style: solid; border-color: var(--brand); outline: none; box-shadow: 0 0 0 3px var(--blue-50); background: var(--surface); }
.composer-code { flex: 1 1 auto; max-width: 300px; text-transform: uppercase; }
.composer-code::placeholder { text-transform: none; font-family: var(--font); }
.composer-mark { width: 92px; text-align: right; -moz-appearance: textfield; }
.composer-mark::-webkit-outer-spin-button, .composer-mark::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
.composer .btn { display: inline-flex; align-items: center; gap: 6px; }
.composer .btn:disabled { opacity: 0.45; cursor: default; }

/* --- side panel ------------------------------------------------------------------- */

.side { display: grid; gap: var(--s3); position: sticky; top: calc(var(--header-h) + var(--s3)); }
.panel {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
  padding: var(--s4) var(--s5); box-shadow: var(--shadow-sm);
}
.panel-title {
  margin: 0 0 var(--s3); font-family: var(--font); font-size: 0.72rem; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted);
}
.panel-title--gap { margin-top: var(--s5); }
.panel-help { margin: calc(-1 * var(--s2)) 0 var(--s3); font-size: 0.78rem; line-height: 1.45; color: var(--muted); }
.panel--summary { display: flex; flex-direction: column; align-items: center; text-align: center; }
.panel--summary .panel-title { align-self: flex-start; }
.ring-big { font: 700 2.1rem var(--font); line-height: 1; letter-spacing: -0.02em; color: var(--text); }
.ring-small { margin-top: 6px; font-size: 0.76rem; font-weight: 600; letter-spacing: 0.08em; color: var(--muted); }
.ring-grade {
  display: inline-flex; align-items: center; gap: var(--s2); margin: var(--s3) 0 0;
  font-size: 0.88rem; font-weight: 500;
}
.panel-note { margin: var(--s3) 0 0; font-size: 0.8rem; color: var(--muted); }

.stats {
  display: grid; grid-template-columns: repeat(3, 1fr); width: 100%;
  margin: var(--s4) 0 0; padding-top: var(--s3); border-top: 1px solid var(--border);
}
.stats div { padding: 0 4px; }
.stats div + div { border-left: 1px solid var(--border); }
.stats dt { font-size: 0.7rem; color: var(--muted); }
.stats dd { margin: 2px 0 0; font-size: 1.2rem; font-weight: 700; color: var(--text); }
.stats dd small { font-size: 0.7rem; font-weight: 500; color: var(--muted); }

.mix { width: 100%; margin-top: var(--s4); text-align: left; }
.mix-title { margin: 0 0 6px; font-size: 0.7rem; color: var(--muted); }
.mix-bar {
  display: flex; gap: 2px; height: 8px; border-radius: var(--radius-pill); overflow: hidden;
  background: var(--surface-2);
}
.mix-seg { display: block; height: 100%; background: var(--tone); transition: width 0.4s ease; }
.mix-legend { list-style: none; display: flex; flex-wrap: wrap; gap: 4px 12px; margin: 8px 0 0; padding: 0; font-size: 0.76rem; color: var(--muted); }
.mix-legend li { display: inline-flex; align-items: center; gap: 5px; font-family: var(--font-mono); }
.mix-legend b { color: var(--text); font-weight: 600; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--tone); }

.panel-warn {
  display: flex; gap: 6px; align-items: flex-start; width: 100%; margin: var(--s3) 0 0;
  padding: var(--s2) var(--s3); border-radius: var(--radius-sm); text-align: left;
  background: var(--warning-bg); color: var(--warning); font-size: 0.78rem; line-height: 1.45;
}
.panel-warn :deep(svg) { margin-top: 2px; }

.projection { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s2) var(--s3); align-items: end; }
.ctl { display: grid; gap: 4px; min-width: 0; }
.ctl--wide { grid-column: 1 / -1; }
.ctl-label { font-size: 0.72rem; color: var(--muted); }
.ctl-input {
  width: 100%; min-width: 0; height: 38px; padding: 0 var(--s3);
  border: 1px solid var(--border-strong); border-radius: var(--radius-sm);
  background: var(--surface); color: var(--text); font: 500 0.92rem var(--font-mono);
}
.ctl-input:focus { border-color: var(--brand); outline: none; box-shadow: 0 0 0 3px var(--blue-50); }

.verdict {
  margin-top: var(--s4); padding: var(--s3) var(--s4); border-radius: var(--radius-sm);
  background: var(--blue-50);
}
.verdict-num {
  display: flex; align-items: center; gap: var(--s2); margin: 0;
  font: 700 1.9rem var(--font); line-height: 1.1; letter-spacing: -0.02em; color: var(--text);
}
.verdict-text { margin: 4px 0 0; font-size: 0.8rem; line-height: 1.45; color: var(--muted); }
.verdict-line {
  margin: var(--s4) 0 0; padding: var(--s3) var(--s4); border-radius: var(--radius-sm);
  background: var(--surface-2); color: var(--muted); font-size: 0.84rem; line-height: 1.45;
}
.verdict-line--warn { background: var(--warning-bg); color: var(--warning); }
.verdict-line--good { background: var(--success-bg); color: var(--success); }

.panel--quiet {
  display: flex; gap: var(--s2); align-items: flex-start; background: var(--surface-2);
  box-shadow: none; color: var(--muted);
}
.panel--quiet p { margin: 0; font-size: 0.76rem; line-height: 1.5; }
.panel--quiet :deep(svg) { margin-top: 2px; }

/* --- how it is worked out ---------------------------------------------------------- */

.rules { margin-top: var(--s7); }
.rules h2 { margin: 0 0 var(--s4); }
.rules-grid { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: var(--s4); align-items: start; }
.grades { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
.grades th {
  padding: 0 0 var(--s2); text-align: left; font-size: 0.7rem; font-weight: 600; color: var(--muted);
  border-bottom: 1px solid var(--border);
}
.grades td { padding: 7px 0; border-bottom: 1px solid var(--border); }
.grades tr:last-child td { border-bottom: 0; }
.grades td:first-child { display: flex; align-items: center; gap: var(--s2); }
.numcol { text-align: right !important; font-family: var(--font-mono); padding-left: var(--s3) !important; }
td.numcol { white-space: nowrap; }
th.numcol { font-family: var(--font); }
.on-scale { font-weight: 700; color: var(--text); }
.gotchas { margin: 0; padding-left: 1.1rem; display: grid; gap: 6px; color: var(--text); }
.links { display: flex; flex-wrap: wrap; gap: 6px var(--s4); margin: var(--s4) 0 0; }
.small { font-size: 0.86rem; line-height: 1.55; }

.dock { display: none; }

/* --- narrower screens ----------------------------------------------------------------- */

@media (max-width: 1100px) {
  .split { grid-template-columns: minmax(0, 1fr); }
  .side { position: static; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: start; }
  .panel--quiet { grid-column: 1 / -1; }
  /* The summary is now below the list, so the numbers ride along at the
     bottom of the screen while the list is being filled in. */
  .dock {
    /* Above the tab bar the site puts at the bottom below 1180px, which is
       56px tall plus the safe area. */
    position: fixed; left: var(--s3); right: var(--s3); bottom: calc(56px + var(--s2) + env(safe-area-inset-bottom));
    z-index: 20; display: flex; justify-content: space-around; gap: var(--s3);
    padding: 10px var(--s4); border-radius: 14px;
    background: var(--ink); color: var(--text-inverse); box-shadow: 0 10px 30px -10px rgba(12, 27, 42, 0.5);
  }
  .dock span { display: grid; text-align: center; font: 700 1.05rem var(--font-mono); }
  .dock small { font: 500 0.66rem var(--font); letter-spacing: 0.06em; opacity: 0.7; }
  .page { padding-bottom: calc(var(--s7) + 64px); }
}

@media (max-width: 760px) {
  .page { padding: var(--s4) var(--s4) calc(var(--s7) + 64px); }
  .tools { width: 100%; }
  .tool { flex: 1; justify-content: center; }
  .board { margin: 0 calc(-1 * var(--s2)); }
  .board-head, .import, .composer { padding-left: var(--s4); padding-right: var(--s4); }
  .notes { padding: 0 var(--s4) var(--s3); }
  .segmented { width: 100%; }
  .seg { flex: 1; padding: 0 8px; }
  .cols { display: none; }
  .group-bar { padding: 10px var(--s4); }
  /* Each unit becomes a small card: the grade, code and title on top, and the
     three numbers in a row of their own with their names above them. */
  .row {
    grid-template-columns: 44px repeat(3, minmax(0, 1fr)) 28px;
    grid-template-areas: "grade unit unit unit remove" ". mark credit level .";
    row-gap: var(--s2); padding: var(--s3) var(--s4);
  }
  .grade { grid-area: grade; }
  .unit { grid-area: unit; }
  .num--mark { grid-area: mark; }
  .row > .num:nth-child(4) { grid-area: credit; }
  .row > .num:nth-child(5) { grid-area: level; }
  .mini--remove { grid-area: remove; align-self: start; }
  .num-label { display: block; margin-bottom: 2px; font-size: 0.68rem; color: var(--muted); }
  .num input { height: 40px; font-size: 16px; text-align: left; }
  .code-input { font-size: 16px; }
  .composer { flex-wrap: wrap; }
  .composer-icon { display: none; }
  .composer-code { flex: 1 1 100%; max-width: none; font-size: 16px; }
  .composer-mark { flex: 1; width: auto; font-size: 16px; }
  .composer .btn { min-height: 40px; }
  .side { grid-template-columns: minmax(0, 1fr); }
  .ctl-input { font-size: 16px; }
  .rules-grid { grid-template-columns: minmax(0, 1fr); }
  .rules .panel { padding: var(--s4); }
  .grades { font-size: 0.8rem; }
  .grades td:first-child { gap: 6px; }
  .rules { margin-top: var(--s6); }
}
</style>
