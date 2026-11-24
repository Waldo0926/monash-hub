export function useSectionNavigation() {
  const { $t } = useNuxtApp()
  const { cnReadonly } = useSiteMode()

  return computed(() => {
    const items = [
      { to: '/guides', label: $t('nav.guides'), icon: '□' },
      { to: '/units', label: $t('nav.units'), icon: '▤' },
      { to: '/courses', label: $t('nav.courses'), icon: '◇' },
      { to: '/plan', label: $t('nav.plan'), icon: '☷' },
      { to: '/tree', label: $t('nav.tree'), icon: '⑂' },
      { to: '/marks', label: $t('nav.marks'), icon: '%' },
      { to: '/mamo', label: $t('nav.mamo'), icon: 'M' }
    ]
    if (!cnReadonly.value) {
      items.push({ to: '/community', label: $t('nav.community'), icon: '☰' })
    }
    return items
  })
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
  const { cnReadonly } = useSiteMode()

  return computed<HeaderNavItem[]>(() => {
    const items: HeaderNavItem[] = [
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
      { to: '/mamo', label: $t('nav.mamo') }
    ]
    if (!cnReadonly.value) {
      items.push({ to: '/community', label: $t('nav.community') })
    }
    return items
  })
}
