/**
 * Dynamic robots.txt so each deployment points crawlers at its own Sitemap URL
 * and omits disabled routes in China read-only mode.
 */
export default defineEventHandler((event) => {
  const config = useRuntimeConfig()
  const site = config.public.siteUrl.replace(/\/$/, '')
  const rawMode: unknown = config.public.cnReadonlyMode
  const cnReadonly = rawMode === true || rawMode === 'true' || rawMode === '1'

  const lines = [
    '# Public pages are meant to be indexed; account and search pages are not.',
    'User-agent: *',
    'Allow: /',
    'Disallow: /login',
    'Disallow: /register',
    'Disallow: /forgot-password',
    'Disallow: /profile',
    'Disallow: /notifications',
    'Disallow: /moderation',
    'Disallow: /search',
    ...(cnReadonly ? ['Disallow: /community'] : []),
    '',
    `Sitemap: ${site}/sitemap.xml`,
    ''
  ]

  setHeader(event, 'content-type', 'text/plain; charset=utf-8')
  return lines.join('\n')
})
