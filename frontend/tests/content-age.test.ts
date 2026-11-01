import { describe, it, expect } from 'vitest'
import { olderThanMonths } from '../utils/contentAge'

describe('community age notice', () => {
  const now = new Date('2026-11-01T12:00:00Z')
  it('marks an older review as historical without asserting it is incorrect', () => {
    expect(olderThanMonths('2024-01-01T00:00:00Z', 18, now)).toBe(true)
    expect(olderThanMonths('2026-02-01T00:00:00Z', 18, now)).toBe(false)
  })
  it('does not flag absent or invalid dates', () => {
    expect(olderThanMonths(null, 18, now)).toBe(false)
    expect(olderThanMonths('not-a-date', 18, now)).toBe(false)
    expect(olderThanMonths('2028-01-01', 18, now)).toBe(false)
  })
})
