/**
 * The current interface language.
 *
 * Resolved once on the server - cookie first, then the browser's
 * Accept-Language - and handed to the client through Nuxt state, so the markup
 * matches on both sides. Getting this wrong is a hydration mismatch, and this
 * app has already paid for one of those.
 */
import { DEFAULT_LOCALE, isLocale, matchLocale, type LocaleCode } from '~/i18n'

const COOKIE = 'mh_locale'
const YEAR_SECONDS = 60 * 60 * 24 * 365

export function useLocale() {
  const cookie = useCookie<string | null>(COOKIE, {
    maxAge: YEAR_SECONDS,
    sameSite: 'lax',
    path: '/'
  })

  const locale = useState<LocaleCode>('locale', () => {
    if (isLocale(cookie.value)) return cookie.value
    if (import.meta.server) {
      const header = useRequestHeaders(['accept-language'])['accept-language']
      const guessed = matchLocale(header)
      if (guessed) return guessed
    }
    return DEFAULT_LOCALE
  })

  function setLocale(next: LocaleCode) {
    if (!isLocale(next) || next === locale.value) return
    locale.value = next
    cookie.value = next
  }

  return { locale, setLocale }
}
