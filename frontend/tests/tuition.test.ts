import { describe, expect, it } from 'vitest'
import { deltaAt, feeNote, feeTitle, filterFees, formatAmount, formatDelta } from '../utils/tuition'

describe('formatAmount', () => {
  it('groups thousands the same way on every machine', () => {
    expect(formatAmount({ value: 148320, written: '148,320', label: null })).toBe('RM 148,320')
    expect(formatAmount({ value: 100, written: '100', label: null })).toBe('RM 100')
  })

  it('shows an amount it could not read exactly as Monash printed it', () => {
    expect(formatAmount({ value: null, written: '74,40', label: null })).toBe('RM 74,40')
  })
})

describe('feeTitle and feeNote', () => {
  const row = { title: 'Bachelor of Computer Science', title_zh: '计算机科学学士' }

  it('uses the Chinese name only in Chinese', () => {
    expect(feeTitle(row, 'zh')).toBe('计算机科学学士')
    expect(feeTitle(row, 'ja')).toBe('Bachelor of Computer Science')
    expect(feeTitle({ ...row, title_zh: null }, 'zh')).toBe('Bachelor of Computer Science')
  })

  it('falls back to the English note outside Chinese', () => {
    const note = { en: 'Two plus two.', zh: '2+2。' }
    expect(feeNote(note, 'zh')).toBe('2+2。')
    expect(feeNote(note, 'ko')).toBe('Two plus two.')
    expect(feeNote(null, 'zh')).toBe('')
  })
})

describe('filterFees', () => {
  const rows = [
    { title: 'Bachelor of Engineering', title_zh: '工程学士', covers: ['Bachelor of Software Engineering (Honours)'] },
    { title: 'Master of Data Science', title_zh: '数据科学硕士', covers: [] }
  ]

  it('finds a degree listed inside another row', () => {
    expect(filterFees(rows, 'software')).toHaveLength(1)
  })

  it('matches Chinese names and ignores case', () => {
    expect(filterFees(rows, '数据')[0]?.title).toBe('Master of Data Science')
    expect(filterFees(rows, 'DATA')).toHaveLength(1)
    expect(filterFees(rows, '  ')).toHaveLength(2)
  })
})

describe('formatDelta and deltaAt', () => {
  it('signs the change and keeps one decimal of percent', () => {
    expect(formatDelta({ previous: 54720, diff: 2880, pct: 5.3 })).toBe('+RM 2,880 (+5.3%)')
    expect(formatDelta({ previous: 9600, diff: -400, pct: -4 })).toBe('−RM 400 (−4.0%)')
  })

  it('finds the delta for one stream and nothing when last year is unknown', () => {
    const change = {
      year: 2026,
      domestic: [{ previous: 39840, diff: 960, pct: 2.4 }, { previous: 45120, diff: 1440, pct: 3.2 }],
      international: null,
      source: 'profile'
    }
    expect(deltaAt(change, 'domestic', 1)?.diff).toBe(1440)
    expect(deltaAt(change, 'international', 0)).toBeNull()
    expect(deltaAt(null, 'domestic', 0)).toBeNull()
  })
})
