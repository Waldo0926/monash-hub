// Nuxt config.
//
// SSR is on because the public pages have to be shareable and indexable: a unit
// page that only renders after JavaScript is a page that never shows up in a
// search result or a chat preview.
export default defineNuxtConfig({
  compatibilityDate: '2026-08-01',
  ssr: true,
  devtools: { enabled: false },

  runtimeConfig: {
    // Server-side calls go straight to the API container over the private
    // Docker network. Never a public hostname - that would leave the box and
    // come back in through the proxy for no reason.
    apiBase: process.env.NUXT_API_BASE || 'http://localhost:8000/api',
    public: {
      // The browser always uses the same origin, so there is no CORS to
      // configure and no second hostname to keep a certificate for.
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '/api',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://monashhub.secureview.tech',
      // Read-only China mirror switch. Overridden at runtime by
      // NUXT_PUBLIC_CN_READONLY_MODE so one build serves both deployments.
      cnReadonlyMode: process.env.NUXT_PUBLIC_CN_READONLY_MODE === 'true',
      // Optional ICP filing number rendered in the footer once approved.
      icpNumber: process.env.NUXT_PUBLIC_ICP_NUMBER || ''
    }
  },

  css: ['~/assets/css/tokens.css', '~/assets/css/base.css'],

  app: {
    head: {
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'theme-color', content: '#006DAE' },
        // Added to an iPhone home screen, open full screen under this name
        // rather than as a Safari bookmark. Android reads the manifest.
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-title', content: 'Monash Hub' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'default' }
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'manifest', href: '/manifest.webmanifest' }
      ]
    }
  },

  nitro: {
    compressPublicAssets: true
  }
})
