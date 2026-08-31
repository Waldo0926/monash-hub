<script setup lang="ts">
// The main way into the product. Submitting always lands on unified search,
// so a student never has to decide which section their question belongs to.
const props = withDefaults(
  defineProps<{
    modelValue?: string
    placeholder?: string
    autofocus?: boolean
    big?: boolean
    compactButton?: boolean
  }>(),
  { modelValue: '', placeholder: '', big: false, compactButton: false }
)
const { $t } = useNuxtApp()
const resolvedPlaceholder = computed(() => props.placeholder || $t('search.placeholder'))
const emit = defineEmits<{ (e: 'update:modelValue', value: string): void; (e: 'submit', value: string): void }>()

// The header and the page can both render a search box, so the id has to be
// unique or the two labels point at the same input.
const inputId = useId()
const value = ref(props.modelValue)
watch(() => props.modelValue, v => { value.value = v })

function submit() {
  emit('update:modelValue', value.value)
  emit('submit', value.value.trim())
}
</script>

<template>
  <form class="search" :class="{ big, 'compact-button': compactButton }" role="search" @submit.prevent="submit">
    <label class="visually-hidden" :for="inputId">{{ $t('search.label') }}</label>
    <input
      :id="inputId"
      v-model="value"
      class="field"
      type="search"
      :placeholder="resolvedPlaceholder"
      :autofocus="autofocus"
      autocomplete="off"
    >
    <button class="btn" type="submit">{{ $t('search.button') }}</button>
  </form>
</template>

<style scoped>
.search { display: flex; gap: var(--s2); width: 100%; }
.field { flex: 1; width: auto; min-width: 0; }
.compact-button .btn { padding-inline: var(--s3); }
.search.big .field { min-height: 56px; font-size: 1.05rem; }
.search.big .btn { min-height: 56px; }
@media (max-width: 520px) {
  .search { flex-direction: column; }
}
</style>
