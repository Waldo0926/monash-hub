import { describe, expect, it } from 'vitest'
import { handbookYearFor } from '../composables/useHandbookYear'

const loaded = [2027, 2026, 2025]

describe('handbookYearFor', () => {
  it('uses the year itself when that Handbook is loaded', () => {
    expect(handbookYearFor(2026, loaded)).toBe(2026)
    expect(handbookYearFor(2027, loaded)).toBe(2027)
  })

  it('reads the latest earlier Handbook for a year not loaded yet', () => {
    expect(handbookYearFor(2029, loaded)).toBe(2027)
  })

  it('reads the earliest Handbook for a year before all of them', () => {
    expect(handbookYearFor(2023, loaded)).toBe(2025)
  })

  it('has no answer before the years are known', () => {
    expect(handbookYearFor(2026, [])).toBeUndefined()
    expect(handbookYearFor(2026, null)).toBeUndefined()
  })
})
