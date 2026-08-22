<script setup lang="ts">
// An empty result has to explain itself and offer the next move. "No results"
// on its own is a dead end.
defineProps<{ title: string; hint?: string }>()
</script>

<template>
  <div class="empty card">
    <h3>{{ title }}</h3>
    <p v-if="hint" class="muted small">{{ hint }}</p>
    <div class="actions"><slot /></div>
  </div>
</template>

<style scoped>
.empty { padding: var(--s6) var(--s5); text-align: center; }
.empty h3 { margin-bottom: var(--s2); }
.actions { display: flex; gap: var(--s3); justify-content: center; flex-wrap: wrap; }
</style>
