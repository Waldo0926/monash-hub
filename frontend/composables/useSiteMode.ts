/**
 * Runtime feature flag for the China mainland read-only deployment.
 *
 * Driven by `NUXT_PUBLIC_CN_READONLY_MODE` so the exact same container image
 * runs both the full overseas site (default: false) and the read-only mirror
 * (true) with zero changes to overseas behaviour.
 */
export function isCnReadonlyFlag(value: unknown): boolean {
  return value === true || value === 'true' || value === '1'
}

export function useSiteMode() {
  const config = useRuntimeConfig()
  const cnReadonly = computed(() => isCnReadonlyFlag(config.public.cnReadonlyMode))
  return { cnReadonly }
}
