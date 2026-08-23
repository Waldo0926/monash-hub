/**
 * Minimal client-side session.
 *
 * Anonymous reading is the default, so this exists only to decide whether to
 * show a compose box or a sign-in prompt. The token lives in localStorage and
 * every write goes through apiFetch, which attaches it.
 */
export type SessionUser = { id: number; nickname: string; email: string; is_admin: boolean }

const TOKEN_KEY = 'mh_token'

export function useAuth() {
  const user = useState<SessionUser | null>('auth-user', () => null)
  const ready = useState<boolean>('auth-ready', () => false)

  function applySession(token: string, account: SessionUser) {
    localStorage.setItem(TOKEN_KEY, token)
    user.value = account
    ready.value = true
  }

  async function restore() {
    if (!import.meta.client || ready.value) return
    ready.value = true
    if (!localStorage.getItem(TOKEN_KEY)) return
    try {
      user.value = await apiFetch<SessionUser>('/v1/auth/me')
    } catch {
      // An expired token, or one issued before a password reset, is not an
      // error worth showing anyone - it just means signed out.
      localStorage.removeItem(TOKEN_KEY)
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
    localStorage.removeItem(TOKEN_KEY)
    user.value = null
    const { unread } = useNotifications()
    unread.value = 0
  }

  return { user, ready, restore, signIn, signOut, applySession }
}
