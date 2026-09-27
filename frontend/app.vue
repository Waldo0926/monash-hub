<script setup lang="ts">
import { LOCALES } from '~/i18n'

// <html lang> follows the switcher. Screen readers pick pronunciation from it,
// and search engines use it to decide who a page is for.
const { locale } = useLocale()
const htmlLang = computed(
  () => LOCALES.find(option => option.code === locale.value)?.htmlLang ?? 'en'
)
useHead({ htmlAttrs: { lang: htmlLang } })

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
const route = useRoute()
const site = config.public.siteUrl.replace(/\/$/, '')
const image = `${site}/og-image.png`
useSeoMeta({
  ogType: 'website',
  ogSiteName: 'Monash Hub',
  ogUrl: () => `${site}${route.path === '/' ? '' : route.path}`,
  // No site-wide og:title or og:description: a crawler falls back to the
  // page's own <title> and description, which is what a shared unit or guide
  // should show. Written here, they would name every page "Monash Hub". The
  // description below is only the default for a page that sets none.
  description:
    'Units, degrees, WAM/GPA tools, official guides and a student community for Monash students. ' +
    'An independent student platform, not affiliated with Monash University.',
  ogImage: image,
  ogImageSecureUrl: image,
  ogImageType: 'image/png',
  ogImageWidth: 1200,
  ogImageHeight: 630,
  ogImageAlt: 'Monash Hub - units, degrees, official guides and a student community',
  twitterCard: 'summary_large_image',
  twitterImage: image,
  twitterImageAlt: 'Monash Hub - units, degrees, official guides and a student community'
})
useHead({ link: [{ rel: 'apple-touch-icon', href: '/apple-touch-icon.png' }] })
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
