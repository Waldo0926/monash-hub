<script setup lang="ts">
/**
 * How one fee moved since last year, under the amount it belongs to.
 * Nothing is shown when last year's fee is not known, which is different
 * from "no change".
 */
import { formatAmount, formatDelta, type FeeDelta } from '~/utils/tuition'

defineProps<{ delta: FeeDelta | null; year?: number | null }>()
</script>

<template>
  <span
    v-if="delta && year"
    class="delta"
    :class="{ 'delta--same': delta.diff === 0 }"
    :title="$t('fees.previousAmount', { year, amount: formatAmount({ value: delta.previous, written: '', label: null }) })"
  >
    <template v-if="delta.diff === 0">{{ $t('fees.sameAs', { year }) }}</template>
    <template v-else>{{ $t('fees.changeSince', { year, change: formatDelta(delta) }) }}</template>
  </span>
</template>

<style scoped>
.delta { display: block; font: 400 0.75rem/1.4 var(--font); color: var(--warning); cursor: help; }
.delta--same { color: var(--muted); }
</style>
