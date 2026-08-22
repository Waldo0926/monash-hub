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

/** SSR-friendly GET. Errors surface to the caller so pages can show a real
 *  error state instead of a blank screen. */
export function useApiFetch<T>(path: string | (() => string), options: Record<string, any> = {}) {
  const url = typeof path === 'function' ? computed(() => apiUrl(path())) : apiUrl(path)
  return useFetch<T>(url as any, { ...options, key: typeof path === 'function' ? undefined : path })
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
