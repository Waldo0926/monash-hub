<script setup lang="ts">
/**
 * Error display that distinguishes the three cases a reader can act on:
 * nothing there (404), the API is unreachable, or something else broke.
 */
const props = defineProps<{ error?: any; onRetry?: () => void }>()
const { $t } = useNuxtApp()

const message = computed(() => {
  const status = props.error?.statusCode || props.error?.status
  // The API's 404 sentences are English ("FIT9999 is not in the 2026 Handbook
  // index yet"); the reader's language wins over the extra detail.
  if (status === 404) return $t('state.notFound')
  return apiErrorMessage(props.error, $t, 'state.generic')
})
</script>

<template>
  <div class="error card" role="alert">
    <h3>{{ $t('state.loadError') }}</h3>
    <p class="small">{{ message }}</p>
    <button v-if="onRetry" class="btn btn--ghost btn--small" @click="onRetry()">
      {{ $t('state.retry') }}
    </button>
  </div>
</template>

<style scoped>
.error { padding: var(--s5); border-color: var(--danger); background: var(--danger-bg); }
.error h3 { color: var(--danger); }
</style>
