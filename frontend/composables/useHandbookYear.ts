/**
 * The Handbook year a page was asked for, from `?year=`.
 *
 * Without it the API reads the current Handbook (or the latest one that lists
 * the code). With it, a page reads that year exactly - the same choice the
 * Handbook's own year picker makes - and every unit, degree and area-of-study
 * link on the page keeps it, so following FIT2004's prerequisites in 2025
 * stays in 2025.
 */
export function useHandbookYear() {
  const route = useRoute()
  const router = useRouter()

  const year = computed<number | null>(() => {
    const value = Number(Array.isArray(route.query.year) ? route.query.year[0] : route.query.year)
    return Number.isInteger(value) && value >= 1990 && value <= 2100 ? value : null
  })

  /** `path` with the chosen year added, or unchanged when none was chosen. */
  function withYear(path: string): string {
    if (!year.value) return path
    return `${path}${path.includes('?') ? '&' : '?'}year=${year.value}`
  }

  /** Switch the page to `next`; `null` goes back to the default (latest) Handbook. */
  function setYear(next: number | null) {
    const query = { ...route.query }
    if (next) query.year = String(next)
    else delete query.year
    router.replace({ query })
  }

  return { year, withYear, setYear }
}

/**
 * The Handbook that describes a calendar year of a plan.
 *
 * Same rule as `handbook_year_for` in backend/app/handbook/plan.py, so the
 * planner searches the Handbook it is checked against: that year's own when it
 * is loaded, else the latest loaded one before it, else the earliest loaded.
 * A unit in 2026 first semester is a 2026 unit. Searching without a year read
 * the site's current Handbook, 2027 once it was loaded, and FIT1058 is not in
 * it, so the picker said nothing matched for a unit taught that semester.
 * `undefined` while the loaded years are not known yet.
 */
export function handbookYearFor(year: number, loaded: number[] | null | undefined): number | undefined {
  if (!loaded?.length) return undefined
  if (loaded.includes(year)) return year
  const earlier = loaded.filter((y) => y <= year)
  return earlier.length ? Math.max(...earlier) : Math.min(...loaded)
}
