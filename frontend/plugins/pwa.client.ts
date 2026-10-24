/**
 * Registers the service worker (public/sw.js) and keeps an installed app up to date.
 *
 * Updates: pages and the API always come from the network first, so a new
 * deploy shows up on the next page load. The case left is an app that stays
 * open on a phone for days. Nuxt already reloads on the next navigation once
 * it sees a new build, but it only looks once an hour, and a phone pauses
 * timers while the app is in the background. So it also looks whenever the
 * app comes back to the front, and asks the browser to check sw.js too.
 *
 * Offline: a link followed inside the app would fetch its data from the API,
 * and only some of that is saved. A full page load instead gets the saved page
 * from the service worker, or the offline page, so that is what an offline
 * navigation does.
 */
export default defineNuxtPlugin(nuxtApp => {
  window.addEventListener('beforeinstallprompt', rememberInstallPrompt)
  window.addEventListener('appinstalled', markInstalled)

  if (!('serviceWorker' in navigator) || import.meta.dev) return

  let registration: ServiceWorkerRegistration | undefined
  onNuxtReady(async () => {
    try {
      registration = await navigator.serviceWorker.register('/sw.js')
    } catch {
      // Private mode, a blocked worker, an old browser: the site still works.
    }
  })

  const { locale } = useLocale()
  watch(locale, () => {
    navigator.serviceWorker.controller?.postMessage({ type: 'locale-changed' })
  })

  let newBuildSeen = false
  let lastCheck = Date.now()
  nuxtApp.hook('app:manifest:update', () => { newBuildSeen = true })

  async function checkForNewBuild() {
    // Switching back and forth between apps should not mean a request each time.
    if (newBuildSeen || Date.now() - lastCheck < 5 * 60_000) return
    lastCheck = Date.now()
    registration?.update().catch(() => {})
    try {
      const [current, latest] = await Promise.all([
        getAppManifest(),
        $fetch<{ id: string }>(`/_nuxt/builds/latest.json?${Date.now()}`)
      ])
      if (latest.id && latest.id !== current.id) {
        await nuxtApp.hooks.callHook('app:manifest:update', latest as any)
      }
    } catch {
      // Offline, or a build without a manifest: try again next time.
    }
  }
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') checkForNewBuild()
  })

  useRouter().beforeEach((to, from) => {
    if (navigator.onLine || !from.matched.length || to.path === from.path) return
    window.location.assign(to.fullPath)
    return false
  })
})
