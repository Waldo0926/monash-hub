/** A commencement-year degree record is never replaced by a nearby edition. */
export type CourseRulesSnapshot = {
  course_code: string
  academic_year: number
  title?: string | null
  source_url: string
  last_checked?: string | null
  containers?: Array<{ title?: string | null; credit_points?: number | null }>
}
export type CommencementRules = {
  code: string
  year: number
  status: 'available' | 'not_indexed' | 'failed' | 'identity_mismatch'
  snapshot: CourseRulesSnapshot | null
}

export async function loadCommencementRules(
  fetcher: (path: string) => Promise<unknown>, code: string, year: number,
  options: Record<string, string> = {}
): Promise<CommencementRules> {
  code = code.trim().toUpperCase()
  const base = { code, year, snapshot: null }
  if (!/^[A-Z]{1,4}\d{4}$/.test(code) || !Number.isInteger(year) || year < 1990 || year > 2100) {
    return { ...base, status: 'failed' }
  }
  try {
    const query = new URLSearchParams({ locale: 'en', ...options, year: String(year) })
    const value = await fetcher(`/v1/courses/${encodeURIComponent(code)}?${query}`) as CourseRulesSnapshot
    const url = new URL(value.source_url)
    if (value.course_code !== code || value.academic_year !== year ||
        url.protocol !== 'https:' || url.hostname !== 'handbook.monash.edu' ||
        url.pathname.replace(/\/$/, '') !== `/${year}/courses/${code}`) {
      return { ...base, status: 'identity_mismatch' }
    }
    return { code, year, status: 'available', snapshot: value }
  } catch (error) {
    const e = error as { status?: number; statusCode?: number; response?: { status?: number } } | null
    const missing = [e?.status, e?.statusCode, e?.response?.status].includes(404)
    return { ...base, status: missing ? 'not_indexed' : 'failed' }
  }
}
