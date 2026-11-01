/**
 * Compare two explicit Handbook snapshots. An absent year is *unavailable*,
 * not evidence that a unit was removed or its requirements changed.
 * Keep nesting of requisite groups: flattening AND/OR trees changes meaning.
 */
export type UnitSnapshot = {
  unit_code: string
  academic_year: number
  title?: string | null
  credit_points?: string | null
  level?: string | null
  has_exam?: boolean | null
  assessment_summary?: string | null
  workload_requirements?: string | null
  offerings?: Array<{
    campus_raw?: string | null
    teaching_period_raw?: string | null
    attendance_mode?: string | null
    campus?: string | null
    teaching_period?: string | null
  }>
  assessments?: Array<{
    number?: number | null
    name?: string | null
    type?: string | null
    weight?: string | null
    hurdle?: string | null
  }>
  requisites?: Array<Record<string, unknown>>
  source_url?: string | null
  last_checked?: string | null
}

export type ComparisonField = 'title' | 'credit_points' | 'level' | 'has_exam' |
  'offerings' | 'assessments' | 'requisites' | 'assessment_summary' | 'workload_requirements'

export type DiffStatus = 'added' | 'removed' | 'changed' | 'unchanged' | 'unavailable'
export type DiffRow = { field: ComparisonField; from: string; to: string; status: DiffStatus }

const fields: readonly ComparisonField[] = [
  'title', 'credit_points', 'level', 'has_exam', 'offerings', 'assessments',
  'requisites', 'assessment_summary', 'workload_requirements'
]

function text(value: unknown): string {
  return value == null ? '' : String(value).trim()
}
function sorted(values: string[]): string[] {
  return values.sort((a, b) => a.localeCompare(b, 'en'))
}

const REQUISITE_LABEL: Record<string, string> = {
  prerequisite: 'Prerequisite', corequisite: 'Corequisite', prohibition: 'Prohibition'
}

/**
 * Preserve AND/OR group boundaries, not just a set of unit codes. Nested
 * groups are bracketed; the Handbook's internal "Container 1.2" titles are
 * layout, not rule text, so they are left out.
 */
function requisiteBody(group: Record<string, unknown>): string {
  const parts = (Array.isArray(group.items) ? group.items : [])
    .map((item: Record<string, unknown>) => text(item.code) || text(item.name))
    .filter(Boolean)
  const children = (Array.isArray(group.groups) ? group.groups : [])
    .map((child: Record<string, unknown>) => requisiteBody(child))
    .filter(Boolean)
    .map(body => /\s(AND|OR|\?)\s/.test(body) ? `(${body})` : body)
  const title = text(group.title)
  const notes = [/^Container\b/i.test(title) ? '' : title, text(group.description)].filter(Boolean)
  return [[...parts, ...children].join(` ${text(group.connector) || '?'} `), ...notes].filter(Boolean).join(' · ')
}

function requisite(group: Record<string, unknown>): string {
  const type = text(group.requisite_type)
  const body = requisiteBody(group)
  return body ? `${REQUISITE_LABEL[type] || type}: ${body}` : ''
}

/** "15" in the Handbook's weight column is a percentage. */
function weight(value: unknown): string {
  const w = text(value)
  return /^\d+(\.\d+)?$/.test(w) ? `${w}%` : w
}

/** "Teaching activities are on-campus (ON-CAMPUS)" reads as its code. */
function mode(value: unknown): string {
  const m = text(value)
  return m.match(/\(([A-Z][A-Z-]+)\)\s*$/)?.[1] || m
}

export function comparable(unit: UnitSnapshot, field: ComparisonField): string {
  switch (field) {
    case 'has_exam':
      return unit.has_exam == null ? '' : unit.has_exam ? 'Yes' : 'No'
    case 'offerings':
      return sorted((unit.offerings || []).map(o =>
        [text(o.campus_raw || o.campus), text(o.teaching_period_raw || o.teaching_period), mode(o.attendance_mode)]
          .filter(Boolean).join(' · ')
      ).filter(Boolean)).join('\n')
    case 'assessments':
      // The name often repeats the number ("1 - Assignment A1a"), so it goes.
      return (unit.assessments || []).map(a =>
        [text(a.name).replace(/^\d+\s*-\s*/, ''), text(a.type), weight(a.weight), text(a.hurdle)]
          .filter(Boolean).join(' · ')
      ).join('\n')
    case 'requisites':
      return sorted((unit.requisites || []).map(g => requisite(g)).filter(Boolean)).join('\n')
    default:
      return text(unit[field])
  }
}

export function compareUnitSnapshots(from: UnitSnapshot | null, to: UnitSnapshot | null): DiffRow[] {
  return fields.map(field => {
    const left = from ? comparable(from, field) : ''
    const right = to ? comparable(to, field) : ''
    const status: DiffStatus = !from || !to ? 'unavailable'
      : left === right ? 'unchanged'
      : !left ? 'added'
      : !right ? 'removed'
      : 'changed'
    return { field, from: left, to: right, status }
  })
}
