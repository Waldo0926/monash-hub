import { describe, expect, it } from 'vitest'
import { MAX_PLANS, MAX_YEARS, sanitise, sanitiseLibrary } from '../composables/usePlan'

const entry = { unit_code: 'fit1045 ', year: 2026, teaching_period: 'First semester' }

describe('sanitise', () => {
  it('keeps a plan name, trimmed and capped', () => {
    const plan = sanitise({ name: '  Main plan  ', entries: [] })
    expect(plan?.name).toBe('Main plan')
    expect(sanitise({ name: 'x'.repeat(200), entries: [] })?.name).toHaveLength(60)
  })

  it('gives a plan from before names an empty one', () => {
    expect(sanitise({ startYear: 2026, entries: [entry] })?.name).toBe('')
  })

  it('cleans unit codes and caps the years', () => {
    const plan = sanitise({ years: 1e9, entries: [entry] })
    expect(plan?.entries[0]?.unit_code).toBe('FIT1045')
    expect(plan?.years).toBe(MAX_YEARS)
  })
})

describe('sanitiseLibrary', () => {
  it('rejects anything that is not a list of plans', () => {
    expect(sanitiseLibrary(null)).toBeNull()
    expect(sanitiseLibrary({ plans: 'nope' })).toBeNull()
    expect(sanitiseLibrary({ plans: [] })).toBeNull()
    expect(sanitiseLibrary({ plans: [{ id: 'a', state: { entries: 'x' } }] })).toBeNull()
  })

  it('points the active id at a plan that exists', () => {
    const library = sanitiseLibrary({
      activeId: 'gone',
      plans: [{ id: 'a', updatedAt: 1, state: { entries: [entry] } }]
    })
    expect(library?.activeId).toBe('a')
  })

  it('gives duplicate or missing ids fresh ones', () => {
    const library = sanitiseLibrary({
      activeId: 'a',
      plans: [
        { id: 'a', state: { entries: [] } },
        { id: 'a', state: { entries: [] } },
        { state: { entries: [] } }
      ]
    })
    const ids = library!.plans.map((p) => p.id)
    expect(new Set(ids).size).toBe(3)
    expect(library!.activeId).toBe('a')
  })

  it('drops broken plans and stops at the limit', () => {
    const plans = Array.from({ length: MAX_PLANS + 5 }, (_, i) => ({ id: `p${i}`, state: { entries: [] } }))
    plans.splice(1, 0, { id: 'bad', state: null as any })
    const library = sanitiseLibrary({ activeId: 'p0', plans })
    expect(library!.plans.length).toBeLessThanOrEqual(MAX_PLANS)
    expect(library!.plans.some((p) => p.id === 'bad')).toBe(false)
  })
})
