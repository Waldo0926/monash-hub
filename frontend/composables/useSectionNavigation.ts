export function useSectionNavigation() {
  const { $t } = useNuxtApp()

  return computed(() => [
    { to: '/guides', label: $t('nav.guides'), icon: '□' },
    { to: '/units', label: $t('nav.units'), icon: '▤' },
    { to: '/courses', label: $t('nav.courses'), icon: '◇' },
    { to: '/plan', label: $t('nav.plan'), icon: '☷' },
    { to: '/tree', label: $t('nav.tree'), icon: '⑂' },
    { to: '/electives', label: $t('nav.electives'), icon: '✦' },
    { to: '/marks', label: $t('nav.marks'), icon: '%' },
    { to: '/fees', label: $t('nav.fees'), icon: '¤' },
    { to: '/mamo', label: $t('nav.mamo'), icon: 'M' },
    { to: '/community', label: $t('nav.community'), icon: '☰' }
  ])
}

export interface HeaderNavItem {
  to?: string
  label: string
  accent?: boolean
  children?: { to: string; label: string }[]
}

/**
 * Desktop header navigation: guides and units come first, the three course-planning
 * tools share one menu, high-frequency tools (WAM/GPA, fees) sit at the top level,
 * and the parents entry is accented so families spot it immediately.
 */
export function useHeaderNavigation() {
  const { $t } = useNuxtApp()
  const { locale } = useLocale()

  return computed<HeaderNavItem[]>(() => {
    const zh = locale.value === 'zh'
    return [
      { to: '/guides', label: $t('nav.guides') },
      { to: '/units', label: $t('nav.units') },
      { to: '/courses', label: $t('nav.courses') },
      {
        label: $t('nav.tools'),
        children: [
          { to: '/plan', label: $t('nav.plan') },
          { to: '/tree', label: $t('nav.tree') },
          { to: '/electives', label: $t('nav.electives') }
        ]
      },
      { to: '/marks', label: 'WAM/GPA' },
      { to: '/fees', label: zh ? $t('nav.fees') : 'Fees' },
      { to: '/mamo', label: $t('nav.mamo') },
      { to: '/community', label: $t('nav.community') },
      { to: '/parents', label: zh ? $t('nav.parents') : 'Parents', accent: true }
    ]
  })
}
