/**
 * Sitemap generated from what is actually indexed.
 *
 * Built at request time rather than at build time: the unit and guide lists
 * grow with every crawl, and a sitemap baked into the image would be stale the
 * day after a deploy.
 */
export default defineEventHandler(async event => {
  const config = useRuntimeConfig()
  const site = config.public.siteUrl.replace(/\/$/, '')
  const api = config.apiBase.replace(/\/$/, '')

  const urls: string[] = ['/', '/units', '/guides', '/community', '/exchange']

  try {
    const units = await $fetch<any>(`${api}/v1/units?limit=1000&sort=code`)
    for (const unit of units.results || []) urls.push(`/units/${unit.unit_code}`)
    const guides = await $fetch<any>(`${api}/v1/guides?limit=200`)
    for (const page of guides.results || []) urls.push(`/guides/${page.slug}`)
  } catch {
    // A sitemap with the static routes beats a 500 if the API is briefly down.
  }

  setHeader(event, 'content-type', 'application/xml; charset=utf-8')
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(path => `  <url><loc>${site}${path}</loc></url>`).join('\n')}
</urlset>
`
})
