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
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://monashhub.secureview.tech'
    }
  },

  css: ['~/assets/css/tokens.css', '~/assets/css/base.css'],

  app: {
    head: {
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'theme-color', content: '#17365D' }
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap'
        }
      ]
    }
  },

  nitro: {
    compressPublicAssets: true
  }
})
