<script setup lang="ts">
// The main way into the product. Submitting always lands on unified search,
// so a student never has to decide which section their question belongs to.
const props = withDefaults(
  defineProps<{ modelValue?: string; placeholder?: string; autofocus?: boolean; big?: boolean }>(),
  { modelValue: '', placeholder: 'Search units, policies or community…', big: false }
)
const emit = defineEmits<{ (e: 'update:modelValue', value: string): void; (e: 'submit', value: string): void }>()

const value = ref(props.modelValue)
watch(() => props.modelValue, v => { value.value = v })

function submit() {
  emit('update:modelValue', value.value)
  emit('submit', value.value.trim())
}
</script>

<template>
  <form class="search" :class="{ big }" role="search" @submit.prevent="submit">
    <label class="visually-hidden" for="search-input">Search Monash Hub</label>
    <input
      id="search-input"
      v-model="value"
      class="field"
      type="search"
      :placeholder="placeholder"
      :autofocus="autofocus"
      autocomplete="off"
    >
    <button class="btn" type="submit">Search</button>
  </form>
</template>

<style scoped>
.search { display: flex; gap: var(--s2); width: 100%; }
.search.big .field { min-height: 56px; font-size: 1.05rem; }
.search.big .btn { min-height: 56px; }
@media (max-width: 520px) {
  .search { flex-direction: column; }
}
</style>
