/**
 * One place that knows how to reach the API.
 *
 * On the server we call the API container directly over the private Docker
 * network; in the browser we call the same origin under /api. Components just
 * ask for a path and never think about which side they are running on.
 */
export function useApiBase(): string {
  const config = useRuntimeConfig()
  return import.meta.server ? config.apiBase : config.public.apiBase
}

export function apiUrl(path: string): string {
  const base = useApiBase().replace(/\/$/, '')
  return `${base}${path.startsWith('/') ? path : `/${path}`}`
}

/**
 * SSR-friendly GET.
 *
 * The key is derived from the API *path*, never from the resolved URL. Those
 * two are not the same string on both sides - the server calls
 * `http://api:8000/api/...` over the private network while the browser calls
 * `/api/...` on the same origin - and a URL-derived key means the server's
 * payload is filed under a name the client never looks up. The client then
 * hydrates with `data` still null, renders a different tree than the server
 * sent, and Vue throws the server's markup away.
 *
 * Errors surface to the caller so pages can show a real error state rather than
 * a blank screen.
 */
export function useApiFetch<T>(path: string | (() => string), options: Record<string, any> = {}) {
  const resolve = typeof path === 'function' ? path : () => path
  // The key includes whatever the path resolves to right now, locale and all,
  // so two languages never share one cache entry. Changes after setup are what
  // the caller's `watch` is for.
  const key = options.key ?? `api:${resolve()}`
  return useFetch<T>(() => apiUrl(resolve()), {
    ...options,
    key,
    // The token lives in localStorage, which the server cannot read, so this
    // is empty during SSR and filled on the client. That is on purpose: the
    // server renders the page as a signed-out reader sees it, and a caller
    // that needs the signed-in view refreshes after mount. Sending it during
    // SSR is not possible; pretending otherwise is a hydration mismatch.
    headers: {
      ...(options.headers || {}),
      ...(import.meta.client && localStorage.getItem('mh_token')
        ? { Authorization: `Bearer ${localStorage.getItem('mh_token')}` }
        : {})
    }
  })
}

/**
 * The same GET, asking for the reader's language.
 *
 * The locale rides in the query string rather than in a header. Three reasons,
 * and the first two are the ones that bite: the SSR fetch and the client fetch
 * have to agree on the cache key or the page hydrates against a different
 * payload than it rendered with, and a header that varies per browser is a poor
 * cache key for a page that is otherwise identical for everyone. The third is
 * that it makes a translated page linkable.
 *
 * The locale is also watched explicitly. Putting `locale.value` in the URL getter
 * is not enough on its own: the cache key is fixed when the composable is set
 * up, so Nuxt keeps handing back the payload it already has and the page ends
 * up with English chrome around Chinese content - which is exactly what a
 * reader sees when they switch language and nothing happens.
 */
export function useLocalisedApiFetch<T>(
  path: string | (() => string),
  options: Record<string, any> = {}
) {
  const { locale } = useLocale()
  const resolve = typeof path === 'function' ? path : () => path
  const watch = options.watch === false ? false : [locale, ...(options.watch ?? [])]
  return useApiFetch<T>(
    () => {
      const resolved = resolve()
      return `${resolved}${resolved.includes('?') ? '&' : '?'}locale=${locale.value}`
    },
    { ...options, watch },
  )
}

/** Imperative call, for form submissions and other browser-side actions. */
export function apiFetch<T>(path: string, options: Record<string, any> = {}): Promise<T> {
  const token = import.meta.client ? localStorage.getItem('mh_token') : null
  return $fetch<T>(apiUrl(path), {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    }
  })
}
