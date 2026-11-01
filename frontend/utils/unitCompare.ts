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

/** Preserve AND/OR group boundaries, not just a set of unit codes. */
function requisite(group: Record<string, unknown>): string {
  const parts = (Array.isArray(group.items) ? group.items : [])
    .map((item: Record<string, unknown>) => text(item.code) || text(item.name))
    .filter(Boolean)
  const children = (Array.isArray(group.groups) ? group.groups : [])
    .map((child: Record<string, unknown>) => requisite(child))
    .filter(Boolean)
  const connector = text(group.connector) || 'AND'
  const label = text(group.requisite_type)
  const body = [...parts, ...children].join(` ${connector} `)
  return `${label}:(${body || text(group.description) || text(group.title)})`
}

export function comparable(unit: UnitSnapshot, field: ComparisonField): string {
  switch (field) {
    case 'has_exam':
      return unit.has_exam == null ? '' : unit.has_exam ? 'Yes' : 'No'
    case 'offerings':
      return sorted((unit.offerings || []).map(o =>
        [o.campus_raw || o.campus, o.teaching_period_raw || o.teaching_period, o.attendance_mode]
          .map(text).filter(Boolean).join(' · ')
      ).filter(Boolean)).join('\n')
    case 'assessments':
      return (unit.assessments || []).map(a =>
        [a.number == null ? '' : String(a.number), a.name, a.type, a.weight, a.hurdle]
          .map(text).filter(Boolean).join(' · ')
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
