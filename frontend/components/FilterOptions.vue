<script setup lang="ts">
/**
 * Checkboxes for one filter, each with the number of units it would leave.
 *
 * Long lists show the first few (the API sends the biggest values first) and
 * hide the rest behind "show more". A ticked value always stays visible, so
 * a filter set from a shared link is never hidden in the folded part.
 */
export interface FilterOption {
  value: string
  label: string
}

const props = withDefaults(defineProps<{
  options: FilterOption[]
  modelValue: string[]
  /** Unit counts by value. Missing while they load, so no numbers are shown yet. */
  counts?: Record<string, number> | null
  /** How many to show before "show more". 0 shows them all. */
  limit?: number
  /** A box to type into, for lists too long to scan. */
  searchable?: boolean
}>(), {
  counts: null,
  limit: 6,
  searchable: false
})
const emit = defineEmits<{ 'update:modelValue': [value: string[]] }>()

const expanded = ref(false)
const find = ref('')

const matching = computed(() => {
  const needle = find.value.trim().toLowerCase()
  if (!needle) return props.options
  return props.options.filter(o => o.label.toLowerCase().includes(needle) || o.value.toLowerCase().includes(needle))
})

const shown = computed(() => {
  // Typing is already a way of asking for more, so a search shows every match.
  if (!props.limit || expanded.value || find.value.trim()) return matching.value
  const head = matching.value.slice(0, props.limit)
  const ticked = matching.value.slice(props.limit).filter(o => props.modelValue.includes(o.value))
  return [...head, ...ticked]
})
const hidden = computed(() => matching.value.length - shown.value.length)

function toggle(value: string, on: boolean) {
  const next = props.modelValue.filter(v => v !== value)
  if (on) next.push(value)
  emit('update:modelValue', next)
}

function countOf(value: string): number | null {
  return props.counts ? (props.counts[value] ?? 0) : null
}
</script>

<template>
  <div class="options">
    <input
      v-if="searchable && options.length > limit"
      v-model="find"
      type="search"
      class="field find"
      :placeholder="$t('units.findOption')"
    >
    <label
      v-for="option in shown"
      :key="option.value"
      class="option"
      :class="{ empty: countOf(option.value) === 0 && !modelValue.includes(option.value) }"
    >
      <input
        type="checkbox"
        :checked="modelValue.includes(option.value)"
        @change="toggle(option.value, ($event.target as HTMLInputElement).checked)"
      >
      <span class="option-label">{{ option.label }}</span>
      <span v-if="countOf(option.value) !== null" class="option-count">{{ countOf(option.value) }}</span>
    </label>
    <button v-if="hidden > 0" type="button" class="more" @click="expanded = true">
      {{ $t('units.showMore', { count: hidden }) }}
    </button>
    <button v-else-if="expanded && !find.trim()" type="button" class="more" @click="expanded = false">
      {{ $t('units.showLess') }}
    </button>
  </div>
</template>

<style scoped>
.options { display: grid; gap: 2px; }
.find { margin-bottom: var(--s2); padding: 6px var(--s2); font-size: 0.85rem; }
.option {
  display: grid; grid-template-columns: 18px minmax(0, 1fr) auto; gap: var(--s2); align-items: start;
  padding: 5px 4px; border-radius: 6px; cursor: pointer; font-size: 0.88rem; line-height: 1.35;
}
.option:hover { background: var(--surface-2); }
.option input { width: 16px; height: 16px; margin: 2px 0 0; accent-color: var(--navy); cursor: pointer; }
.option-count { color: var(--muted); font-size: 0.8rem; font-variant-numeric: tabular-nums; padding-top: 1px; }
.option.empty .option-label { color: var(--muted); }
.more {
  justify-self: start; margin-top: 4px; padding: 4px; border: 0; background: none; cursor: pointer;
  color: var(--brand); font: inherit; font-size: 0.85rem; font-weight: 500;
}
.more:hover { text-decoration: underline; }
</style>
