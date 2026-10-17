<script setup lang="ts">
/**
 * Five stars to pick a score with.
 *
 * Underneath it is a plain radio group, so arrow keys, Tab and screen readers
 * work the way they do for any other choice; the stars are just how the
 * labels look. Hovering previews a score without picking it. An optional
 * score can be cleared again, because "I did not notice the teaching either
 * way" is a fair answer and should not have to be a 3.
 */
import { STAR_PATH } from './StarRating.vue'

const props = withDefaults(defineProps<{
  modelValue: number | null
  name: string
  label: string
  optional?: boolean
  size?: 'md' | 'lg'
}>(), { optional: false, size: 'md' })
const emit = defineEmits<{ 'update:modelValue': [value: number | null] }>()
const { $t } = useNuxtApp()

const hover = ref<number | null>(null)
const shown = computed(() => hover.value ?? props.modelValue ?? 0)

function pick(value: number) {
  emit('update:modelValue', value)
}
</script>

<template>
  <fieldset class="star-input" :class="`star-input--${size}`" @mouseleave="hover = null">
    <legend class="visually-hidden">{{ label }}</legend>
    <label v-for="i in 5" :key="i" class="star" :class="{ on: i <= shown }" @mouseenter="hover = i">
      <input
        type="radio"
        class="visually-hidden"
        :name="name"
        :value="i"
        :checked="modelValue === i"
        @change="pick(i)"
      >
      <svg viewBox="0 0 24 24" aria-hidden="true"><path :d="STAR_PATH" /></svg>
      <span class="visually-hidden">{{ $t('reviews.starCount', { count: i }) }}</span>
    </label>
    <button
      v-if="optional && modelValue"
      type="button"
      class="clear tiny"
      @click="emit('update:modelValue', null)"
    >
      {{ $t('reviews.clear') }}
    </button>
  </fieldset>
</template>

<style scoped>
.star-input { display: inline-flex; align-items: center; gap: 2px; border: 0; margin: 0; padding: 0; }
.star {
  display: grid; place-items: center; cursor: pointer; border-radius: 6px;
  min-width: 32px; min-height: 32px;
}
.star svg { width: 22px; height: 22px; fill: var(--star-empty); transition: fill 0.1s, transform 0.1s; }
.star-input--lg .star { min-width: 40px; min-height: 40px; }
.star-input--lg .star svg { width: 30px; height: 30px; }
.star.on svg { fill: var(--star); }
.star:hover svg { transform: scale(1.08); }
.star:has(input:focus-visible) { outline: 2px solid var(--brand); outline-offset: 1px; }
.clear {
  margin-left: var(--s2); padding: 2px 8px; border: 0; background: none;
  color: var(--muted); text-decoration: underline; cursor: pointer; font: inherit; font-size: 0.78rem;
}
@media (prefers-reduced-motion: reduce) {
  .star svg { transition: none; }
  .star:hover svg { transform: none; }
}
</style>
