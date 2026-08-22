<script setup lang="ts">
/**
 * When we last read the source.
 *
 * Shown everywhere official data appears. Anything older than a fortnight is
 * flagged rather than hidden: stale data that admits it is stale is still
 * useful, stale data pretending to be current is not.
 */
const props = defineProps<{ value?: string | null; label?: string }>()

const STALE_AFTER_DAYS = 14

const formatted = computed(() => {
  if (!props.value) return null
  const date = new Date(props.value)
  if (Number.isNaN(date.getTime())) return null
  return date.toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric' })
})

const isStale = computed(() => {
  if (!props.value) return false
  const days = (Date.now() - new Date(props.value).getTime()) / 86_400_000
  return days > STALE_AFTER_DAYS
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
