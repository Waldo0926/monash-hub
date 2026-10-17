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
 */
const KEY = 'mh_plan_v1'

export interface PlanEntry {
  unit_code: string
  year: number
  teaching_period: string
}

export interface PlanState {
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
    startYear: new Date().getFullYear(),
    years: 3,
    campus: 'Malaysia',
    courseCode: '',
    periods: [...DEFAULT_PERIODS],
    entries: []
  }
}

/**
 * Reading is wrapped because storage throws rather than returning null in a
 * private window and in previews, and a planner that white-screens on a
 * browser setting is worse than one that forgets.
 */
function read(): PlanState {
  if (import.meta.server) return blank()
  try {
    const raw = window.localStorage.getItem(KEY)
    if (!raw) return blank()
    return sanitise(JSON.parse(raw)) ?? blank()
  } catch {
    return blank()
  }
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

/** True when the plan actually reached storage, so the page can say so. */
function write(state: PlanState): boolean {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(state))
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
      const stored = read()
      // Only flag the write when it will actually change something, or the
      // flag would sit there and swallow the reader's first real edit.
      replaying.value = JSON.stringify(stored) !== JSON.stringify(plan.value)
      plan.value = stored
      loaded.value = true
    }
  })

  watch(plan, (value) => {
    if (loaded.value && write(value)) savedAt.value = Date.now()
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
    plan.value = blank()
  }

  function addYear() {
    plan.value.years = Math.min(MAX_YEARS, plan.value.years + 1)
  }

  function removeYear(year: number) {
    plan.value.entries = plan.value.entries.filter((e) => e.year !== year)
    if (year === plan.value.startYear) plan.value.startYear += 1
    plan.value.years = Math.max(1, plan.value.years - 1)
  }

  function exported(): string {
    return JSON.stringify({ version: 1, ...plan.value }, null, 2)
  }

  /** Returns an error key, or null. An unreadable file must not wipe the plan. */
  function imported(text: string): string | null {
    try {
      const cleaned = sanitise(JSON.parse(text))
      if (!cleaned) return 'plan.importShape'
      plan.value = cleaned
      return null
    } catch {
      return 'plan.importParse'
    }
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
    undo,
    redo,
    canUndo,
    canRedo,
    savedAt
  }
}
