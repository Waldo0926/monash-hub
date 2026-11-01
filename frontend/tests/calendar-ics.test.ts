import { describe, it, expect } from 'vitest'
import { buildKeyDatesIcs } from '../utils/calendarIcs'
import type { KeyDates } from '../utils/keyDates'

const data: KeyDates = {
  campus: 'malaysia', today: '2026-11-01',
  sources: { dates: { title: 'Official page', url: 'https://www.monash.edu.my/dates', last_checked: '2026-10-30' } },
  items: [
    { date: '2027-02-01', end: '2027-02-03', kind: 'exams', period: 'S1-01', name: null, source: 'dates' },
    { date: '2027-12-31', end: '2028-01-01', kind: 'holiday', period: null, name: 'Holiday', source: 'dates' }
  ]
}
describe('official date calendar export', () => {
  it('uses all-day ranges with exclusive end, including year boundaries', () => {
    const out = buildKeyDatesIcs(data, 'en', true, new Date('2026-11-01T00:00:00Z'))
    expect(out).toContain('DTSTART;VALUE=DATE:20270201')
    expect(out).toContain('DTEND;VALUE=DATE:20270204')
    expect(out).toContain('DTEND;VALUE=DATE:20280102')
    expect(out).toContain('Official source: https://www.monash.edu.my/dates')
  })
  it('uses stable UIDs and respects holiday filter', () => {
    const a = buildKeyDatesIcs(data, 'en', false, new Date('2026-11-01T00:00:00Z'))
    const b = buildKeyDatesIcs(data, 'en', false, new Date('2026-12-01T00:00:00Z'))
    expect([...a.matchAll(/UID:([^\r\n]+)/g)].map(x => x[1])).toEqual([...b.matchAll(/UID:([^\r\n]+)/g)].map(x => x[1]))
    expect((a.match(/BEGIN:VEVENT/g) || []).length).toBe(1)
  })
  it('skips malformed or impossible source dates', () => {
    const bad: KeyDates = { ...data, items: [{ ...data.items[0]!, date: '2027-02-31' }] }
    expect(buildKeyDatesIcs(bad, 'zh')).not.toContain('BEGIN:VEVENT')
  })
})
