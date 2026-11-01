import { describe, expect, it } from 'vitest'
import { possibleMissingExplicitUnits } from '../utils/courseGaps'

describe('conservative graduation review candidates', () => {
  const structure = [{ title: 'Part A', containers: [
    { title: 'Core unit', items: [{ type: 'unit', code: 'FIT1045' }] },
    { title: 'Choose one', items: [{ type: 'unit', code: 'FIT1047' }] },
    { title: 'Alternative', connector: 'OR', items: [{ type: 'unit', code: 'FIT1055' }] },
    { title: 'Elective', free_elective: true, items: [{ type: 'unit', code: 'FIT2099' }] },
    { title: 'List', items: [{ type: 'unit', code: 'FIT1050' }, { type: 'unit', code: 'FIT1060' }] }
  ] }]
  it('suggests only one-unit explicit leaves, not alternatives', () => {
    expect(possibleMissingExplicitUnits(structure, [])).toEqual([{ code: 'FIT1045', part: 'Core unit' }])
  })
  it('never suggests units already planned', () => {
    expect(possibleMissingExplicitUnits(structure, ['fit1045'])).toEqual([])
  })
})
