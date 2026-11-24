<script setup lang="ts">
import { LOCALES } from '~/i18n'

// <html lang> follows the switcher. Screen readers pick pronunciation from it,
// and search engines use it to decide who a page is for.
const { locale } = useLocale()
const htmlLang = computed(
  () => LOCALES.find(option => option.code === locale.value)?.htmlLang ?? 'en'
)
useHead({ htmlAttrs: { lang: htmlLang } })

// Every tab reads "Page | Monash Hub", the way most sites name their tabs, so a
// row of open tabs still says which site each one is. Pages set only their own
// name. A title that already has the site name in it (the home page, "Search
// Monash Hub") is left alone, and a page with no title gets just the site name.
useHead({
  titleTemplate: (title?: string) =>
    !title ? 'Monash Hub' : title.includes('Monash Hub') ? title : `${title} | Monash Hub`
})

/*
 * Link previews - LinkedIn, WhatsApp, WeChat, Slack, X.
 *
 * Pages set their own title and description; these are the parts every page
 * shares, and the ones a preview cannot be drawn without. LinkedIn in
 * particular shows a bare link when there is no og:image, and it will not use
 * an SVG, so the card is a PNG made for the 1200x630 slot the crawlers ask
 * for. Every URL here is absolute: a crawler does not resolve relative ones.
 */
const config = useRuntimeConfig()
const { cnReadonly } = useSiteMode()
const route = useRoute()
const site = config.public.siteUrl.replace(/\/$/, '')
const image = `${site}/og-image.png`
const defaultDescription = cnReadonly.value
  ? 'Units, degrees, WAM/GPA tools and official guides for Monash students. ' +
    'An independent student platform, not affiliated with Monash University.'
  : 'Units, degrees, WAM/GPA tools, official guides and a student community for Monash students. ' +
    'An independent student platform, not affiliated with Monash University.'
const defaultImageAlt = cnReadonly.value
  ? 'Monash Hub - units, degrees and official guides'
  : 'Monash Hub - units, degrees, official guides and a student community'

useSeoMeta({
  ogType: 'website',
  ogSiteName: 'Monash Hub',
  ogUrl: () => `${site}${route.path === '/' ? '' : route.path}`,
  // No site-wide og:title or og:description: a crawler falls back to the
  // page's own <title> and description, which is what a shared unit or guide
  // should show. Written here, they would name every page "Monash Hub". The
  // description below is only the default for a page that sets none.
  description: defaultDescription,
  ogImage: image,
  ogImageSecureUrl: image,
  ogImageType: 'image/png',
  ogImageWidth: 1200,
  ogImageHeight: 630,
  ogImageAlt: defaultImageAlt,
  twitterCard: 'summary_large_image',
  twitterImage: image,
  twitterImageAlt: defaultImageAlt
})

// Load Google Fonts only outside China read-only mode; CN visitors fall back
// immediately to local system CJK/Latin fonts with zero blocked third-party calls.
useHead({
  link: cnReadonly.value
    ? [{ rel: 'apple-touch-icon', href: '/apple-touch-icon.png' }]
    : [
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@500;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap'
        }
      ]
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
