<script setup lang="ts">
// The main way into the product. Submitting always lands on unified search,
// so a student never has to decide which section their question belongs to.
const props = withDefaults(
  defineProps<{
    modelValue?: string
    placeholder?: string
    autofocus?: boolean
    big?: boolean
    inset?: boolean
  }>(),
  { modelValue: '', placeholder: '', big: false, inset: false }
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
  <form class="search" :class="{ big, inset }" role="search" @submit.prevent="submit">
    <label class="visually-hidden" :for="inputId">{{ $t('search.label') }}</label>
    <PlanIcon v-if="inset" name="search" class="lead" />
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

/* The header version is one soft pill with the button sitting inside it, so
   the field and its button read as one control rather than two boxes. The
   ring goes on the whole pill when the input has focus. */
.search.inset {
  align-items: center;
  gap: 0;
  height: 40px;
  padding: 4px;
  border: 1px solid transparent;
  border-radius: var(--radius-pill);
  background: var(--surface-2);
  transition: background-color 0.15s, border-color 0.15s, box-shadow 0.15s;
}
.search.inset:hover { border-color: var(--border); }
.search.inset:focus-within {
  border-color: var(--blue);
  background: var(--surface);
  box-shadow: 0 0 0 3px var(--blue-50);
}
.inset .lead { margin-left: var(--s2); color: var(--muted); }
.inset .field {
  min-height: 0;
  height: 100%;
  padding: 0 var(--s2);
  border: 0;
  background: transparent;
  font-size: 0.9rem;
}
.inset .field:focus-visible { outline: none; }
.inset .field::-webkit-search-cancel-button { -webkit-appearance: none; }
.inset .btn {
  min-height: 0;
  height: 100%;
  padding-inline: var(--s4);
  border-radius: var(--radius-pill);
  font-size: 0.85rem;
  box-shadow: 0 1px 2px rgba(12, 27, 42, 0.2);
}
.search.big .field { min-height: 56px; font-size: 1.05rem; }
.search.big .btn { min-height: 56px; }
@media (max-width: 520px) {
  .search:not(.inset) { flex-direction: column; }
}
</style>
