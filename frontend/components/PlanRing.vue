<script setup lang="ts">
/**
 * A progress ring for the course map's credit point total.
 *
 * `value` is a fraction from 0 to 1, or null when there is nothing to measure
 * against (no degree picked). Null draws the empty track instead of a 0% that
 * would read as "you have done nothing" when the real answer is "we don't know
 * what done looks like yet".
 */
const props = withDefaults(defineProps<{ value: number | null; size?: number; stroke?: number }>(), {
  size: 168,
  stroke: 12
})

const radius = computed(() => (props.size - props.stroke) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const offset = computed(() => {
  const clamped = Math.min(1, Math.max(0, props.value ?? 0))
  return circumference.value * (1 - clamped)
})
</script>

<template>
  <div class="ring" :style="{ width: `${size}px`, height: `${size}px` }">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`" aria-hidden="true">
      <circle
        class="track"
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        :stroke-width="stroke"
      />
      <circle
        v-if="value !== null && value > 0"
        class="fill"
        :class="{ 'fill--done': value >= 1 }"
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        :stroke-width="stroke"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="offset"
      />
    </svg>
    <div class="centre"><slot /></div>
  </div>
</template>

<style scoped>
.ring { position: relative; flex: none; }
svg { display: block; transform: rotate(-90deg); }
circle { fill: none; }
.track { stroke: var(--surface-2); }
.fill {
  stroke: var(--brand);
  stroke-linecap: round;
  transition: stroke-dashoffset 0.5s ease;
}
.fill--done { stroke: var(--success); }
.centre {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center;
}
@media (prefers-reduced-motion: reduce) {
  .fill { transition: none; }
}
</style>
