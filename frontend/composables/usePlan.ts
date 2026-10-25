/**
 * A course plan, kept in the reader's own browser.
 *
 * There is no account behind this on purpose. A planner you have to sign up
 * for is one most students will not open, and the plan itself is not something
 * this site needs to know: checking it takes the Handbook and the plan, and
 * the Handbook is already here.
 *
 * The trade is that a plan does not follow you to another device, which is
 * what export and import are for.
 *
 * A reader can keep several plans (a "what if I switch to Data Science" next
 * to the real one). They live together under one key as a small library with
 * one plan marked active; the course map always edits the active one.
 */
import { decodePlan } from '../utils/planCode'

const KEY = 'mh_plans_v1'
/** Where the single plan lived before there could be more than one. Read once, on upgrade. */
const OLD_KEY = 'mh_plan_v1'

export interface PlanEntry {
  unit_code: string
  year: number
  teaching_period: string
}

export interface PlanState {
  /** The reader's own name for the plan. Empty means "untitled"; the page supplies the wording. */
  name: string
  startYear: number
  years: number
  campus: string
  courseCode: string
  periods: string[]
  entries: PlanEntry[]
}

/** The periods a plan shows by default. Others are added by the reader. */
export const DEFAULT_PERIODS = ['First semester', 'Second semester']

export const OPTIONAL_PERIODS = [
  'Summer semester A',
  'Summer semester B',
  'Winter semester',
  'Full year',
  'October intake teaching period, Malaysia campus'
]

function blank(): PlanState {
  return {
    name: '',
    startYear: new Date().getFullYear(),
    years: 3,
    campus: 'Malaysia',
    courseCode: '',
    periods: [...DEFAULT_PERIODS],
    entries: []
  }
}

export interface StoredPlan {
  id: string
  updatedAt: number
  state: PlanState
}

export interface PlanLibrary {
  activeId: string
  plans: StoredPlan[]
}

export const MAX_PLANS = 20

function newId(): string {
  try {
    return crypto.randomUUID()
  } catch {
    return `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`
  }
}

function fresh(state: PlanState = blank()): StoredPlan {
  return { id: newId(), updatedAt: Date.now(), state }
}

function freshLibrary(): PlanLibrary {
  const first = fresh()
  return { activeId: first.id, plans: [first] }
}

/**
 * A library from storage, taken apart and rebuilt the same way a single plan
 * is: every plan through sanitise(), ids that are strings, an active id that
 * points at a plan that exists. Anything else and the reader would open the
 * map on a plan that is not in the list.
 */
export function sanitiseLibrary(parsed: unknown): PlanLibrary | null {
  if (!parsed || typeof parsed !== 'object') return null
  const raw = parsed as Record<string, unknown>
  if (!Array.isArray(raw.plans)) return null
  const plans: StoredPlan[] = []
  const seen = new Set<string>()
  for (const item of raw.plans.slice(0, MAX_PLANS)) {
    if (!item || typeof item !== 'object') continue
    const p = item as Record<string, unknown>
    const state = sanitise(p.state)
    if (!state) continue
    let id = typeof p.id === 'string' && p.id ? p.id.slice(0, 64) : newId()
    if (seen.has(id)) id = newId()
    seen.add(id)
    const updatedAt = Number(p.updatedAt)
    plans.push({ id, updatedAt: Number.isFinite(updatedAt) ? updatedAt : Date.now(), state })
  }
  if (!plans.length) return null
  const activeId = typeof raw.activeId === 'string' && seen.has(raw.activeId)
    ? raw.activeId
    : plans[0]!.id
  return { activeId, plans }
}

/**
 * Reading is wrapped because storage throws rather than returning null in a
 * private window and in previews, and a planner that white-screens on a
 * browser setting is worse than one that forgets.
 *
 * A reader from before multiple plans has their one plan under the old key.
 * It becomes the first plan in the library, and the old key is left alone, so
 * going back to an older build of the site still finds it.
 */
function readLibrary(): PlanLibrary {
  if (import.meta.server) return freshLibrary()
  try {
    const raw = window.localStorage.getItem(KEY)
    if (raw) return sanitiseLibrary(JSON.parse(raw)) ?? freshLibrary()
    const old = window.localStorage.getItem(OLD_KEY)
    const state = old ? sanitise(JSON.parse(old)) : null
    if (!state) return freshLibrary()
    // Written straight away so the upgraded plan keeps one id from now on.
    const upgraded = single(state)
    write(upgraded)
    return upgraded
  } catch {
    return freshLibrary()
  }
}

function single(state: PlanState): PlanLibrary {
  const only = fresh(state)
  return { activeId: only.id, plans: [only] }
}

export const MAX_YEARS = 10

/**
 * A plan from a file or from storage is only taken field by field, and only
 * where it makes sense. `years: 1e9` from a hand-edited export used to ask
 * for a billion rows and freeze the tab; a `periods` that was not a list
 * crashed the first `.includes`.
 */
export function sanitise(parsed: unknown): PlanState | null {
  if (!parsed || typeof parsed !== 'object') return null
  const raw = parsed as Record<string, unknown>
  if (!Array.isArray(raw.entries)) return null
  const base = blank()
  const year = Number(raw.startYear)
  const years = Number(raw.years)
  const entries: PlanEntry[] = []
  for (const entry of raw.entries) {
    if (!entry || typeof entry !== 'object') continue
    const e = entry as Record<string, unknown>
    const code = String(e.unit_code ?? '').trim().toUpperCase()
    const entryYear = Number(e.year)
    const period = String(e.teaching_period ?? '').trim()
    if (!code || !Number.isInteger(entryYear) || !period) continue
    entries.push({ unit_code: code.slice(0, 16), year: entryYear, teaching_period: period.slice(0, 120) })
  }
  return {
    name: typeof raw.name === 'string' ? raw.name.trim().slice(0, 60) : base.name,
    startYear: Number.isInteger(year) && year >= 1990 && year <= 2100 ? year : base.startYear,
    years: Number.isInteger(years) ? Math.min(MAX_YEARS, Math.max(1, years)) : base.years,
    campus: typeof raw.campus === 'string' ? raw.campus.slice(0, 64) : base.campus,
    courseCode: typeof raw.courseCode === 'string' ? raw.courseCode.slice(0, 16) : base.courseCode,
    periods: Array.isArray(raw.periods) && raw.periods.every((p) => typeof p === 'string')
      ? (raw.periods as string[]).slice(0, 12)
      : base.periods,
    entries
  }
}

/** True when the library actually reached storage, so the page can say so. */
function write(library: PlanLibrary): boolean {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(library))
    return true
  } catch {
    /* a plan that cannot be saved is still a plan that can be used today */
    return false
  }
}

/** How many steps undo remembers. A plan is small, so this is cheap. */
const HISTORY = 50

export function usePlan() {
  const plan = useState<PlanState>('plan', blank)
  const library = useState<PlanLibrary>('plan-library', freshLibrary)
  const loaded = useState<boolean>('plan-loaded', () => false)
  const savedAt = useState<number | null>('plan-saved-at', () => null)

  // Undo history, as JSON snapshots of the whole plan. Snapshots rather than
  // a list of operations because the plan changes through v-model as well
  // (campus, degree, start year), and diffing every one of those by hand is
  // how an undo stack ends up skipping a step.
  const past = useState<string[]>('plan-past', () => [])
  const future = useState<string[]>('plan-future', () => [])
  // Set while undo/redo or the first load writes the plan, so that write is
  // not itself recorded as a step.
  const replaying = useState<boolean>('plan-replaying', () => false)

  onMounted(() => {
    if (!loaded.value) {
      library.value = readLibrary()
      openActive()
      loaded.value = true
    }
  })

  /** Put the active plan from the library on the map, with a clean undo history. */
  function openActive() {
    const active = library.value.plans.find((p) => p.id === library.value.activeId)
      ?? library.value.plans[0]!
    library.value.activeId = active.id
    const state = JSON.parse(JSON.stringify(active.state)) as PlanState
    // Only flag the write when it will actually change something, or the
    // flag would sit there and swallow the reader's first real edit.
    replaying.value = JSON.stringify(state) !== JSON.stringify(plan.value)
    plan.value = state
    past.value = []
    future.value = []
  }

  function persist() {
    if (write(library.value)) savedAt.value = Date.now()
  }

  // Every edit on the map is copied into the active plan's slot in the
  // library and the whole library saved. A library is a handful of small
  // plans, so writing all of it is simpler than writing one and cheap enough.
  watch(plan, (value) => {
    if (!loaded.value) return
    const active = library.value.plans.find((p) => p.id === library.value.activeId)
    if (!active) return
    const next = JSON.stringify(value)
    if (next === JSON.stringify(active.state)) return
    active.state = JSON.parse(next)
    active.updatedAt = Date.now()
    persist()
  }, { deep: true })

  watch(() => JSON.stringify(plan.value), (now, before) => {
    if (!loaded.value || replaying.value) {
      replaying.value = false
      return
    }
    if (now === before) return
    past.value.push(before)
    if (past.value.length > HISTORY) past.value.shift()
    future.value = []
  })

  function restore(snapshot: string) {
    const cleaned = sanitise(JSON.parse(snapshot))
    if (!cleaned) return
    replaying.value = JSON.stringify(cleaned) !== JSON.stringify(plan.value)
    plan.value = cleaned
  }

  function undo() {
    const previous = past.value.pop()
    if (previous === undefined) return
    future.value.push(JSON.stringify(plan.value))
    restore(previous)
  }

  function redo() {
    const next = future.value.pop()
    if (next === undefined) return
    past.value.push(JSON.stringify(plan.value))
    restore(next)
  }

  const canUndo = computed(() => past.value.length > 0)
  const canRedo = computed(() => future.value.length > 0)

  const yearsList = computed(() =>
    Array.from({ length: plan.value.years }, (_, i) => plan.value.startYear + i)
  )

  function slotEntries(year: number, period: string) {
    return plan.value.entries.filter((e) => e.year === year && e.teaching_period === period)
  }

  function add(unitCode: string, year: number, period: string) {
    const code = unitCode.trim().toUpperCase()
    if (!code) return
    const already = plan.value.entries.some(
      (e) => e.unit_code === code && e.year === year && e.teaching_period === period
    )
    if (already) return
    plan.value.entries.push({ unit_code: code, year, teaching_period: period })
  }

  function remove(entry: PlanEntry) {
    plan.value.entries = plan.value.entries.filter(
      (e) =>
        !(
          e.unit_code === entry.unit_code &&
          e.year === entry.year &&
          e.teaching_period === entry.teaching_period
        )
    )
  }

  function move(entry: PlanEntry, year: number, period: string) {
    if (entry.year === year && entry.teaching_period === period) return
    remove(entry)
    add(entry.unit_code, year, period)
  }

  function reset() {
    // Clearing empties the plan; it does not forget what the reader called it.
    plan.value = { ...blank(), name: plan.value.name }
  }

  function addYear() {
    plan.value.years = Math.min(MAX_YEARS, plan.value.years + 1)
  }

  function removeYear(year: number) {
    plan.value.entries = plan.value.entries.filter((e) => e.year !== year)
    if (year === plan.value.startYear) plan.value.startYear += 1
    plan.value.years = Math.max(1, plan.value.years - 1)
  }

  // --- the library ---------------------------------------------------------

  function switchTo(id: string) {
    if (!library.value.plans.some((p) => p.id === id)) return
    library.value.activeId = id
    openActive()
    persist()
  }

  /** A new empty plan, made active. Returns its id, or null at the limit. */
  function create(name = ''): string | null {
    if (library.value.plans.length >= MAX_PLANS) return null
    const state = blank()
    state.name = name.trim().slice(0, 60)
    // Same campus as the plan the reader was just looking at: someone at
    // Malaysia making a second plan is still at Malaysia.
    state.campus = plan.value.campus
    const made = fresh(state)
    library.value.plans.push(made)
    switchTo(made.id)
    return made.id
  }

  function duplicate(id: string, copyName: (name: string) => string): string | null {
    if (library.value.plans.length >= MAX_PLANS) return null
    const source = library.value.plans.find((p) => p.id === id)
    if (!source) return null
    const state = JSON.parse(JSON.stringify(source.state)) as PlanState
    state.name = copyName(source.state.name).slice(0, 60)
    const made = fresh(state)
    library.value.plans.splice(library.value.plans.indexOf(source) + 1, 0, made)
    persist()
    return made.id
  }

  /** Deleting the last plan leaves one empty plan rather than none. */
  function removePlan(id: string) {
    const at = library.value.plans.findIndex((p) => p.id === id)
    if (at < 0) return
    library.value.plans.splice(at, 1)
    if (!library.value.plans.length) library.value.plans.push(fresh())
    if (library.value.activeId === id) {
      library.value.activeId = library.value.plans[Math.max(0, at - 1)]!.id
      openActive()
    }
    persist()
  }

  function rename(id: string, name: string) {
    const target = library.value.plans.find((p) => p.id === id)
    if (!target) return
    const clean = name.trim().slice(0, 60)
    if (id === library.value.activeId) plan.value.name = clean
    else {
      target.state.name = clean
      target.updatedAt = Date.now()
      persist()
    }
  }

  function exported(): string {
    return JSON.stringify({ version: 1, ...plan.value }, null, 2)
  }

  // An imported plan arrives as a new plan rather than on top of the one on
  // screen, so importing a friend's plan never costs you your own. At the
  // limit it has nowhere else to go, so it replaces the active one.
  function adopt(cleaned: PlanState) {
    if (library.value.plans.length < MAX_PLANS) {
      const made = fresh(cleaned)
      library.value.plans.push(made)
      switchTo(made.id)
    } else {
      plan.value = cleaned
    }
  }

  /** Returns an error key, or null. An unreadable file must not wipe the plan. */
  function imported(text: string): string | null {
    try {
      const cleaned = sanitise(JSON.parse(text))
      if (!cleaned) return 'plan.importShape'
      adopt(cleaned)
      return null
    } catch {
      return 'plan.importParse'
    }
  }

  /** A plan from a pasted plan code (see utils/planCode). Returns an error key, or null. */
  function importedCode(text: string): string | null {
    const raw = decodePlan(text)
    const cleaned = raw && sanitise(raw)
    if (!cleaned) return 'plan.codeShape'
    adopt(cleaned)
    return null
  }

  return {
    plan,
    yearsList,
    slotEntries,
    add,
    remove,
    move,
    reset,
    addYear,
    removeYear,
    exported,
    imported,
    importedCode,
    undo,
    redo,
    canUndo,
    canRedo,
    savedAt,
    library,
    switchTo,
    create,
    duplicate,
    removePlan,
    rename
  }
}
