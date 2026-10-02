<script setup lang="ts">
/**
 * Which Handbook year a page shows, like the year picker on handbook.monash.edu.
 *
 * `years` comes from the API, newest first: every loaded year on a list page,
 * only the years that list this code on a detail page, so the picker never
 * offers a year that would answer "not found".
 */
const props = defineProps<{ years: number[]; modelValue: number | null | undefined }>()
const emit = defineEmits<{ 'update:modelValue': [value: number] }>()

const options = computed(() => [...new Set(props.years)].sort((a, b) => b - a))
</script>

<template>
  <label v-if="options.length" class="year-picker">
    <span class="tiny muted">{{ $t('handbook.year') }}</span>
    <select
      class="field"
      :value="modelValue ?? options[0]"
      @change="emit('update:modelValue', Number(($event.target as HTMLSelectElement).value))"
    >
      <option v-for="y in options" :key="y" :value="y">{{ y }}</option>
    </select>
  </label>
</template>

<style scoped>
.year-picker { display: inline-flex; flex-direction: column; gap: var(--s1); min-width: 7rem; }
</style>
