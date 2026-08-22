/**
 * Minimal client-side session.
 *
 * Anonymous reading is the default, so this only exists to decide whether to
 * show a compose box or a sign-in prompt. The token lives in localStorage and
 * every write goes through apiFetch, which attaches it.
 */
export type SessionUser = { id: number; nickname: string; email: string; is_admin: boolean }

export function useAuth() {
  const user = useState<SessionUser | null>('auth-user', () => null)
  const ready = useState<boolean>('auth-ready', () => false)

  async function restore() {
    if (!import.meta.client || ready.value) return
    ready.value = true
    if (!localStorage.getItem('mh_token')) return
    try {
      user.value = await apiFetch<SessionUser>('/v1/auth/me')
    } catch {
      // An expired or tampered token is not an error worth showing anyone.
      localStorage.removeItem('mh_token')
      user.value = null
    }
  }

  async function signIn(email: string, password: string) {
    const result = await apiFetch<{ token: string; user: SessionUser }>('/v1/auth/signin', {
      method: 'POST',
      body: { email, password }
    })
    localStorage.setItem('mh_token', result.token)
    user.value = result.user
  }

  async function signUp(email: string, nickname: string, password: string) {
    const result = await apiFetch<{ token: string; user: SessionUser }>('/v1/auth/signup', {
      method: 'POST',
      body: { email, nickname, password }
    })
    localStorage.setItem('mh_token', result.token)
    user.value = result.user
  }

  function signOut() {
    localStorage.removeItem('mh_token')
    user.value = null
  }

  return { user, restore, signIn, signUp, signOut }
}
