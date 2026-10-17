<script setup lang="ts">
/**
 * The "add a unit" dialog on the course map.
 *
 * The old picker was a list of codes and titles, and clicking one put it in
 * the plan straight away. You found out it was not taught that semester, or
 * that you were missing its prerequisite, only after it was on the map with a
 * red mark under it. This shows the unit first: what it is, where and when it
 * runs, what it needs, and whether it fits the slot you opened, checked by the
 * same /plan/check the map uses so the two can never disagree.
 */
import type { PlanEntry } from '~/composables/usePlan'

const props = defineProps<{
  year: number
  period: string
  campus: string
  entries: PlanEntry[]
  /** The plan page's wording for one check finding, so both say the same thing. */
  describe: (issue: any) => string
  /** The plan page's short name for a teaching period. */
  periodName: (period: string) => string
  /**
   * The Handbook the slot's year is checked against (see handbookYearFor).
   * Left out, the slot's own year.
   */
  handbookYear?: number
}>()
const emit = defineEmits<{ add: [code: string]; close: [] }>()

const { $t, $term } = useNuxtApp() as any
const { locale } = useLocale()
const campusName = useCampusName()

const slotLabel = computed(() => `${props.periodName(props.period)}, ${props.year}`)
const handbook = computed(() => props.handbookYear ?? props.year)

// --- search ----------------------------------------------------------------

const query = ref('')
const results = ref<any[]>([])
const searching = ref(false)
const searchError = ref('')
const active = ref<string | null>(null)
const lastAdded = ref('')
const input = ref<HTMLInputElement | null>(null)

let searchTimer: ReturnType<typeof setTimeout> | undefined
let searchSeq = 0
watch(query, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(search, 200)
})

async function search() {
  const term = query.value.trim()
  const seq = ++searchSeq
  if (term.length < 2) {
    results.value = []
    return
  }
  searching.value = true
  searchError.value = ''
  try {
    const params = new URLSearchParams({
      q: term,
      limit: '30',
      year: String(handbook.value),
      locale: locale.value
    })
    if (props.campus) params.set('campus', props.campus)
    const body = await apiFetch<any>(`/v1/units?${params.toString()}`)
    // A slow answer to an older query must not replace a newer one.
    if (seq !== searchSeq) return
    results.value = body.results || []
    if (!results.value.some((r) => r.unit_code === active.value)) {
      active.value = results.value[0]?.unit_code ?? null
    }
  } catch (caught) {
    if (seq !== searchSeq) return
    results.value = []
    searchError.value = apiErrorMessage(caught, $t)
  } finally {
    if (seq === searchSeq) searching.value = false
  }
}

/** S1, S2 and so on at the plan's campus; anything rarer is folded into "Other". */
function tags(unit: any): string[] {
  const here = (unit.offerings || []).filter((o: any) => !props.campus || o.campus_raw === props.campus)
  const seen: string[] = []
  let other = false
  for (const o of here) {
    const label = o.short && o.short.length <= 3 ? o.short : null
    if (!label) other = true
    else if (!seen.includes(label)) seen.push(label)
  }
  const order = ['S1', 'S2', 'SA', 'SB', 'W', 'FY', 'OCT']
  seen.sort((a, b) => (order.indexOf(a) + 99) % 99 - (order.indexOf(b) + 99) % 99)
  return other ? [...seen, $t('picker.other')] : seen
}

/** The plan's period names, as the short labels the API puts on offerings. */
const SLOT_SHORT: Record<string, string> = {
  'First semester': 'S1',
  'Second semester': 'S2',
  'Summer semester A': 'SA',
  'Summer semester B': 'SB',
  'Winter semester': 'W',
  'Full year': 'FY',
  'October intake teaching period, Malaysia campus': 'OCT'
}
const slotShort = computed(() => SLOT_SHORT[props.period] ?? props.period)

/**
 * Whether the unit runs in the period this dialog was opened for. Compared by
 * short label, because the Handbook spells one semester more than one way.
 */
function runsInSlot(unit: any): boolean {
  return (unit.offerings || []).some(
    (o: any) => (!props.campus || o.campus_raw === props.campus) && o.short === slotShort.value
  )
}

// --- preview ---------------------------------------------------------------

const details = reactive<Record<string, any>>({})
const verdicts = reactive<Record<string, any[] | 'error'>>({})
const loadingDetail = ref(false)

async function loadDetail(code: string) {
  if (details[code]) return
  loadingDetail.value = true
  try {
    details[code] = await apiFetch<any>(`/v1/units/${code}?year=${handbook.value}&locale=${locale.value}`)
  } catch {
    details[code] = { failed: true }
  } finally {
    loadingDetail.value = false
  }
}

async function loadVerdict(code: string) {
  if (verdicts[code]) return
  try {
    const report = await apiFetch<any>('/v1/plan/check', {
      method: 'POST',
      body: {
        campus: props.campus,
        entries: [...props.entries, { unit_code: code, year: props.year, teaching_period: props.period }]
      }
    })
    verdicts[code] = (report.issues || []).filter(
      (i: any) => i.unit_code === code && i.year === props.year && i.teaching_period === props.period
    )
  } catch {
    verdicts[code] = 'error'
  }
}

let previewTimer: ReturnType<typeof setTimeout> | undefined
watch(active, (code) => {
  clearTimeout(previewTimer)
  if (!code) return
  // Arrowing down a list should not fire two requests per row it passes.
  previewTimer = setTimeout(() => {
    loadDetail(code)
    loadVerdict(code)
  }, 120)
})

// The loaded years can arrive after the dialog opened, and a 2027 answer to a
// 2026 slot is the bug this year exists to prevent.
watch(handbook, () => {
  for (const key of Object.keys(details)) delete details[key]
  search()
  if (active.value) loadDetail(active.value)
})

// A plan that changed (a unit just added) makes every cached verdict stale.
watch(() => props.entries.length, () => {
  for (const key of Object.keys(verdicts)) delete verdicts[key]
  if (active.value) loadVerdict(active.value)
})

const detail = computed(() => (active.value ? details[active.value] : null))
const verdict = computed(() => (active.value ? verdicts[active.value] : undefined))
const errors = computed(() => (Array.isArray(verdict.value) ? verdict.value.filter((i) => i.severity === 'error') : []))
const warnings = computed(() => (Array.isArray(verdict.value) ? verdict.value.filter((i) => i.severity !== 'error') : []))
const alreadyHere = computed(() =>
  props.entries.some((e) => e.unit_code === active.value && e.year === props.year && e.teaching_period === props.period)
)

/** Offerings grouped by teaching period, the way a student reads them. */
const offeringGroups = computed(() => {
  const groups = new Map<string, any[]>()
  for (const o of detail.value?.offerings || []) {
    const key = o.teaching_period || '—'
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key)!.push(o)
  }
  return [...groups.entries()]
})

const requisiteGroups = computed(() => {
  const byType: Record<string, any[]> = {}
  for (const group of detail.value?.requisites || []) {
    ;(byType[group.requisite_type] ||= []).push(group)
  }
  return byType
})

// --- actions ---------------------------------------------------------------

function add(code: string | null = active.value) {
  if (!code) return
  emit('add', code)
  lastAdded.value = code
  query.value = ''
  results.value = []
  active.value = null
  nextTick(() => input.value?.focus())
}

function move(step: number) {
  if (!results.value.length) return
  const index = results.value.findIndex((r) => r.unit_code === active.value)
  const next = Math.min(results.value.length - 1, Math.max(0, index + step))
  active.value = results.value[next].unit_code
  nextTick(() => document.getElementById(`pick-${active.value}`)?.scrollIntoView({ block: 'nearest' }))
}

function onKey(event: KeyboardEvent) {
  if (event.key === 'Escape') emit('close')
}

onMounted(() => {
  nextTick(() => input.value?.focus())
  document.addEventListener('keydown', onKey)
  document.documentElement.style.overflow = 'hidden'
})
onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKey)
  document.documentElement.style.overflow = ''
})
</script>

<template>
  <div class="backdrop" @click.self="emit('close')">
    <div class="dialog" role="dialog" aria-modal="true" :aria-label="$t('picker.title', { slot: slotLabel })">
      <header class="top">
        <svg class="glass" viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.5" /><path d="M13 13l4 4" /></svg>
        <input
          ref="input"
          v-model="query"
          class="search"
          :placeholder="$t('picker.placeholder', { slot: slotLabel })"
          autocomplete="off"
          :aria-label="$t('plan.searchPlaceholder')"
          @keydown.down.prevent="move(1)"
          @keydown.up.prevent="move(-1)"
          @keydown.enter.prevent="add()"
        />
        <button class="close" type="button" :aria-label="$t('picker.close')" @click="emit('close')">×</button>
      </header>

      <div class="body">
        <div class="list">
          <p v-if="lastAdded && !query" class="added" role="status">{{ $t('picker.added', { code: lastAdded, slot: slotLabel }) }}</p>
          <p v-if="searchError" class="hint bad-text" role="alert">{{ searchError }}</p>
          <p v-else-if="query.trim().length < 2" class="hint">{{ $t('picker.hint', { campus: campusName(campus), year: handbook }) }}</p>
          <p v-else-if="!searching && !results.length" class="hint">{{ $t('plan.noMatches') }}</p>
          <ul v-if="results.length" role="listbox" :aria-label="$t('picker.results')">
            <li
              v-for="unit in results"
              :id="`pick-${unit.unit_code}`"
              :key="unit.unit_code"
              role="option"
              :aria-selected="active === unit.unit_code"
            >
              <button
                type="button"
                class="row"
                :class="{ 'row--on': active === unit.unit_code, 'row--off': !runsInSlot(unit) }"
                @click="active = unit.unit_code"
                @dblclick="add(unit.unit_code)"
              >
                <span class="row-top">
                  <span class="mono code">{{ unit.unit_code }}</span>
                  <span class="title">{{ unit.title }}</span>
                  <span v-if="unit.credit_points" class="cp">{{ unit.credit_points }}cp</span>
                </span>
                <span class="tags">
                  <span
                    v-for="t in tags(unit)"
                    :key="t"
                    class="tag"
                    :class="{ 'tag--slot': t === slotShort }"
                  >{{ t }}</span>
                </span>
              </button>
            </li>
          </ul>
        </div>

        <section class="preview" aria-live="polite">
          <p v-if="!active" class="empty">{{ $t('picker.pick') }}</p>
          <template v-else>
            <div class="verdict-bar">
              <span v-if="verdict === undefined" class="verdict verdict--wait">{{ $t('picker.checking') }}</span>
              <span v-else-if="verdict === 'error'" class="verdict verdict--wait">{{ $t('picker.checkFailed') }}</span>
              <span v-else-if="alreadyHere" class="verdict verdict--wait">{{ $t('picker.alreadyHere') }}</span>
              <span v-else-if="!errors.length && !warnings.length" class="verdict verdict--ok">
                <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.5l3 3 7-7" /></svg>
                {{ $t('picker.fits', { slot: slotLabel }) }}
              </span>
              <template v-else>
                <span v-for="(issue, i) in errors" :key="`e${i}`" class="verdict verdict--bad">{{ describe(issue) }}</span>
                <span v-for="(issue, i) in warnings" :key="`w${i}`" class="verdict verdict--warn">{{ describe(issue) }}</span>
              </template>
            </div>

            <div class="scroll">
              <Skeleton v-if="loadingDetail && !detail" :lines="5" />
              <p v-else-if="detail?.failed" class="hint bad-text">{{ $t('picker.detailFailed') }}</p>
              <template v-else-if="detail">
                <div class="head">
                  <h3><span class="mono">{{ detail.unit_code }}</span> <span v-if="detail.credit_points" class="cp">{{ detail.credit_points }}cp</span></h3>
                  <NuxtLink :to="`/units/${detail.unit_code}?year=${detail.academic_year}`" target="_blank" class="small">
                    {{ $t('picker.viewDetails') }} ↗
                  </NuxtLink>
                </div>
                <p class="name">{{ detail.title }}</p>
                <p class="chips">
                  <span class="chip">{{ $t('unit.handbookYear', { year: detail.academic_year }) }}</span>
                  <span v-if="detail.level" class="chip">{{ $term('level', detail.level) }}</span>
                  <span v-if="detail.faculty" class="chip">{{ $term('faculty', detail.faculty) }}</span>
                </p>

                <template v-if="detail.overview">
                  <h4 class="label">{{ $t('unit.overview') }}</h4>
                  <p class="overview">{{ detail.overview }}</p>
                </template>

                <h4 class="label">{{ $t('unit.offerings') }}</h4>
                <dl v-if="offeringGroups.length" class="offerings">
                  <template v-for="[periodLabel, list] in offeringGroups" :key="periodLabel">
                    <dt>{{ $term('period', periodLabel) || periodLabel }}</dt>
                    <dd>
                      <span
                        v-for="(o, i) in list"
                        :key="i"
                        class="place"
                        :class="{ 'place--here': o.campus_raw === campus }"
                      >{{ $term('campus', o.campus) || o.campus }}<span class="mode">{{ $term('mode', o.attendance_mode) || o.attendance_mode }}</span></span>
                    </dd>
                  </template>
                </dl>
                <p v-else class="hint">{{ $t('unit.noOfferingsPublished') }}</p>

                <template v-for="(groups, type) in requisiteGroups" :key="type">
                  <h4 class="label" :class="{ 'label--warn': String(type).startsWith('prohib') }">
                    {{ $term('requisiteType', String(type)) }}
                  </h4>
                  <RequisiteRule v-for="(group, gi) in groups" :key="gi" :rule="group" />
                </template>
              </template>
            </div>

            <footer class="foot">
              <button class="btn btn--primary" type="button" :disabled="alreadyHere" @click="add()">
                {{ $t('picker.add', { slot: slotLabel }) }}
              </button>
            </footer>
          </template>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.backdrop {
  position: fixed; inset: 0; z-index: 60; display: grid; place-items: center;
  padding: var(--s5) var(--s4); background: rgba(12, 27, 42, 0.42);
}
.dialog {
  width: min(1040px, 100%); height: min(720px, 100%); display: grid; grid-template-rows: auto minmax(0, 1fr);
  background: var(--surface); border-radius: 14px; overflow: hidden;
  box-shadow: 0 24px 64px -24px rgba(12, 27, 42, 0.45);
}
.top { display: flex; align-items: center; gap: var(--s3); padding: var(--s3) var(--s4); border-bottom: 1px solid var(--border); }
.glass { width: 18px; height: 18px; fill: none; stroke: var(--muted); stroke-width: 1.8; flex: none; }
.search { flex: 1; min-width: 0; border: 0; outline: 0; font: inherit; font-size: 1.05rem; padding: var(--s2) 0; background: transparent; color: var(--text); }
.close { border: 0; background: none; font-size: 1.5rem; line-height: 1; color: var(--muted); cursor: pointer; width: 40px; height: 40px; border-radius: var(--radius-sm); }
.close:hover { background: var(--surface-2); }

.body { display: grid; grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr); min-height: 0; }
.list { overflow-y: auto; border-right: 1px solid var(--border); padding: var(--s2); }
.list ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; }
.hint { color: var(--muted); font-size: 0.9rem; padding: var(--s3); margin: 0; }
.added { margin: var(--s2); padding: var(--s2) var(--s3); border-radius: var(--radius-sm); background: var(--success-bg); color: var(--success); font-size: 0.88rem; }
.row {
  width: 100%; display: grid; gap: 6px; padding: var(--s3); border: 0; border-radius: var(--radius-sm);
  background: transparent; text-align: left; font: inherit; color: var(--text); cursor: pointer;
}
.row:hover { background: var(--surface-2); }
.row--on, .row--on:hover { background: var(--blue-50); box-shadow: inset 3px 0 0 var(--brand); }
.row--off .title { color: var(--muted); }
.row-top { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; gap: var(--s2); align-items: baseline; }
.code { font-weight: 600; font-size: 0.88rem; color: var(--navy); }
.title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cp { color: var(--muted); font-size: 0.8rem; font-weight: 400; }
.tags { display: flex; gap: 4px; flex-wrap: wrap; }
.tag { padding: 0 6px; border-radius: 4px; font-size: 0.72rem; line-height: 1.6; background: var(--surface-2); border: 1px solid var(--border); color: var(--muted); }
.tag--slot { background: var(--brand); border-color: var(--brand); color: #fff; }

.preview { display: grid; grid-template-rows: auto minmax(0, 1fr) auto; min-height: 0; background: var(--bg); }
.empty { margin: auto; padding: var(--s6); color: var(--muted); text-align: center; grid-row: 1 / -1; }
.verdict-bar { display: grid; gap: var(--s1); padding: var(--s3) var(--s4); border-bottom: 1px solid var(--border); background: var(--surface); }
.verdict { display: inline-flex; align-items: center; gap: 6px; justify-self: start; padding: 3px 10px; border-radius: var(--radius-sm); font-size: 0.86rem; font-weight: 500; }
.verdict svg { width: 14px; height: 14px; fill: none; stroke: currentColor; stroke-width: 2; }
.verdict--ok { background: var(--success-bg); color: var(--success); border: 1px solid color-mix(in srgb, var(--success) 35%, transparent); }
.verdict--bad { background: var(--danger-bg); color: var(--danger); }
.verdict--warn { background: var(--warning-bg); color: var(--warning); }
.verdict--wait { background: var(--surface-2); color: var(--muted); }
.scroll { overflow-y: auto; padding: var(--s4) var(--s5); }
.head { display: flex; align-items: baseline; justify-content: space-between; gap: var(--s3); }
.head h3 { margin: 0; font-size: 1.35rem; }
.name { font-size: 1.1rem; font-weight: 500; margin: var(--s1) 0 var(--s3); }
.chips { display: flex; flex-wrap: wrap; gap: var(--s2); margin-bottom: var(--s4); }
.chip { padding: 2px 10px; border-radius: var(--radius-pill); background: var(--surface); border: 1px solid var(--border); font-size: 0.78rem; }
.label {
  margin: var(--s4) 0 var(--s2); padding-top: var(--s4); border-top: 1px solid var(--border);
  font-family: var(--font); font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted);
}
.label--warn { color: var(--danger); }
.overview { color: var(--muted); font-size: 0.92rem; display: -webkit-box; -webkit-line-clamp: 6; -webkit-box-orient: vertical; overflow: hidden; margin: 0; }
.offerings { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: var(--s2) var(--s4); margin: 0; font-size: 0.86rem; }
.offerings dt { color: var(--muted); padding-top: 3px; }
.offerings dd { margin: 0; display: flex; flex-wrap: wrap; gap: var(--s1); }
.place { padding: 2px 8px; border-radius: var(--radius-sm); background: var(--surface); border: 1px solid var(--border); }
.place--here { border-color: var(--brand); background: var(--blue-50); }
.mode { color: var(--muted); font-size: 0.75rem; margin-left: 6px; }
.foot { display: flex; justify-content: flex-end; padding: var(--s3) var(--s4); border-top: 1px solid var(--border); background: var(--surface); }

@media (max-width: 760px) {
  .backdrop { padding: 0; }
  .dialog { height: 100%; border-radius: 0; }
  .body { grid-template-columns: 1fr; grid-template-rows: minmax(140px, 38%) minmax(0, 1fr); }
  .list { border-right: 0; border-bottom: 1px solid var(--border); }
  .scroll { padding: var(--s4); }
  .foot .btn { width: 100%; min-height: 44px; }
}
</style>
