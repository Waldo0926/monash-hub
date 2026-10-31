export function useSectionNavigation() {
  const { $t } = useNuxtApp()

  return computed(() => [
    { to: '/guides', label: $t('nav.guides'), icon: '□' },
    { to: '/units', label: $t('nav.units'), icon: '▤' },
    { to: '/courses', label: $t('nav.courses'), icon: '◇' },
    { to: '/plan', label: $t('nav.plan'), icon: '☷' },
    { to: '/tree', label: $t('nav.tree'), icon: '⑂' },
    { to: '/marks', label: $t('nav.marks'), icon: '%' },
    { to: '/mamo', label: $t('nav.mamo'), icon: 'M' },
    { to: '/community', label: $t('nav.community'), icon: '☰' }
  ])
}

export interface HeaderNavItem {
  to?: string
  label: string
  children?: { to: string; label: string }[]
}

/**
 * The desktop header, six entries instead of eight. Degrees keep their own
 * place: put under units, students who want to see what degrees exist never
 * find them. The three planning tools share one menu.
 */
export function useHeaderNavigation() {
  const { $t } = useNuxtApp()

  return computed<HeaderNavItem[]>(() => [
    { to: '/units', label: $t('nav.units') },
    { to: '/courses', label: $t('nav.courses') },
    {
      label: $t('nav.tools'),
      children: [
        { to: '/plan', label: $t('nav.plan') },
        { to: '/tree', label: $t('nav.tree') },
        { to: '/marks', label: $t('nav.marks') }
      ]
    },
    { to: '/guides', label: $t('nav.guides') },
    { to: '/mamo', label: $t('nav.mamo') },
    { to: '/community', label: $t('nav.community') }
  ])
}
