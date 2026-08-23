/**
 * The unread badge in the header.
 *
 * Polled rather than pushed: a WebSocket for a number that changes a few times
 * a day would mean a connection per open tab for the entire session, and the
 * count endpoint is a single indexed count. Polling stops while the tab is
 * hidden, so a forgotten tab costs nothing.
 */
const POLL_MS = 60_000

export function useNotifications() {
  const unread = useState<number>('notifications-unread', () => 0)
  const timer = useState<number | null>('notifications-timer', () => null)

  async function refresh() {
    if (!import.meta.client || !localStorage.getItem('mh_token')) {
      unread.value = 0
      return
    }
    try {
      const result = await apiFetch<{ unread: number }>('/v1/notifications/unread-count')
      unread.value = result.unread
    } catch {
      // An expired session or a blip should not put an error in the header.
      unread.value = 0
    }
  }

  function start() {
    if (!import.meta.client || timer.value !== null) return
    refresh()
    timer.value = window.setInterval(() => {
      if (document.visibilityState === 'visible') refresh()
    }, POLL_MS)
  }

  function stop() {
    if (timer.value !== null) {
      clearInterval(timer.value)
      timer.value = null
    }
  }

  return { unread, refresh, start, stop }
}
