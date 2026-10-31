import { describe, expect, it } from 'vitest'
import { MESSAGES } from '../i18n'

// Chinese UI copy on this site does not end with 。: one-line hints, labels and
// short notes read stiff with it. Sentences inside a longer message are fine.
describe('Chinese interface copy', () => {
  it('has no message ending with 。', () => {
    const ending = Object.entries(MESSAGES.zh)
      .filter(([, text]) => typeof text === 'string' && text.trimEnd().endsWith('。'))
      .map(([key]) => key)
    expect(ending).toEqual([])
  })
})
