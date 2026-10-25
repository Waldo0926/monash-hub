import { describe, expect, it } from 'vitest'
import { degreeCandidates, firstOpenSlot, type CandidatePart } from '../utils/planCandidates'

const part = (index: number, extra: Partial<CandidatePart> = {}): CandidatePart => ({
  index,
  title: `Part ${'ABC'[index]}`,
  letter: 'ABC'[index]!,
  tone: index + 1,
  free: false,
  aos: null,
  ...extra
})

const course = {
  containers: [
    {
      title: 'Part A. Core',
      items: [
        { type: 'unit', code: 'FIT1008' },
        { type: 'unit', code: 'FIT1045' },
        { type: 'unit', code: 'FIT1999' }
      ],
      containers: [{ title: 'Later', items: [{ type: 'unit', code: 'FIT2004' }], containers: [] }]
    },
    {
      title: 'Part B. Specialist studies',
      items: [
        { type: 'specialisation', code: 'ALGO' },
        { type: 'specialisation', code: 'DATA' }
      ],
      containers: []
    },
    { title: 'Part C. Free electives', items: [], containers: [] }
  ],
  units: {
    FIT1008: { in_year: true, title: 'Intro', credit_points: 6, periods: ['S1', 'S2'], offered_at_campus: true },
    FIT1045: { in_year: true, title: 'Programming', credit_points: 6, periods: ['S1'], offered_at_campus: false },
    FIT1999: { in_year: false, title: 'Gone' },
    FIT2004: { in_year: true, title: 'Algorithms', credit_points: 6, periods: ['S1'], offered_at_campus: true },
    FIT3155: { in_year: true, title: 'Advanced algorithms', credit_points: 6, periods: ['S2'], offered_at_campus: true },
    FIT3181: { in_year: true, title: 'Deep learning', credit_points: 6, periods: ['S1'], offered_at_campus: true }
  },
  areas_of_study: [
    { code: 'ALGO', title: 'Algorithms and software', unit_codes: ['FIT2004', 'FIT3155'] },
    { code: 'DATA', title: 'Data science', unit_codes: ['FIT3181'] }
  ]
}

describe('degreeCandidates', () => {
  it('lists what the degree names and the plan lacks, in the degree order', () => {
    const got = degreeCandidates(course, [part(0), part(1), part(2, { free: true })], new Set(['FIT1008']))
    expect(got.map((c) => c.unit_code)).toEqual(['FIT1045', 'FIT2004', 'FIT3155', 'FIT3181'])
    expect(got[0]).toMatchObject({ title: 'Programming', periods: ['S1'], offered_at_campus: false, via: null })
    expect(got[0]!.part.letter).toBe('A')
  })

  it('names the specialisation a unit comes through, and a unit in two parts once', () => {
    const got = degreeCandidates(course, [part(0), part(1), part(2, { free: true })], new Set())
    const byCode = Object.fromEntries(got.map((c) => [c.unit_code, c]))
    // FIT2004 is in Part A directly and in the ALGO specialisation: Part A wins.
    expect(byCode.FIT2004!.part.letter).toBe('A')
    expect(byCode.FIT2004!.via).toBeNull()
    expect(byCode.FIT3155).toMatchObject({ via: 'Algorithms and software' })
    expect(byCode.FIT3181).toMatchObject({ via: 'Data science' })
    expect(byCode.FIT3181!.part.letter).toBe('B')
  })

  it('offers only the started specialisation once the plan has one', () => {
    const got = degreeCandidates(course, [part(0), part(1, { aos: 'ALGO' }), part(2, { free: true })], new Set())
    expect(got.map((c) => c.unit_code)).not.toContain('FIT3181')
    expect(got.map((c) => c.unit_code)).toContain('FIT3155')
  })

  it('leaves out units the Handbook year does not list', () => {
    const got = degreeCandidates(course, [part(0), part(1), part(2, { free: true })], new Set())
    expect(got.map((c) => c.unit_code)).not.toContain('FIT1999')
  })

  it('is empty without a degree or its parts', () => {
    expect(degreeCandidates(null, [part(0)], new Set())).toEqual([])
    expect(degreeCandidates(course, [], new Set())).toEqual([])
  })
})

describe('firstOpenSlot', () => {
  const periods = ['First semester', 'Second semester']
  it('is the earliest semester with room', () => {
    const full = new Set(['2026|First semester'])
    const count = (y: number, p: string) => (full.has(`${y}|${p}`) ? 4 : 0)
    expect(firstOpenSlot([2026, 2027], periods, count, 4)).toEqual({ year: 2026, period: 'Second semester' })
  })
  it('falls back to the last year when everything is full', () => {
    expect(firstOpenSlot([2026, 2027], periods, () => 4, 4)).toEqual({ year: 2027, period: 'First semester' })
  })
  it('is null with nowhere to put a unit', () => {
    expect(firstOpenSlot([], periods, () => 0, 4)).toBeNull()
  })
})
