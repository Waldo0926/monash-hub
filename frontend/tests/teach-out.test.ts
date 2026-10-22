import { describe, expect, it } from 'vitest'
import { teachOutFor, teachOutRegion } from '../utils/teachOut'

describe('teach-out notices by campus', () => {
  it('sends Malaysia to the Malaysian page and every other campus to monash.edu', () => {
    expect(teachOutRegion('Malaysia')).toBe('malaysia')
    expect(teachOutRegion('Clayton')).toBe('australia')
    expect(teachOutRegion('Caulfield')).toBe('australia')
  })

  it('keeps the rows for that campus and rows meant for every campus', () => {
    const entries = [
      { plan: 'au', applies_to: 'australia' },
      { plan: 'my', applies_to: 'malaysia' },
      { plan: 'both', applies_to: 'all' }
    ]
    expect(teachOutFor(entries, 'malaysia').map(e => e.plan)).toEqual(['my', 'both'])
    expect(teachOutFor(entries, 'australia').map(e => e.plan)).toEqual(['au', 'both'])
  })
})
