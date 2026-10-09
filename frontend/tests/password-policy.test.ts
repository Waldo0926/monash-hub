import { describe, expect, it } from 'vitest'
import { emailLooksValid, nicknameProblem, passwordProblem } from '../utils/password-policy'

describe('passwordProblem', () => {
  it('wants eight characters', () => {
    expect(passwordProblem('Ab1')).toBe('auth.errPasswordShort')
  })
  it('wants two character classes', () => {
    expect(passwordProblem('alllowercase')).toBe('auth.errPasswordClasses')
    expect(passwordProblem('Mixed-case')).toBeNull()
  })
  it('refuses a password built from the nickname or the email', () => {
    expect(passwordProblem('quietfox-Rules-1', ['quietfox'])).toBe('auth.errPasswordSimilar')
    expect(passwordProblem('quietfox-Rules-1', ['quietfox@example.com'])).toBe('auth.errPasswordSimilar')
    expect(passwordProblem('Brand-New-Pass-7', ['quietfox'])).toBeNull()
  })
  it('ignores avoid terms shorter than three characters', () => {
    expect(passwordProblem('Ab-Password-9', ['ab'])).toBeNull()
  })
})

describe('nicknameProblem', () => {
  it('bounds the length', () => {
    expect(nicknameProblem('ab')).toBe('auth.errNicknameShort')
    expect(nicknameProblem('a'.repeat(49))).toBe('auth.errNicknameLong')
  })
  it('allows letters in any script and three separators', () => {
    expect(nicknameProblem('王小明_2026')).toBeNull()
    expect(nicknameProblem('wal.do-26')).toBeNull()
    expect(nicknameProblem('wal do')).toBe('auth.errNicknameChars')
  })
})

describe('emailLooksValid', () => {
  it('accepts an ordinary address and refuses the obvious', () => {
    expect(emailLooksValid(' someone@student.monash.edu ')).toBe(true)
    expect(emailLooksValid('someone@')).toBe(false)
    expect(emailLooksValid('no at sign')).toBe(false)
  })
})
