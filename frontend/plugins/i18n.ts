/**
 * Makes ``$t`` and ``$term`` available in every template.
 *
 * Both read the locale ref at call time, so a template that calls either one
 * tracks the locale as a reactive dependency and re-renders when the switcher
 * changes it. No page reload, no per-component import.
 *
 * The two are not the same thing and the difference matters:
 *
 * - ``$t`` translates *our* interface. The key names a string we wrote.
 * - ``$term`` translates a value that came from the Handbook - a campus, a
 *   teaching period, an assessment type. It is a dictionary lookup over the
 *   Handbook's own closed vocabulary, and anything not in that dictionary comes
 *   back in the language Monash published it in.
 */
import { translate } from '~/i18n'
import { assessmentName, handbookTerm, type TermKind } from '~/i18n/handbook-terms'

export default defineNuxtPlugin(nuxtApp => {
  const { locale } = useLocale()

  const t = (key: string, params?: Record<string, string | number>) =>
    translate(locale.value, key, params)

  const term = (kind: TermKind, value: string | null | undefined) =>
    handbookTerm(kind, value, locale.value)

  const assessment = (value: string | null | undefined) => assessmentName(value, locale.value)

  nuxtApp.vueApp.config.globalProperties.$t = t
  nuxtApp.vueApp.config.globalProperties.$term = term
  nuxtApp.vueApp.config.globalProperties.$assessmentName = assessment
  return { provide: { t, term, assessmentName: assessment } }
})
