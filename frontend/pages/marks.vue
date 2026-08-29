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
const showPaste = ref(false)
const lookupNote = ref('')
let nextId = 1

function blank(): MarkEntry {
  return { id: nextId++, unitCode: '', title: null, creditPoints: null, level: null, mark: null, grade: null }
}

onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')
    if (saved?.entries?.length) {
      entries.value = saved.entries
      nextId = Math.max(...saved.entries.map((e: MarkEntry) => e.id)) + 1
    }
    if (saved?.scale) scale.value = saved.scale
  } catch {
    // A corrupt or unreadable store is not worth an error on screen; the page
    // simply starts empty.
  }
  if (!entries.value.length) entries.value = [blank(), blank(), blank(), blank()]
})

watch([entries, scale], () => {
  if (!import.meta.client) return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ entries: entries.value, scale: scale.value }))
  } catch { /* private mode, or the quota is full */ }
}, { deep: true })

/** Fill in credit points and level from the Handbook for whatever is typed. */
async function lookup(codes: string[]) {
  const wanted = [...new Set(codes.map(c => c.trim().toUpperCase()).filter(Boolean))]
  if (!wanted.length) return
  lookupNote.value = ''
  try {
    const result = await apiFetch<any>(`/v1/marks/units?codes=${wanted.join(',')}`)
    const byCode = new Map(result.results.map((u: any) => [u.unit_code, u]))
    for (const entry of entries.value) {
      const found = byCode.get(entry.unitCode.trim().toUpperCase()) as any
      if (!found) continue
      entry.title = found.title
      if (found.credit_points !== null) entry.creditPoints = found.credit_points
      if (found.level !== null) entry.level = found.level
    }
    if (result.missing.length) {
      lookupNote.value = $t('marks.notFound', {
        year: result.academic_year,
        codes: result.missing.join(', ')
      })
    }
  } catch {
    lookupNote.value = $t('marks.lookupFailed')
  }
}

function onCodeEntered(entry: MarkEntry) {
  if (entry.unitCode.trim()) lookup([entry.unitCode])
}

function addRow() {
  entries.value.push(blank())
}

function removeRow(id: number) {
  entries.value = entries.value.filter(e => e.id !== id)
  if (!entries.value.length) entries.value = [blank()]
}

function clearAll() {
  entries.value = [blank(), blank(), blank(), blank()]
  pasted.value = ''
  lookupNote.value = ''
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
  // Drop the untouched blank rows the page started with.
  entries.value = entries.value.filter(e => e.unitCode.trim() || e.mark !== null)
  showPaste.value = false
  pasted.value = ''
  lookup(rows.map(r => r.unitCode))
}

const counted = computed(() =>
  reference.value ? countable(entries.value, reference.value) : []
)
const wamValue = computed(() =>
  reference.value ? applyWam(entries.value, reference.value) : null
)
const gpaValue = computed(() =>
  reference.value ? applyGpa(entries.value, reference.value, scale.value) : null
)

function gradeOf(entry: MarkEntry): string | null {
  return reference.value ? resolveGrade(entry, reference.value) : null
}

function weightOf(entry: MarkEntry): number | null {
  if (!reference.value) return null
  return entry.level === 1
    ? reference.value.level_weights.first_year
    : reference.value.level_weights.other
}

// --- the projection -------------------------------------------------------
const target = ref(70)
const plannedCount = ref(4)
const plannedCredit = ref(6)
const plannedLevel = ref(2)

const plannedWeight = computed(() => {
  if (!reference.value) return 0
  const weight = plannedLevel.value === 1
    ? reference.value.level_weights.first_year
    : reference.value.level_weights.other
  return plannedCount.value * plannedCredit.value * weight
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
    my: reference.value!.grade_points[MALAYSIA]?.[code]
  }))
})

function fmt(value: number | null, digits = 2): string {
  return value === null || Number.isNaN(value) ? '—' : value.toFixed(digits)
}

useSeoMeta({
  title: () => $t('marks.metaTitle'),
  description: () => $t('marks.metaDescription')
})
</script>

<template>
  <div class="container page">
    <header class="intro">
      <h1>{{ $t('marks.title') }}</h1>
      <p class="lede">{{ $t('marks.lede') }}</p>
      <p class="tiny muted">{{ $t('marks.privacy') }}</p>
    </header>

    <section class="card section">
      <div class="head-row">
        <label class="field">
          <span class="tiny muted">{{ $t('marks.scale') }}</span>
          <select v-model="scale" class="field-input">
            <option :value="MALAYSIA">{{ $t('marks.scaleMalaysia') }}</option>
            <option :value="AUSTRALIA">{{ $t('marks.scaleAustralia') }}</option>
          </select>
        </label>
        <div class="head-actions">
          <button class="btn btn--ghost btn--small" type="button" @click="showPaste = !showPaste">
            {{ $t('marks.paste') }}
          </button>
          <button class="btn btn--ghost btn--small" type="button" @click="clearAll">
            {{ $t('marks.clear') }}
          </button>
        </div>
      </div>

      <div v-if="showPaste" class="paste">
        <p class="tiny muted">{{ $t('marks.pasteHelp') }}</p>
        <textarea v-model="pasted" class="field-input paste-box" rows="6"
                  :placeholder="$t('marks.pastePlaceholder')" />
        <button class="btn btn--small" type="button" @click="applyPaste">
          {{ $t('marks.pasteApply') }}
        </button>
      </div>

      <div class="scroll-x">
        <table class="entries">
          <thead>
            <tr>
              <th scope="col">{{ $t('marks.colUnit') }}</th>
              <th scope="col">{{ $t('marks.colCredit') }}</th>
              <th scope="col">{{ $t('marks.colLevel') }}</th>
              <th scope="col">{{ $t('marks.colWeight') }}</th>
              <th scope="col">{{ $t('marks.colMark') }}</th>
              <th scope="col">{{ $t('marks.colGrade') }}</th>
              <th scope="col"><span class="visually-hidden">{{ $t('marks.colRemove') }}</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in entries" :key="entry.id">
              <td class="cell-unit">
                <input v-model="entry.unitCode" class="field-input mono" :placeholder="$t('marks.unitPlaceholder')"
                       @change="onCodeEntered(entry)" @blur="onCodeEntered(entry)">
                <span v-if="entry.title" class="tiny muted title">{{ entry.title }}</span>
              </td>
              <td><input v-model.number="entry.creditPoints" class="field-input narrow" type="number" min="0" step="1"></td>
              <td><input v-model.number="entry.level" class="field-input narrow" type="number" min="0" max="9"></td>
              <td class="tiny muted">×{{ weightOf(entry) ?? '—' }}</td>
              <td><input v-model.number="entry.mark" class="field-input narrow" type="number" min="0" max="100" step="0.01"></td>
              <td>
                <input v-model="entry.grade" class="field-input narrow mono"
                       :placeholder="gradeOf(entry) || '—'">
              </td>
              <td>
                <button class="remove" type="button" :aria-label="$t('marks.colRemove')"
                        @click="removeRow(entry.id)">×</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-if="lookupNote" class="tiny note">{{ lookupNote }}</p>
      <button class="btn btn--ghost btn--small" type="button" @click="addRow">
        {{ $t('marks.addRow') }}
      </button>
    </section>

    <section class="results">
      <div class="card result">
        <p class="tiny muted">{{ $t('marks.wam') }}</p>
        <p class="figure">{{ fmt(wamValue, 3) }}</p>
        <p class="tiny muted">{{ $t('marks.wamHow') }}</p>
      </div>
      <div class="card result">
        <p class="tiny muted">
          {{ scale === MALAYSIA ? $t('marks.cgpa') : $t('marks.gpa') }}
        </p>
        <p class="figure">{{ fmt(gpaValue, 3) }}</p>
        <p class="tiny muted">{{ $t('marks.gpaHow') }}</p>
      </div>
      <div class="card result">
        <p class="tiny muted">{{ $t('marks.counted') }}</p>
        <p class="figure">{{ counted.length }}</p>
        <p class="tiny muted">{{ $t('marks.countedHow') }}</p>
      </div>
    </section>

    <section class="card section">
      <h2>{{ $t('marks.projection') }}</h2>
      <p class="small muted">{{ $t('marks.projectionHelp') }}</p>
      <div class="projection">
        <label class="field">
          <span class="tiny muted">{{ $t('marks.targetWam') }}</span>
          <input v-model.number="target" class="field-input narrow" type="number" min="0" max="100">
        </label>
        <label class="field">
          <span class="tiny muted">{{ $t('marks.plannedCount') }}</span>
          <input v-model.number="plannedCount" class="field-input narrow" type="number" min="1" max="12">
        </label>
        <label class="field">
          <span class="tiny muted">{{ $t('marks.plannedCredit') }}</span>
          <input v-model.number="plannedCredit" class="field-input narrow" type="number" min="1" max="48">
        </label>
        <label class="field">
          <span class="tiny muted">{{ $t('marks.plannedLevel') }}</span>
          <input v-model.number="plannedLevel" class="field-input narrow" type="number" min="0" max="9">
        </label>
      </div>

      <p v-if="needed === null" class="verdict small">{{ $t('marks.needNothing') }}</p>
      <p v-else-if="needed > 100" class="verdict verdict--warn small">
        {{ $t('marks.needImpossible', { target, need: fmt(needed, 1) }) }}
      </p>
      <p v-else-if="needed <= 0" class="verdict verdict--good small">
        {{ $t('marks.needSecured', { target }) }}
      </p>
      <p v-else class="verdict small">
        {{ $t('marks.needEach', { need: fmt(needed, 1), target }) }}
        <span v-if="neededGrade"> ({{ neededGrade }})</span>
      </p>
    </section>

    <section class="card section">
      <h2>{{ $t('marks.rules') }}</h2>

      <h3>{{ $t('marks.rulesGrades') }}</h3>
      <div class="scroll-x">
        <table>
          <thead>
            <tr>
              <th scope="col">{{ $t('marks.colGrade') }}</th>
              <th scope="col">{{ $t('marks.colCode') }}</th>
              <th scope="col">{{ $t('marks.colGpaAu') }}</th>
              <th scope="col">{{ $t('marks.colGpaMy') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in gradeRows" :key="row.code">
              <td>{{ row.name }}</td>
              <td class="mono">{{ row.code }}</td>
              <td>{{ row.au?.toFixed(2) }}</td>
              <td>{{ row.my?.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3>{{ $t('marks.rulesWeights') }}</h3>
      <p class="small">{{ $t('marks.rulesWeightsBody') }}</p>

      <h3>{{ $t('marks.rulesGotchas') }}</h3>
      <ul class="small">
        <li>{{ $t('marks.gotchaFail') }}</li>
        <li>{{ $t('marks.gotchaWithdrawn') }}</li>
        <li>{{ $t('marks.gotchaLevel') }}</li>
        <li>{{ $t('marks.gotchaRounding') }}</li>
        <li v-if="reference">
          {{ $t('marks.gotchaExcluded', { codes: reference.excluded_grades.join(', ') }) }}
        </li>
      </ul>

      <p v-if="reference" class="small">
        <a :href="reference.sources.wam" rel="noopener external" target="_blank">
          {{ $t('marks.sourceWam') }}
        </a>
        ·
        <a :href="reference.sources.gpa" rel="noopener external" target="_blank">
          {{ $t('marks.sourceGpa') }}
        </a>
        ·
        <NuxtLink :to="reference.guides.wam">{{ $t('marks.guideWam') }}</NuxtLink>
        ·
        <NuxtLink :to="reference.guides.gpa">{{ $t('marks.guideGpa') }}</NuxtLink>
      </p>
    </section>
  </div>
</template>

<style scoped>
.page { display: grid; gap: var(--s4); padding-bottom: var(--s7); }
.intro { padding-top: var(--s5); }
.lede { max-width: 68ch; color: var(--muted); }
.section { padding: var(--s5); }

.head-row { display: flex; flex-wrap: wrap; gap: var(--s3); align-items: end; justify-content: space-between; }
.head-actions { display: flex; gap: var(--s2); }
.field { display: grid; gap: var(--s1); min-width: 0; }
/* Without this the scale <select> stretches the width of the card, the way the
   planner's filters used to. A control should be as wide as what it holds. */
.head-row > .field { max-width: 260px; }
.field-input {
  padding: var(--s2) var(--s3); border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm); font: inherit; background: var(--surface);
  color: var(--text); width: 100%; min-width: 0;
}
.narrow { max-width: 92px; }
.paste { display: grid; gap: var(--s2); margin: var(--s4) 0; }
.paste-box { font-family: var(--font-mono); font-size: 0.85rem; }

.entries { margin-top: var(--s4); }
.entries td { vertical-align: top; }
.cell-unit { min-width: 190px; }
.cell-unit .title { display: block; margin-top: var(--s1); }
.remove {
  border: 0; background: none; color: var(--muted); font-size: 1.2rem;
  line-height: 1; cursor: pointer; padding: var(--s2);
}
.remove:hover { color: var(--danger); }
.note { color: var(--warning); margin: var(--s3) 0; }

.results { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--s4); }
.result { padding: var(--s5); }
.result p { margin: 0; }
.figure { font-size: 2.4rem; font-weight: 600; line-height: 1.1; margin: var(--s2) 0 !important; }

/* Each of these holds a two-digit number, so they sit side by side. Left as
   flex items with no cap they stretch to the card and stack, which is what the
   planner's toolbar was doing. */
.projection {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 140px));
  gap: var(--s4); margin: var(--s4) 0;
}
.projection .field-input { max-width: 100%; }
.verdict {
  padding: var(--s3) var(--s4); border-left: 3px solid var(--blue);
  background: var(--blue-50); border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.verdict--warn { border-left-color: var(--warning); background: var(--warning-bg); }
.verdict--good { border-left-color: var(--success); background: var(--success-bg); }

h3 { margin-top: var(--s5); }
</style>
