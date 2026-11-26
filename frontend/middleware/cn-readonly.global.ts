/**
 * Block interactive / UGC / account routes when running in China read-only mode.
 *
 * Returning a 404 error in global middleware stops direct URL hits during both
 * SSR and client-side navigation, matching the backend's 403/404 API guard.
 */
const BLOCKED_PREFIXES = [
  '/community',
  '/login',
  '/register',
  '/forgot-password',
  '/auth',
  '/profile',
  '/notifications',
  '/moderation'
]

function isBlockedInReadonly(path: string): boolean {
  const clean = path.replace(/\/+$/, '') || '/'
  return BLOCKED_PREFIXES.some(prefix => clean === prefix || clean.startsWith(`${prefix}/`))
}

export default defineNuxtRouteMiddleware((to) => {
  const { cnReadonly } = useSiteMode()
  if (cnReadonly.value && isBlockedInReadonly(to.path)) {
    return abortNavigation(createError({ statusCode: 404, statusMessage: 'Page not found' }))
  }
})
