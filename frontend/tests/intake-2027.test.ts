import { describe, expect, it } from 'vitest'
import { october2027Status, OCTOBER_2027_SOURCE } from '../utils/intake2027'

describe('verified 2027 October intake evidence', () => {
  it('recognises only exact titles publicly listed on the university site', () => {
    expect(october2027Status('Bachelor of Psychology and Business')).toBe('listed')
    expect(october2027Status('Bachelor of Psychology')).toBe('listed')
    expect(october2027Status('Master of Clinical Psychology')).toBe('not_verified')
    expect(october2027Status('Bachelor of Psychology and Business (Honours)')).toBe('not_verified')
    expect(OCTOBER_2027_SOURCE).toMatch(/^https:\/\/www\.monash\.edu\.my\//)
  })
})
