/**
 * Web app manifest, in the reader's language.
 *
 * Served by a route rather than from public/ so the description and the
 * shortcuts on the home-screen icon match the language the site is shown in.
 * Same order as the pages: the language cookie, then Accept-Language.
 * The name stays "Monash Hub" in every language, the same as the header.
 */
import { DEFAULT_LOCALE, LOCALES, isLocale, matchLocale, translate } from '~/i18n'

export default defineEventHandler(event => {
  const cookie = getCookie(event, 'mh_locale')
  const locale = isLocale(cookie)
    ? cookie
    : matchLocale(getRequestHeader(event, 'accept-language')) ?? DEFAULT_LOCALE
  const t = (key: string) => translate(locale, key)

  setResponseHeaders(event, {
    'Content-Type': 'application/manifest+json; charset=utf-8',
    'Cache-Control': 'no-cache',
    Vary: 'Cookie, Accept-Language'
  })

  const shortcut = (key: string, url: string) => ({
    name: t(key),
    url,
    icons: [{ src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' }]
  })

  return {
    id: '/',
    name: 'Monash Hub',
    short_name: 'Monash Hub',
    description: t('pwa.description'),
    lang: LOCALES.find(option => option.code === locale)?.htmlLang ?? 'en',
    start_url: '/',
    scope: '/',
    display: 'standalone',
    orientation: 'any',
    background_color: '#fcfcfd',
    theme_color: '#006DAE',
    categories: ['education'],
    icons: [
      { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
      { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
      { src: '/icons/maskable-192.png', sizes: '192x192', type: 'image/png', purpose: 'maskable' },
      { src: '/icons/maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
    ],
    shortcuts: [
      shortcut('nav.units', '/units'),
      shortcut('nav.courses', '/courses'),
      shortcut('nav.guides', '/guides'),
      shortcut('nav.plan', '/plan')
    ]
  }
})
