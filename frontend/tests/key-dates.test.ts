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

  it('puts the printed time beside the teaching period', () => {
    const close = item({ kind: 'allocate_adjust_close', period: 'OCT-MY-01', time: '17:00', source: 'allocate-dates' })
    expect(keyDateLabel(close, 'zh')).toEqual({ main: 'Allocate+ 调整课表截止', sub: '十月入学 · 17:00' })
    expect(keyDateLabel(close, 'en')).toEqual({ main: 'Allocate+ timetable adjustment closes', sub: 'October intake · 17:00' })
    const wes = item({ kind: 'wes_open', period: 'S2-01', source: 'dates-wes-access' })
    expect(keyDateLabel(wes, 'zh')).toEqual({ main: 'WES 开放选课（新生首次选课）', sub: '第二学期' })
    const reenrol = item({ kind: 'reenrol', period: null, date: '2026-10-12', end: '2026-11-27', source: 'malaysia-re-enrol' })
    expect(keyDateLabel(reenrol, 'zh')).toEqual({ main: 'WES 续注册（选下一学年的课）', sub: null })
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
    expect(matchTools('什么时候选课').map(t => t.id)).toContain('dates')
    expect(matchTools('When does WES open?').map(t => t.id)).toContain('dates')
  })
})
