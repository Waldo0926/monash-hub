import { describe, expect, it } from 'vitest'
import { sanitise, type PlanState } from '../composables/usePlan'
import { decodePlan, encodePlan, findPlanCode } from '../utils/planCode'

const plan: PlanState = {
  name: '我的 plan | v2',
  startYear: 2026,
  years: 3,
  campus: 'Malaysia',
  courseCode: 'C2001',
  periods: ['First semester', 'Second semester', 'Summer semester A'],
  entries: [
    { unit_code: 'FIT1008', year: 2026, teaching_period: 'First semester' },
    { unit_code: 'FIT2004', year: 2027, teaching_period: 'Second semester' },
    { unit_code: 'FIT3155', year: 2028, teaching_period: 'Summer semester A' }
  ]
}

describe('plan code', () => {
  it('is one line with no spaces, and comes back as the same plan', () => {
    const code = encodePlan(plan)
    expect(code).toMatch(/^MH1\|/)
    expect(code).not.toMatch(/\s/)
    expect(code).toContain('|S1;S2;SA|FIT1008@0.0,FIT2004@1.1,FIT3155@2.2')
    expect(sanitise(decodePlan(code))).toEqual(plan)
  })

  it('is found inside a link or a message around it', () => {
    const code = encodePlan(plan)
    const link = `https://monashhub.secureview.tech/plan#plan=${encodeURIComponent(code)}`
    expect(findPlanCode(link)).toBe(code)
    expect(findPlanCode(`这是我的规划 ${code} 你看看`)).toBe(code)
    expect(findPlanCode('#plan=' + encodeURIComponent(code))).toBe(code)
  })

  it('keeps a period it has no short code for', () => {
    const odd = { ...plan, periods: ['Term 4'], entries: [{ unit_code: 'FIT1008', year: 2026, teaching_period: 'Term 4' }] }
    expect(sanitise(decodePlan(encodePlan(odd)))).toEqual(odd)
  })

  it('drops an entry whose period the plan does not list, and reads nothing from other text', () => {
    const stray = { ...plan, entries: [...plan.entries, { unit_code: 'MAT1830', year: 2026, teaching_period: 'Winter semester' }] }
    expect(sanitise(decodePlan(encodePlan(stray)))?.entries.map((e) => e.unit_code)).toEqual(['FIT1008', 'FIT2004', 'FIT3155'])
    expect(decodePlan('hello')).toBeNull()
    expect(decodePlan('MH1|only|two')).toBeNull()
    expect(sanitise(decodePlan('MH1|x|2026|3|Malaysia||S1;S2|FIT1008@0.9,junk,FIT2004@0.1'))?.entries).toEqual([
      { unit_code: 'FIT2004', year: 2026, teaching_period: 'Second semester' }
    ])
  })
})
