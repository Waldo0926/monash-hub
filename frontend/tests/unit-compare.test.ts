import { describe, expect, it } from 'vitest'
import { compareUnitSnapshots, type UnitSnapshot } from '../utils/unitCompare'

const unit: UnitSnapshot = {
  unit_code: 'FIT2102',
  academic_year: 2026,
  title: 'Programming paradigms',
  credit_points: '6',
  has_exam: null,
  offerings: [{ campus_raw: 'Malaysia', teaching_period_raw: 'Second semester' }],
  assessments: [{ number: 1, name: 'Assignment', weight: '30%' }],
  requisites: [{ requisite_type: 'prerequisite', connector: 'OR', items: [{ code: 'FIT1045' }, { code: 'FIT1048' }] }]
}

describe('Handbook year comparison', () => {
  it('never calls a missing year a removed requisite or offering', () => {
    expect(compareUnitSnapshots(unit, null).every(row => row.status === 'unavailable')).toBe(true)
  })
  it('compares offerings independent of their database order', () => {
    const left = { ...unit, offerings: [
      { campus_raw: 'Malaysia', teaching_period_raw: 'First semester' },
      { campus_raw: 'Clayton', teaching_period_raw: 'Second semester' }
    ] }
    const right = { ...left, offerings: [...left.offerings].reverse(), academic_year: 2027 }
    const row = compareUnitSnapshots(left, right).find(x => x.field === 'offerings')
    expect(row?.status).toBe('unchanged')
  })
  it('detects changed assessment weights and preserves OR versus AND', () => {
    const next = { ...unit, academic_year: 2027, assessments: [{ number: 1, name: 'Assignment', weight: '50%' }],
      requisites: [{ requisite_type: 'prerequisite', connector: 'AND', items: [{ code: 'FIT1045' }, { code: 'FIT1048' }] }] }
    const rows = compareUnitSnapshots(unit, next)
    expect(rows.find(x => x.field === 'assessments')?.status).toBe('changed')
    expect(rows.find(x => x.field === 'requisites')?.status).toBe('changed')
    expect(rows.find(x => x.field === 'has_exam')?.status).toBe('unchanged')
  })
  it('does not confuse unknown with an explicit no-exam entry', () => {
    expect(compareUnitSnapshots(unit, { ...unit, has_exam: false })
      .find(x => x.field === 'has_exam')?.status).toBe('added')
  })
})
