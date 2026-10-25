import { describe, expect, it } from 'vitest'
import { checkedOnLabel, keyDateLabel, keyDateRange, type KeyDate } from '../utils/keyDates'
import { matchTools } from '../utils/assistant'

const item = (over: Partial<KeyDate>): KeyDate => ({
  date: '2026-11-02', end: null, kind: 'exams', period: 'S2-01', name: null, source: 'final-assessment-dates', ...over
})

describe('key date wording', () => {
  it('names an academic date and its teaching period', () => {
    expect(keyDateLabel(item({}), 'zh')).toEqual({ main: '期末考核', sub: '第二学期' })
    expect(keyDateLabel(item({}), 'en')).toEqual({ main: 'Final assessments', sub: 'Semester 2' })
  })

  it('translates a known holiday and keeps an unknown one in English', () => {
    const deepavali = item({ kind: 'holiday', period: null, name: 'Deepavali' })
    expect(keyDateLabel(deepavali, 'zh')).toEqual({ main: '屠妖节 Deepavali', sub: 'Deepavali' })
    const unknown = item({ kind: 'holiday', period: null, name: 'Some New Day' })
    expect(keyDateLabel(unknown, 'zh')).toEqual({ main: 'Some New Day', sub: null })
  })

  it('prints the year only for dates outside the current one', () => {
    const exams = item({ end: '2026-11-18' })
    expect(keyDateRange(exams, 'zh', '2026-10-25')).toBe('11月2–18日')
    expect(keyDateRange(exams, 'en', '2026-10-25')).toBe('2–18 Nov')
    expect(keyDateRange(item({ date: '2027-03-31' }), 'zh', '2026-10-25')).toBe('2027年3月31日')
  })

  it('reports the latest check across the sources', () => {
    const sources = [{ last_checked: '2026-10-17T02:00:00Z' }, { last_checked: '2026-10-20T08:00:00Z' }, { last_checked: null }]
    expect(checkedOnLabel(sources, 'zh')).toBe('10月20日')
    expect(checkedOnLabel(sources, 'en')).toBe('20 Oct')
    expect(checkedOnLabel([], 'en')).toBe('')
  })
})

describe('the assistant offers the dates page', () => {
  it('for a question about the calendar', () => {
    expect(matchTools('期末考试周是什么时候').map(t => t.id)).toContain('dates')
    expect(matchTools('When is the census date?').map(t => t.id)).toContain('dates')
  })
})
