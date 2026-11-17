import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { october2027Status, intake2027Status, INTAKES_2027, APPLICATION_STATUS_2027, OCTOBER_2027_SOURCE } from '../utils/intake2027'

describe('verified 2027 October intake evidence', () => {
  beforeEach(() => { vi.useFakeTimers(); vi.setSystemTime(new Date('2026-11-08T12:00:00Z')) })
  afterEach(() => { vi.useRealTimers() })
  it('does not reuse a dated list for another year or after its review expires', () => {
    expect(intake2027Status('Bachelor of Psychology', 'october', 2028)).toBe('not_verified')
    vi.setSystemTime(new Date('2027-01-01T00:00:00Z'))
    expect(intake2027Status('Bachelor of Psychology', 'october', 2027)).toBe('not_verified')
  })
  it('recognises only exact titles publicly listed on the university site', () => {
    expect(october2027Status('Bachelor of Psychology and Business')).toBe('listed')
    expect(october2027Status('Bachelor of Psychology')).toBe('listed')
    expect(october2027Status('Master of Clinical Psychology')).toBe('not_verified')
    expect(october2027Status('Bachelor of Psychology and Business (Honours)')).toBe('not_verified')
    expect(OCTOBER_2027_SOURCE).toMatch(/^https:\/\/www\.monash\.edu\.my\//)
  })
  it('does not infer individual programme eligibility from general February and July deadlines', () => {
    expect(intake2027Status('Bachelor of Psychology and Business', 'february')).toBe('not_verified')
    expect(intake2027Status('Bachelor of Psychology and Business', 'july')).toBe('not_verified')
    expect(intake2027Status('Bachelor of Psychology and Business', 'october')).toBe('listed')
    expect(intake2027Status('Master of Clinical Psychology', 'october')).toBe('not_verified')
  })
  it('records reviewed primary sources and the correct general deadlines for all three 2027 intakes', () => {
    expect(INTAKES_2027.map(item => item.id)).toEqual(['february', 'july', 'october'])
    expect(INTAKES_2027.map(item => item.hasVerifiedDegreeList)).toEqual([false, false, true])
    expect(INTAKES_2027[0]?.generalDeadlineInternational).toBe('2026-12-18')
    expect(INTAKES_2027[1]?.generalDeadlineMalaysia).toBe('2027-07-16')
    expect(INTAKES_2027[2]?.generalDeadlineMalaysia).toBe('2027-10-15')
    for (const item of INTAKES_2027) {
      expect(item.source).toMatch(/^https:\/\/www\.monash\.edu\.my\//)
      expect(item.checkedOn).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    }
    expect(APPLICATION_STATUS_2027).toBe('not_verified')
  })

})
