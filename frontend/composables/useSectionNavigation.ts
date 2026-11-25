export function useSectionNavigation() {
  const { $t } = useNuxtApp()
  const { cnReadonly } = useSiteMode()
  const { locale } = useLocale()
  const electivesLabel = computed(() => (locale.value === 'zh' ? '找选修课' : 'Electives'))
  const unitsLabel = computed(() => (cnReadonly.value && locale.value === 'zh' ? '课程查询' : $t('nav.units')))

  return computed(() => {
    const items = [
      { to: '/guides', label: $t('nav.guides'), icon: '□' },
      { to: '/units', label: unitsLabel.value, icon: '▤' },
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
  accent?: boolean
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

  return computed<HeaderNavItem[]>(() => {
    if (cnReadonly.value) {
      const zh = locale.value === 'zh'
      return [
        { to: '/guides', label: $t('nav.guides') },
        { to: '/units', label: zh ? '课程查询' : $t('nav.units') },
        { to: '/courses', label: $t('nav.courses') },
        {
          label: $t('nav.tools'),
          children: [
            { to: '/plan', label: $t('nav.plan') },
            { to: '/tree', label: $t('nav.tree') },
            { to: '/electives', label: zh ? '找选修课' : 'Electives' }
          ]
        },
        { to: '/marks', label: 'WAM/GPA' },
        { to: '/fees', label: zh ? '学费查询' : $t('nav.fees') },
        { to: '/mamo', label: $t('nav.mamo') },
        { to: '/parents', label: zh ? '家长入口' : $t('nav.parents'), accent: true }
      ]
    }
    return [
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
    ]
  })
}
