/**
 * Sitemap generated from what is actually indexed.
 *
 * Built at request time rather than at build time: the unit and guide lists
 * grow with every crawl, and a sitemap baked into the image would be stale the
 * day after a deploy.
 */
/*
 * Cached for an hour. Building it walks the whole catalogue - some sixty API
 * calls - and a crawler that fetches the sitemap on every visit would
 * otherwise put that load on the API each time.
 */
/** A slug or code is API data; `&` in one would make the whole file invalid. */
function escapeXml(value: string): string {
  return value.replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' } as Record<string, string>
  )[c]!)
}

export default defineCachedEventHandler(async event => {
  const config = useRuntimeConfig()
  const site = config.public.siteUrl.replace(/\/$/, '')
  const api = config.apiBase.replace(/\/$/, '')

  const urls: string[] = [
    '/', '/units', '/courses', '/guides', '/community', '/exchange',
    '/plan', '/tree', '/marks', '/mamo'
  ]

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
    // Degrees were missing entirely, and they are what a prospective student
    // searches for by name.
    for (let offset = 0; ; offset += PAGE) {
      const courses = await $fetch<any>(`${api}/v1/courses?limit=${PAGE}&offset=${offset}`)
      for (const course of courses.results || []) urls.push(`/courses/${course.course_code}`)
      if (offset + PAGE >= (courses.total || 0)) break
    }
    for (let offset = 0; ; offset += PAGE) {
      const posts = await $fetch<any>(`${api}/v1/community/posts?limit=${PAGE}&offset=${offset}`)
      for (const post of posts.results || []) urls.push(`/community/post/${post.id}`)
      if (offset + PAGE >= (posts.total || 0)) break
    }
  } catch (caught) {
    // Not cached, and not served either: a half-walked list cached for an
    // hour tells a crawler most of the site has gone. 503 is "come back".
    console.error('sitemap: API walk failed', caught)
    throw createError({ statusCode: 503, statusMessage: 'Sitemap temporarily unavailable' })
  }

  setHeader(event, 'content-type', 'application/xml; charset=utf-8')
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${[...new Set(urls)].map(path => `  <url><loc>${escapeXml(site + path)}</loc></url>`).join('\n')}
</urlset>
`
}, { maxAge: 60 * 60, name: 'sitemap', getKey: () => 'all' })
