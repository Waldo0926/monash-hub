/**
 * Makes ``$t`` available in every template.
 *
 * It reads the locale ref at call time, so a template that calls ``$t`` tracks
 * the locale as a reactive dependency and re-renders when the switcher changes
 * it. No page reload, no per-component import.
 */
import { translate } from '~/i18n'

export default defineNuxtPlugin(nuxtApp => {
  const { locale } = useLocale()

  const t = (key: string, params?: Record<string, string | number>) =>
    translate(locale.value, key, params)

  nuxtApp.vueApp.config.globalProperties.$t = t
  return { provide: { t } }
})
