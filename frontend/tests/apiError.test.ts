import { describe, expect, it } from 'vitest'
import { apiErrorMessage } from '../utils/apiError'

const t = (key: string, params?: Record<string, string | number>) =>
  params ? `${key}:${JSON.stringify(params)}` : key

describe('apiErrorMessage', () => {
  it('maps a known API sentence to a key in the reader\'s language', () => {
    const caught = { status: 401, data: { detail: 'Wrong email or password' } }
    expect(apiErrorMessage(caught, t)).toBe('error.wrongPassword')
  })
  it('turns a 429 with Retry-After into minutes', () => {
    const headers = new Headers({ 'retry-after': '150' })
    const caught = { status: 429, response: { status: 429, headers } }
    expect(apiErrorMessage(caught, t)).toBe('error.tooManyWait:{"minutes":3}')
  })
  it('reads the length out of a length sentence', () => {
    const caught = { status: 422, data: { detail: 'Use at least 8 characters.' } }
    expect(apiErrorMessage(caught, t)).toBe('error.tooShort:{"n":"8"}')
  })
  it('shows an unknown sentence as written rather than a vaguer translation', () => {
    const caught = { status: 400, data: { detail: 'Something specific happened' } }
    expect(apiErrorMessage(caught, t)).toBe('Something specific happened')
  })
  it('tells offline from a server error from the fallback', () => {
    expect(apiErrorMessage({}, t)).toBe('state.offline')
    expect(apiErrorMessage({ status: 502 }, t)).toBe('state.serverError')
    expect(apiErrorMessage({ status: 400 }, t, 'community.actionFailed')).toBe('community.actionFailed')
  })
})
