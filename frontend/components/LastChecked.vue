<script setup lang="ts">
/**
 * When we last read the source.
 *
 * Shown everywhere official data appears, which means it renders on the server
 * and again in the browser — and those two run in different time zones. Node is
 * on UTC, a student in Malaysia is on UTC+8, and "22 Aug" against "23 Aug" is a
 * hydration mismatch that Vue then tries to repair, in one case badly enough to
 * drop the search results underneath it.
 *
 * So the date is formatted by hand, in UTC, with no Intl and no local clock.
 * Same string on both sides, every time.
 *
 * Staleness is the one thing that cannot be decided that way — it depends on
 * "now" — so it is computed after mount and starts out false, which is also the
 * safe direction: the warning appears, it never wrongly disappears.
 */
const props = defineProps<{ value?: string | null; label?: string }>()

const STALE_AFTER_DAYS = 14
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const parsed = computed(() => {
  if (!props.value) return null
  const date = new Date(props.value)
  return Number.isNaN(date.getTime()) ? null : date
})

const formatted = computed(() => {
  const date = parsed.value
  if (!date) return null
  return `${date.getUTCDate()} ${MONTHS[date.getUTCMonth()]} ${date.getUTCFullYear()} UTC`
})

const isStale = ref(false)
onMounted(() => {
  const date = parsed.value
  if (!date) return
  isStale.value = (Date.now() - date.getTime()) / 86_400_000 > STALE_AFTER_DAYS
})
</script>

<template>
  <span v-if="formatted" class="last-checked tiny" :class="{ stale: isStale }">
    {{ label || 'Last checked' }}: {{ formatted }}
    <span v-if="isStale"> · source may have changed since</span>
  </span>
</template>

<style scoped>
.last-checked { color: var(--muted); }
.stale { color: var(--warning); }
</style>
