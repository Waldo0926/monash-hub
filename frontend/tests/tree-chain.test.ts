import { describe, expect, it } from 'vitest'
import { chainOf } from '../utils/treeChain'

// FIT1045 -> FIT1008 -> FIT2004 -> FIT3155, with FIT1047 -> FIT2004 as well,
// and FIT2102 hanging off FIT1008 on a branch of its own.
const edges = [
  { source: 'FIT1045', target: 'FIT1008' },
  { source: 'FIT1008', target: 'FIT2004' },
  { source: 'FIT1047', target: 'FIT2004' },
  { source: 'FIT2004', target: 'FIT3155' },
  { source: 'FIT1008', target: 'FIT2102' }
]

describe('chainOf', () => {
  it('walks every step back and every step forward', () => {
    expect([...chainOf('FIT2004', edges)].sort()).toEqual(['FIT1008', 'FIT1045', 'FIT1047', 'FIT2004', 'FIT3155'])
  })

  it('leaves out a sibling branch', () => {
    expect(chainOf('FIT2004', edges).has('FIT2102')).toBe(false)
    expect([...chainOf('FIT2102', edges)].sort()).toEqual(['FIT1008', 'FIT1045', 'FIT2102'])
  })

  it('is just the unit when nothing connects to it', () => {
    expect([...chainOf('MAT1830', edges)]).toEqual(['MAT1830'])
  })
})
