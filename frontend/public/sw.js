/*
 * Service worker for the installed app (and for any browser that visits).
 *
 * What it is for: a student who added Monash Hub to their home screen can open
 * the unit, degree and guide pages they have already read when there is no
 * signal. That is all. It is not a way to make the site faster online, and it
 * must never make a student read something older than what the server has.
 *
 * So every page and API call goes to the network first. A saved copy is used
 * only when the network cannot be reached at all; a 404 or a 500 from the
 * server is passed through as it is, and only a 200 is ever saved. Anything
 * live or personal - accounts, community, ratings, notifications, search, the
 * assistant - is never saved and never answered from a saved copy.
 *
 * Built files under /_nuxt/ have a hash in their name, so a saved copy of one
 * is the same file forever and can be served straight from the cache. The one
 * exception is /_nuxt/builds/, which is how Nuxt notices a new deploy and must
 * always come from the network.
 *
 * Bump VERSION when the caching rules change. The new worker deletes every
 * cache the old one made, so nothing saved under old rules survives.
 */
const VERSION = 'v1'
const SHELL = `mh-shell-${VERSION}`
const PAGES = `mh-pages-${VERSION}`
const API = `mh-api-${VERSION}`
const ASSETS = `mh-assets-${VERSION}`

const OFFLINE_PAGE = '/offline.html'
const SHELL_FILES = [OFFLINE_PAGE, '/favicon.svg', '/icons/icon-192.png']

/* Oldest entries go first once a cache is past its limit. */
const LIMITS = { [PAGES]: 80, [API]: 300, [ASSETS]: 200 }

/*
 * Pages worth reading offline: reference material that changes at most with a
 * crawl. The planner, tree and marks calculator keep their data in the browser,
 * so their page is enough to use them offline too.
 */
const OFFLINE_PAGES = [
  /^\/$/,
  /^\/units(\/[^/]+)?\/?$/,
  /^\/courses(\/aos)?(\/[^/]+)?\/?$/,
  /^\/guides(\/[^/]+)?\/?$/,
  /^\/(mamo|exchange|plan|plans|tree|marks)\/?$/
]

/* The API calls those pages make. Reviews, community, auth and search are left out on purpose. */
const OFFLINE_API = [
  /^\/api\/v1\/units(\/|$)/,
  /^\/api\/v1\/courses(\/|$)/,
  /^\/api\/v1\/guides(\/|$)/,
  /^\/api\/v1\/(faq|key-dates)$/,
  /^\/api\/v1\/exchange$/,
  /^\/api\/v1\/marks\/(reference|units)$/
]

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(SHELL)
      .then(cache => cache.addAll(SHELL_FILES))
      .then(() => self.skipWaiting())
  )
})

self.addEventListener('activate', event => {
  const keep = new Set([SHELL, PAGES, API, ASSETS])
  event.waitUntil(
    caches.keys()
      .then(names => Promise.all(names.filter(n => n.startsWith('mh-') && !keep.has(n)).map(n => caches.delete(n))))
      .then(() => self.clients.claim())
  )
})

self.addEventListener('message', event => {
  // A saved page is in the language it was rendered in. When the reader
  // switches language, the saved pages are in the wrong one, so they go.
  // API answers carry the locale in their URL and can stay.
  if (event.data?.type === 'locale-changed') event.waitUntil(caches.delete(PAGES))
})

self.addEventListener('fetch', event => {
  const request = event.request
  if (request.method !== 'GET') return
  const url = new URL(request.url)
  if (url.origin !== self.location.origin) return

  if (request.mode === 'navigate') {
    const saveable = OFFLINE_PAGES.some(re => re.test(url.pathname))
    event.respondWith(page(event, saveable))
    return
  }
  if (url.pathname.startsWith('/_nuxt/builds/')) return
  if (url.pathname.startsWith('/_nuxt/')) {
    event.respondWith(cacheFirst(event, ASSETS))
    return
  }
  if (OFFLINE_API.some(re => re.test(url.pathname))) {
    event.respondWith(networkFirst(event, API))
  }
})

async function page(event, saveable) {
  try {
    const response = await fetch(event.request)
    if (saveable) save(event, PAGES, response)
    return response
  } catch (error) {
    if (saveable) {
      const saved = await caches.open(PAGES).then(cache => cache.match(event.request))
      if (saved) return saved
    }
    const offline = await caches.match(OFFLINE_PAGE)
    if (offline) return offline
    throw error
  }
}

async function networkFirst(event, cacheName) {
  try {
    const response = await fetch(event.request)
    save(event, cacheName, response)
    return response
  } catch (error) {
    const saved = await caches.open(cacheName).then(cache => cache.match(event.request))
    if (saved) return saved
    throw error
  }
}

async function cacheFirst(event, cacheName) {
  const saved = await caches.open(cacheName).then(cache => cache.match(event.request))
  if (saved) return saved
  const response = await fetch(event.request)
  save(event, cacheName, response)
  return response
}

/** Only a complete, successful, same-origin answer is worth keeping. */
function save(event, cacheName, response) {
  if (response.status !== 200 || response.type !== 'basic') return
  if ((response.headers.get('Cache-Control') || '').includes('no-store')) return
  const copy = response.clone()
  event.waitUntil(
    caches.open(cacheName)
      .then(cache => cache.put(event.request, copy).then(() => trim(cache, LIMITS[cacheName])))
      .catch(() => {})
  )
}

async function trim(cache, limit) {
  if (!limit) return
  const keys = await cache.keys()
  await Promise.all(keys.slice(0, Math.max(0, keys.length - limit)).map(key => cache.delete(key)))
}
