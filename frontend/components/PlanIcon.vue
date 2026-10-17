<script setup lang="ts">
/**
 * The handful of line icons the course map uses.
 *
 * Drawn here rather than pulled from an icon package: the page needs about ten
 * glyphs, and a dependency for ten paths is a lot of node_modules for nothing.
 * They inherit the text colour, so a button's hover colour reaches the icon too.
 */
const props = withDefaults(defineProps<{ name: string; size?: number }>(), { size: 16 })

const PATHS: Record<string, string[]> = {
  plus: ['M12 5v14', 'M5 12h14'],
  trash: ['M4 7h16', 'M9 7V4.5h6V7', 'M6.5 7l.9 12.5h9.2L17.5 7', 'M10 11v5', 'M14 11v5'],
  download: ['M12 4v11', 'M7.5 10.5 12 15l4.5-4.5', 'M5 20h14'],
  upload: ['M12 20V9', 'M7.5 13.5 12 9l4.5 4.5', 'M5 4h14'],
  calendar: ['M4 6.5h16v13.5H4z', 'M4 10.5h16', 'M8.5 3.5v5', 'M15.5 3.5v5'],
  close: ['M6.5 6.5l11 11', 'M17.5 6.5l-11 11'],
  check: ['M5 12.5l4.5 4.5L19 7.5'],
  alert: ['M12 4 2.8 19.5h18.4z', 'M12 10v4.5', 'M12 17.2v.3'],
  move: ['M12 3v18', 'M8.5 6.5 12 3l3.5 3.5', 'M8.5 17.5 12 21l3.5-3.5'],
  tree: ['M6 4.5v15', 'M6 9.5h6.5a3 3 0 0 1 3 3v2', 'M15.5 14.5v5', 'M13 17l2.5 2.5L18 17'],
  lock: ['M6 11h12v9H6z', 'M8.5 11V8a3.5 3.5 0 0 1 7 0v3'],
  undo: ['M9 14 4.5 9.5 9 5', 'M4.5 9.5h10a5 5 0 0 1 0 10H11'],
  redo: ['M15 14l4.5-4.5L15 5', 'M19.5 9.5h-10a5 5 0 0 0 0 10H13'],
  print: ['M7 9V3.5h10V9', 'M7 17H4.5V10h15v7H17', 'M7 14h10v6.5H7z'],
  spinner: ['M12 4a8 8 0 1 1-8 8']
}

const paths = computed(() => PATHS[props.name] || [])
</script>

<template>
  <svg
    class="icon"
    :class="{ 'icon--spin': name === 'spinner' }"
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    <path v-for="d in paths" :key="d" :d="d" />
  </svg>
</template>

<style scoped>
.icon { flex: none; display: block; }
.icon--spin { animation: spin 0.9s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) {
  .icon--spin { animation: none; }
}
</style>
