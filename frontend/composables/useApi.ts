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
  const key = options.key ?? `api:${resolve()}`
  return useFetch<T>(() => apiUrl(resolve()), { ...options, key })
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
