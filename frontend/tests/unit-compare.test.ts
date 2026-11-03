import { describe, expect, it } from 'vitest'
import { comparable, compareUnitSnapshots, type UnitSnapshot } from '../utils/unitCompare'

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
    expect(rows.find(x => x.field === 'has_exam')?.status).toBe('unavailable')
  })
  it('does not confuse unknown with an explicit no-exam entry', () => {
    expect(compareUnitSnapshots(unit, { ...unit, has_exam: false })
      .find(x => x.field === 'has_exam')?.status).toBe('unavailable')
  })
})

describe('Handbook year comparison text', () => {
  it('reads nested requisite groups without the Handbook container titles', () => {
    const nested = { ...unit, requisites: [{
      requisite_type: 'prerequisite', connector: 'AND', title: 'Container 1', items: [], groups: [
        { connector: 'OR', title: 'Container 1.2', items: [{ code: 'FIT1045' }, { code: 'FIT1053' }] },
        { connector: 'OR', title: 'Container 1.5', items: [{ code: 'FIT1058' }, { code: 'MAT1830' }] }
      ]
    }] }
    expect(comparable(nested, 'requisites')).toBe('Prerequisite: (FIT1045 OR FIT1053) AND (FIT1058 OR MAT1830)')
  })
  it('shows assessment weights as percentages without repeating the number', () => {
    const marked = { ...unit, assessments: [{ number: 1, name: '1 - Assignment A1a', type: 'Artefact', weight: '15' }] }
    expect(comparable(marked, 'assessments')).toBe('Assignment A1a · Artefact · 15%')
  })
})


describe('equivalent requisite ordering', () => {
  it('does not report source-only reordering of AND/OR alternatives as a rule change', () => {
    const before = { ...unit, requisites: [{ requisite_type: 'prerequisite', connector: 'AND', groups: [
      { connector: 'OR', items: [{ code: 'FIT1045' }, { code: 'FIT1053' }] },
      { connector: 'OR', items: [{ code: 'FIT1058' }, { code: 'MAT1830' }] }
    ] }] }
    const after = { ...before, academic_year: 2027, requisites: [{ ...before.requisites[0], groups:
      [...before.requisites[0]!.groups].reverse().map(g => ({ ...g, items: [...g.items].reverse() }))
    }] }
    expect(compareUnitSnapshots(before, after).find(r => r.field === 'requisites')?.status).toBe('unchanged')
    after.requisites[0]!.connector = 'OR'
    expect(compareUnitSnapshots(before, after).find(r => r.field === 'requisites')?.status).toBe('changed')
  })
})


describe('partial field availability', () => {
  it('does not label two missing source fields as unchanged', () => {
    expect(compareUnitSnapshots(unit, { ...unit, academic_year: 2027 })
      .find(row => row.field === 'workload_requirements')?.status).toBe('unavailable')
  })
  it('does not call a newly populated source field an added rule', () => {
    const next = { ...unit, workload_requirements: 'Twelve hours per week' }
    expect(compareUnitSnapshots(unit, next).find(row => row.field === 'workload_requirements')?.status).toBe('unavailable')
  })
  it('distinguishes missing arrays from explicitly empty lists', () => {
    const before = { ...unit, requisites: [] }
    const after = { ...unit, requisites: undefined }
    expect(compareUnitSnapshots(before, after).find(row => row.field === 'requisites')?.status).toBe('unavailable')
    expect(compareUnitSnapshots(before, { ...unit, requisites: [] }).find(row => row.field === 'requisites')?.status).toBe('unchanged')
  })
})
