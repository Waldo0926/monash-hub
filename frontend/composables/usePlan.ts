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
    const parsed = JSON.parse(raw)
    return { ...blank(), ...parsed, entries: Array.isArray(parsed.entries) ? parsed.entries : [] }
  } catch {
    return blank()
  }
}

function write(state: PlanState) {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(state))
  } catch {
    /* a plan that cannot be saved is still a plan that can be used today */
  }
}

export function usePlan() {
  const plan = useState<PlanState>('plan', blank)
  const loaded = useState<boolean>('plan-loaded', () => false)

  onMounted(() => {
    if (!loaded.value) {
      plan.value = read()
      loaded.value = true
    }
  })

  watch(plan, (value) => {
    if (loaded.value) write(value)
  }, { deep: true })

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
    remove(entry)
    add(entry.unit_code, year, period)
  }

  function reset() {
    plan.value = blank()
  }

  function addYear() {
    plan.value.years += 1
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
      const parsed = JSON.parse(text)
      if (!parsed || !Array.isArray(parsed.entries)) return 'plan.importShape'
      plan.value = { ...blank(), ...parsed, entries: parsed.entries }
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
    imported
  }
}
