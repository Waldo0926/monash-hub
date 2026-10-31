<script setup lang="ts">
/**
 * Says so when the reader has no connection.
 *
 * With no network the service worker answers with the last saved copy of a
 * page. That copy was right when it was saved, but a student reading a census
 * date should know it may have changed since.
 */
const offline = ref(false)

function update() { offline.value = !navigator.onLine }

onMounted(() => {
  update()
  window.addEventListener('online', update)
  window.addEventListener('offline', update)
})
onBeforeUnmount(() => {
  window.removeEventListener('online', update)
  window.removeEventListener('offline', update)
})
</script>

<template>
  <div v-if="offline" class="container offline" role="status">
    <p class="small notice">{{ $t('pwa.offline') }}</p>
  </div>
</template>

<style scoped>
.offline { margin-bottom: var(--s5); }
.notice {
  margin: 0;
  padding: var(--s3) var(--s4);
  border: 1px solid var(--warning);
  border-radius: var(--radius);
  background: var(--warning-bg);
  color: var(--text);
}
</style>
