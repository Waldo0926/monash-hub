/**
 * Minimal client-side session.
 *
 * Anonymous reading is the default, so this exists only to decide whether to
 * show a compose box or a sign-in prompt. The token lives in localStorage and
 * every write goes through apiFetch, which attaches it.
 */
export type SessionUser = {
  id: number
  nickname: string
  email: string
  is_admin: boolean
  avatar_url?: string | null
}

export const TOKEN_KEY = 'mh_token'

/**
 * Storage access is wrapped because Safari in private mode and a browser with
 * site data blocked throw on the read itself, and every page that fetches
 * went down with it.
 */
export function readToken(): string | null {
  if (!import.meta.client) return null
  try {
    return window.localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

function writeToken(token: string | null) {
  try {
    if (token === null) window.localStorage.removeItem(TOKEN_KEY)
    else window.localStorage.setItem(TOKEN_KEY, token)
  } catch {
    /* no storage means the session lasts until the tab closes */
  }
}

export function useAuth() {
  const user = useState<SessionUser | null>('auth-user', () => null)
  const ready = useState<boolean>('auth-ready', () => false)

  function applySession(token: string, account: SessionUser) {
    writeToken(token)
    user.value = account
    ready.value = true
  }

  async function restore() {
    if (!import.meta.client || ready.value) return
    ready.value = true
    if (!readToken()) return
    try {
      user.value = await apiFetch<SessionUser>('/v1/auth/me')
    } catch {
      // An expired token, or one issued before a password reset, is not an
      // error worth showing anyone - it just means signed out.
      writeToken(null)
      user.value = null
    }
  }

  async function signIn(email: string, password: string) {
    const result = await apiFetch<{ token: string; user: SessionUser }>('/v1/auth/signin', {
      method: 'POST',
      body: { email, password }
    })
    applySession(result.token, result.user)
  }

  function signOut() {
    writeToken(null)
    user.value = null
    const { unread } = useNotifications()
    unread.value = 0
  }

  return { user, ready, restore, signIn, signOut, applySession }
}
