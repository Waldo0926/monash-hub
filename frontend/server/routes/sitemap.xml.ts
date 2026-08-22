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

  // The API caps a page at 100 results, so walk it rather than asking for
  // everything at once - which silently 422s and leaves the sitemap empty.
  const PAGE = 100

  try {
    for (let offset = 0; ; offset += PAGE) {
      const units = await $fetch<any>(`${api}/v1/units?limit=${PAGE}&offset=${offset}&sort=code`)
      for (const unit of units.results || []) urls.push(`/units/${unit.unit_code}`)
      if (offset + PAGE >= (units.total || 0)) break
    }
    for (let offset = 0; ; offset += PAGE) {
      const guides = await $fetch<any>(`${api}/v1/guides?limit=${PAGE}&offset=${offset}`)
      for (const page of guides.results || []) urls.push(`/guides/${page.slug}`)
      if (offset + PAGE >= (guides.total || 0)) break
    }
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
