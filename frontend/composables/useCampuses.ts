/**
 * The campuses a filter offers, and what to call them.
 *
 * The filters used to offer Malaysia and Clayton and nothing else, so a
 * Caulfield student - most of business and IT postgraduates - could not ask
 * "is this taught where I study". The values are the Handbook's own campus
 * names, which is what the API filters on; the label goes through the same
 * closed dictionary as every other Handbook value.
 */
export const CAMPUS_CHOICES = ['Malaysia', 'Clayton', 'Caulfield', 'Peninsula', 'Parkville'] as const

export function useCampusName() {
  const { $t, $term } = useNuxtApp()
  return (campus: string | null | undefined): string => {
    if (!campus) return ''
    if (campus === 'Malaysia') return $t('tree.campusMalaysia')
    return $term('campus', campus) ?? campus
  }
}
