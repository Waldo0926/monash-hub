import { describe, expect, it } from 'vitest'
import { estimateFeeScenario } from '../utils/feeScenario'
import type { FeeRow } from '../utils/tuition'

function fee(basis: FeeRow['basis'], value: number | null): FeeRow {
  return {
    title: 'Test degree', title_zh: null, covers: [], school: '', source: 'official',
    duration: null, mode: null, variant: null, basis, domestic: [],
    international: [{ value, written: String(value), label: null }],
    unreadable: false, note: null, change: null
  }
}
describe('fee scenario estimation', () => {
  it('separates tuition discount and optional living costs for annual fee', () => {
    const result = estimateFeeScenario({ row: fee('per_year', 40000), feeSide: 'international',
      amountIndex: 0, yearsRemaining: 2, scholarshipPercent: 50, livingPerYear: 12000 })
    expect(result).toMatchObject({ published: 40000, grossTuition: 80000, discount: 40000, netTuition: 40000, living: 24000, total: 64000 })
  })
  it('does not multiply a full-course fee by remaining years', () => {
    const result = estimateFeeScenario({ row: fee('full_course', 60000), feeSide: 'international',
      amountIndex: 0, yearsRemaining: 3, scholarshipPercent: 0, livingPerYear: 0 })
    expect(result?.grossTuition).toBe(60000)
  })
  it('declines unreadable, unpriced and unidentified fee basis', () => {
    const props = { feeSide: 'international' as const, amountIndex: 0, yearsRemaining: 2, scholarshipPercent: 0, livingPerYear: 0 }
    expect(estimateFeeScenario({ ...props, row: fee('per_year', null) })).toBeNull()
    expect(estimateFeeScenario({ ...props, row: fee(null, 1000) })).toBeNull()
    expect(estimateFeeScenario({ ...props, row: { ...fee('per_year', 1000), unreadable: true } })).toBeNull()
    expect(estimateFeeScenario({ ...props, row: fee('per_year', 1000), scholarshipPercent: 110 })).toBeNull()
  })
})
