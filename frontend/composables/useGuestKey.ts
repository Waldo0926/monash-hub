/**
 * The key a signed-out browser rates with.
 *
 * Rating a unit does not need an account. Instead the browser makes up a
 * random key the first time it rates, keeps it in localStorage, and sends it
 * with every rating call, so it can change or remove its rating later. It is
 * not a login and proves nothing about who someone is; the API limits
 * signed-out ratings per network as well (see backend/app/api/v1/reviews.py).
 */
export const GUEST_KEY = 'mh_guest_key'

export function readGuestKey(): string | null {
  if (!import.meta.client) return null
  try {
    return window.localStorage.getItem(GUEST_KEY)
  } catch {
    return null
  }
}

function makeGuestKey(): string | null {
  const key = typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : Array.from({ length: 4 }, () => Math.random().toString(16).slice(2, 10)).join('-')
  try {
    window.localStorage.setItem(GUEST_KEY, key)
    return key
  } catch {
    // No storage: the rating still saves, it just cannot be edited from here later.
    return key
  }
}

/** The header for a signed-out rating call, making the key on the first write. */
export function guestHeaders(create = false): Record<string, string> {
  if (!import.meta.client || readToken()) return {}
  const key = readGuestKey() ?? (create ? makeGuestKey() : null)
  return key ? { 'X-Guest-Key': key } : {}
}
