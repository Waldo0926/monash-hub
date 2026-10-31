import { describe, expect, it } from 'vitest'
import { csvCell, toCsv } from '../utils/csv'

describe('csvCell', () => {
  it('quotes titles with commas and doubles inner quotes', () => {
    expect(csvCell('Introduction to computer systems, networks and security'))
      .toBe('"Introduction to computer systems, networks and security"')
    expect(csvCell('the "core" unit')).toBe('"the ""core"" unit"')
  })

  it('stops Excel reading a cell as a formula', () => {
    expect(csvCell('=HYPERLINK("x")')).toBe(`"'=HYPERLINK(""x"")"`)
    expect(csvCell('+1')).toBe(`"'+1"`)
    expect(csvCell('@SUM(A1)')).toBe(`"'@SUM(A1)"`)
  })

  it('writes empty values as empty cells, not "undefined"', () => {
    expect(csvCell(undefined)).toBe('""')
    expect(csvCell(null)).toBe('""')
    expect(csvCell(6)).toBe('"6"')
  })
})

describe('toCsv', () => {
  it('starts with a BOM and uses CRLF between rows', () => {
    const text = toCsv([['year', 'unit_code'], [2026, 'FIT1045']])
    expect(text.startsWith('﻿')).toBe(true)
    expect(text.slice(1)).toBe('"year","unit_code"\r\n"2026","FIT1045"')
  })
})
