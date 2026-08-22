<script setup lang="ts">
// Loading placeholders keep the layout still. A full-page spinner throws the
// page away and then rebuilds it, which reads as slower than it is.
withDefaults(defineProps<{ lines?: number; height?: string }>(), { lines: 3, height: '16px' })
</script>

<template>
  <div class="skeleton" aria-hidden="true">
    <div v-for="n in lines" :key="n" class="line" :style="{ height }" />
  </div>
</template>

<style scoped>
.skeleton { display: grid; gap: var(--s3); }
.line {
  border-radius: var(--radius-sm);
  background: linear-gradient(90deg, var(--surface-2) 25%, var(--border) 37%, var(--surface-2) 63%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
}
.line:last-child { width: 65%; }
@keyframes shimmer {
  0% { background-position: 100% 50%; }
  100% { background-position: 0 50%; }
}
@media (prefers-reduced-motion: reduce) {
  .line { animation: none; }
}
</style>
