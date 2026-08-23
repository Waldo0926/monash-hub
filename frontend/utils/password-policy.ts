/**
 * The same password rule the API enforces, restated for the browser.
 *
 * Duplicated on purpose: the server's copy is the one that decides, and this
 * one exists only so a person is told what is wrong while they are still
 * looking at the field, rather than after a round trip. If the two ever
 * disagree, the server wins and the form shows its message.
 */
export const PASSWORD_MIN_LENGTH = 8

export function passwordProblem(password: string, avoid: string[] = []): string | null {
  if (password.length < PASSWORD_MIN_LENGTH) return 'auth.errPasswordShort'

  const classes = [
    /[a-z]/.test(password),
    /[A-Z]/.test(password),
    /\d/.test(password),
    /[^A-Za-z0-9]/.test(password)
  ].filter(Boolean).length
  if (classes < 2) return 'auth.errPasswordClasses'

  const lowered = password.toLowerCase()
  for (const raw of avoid) {
    const term = (raw || '').trim().toLowerCase().split('@')[0]!
    if (term.length >= 3 && lowered.includes(term)) return 'auth.errPasswordSimilar'
  }
  return null
}

export const NICKNAME_MIN_LENGTH = 3
export const NICKNAME_MAX_LENGTH = 48
// Mirrors the server: letters in any script, digits, and three separators.
const NICKNAME_PATTERN = /^[\p{L}\p{N}_.\-]+$/u

export function nicknameProblem(nickname: string): string | null {
  const value = nickname.trim()
  if (value.length < NICKNAME_MIN_LENGTH) return 'auth.errNicknameShort'
  if (value.length > NICKNAME_MAX_LENGTH) return 'auth.errNicknameLong'
  if (!NICKNAME_PATTERN.test(value)) return 'auth.errNicknameChars'
  return null
}

export function emailLooksValid(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())
}
