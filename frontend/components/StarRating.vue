<script setup lang="ts">
/**
 * Five stars filled to a score, for showing a rating rather than giving one.
 *
 * The filled row sits on top of the empty row and is clipped to the score, so
 * 3.6 shows three full stars and most of the fourth. The number itself is in
 * the label for screen readers, and the callers print it next to the stars
 * too, since a part-filled star is hard to read at 14px.
 */
const props = withDefaults(defineProps<{ value: number | null | undefined; size?: 'sm' | 'md' | 'lg' }>(), {
  size: 'md'
})
const { $t } = useNuxtApp()

const percent = computed(() => {
  const v = Number(props.value ?? 0)
  return Math.max(0, Math.min(100, (v / 5) * 100))
})
const label = computed(() =>
  props.value == null ? $t('reviews.noScore') : $t('reviews.outOfFive', { score: Number(props.value).toFixed(1) })
)
</script>

<script lang="ts">
export const STAR_PATH =
  'M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 17.4l-5.8 3.1 1.1-6.5L2.6 9.4l6.5-.9z'
</script>

<template>
  <span class="stars" :class="`stars--${size}`" role="img" :aria-label="label">
    <span class="row row--empty" aria-hidden="true">
      <svg v-for="i in 5" :key="i" viewBox="0 0 24 24"><path :d="STAR_PATH" /></svg>
    </span>
    <span class="row row--full" :style="{ width: `${percent}%` }" aria-hidden="true">
      <svg v-for="i in 5" :key="i" viewBox="0 0 24 24"><path :d="STAR_PATH" /></svg>
    </span>
  </span>
</template>

<style scoped>
.stars { position: relative; display: inline-block; line-height: 0; vertical-align: middle; flex: none; }
.row { display: inline-flex; gap: 1px; white-space: nowrap; }
.row--full { position: absolute; inset: 0 auto 0 0; overflow: hidden; }
.row svg { flex: none; }
.row--empty svg { fill: var(--star-empty); }
.row--full svg { fill: var(--star); }
.stars--sm svg { width: 13px; height: 13px; }
.stars--md svg { width: 17px; height: 17px; }
.stars--lg svg { width: 24px; height: 24px; }
</style>
