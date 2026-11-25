export function useSectionNavigation() {
  const { $t } = useNuxtApp()
  const { cnReadonly } = useSiteMode()
  const { locale } = useLocale()
  const electivesLabel = computed(() => (locale.value === 'zh' ? '找选修课' : 'Electives'))

  return computed(() => {
    const items = [
      { to: '/guides', label: $t('nav.guides'), icon: '□' },
      { to: '/units', label: $t('nav.units'), icon: '▤' },
      { to: '/courses', label: $t('nav.courses'), icon: '◇' },
      { to: '/plan', label: $t('nav.plan'), icon: '☷' },
      { to: '/tree', label: $t('nav.tree'), icon: '⑂' },
      ...(cnReadonly.value ? [{ to: '/electives', label: electivesLabel.value, icon: '✦' }] : []),
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
  const { locale } = useLocale()
  const electivesLabel = computed(() => (locale.value === 'zh' ? '找选修课' : 'Electives'))

  return computed<HeaderNavItem[]>(() => {
    const toolChildren = [
      { to: '/plan', label: $t('nav.plan') },
      { to: '/tree', label: $t('nav.tree') },
      ...(cnReadonly.value ? [{ to: '/electives', label: electivesLabel.value }] : []),
      { to: '/marks', label: $t('nav.marks') }
    ]
    const items: HeaderNavItem[] = [
      { to: '/units', label: $t('nav.units') },
      { to: '/courses', label: $t('nav.courses') },
      {
        label: $t('nav.tools'),
        children: toolChildren
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
