import { describe, expect, it } from 'vitest'
import { assessmentName, handbookTerm } from '../i18n/handbook-terms'

describe('handbookTerm', () => {
  it('leaves English alone', () => {
    expect(handbookTerm('campus', 'Clayton', 'en')).toBe('Clayton')
  })

  it('names a campus and a period in every translated language', () => {
    expect(handbookTerm('campus', 'Clayton', 'zh')).toBe('Clayton 校区')
    expect(handbookTerm('campus', 'Clayton', 'ja')).toBe('Clayton キャンパス')
    expect(handbookTerm('period', 'First semester', 'ko')).toBe('1학기')
  })

  it('joins a period range the way each language writes one', () => {
    expect(handbookTerm('period', 'Second semester to First semester', 'zh')).toBe('第二学期至第一学期')
    expect(handbookTerm('period', 'Second semester to First semester', 'ja')).toBe('第2学期〜第1学期')
    expect(handbookTerm('period', 'Winter semester - alternate', 'ko')).toBe('겨울 학기(대체 일정)')
  })

  it('keeps the attendance code, in brackets of that language', () => {
    const mode = 'Teaching activities are on-campus (ON-CAMPUS)'
    expect(handbookTerm('mode', mode, 'ja')).toBe('対面授業（ON-CAMPUS）')
    expect(handbookTerm('mode', mode, 'ko')).toBe('대면 수업(ON-CAMPUS)')
  })

  it('falls back to the English it does not know', () => {
    expect(handbookTerm('campus', 'Somewhere new', 'ja')).toBe('Somewhere new')
  })
})

describe('assessmentName', () => {
  it('translates the generated label and nothing a faculty wrote', () => {
    expect(assessmentName('1 - Project', 'zh')).toBe('第 1 项 · 项目作业')
    expect(assessmentName('2 - Thesis', 'ko')).toBe('2번 · 학위 논문')
    expect(assessmentName('Weekly quiz', 'ja')).toBe('Weekly quiz')
  })
})
