/**
 * WAM and GPA, computed in the browser.
 *
 * The scoring tables come from `/v1/marks/reference`, which is where they are
 * pinned against Monash's own worked examples. This file is only the two
 * weighted averages plus the parsing, and it runs client-side on purpose: a
 * student's marks never leave their machine, so there is no request body with
 * somebody's failed unit in it and nothing in an access log.
 *
 * Every rule that is easy to get wrong is in `applyWam` and `applyGpa`, and
 * each one is there because a homemade calculator usually gets it wrong the
 * other way:
 *
 * - a fail counts, at its actual mark
 * - a withdrawn fail counts as zero and keeps its weight in the denominator
 * - the level weight applies to WAM only, never to GPA
 * - the level weight goes in the numerator *and* the denominator
 */

export interface MarksReference {
  grade_points: Record<string, Record<string, number>>
  grade_names: Record<string, string>
  grade_bands: { floor: number; grade: string }[]
  excluded_grades: string[]
  level_weights: { first_year: number; other: number }
  sources: Record<string, string>
  guides: Record<string, string>
}

export interface MarkEntry {
  id: number
  unitCode: string
  title?: string | null
  creditPoints: number | null
  level: number | null
  /** The mark out of 100. Null when only a grade is known. */
  mark: number | null
  /** An explicit grade code, for WN and the excluded grades. */
  grade: string | null
}

export const AUSTRALIA = 'australia'
export const MALAYSIA = 'malaysia'

/** Monash rounds the final mark, so 79.51 is an 80 and an HD. */
export function roundMark(mark: number): number {
  return mark >= 0 ? Math.floor(mark + 0.5) : Math.ceil(mark - 0.5)
}

export function gradeForMark(mark: number, ref: MarksReference): string | null {
  const rounded = roundMark(mark)
  if (rounded < 0 || rounded > 100) return null
  for (const band of ref.grade_bands) {
    if (rounded >= band.floor) return band.grade
  }
  return null
}

/** The grade an entry scores under, or null when it does not count at all. */
export function resolveGrade(entry: MarkEntry, ref: MarksReference): string | null {
  if (entry.grade) {
    const code = entry.grade.trim().toUpperCase()
    if (ref.excluded_grades.includes(code)) return null
    return code in ref.grade_names ? code : null
  }
  if (entry.mark === null || Number.isNaN(entry.mark)) return null
  return gradeForMark(entry.mark, ref)
}

function levelWeight(entry: MarkEntry, ref: MarksReference): number {
  return entry.level === 1 ? ref.level_weights.first_year : ref.level_weights.other
}

/** Entries that can actually be scored — the rest are shown but not counted. */
export function countable(entries: MarkEntry[], ref: MarksReference): MarkEntry[] {
  return entries.filter(e => e.creditPoints !== null && resolveGrade(e, ref) !== null)
}

export function applyWam(entries: MarkEntry[], ref: MarksReference): number | null {
  let top = 0
  let bottom = 0
  for (const entry of entries) {
    const grade = resolveGrade(entry, ref)
    if (grade === null || entry.creditPoints === null) continue
    const weight = entry.creditPoints * levelWeight(entry, ref)
    // A withdrawn fail has no mark and scores zero — but its weight stays in
    // the denominator, which is exactly what makes a WN so expensive.
    const mark = grade === 'WN' ? 0 : entry.mark
    if (mark === null || Number.isNaN(mark)) continue
    top += mark * weight
    bottom += weight
  }
  return bottom > 0 ? top / bottom : null
}

export function applyGpa(
  entries: MarkEntry[],
  ref: MarksReference,
  scale: string
): number | null {
  const points = ref.grade_points[scale]
  if (!points) return null
  let top = 0
  let bottom = 0
  for (const entry of entries) {
    const grade = resolveGrade(entry, ref)
    if (grade === null || entry.creditPoints === null) continue
    // No level weight here. GPA does not use it; only WAM does.
    top += points[grade]! * entry.creditPoints
    bottom += entry.creditPoints
  }
  return bottom > 0 ? top / bottom : null
}

/**
 * The same mark in every planned unit that would reach `target` WAM.
 *
 * Returned unclamped on purpose. Above 100 means the target is already out of
 * reach and below 0 means it is already secured, and both of those are more
 * useful answers than a number pinned to the end of the scale.
 */
export function markNeeded(
  done: MarkEntry[],
  plannedWeight: number,
  target: number,
  ref: MarksReference
): number | null {
  if (plannedWeight <= 0) return null
  let top = 0
  let bottom = 0
  for (const entry of done) {
    const grade = resolveGrade(entry, ref)
    if (grade === null || entry.creditPoints === null) continue
    const weight = entry.creditPoints * levelWeight(entry, ref)
    const mark = grade === 'WN' ? 0 : entry.mark
    if (mark === null || Number.isNaN(mark)) continue
    top += mark * weight
    bottom += weight
  }
  return (target * (bottom + plannedWeight) - top) / plannedWeight
}

/**
 * Pull unit codes, marks and grades out of text pasted from WES.
 *
 * Deliberately tolerant rather than clever. WES has changed its results layout
 * more than once and students paste from the transcript, the portal and a
 * spreadsheet, so this looks for the two things every one of those has on a
 * line — a unit code and a number — instead of trying to match a table shape.
 *
 * A line that has a code but no mark still comes back, so the entry appears in
 * the table with the mark blank rather than being dropped silently.
 */
const UNIT_CODE = /\b([A-Z]{2,4}\d{4})\b/
const GRADE_TOKEN = /\b(HD|NH|NP|WN|SFR|NAS|NE|WI|PGO|NPGO|WNGO|[NDCP])\b/
const NUMBER = /\b(\d{1,3}(?:\.\d+)?)\b/g

/** The credit point values the Handbook actually uses. */
const CREDIT_POINT_VALUES = [3, 6, 9, 12, 18, 24, 36, 48]
/** Grades that exist without a mark behind them. */
const MARKLESS_GRADES = ['WN', 'SFR', 'NAS', 'NE', 'WI', 'PGO', 'NPGO', 'WNGO']

export interface ParsedRow {
  unitCode: string
  mark: number | null
  grade: string | null
  creditPoints: number | null
}

export function parsePastedResults(text: string): ParsedRow[] {
  const rows: ParsedRow[] = []
  const seen = new Set<string>()

  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim()
    if (!line) continue
    const codeMatch = UNIT_CODE.exec(line.toUpperCase())
    if (!codeMatch) continue
    const unitCode = codeMatch[1]!
    if (seen.has(unitCode)) continue
    seen.add(unitCode)

    // Numbers after the code, so the digits inside the code itself are not
    // read as a mark.
    const after = line.toUpperCase().slice(codeMatch.index + unitCode.length)
    const numbers = [...after.matchAll(NUMBER)].map(m => Number(m[1]))

    const gradeMatch = GRADE_TOKEN.exec(after)
    const grade = gradeMatch ? gradeMatch[1]! : null
    // A mark is 0-100; credit points are one of the Handbook's small values, so
    // a lone 6, 12 or 24 sitting beside a mark is the credit points, not a mark.
    const marks = numbers.filter(n => n >= 0 && n <= 100)
    let creditPoints: number | null = null
    let mark: number | null = null

    if (marks.length >= 2 && CREDIT_POINT_VALUES.includes(marks[0]!)) {
      creditPoints = marks[0]!
      mark = marks[1]!
    } else if (marks.length === 1 && grade && CREDIT_POINT_VALUES.includes(marks[0]!)) {
      // One number and a grade: a withdrawn fail or an excluded grade has no
      // mark at all, so the number is the credit points. Reading it as a mark
      // of 6 would drop the unit out of the WAM entirely — and a WN has to stay
      // in the denominator, which is the whole reason it is expensive.
      creditPoints = marks[0]!
    } else if (marks.length >= 1) {
      mark = marks[marks.length - 1]!
    }

    // These grades never carry a mark, whatever else was on the line.
    if (grade && MARKLESS_GRADES.includes(grade)) mark = null

    rows.push({
      unitCode,
      mark: mark === null || Number.isNaN(mark) ? null : mark,
      grade,
      creditPoints
    })
  }
  return rows
}
