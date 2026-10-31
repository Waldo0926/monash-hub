import type { Ref } from 'vue'

/**
 * Give a page whose data did not load the status it deserves.
 *
 * The detail pages render an error card for a unit, guide, degree or post the
 * API does not have, but the response itself said 200, so a search engine
 * indexed /units/NOPE1234 as a real page and kept it. The card stays; the
 * status code now says what it is.
 */
export function useErrorStatus(error: Ref<any>) {
  if (!import.meta.server) return
  const status = Number(error.value?.statusCode ?? error.value?.status ?? 0)
  const event = useRequestEvent()
  if (!event || !status) return
  if (status === 404) setResponseStatus(event, 404)
  else if (status >= 500) setResponseStatus(event, 503)
}
