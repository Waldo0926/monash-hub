<script setup lang="ts">
/**
 * Which Handbook a student should be reading, and what to do about a unit that
 * has closed.
 *
 * A course map and its requisites are fixed by the year a student commenced:
 * the {year} map is for students starting in {year}, and anyone who started
 * earlier follows the map of their own intake year. Nobody should plan a degree
 * from the newest Handbook just because it is the default view. The year picker
 * on the page is how they get to their own.
 *
 * Closing a unit is a faculty decision with a faculty notice: a replacement
 * applies once the unit closes, not before, and the faculty says which one.
 * This page does not guess a replacement; it says where the answer comes from.
 */
defineProps<{ year: number; closed?: boolean }>()
</script>

<template>
  <aside class="intake small" aria-label="Intake year">
    <p>{{ $t('year.intakeNote', { year }) }}</p>
    <p v-if="closed">{{ $t('year.closedNote') }}</p>
  </aside>
</template>

<style scoped>
.intake {
  margin: 0 0 var(--s4);
  padding: var(--s3) var(--s4);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface-2);
  color: var(--muted);
}
.intake p { margin: 0; }
.intake p + p { margin-top: var(--s2); }
</style>
