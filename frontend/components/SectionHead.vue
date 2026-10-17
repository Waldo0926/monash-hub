<script setup lang="ts">
/**
 * A section heading with a small icon tile in front of it.
 *
 * A unit page is a dozen cards of similar shape, and on a long scroll the
 * icon is what lets you find "assessment" again without reading every title.
 * The icons are drawn here as plain strokes rather than pulled from an icon
 * package, so the page does not ship a library for twelve glyphs.
 */
defineProps<{ icon: keyof typeof ICONS; title: string; tag?: 'h2' | 'h3' }>()
</script>

<script lang="ts">
const ICONS = {
  overview: 'M2 4h6a4 4 0 0 1 4 4v12a3 3 0 0 0-3-3H2z M22 4h-6a4 4 0 0 0-4 4v12a3 3 0 0 1 3-3h7z',
  offerings: 'M3 5h18v16H3z M3 10h18 M8 3v4 M16 3v4',
  assessment: 'M9 3h6v3H9z M7 4.5H5V21h14V4.5h-2 M9 13l2 2 4-4',
  requisites: 'M6 3v12 M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6z M18 9a9 9 0 0 1-9 9',
  outcomes: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10z M12 13a1 1 0 1 0 0-2 1 1 0 0 0 0 2z',
  workload: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z M12 7v5l3 2',
  resources: 'M4 4v16 M8 4v16 M12 4v16 M16 4.5l4 15',
  fits: 'M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z M9 3v15 M15 6v15',
  faq: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6 M12 17.2v.1',
  details: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z M12 11v6 M12 7.4v.1',
  ask: 'M4 5h16v11H9l-5 4z',
  community: 'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M2 21a7 7 0 0 1 14 0 M17 3.5a4 4 0 0 1 0 7.5 M22 21a7 7 0 0 0-4-6.3'
} as const
</script>

<template>
  <div class="section-head">
    <span class="tile" aria-hidden="true">
      <svg viewBox="0 0 24 24"><path :d="ICONS[icon]" /></svg>
    </span>
    <component :is="tag || 'h2'" class="title">{{ title }}</component>
    <div v-if="$slots.default" class="extra"><slot /></div>
  </div>
</template>

<style scoped>
.section-head { display: flex; align-items: center; gap: var(--s3); margin-bottom: var(--s4); }
.tile {
  flex: none; width: 36px; height: 36px; display: grid; place-items: center;
  border-radius: var(--radius-sm); background: var(--blue-50);
}
.tile svg {
  width: 20px; height: 20px; fill: none; stroke: var(--brand);
  stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round;
}
.title { margin: 0; flex: 1; min-width: 0; }
.extra { flex: none; }
</style>
