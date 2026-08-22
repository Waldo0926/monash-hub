<script setup lang="ts">
/**
 * Error display that distinguishes the three cases a reader can act on:
 * nothing there (404), the API is unreachable, or something else broke.
 */
const props = defineProps<{ error?: any; onRetry?: () => void }>()

const message = computed(() => {
  const status = props.error?.statusCode || props.error?.status
  if (status === 404) return props.error?.data?.detail || 'We could not find that.'
  if (!status) return 'We could not reach Monash Hub. Check your connection and try again.'
  if (status >= 500) return 'Monash Hub had a problem loading this. It is not your connection.'
  return props.error?.data?.detail || 'Something went wrong loading this page.'
})
</script>

<template>
  <div class="error card" role="alert">
    <h3>Could not load this</h3>
    <p class="small">{{ message }}</p>
    <button v-if="onRetry" class="btn btn--ghost btn--small" @click="onRetry()">Retry</button>
  </div>
</template>

<style scoped>
.error { padding: var(--s5); border-color: var(--danger); background: var(--danger-bg); }
.error h3 { color: var(--danger); }
</style>
