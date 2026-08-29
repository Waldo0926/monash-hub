export function useSectionNavigation() {
  const { $t } = useNuxtApp()

  return computed(() => [
    { to: '/units', label: $t('nav.units'), icon: '▤' },
    { to: '/courses', label: $t('nav.courses'), icon: '◇' },
    { to: '/plan', label: $t('nav.plan'), icon: '☷' },
    { to: '/tree', label: $t('nav.tree'), icon: '⑂' },
    { to: '/marks', label: $t('nav.marks'), icon: '%' },
    { to: '/guides', label: $t('nav.guides'), icon: '□' },
    { to: '/community', label: $t('nav.community'), icon: '☰' },
    { to: '/mamo', label: $t('nav.mamo'), icon: 'M' }
  ])
}
