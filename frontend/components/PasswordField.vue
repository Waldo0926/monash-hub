<script setup lang="ts">
/**
 * A password input with a reveal toggle.
 *
 * The toggle matters more than it looks: without it people pick shorter, weaker
 * passwords because they cannot check what they typed, and on a phone they
 * mistype and give up.
 */
const props = withDefaults(
  defineProps<{
    modelValue: string
    label: string
    hint?: string
    error?: string
    autocomplete?: string
    placeholder?: string
  }>(),
  { autocomplete: 'current-password' }
)
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
}>()

const revealed = ref(false)
const input = ref<HTMLInputElement | null>(null)
const id = useId()

defineExpose({ focus: () => input.value?.focus() })
</script>

<template>
  <div class="field-row">
    <label :for="id" class="tiny muted">{{ label }}</label>
    <div class="wrap">
      <input
        :id="id"
        ref="input"
        class="field"
        :type="revealed ? 'text' : 'password'"
        :value="modelValue"
        :placeholder="placeholder"
        :autocomplete="autocomplete"
        :aria-invalid="error ? 'true' : undefined"
        :aria-describedby="error ? `${id}-error` : hint ? `${id}-hint` : undefined"
        :class="{ bad: error }"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="emit('blur')"
      >
      <button type="button" class="toggle tiny" @click="revealed = !revealed">
        {{ revealed ? '🙈' : '👁' }}
      </button>
    </div>
    <p v-if="error" :id="`${id}-error`" class="tiny bad-text" role="alert">{{ error }}</p>
    <p v-else-if="hint" :id="`${id}-hint`" class="tiny muted">{{ hint }}</p>
  </div>
</template>

<style scoped>
.field-row { display: grid; gap: var(--s1); }
.wrap { position: relative; display: flex; }
.wrap .field { padding-right: 44px; }
.toggle {
  position: absolute;
  top: 0;
  right: 0;
  width: 44px;
  height: 100%;
  border: 0;
  background: none;
  cursor: pointer;
  line-height: 1;
}
.bad { border-color: var(--danger); }
.bad-text { color: var(--danger); margin: 0; }
p { margin: 0; }
</style>
