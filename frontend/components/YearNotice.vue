<script setup lang="ts">
/**
 * Shown when a page is read from an earlier Handbook because the current one
 * no longer lists the code (see backend app/handbook/years.py). Monash
 * renumbers units between years, so a unit a student is sitting now can be
 * missing from next year's Handbook; the reader must know which year they are
 * looking at before relying on it.
 */
defineProps<{ code: string; year: number; missing: number }>()
</script>

<template>
  <p class="year-notice small" role="status">
    {{ $t('handbook.notInYear', { code, year, missing }) }}
  </p>
</template>

<style scoped>
.year-notice {
  margin: 0 0 var(--s3); padding: var(--s3) var(--s4); border-radius: var(--radius-sm);
  background: var(--warning-bg); color: var(--warning);
}
</style>
