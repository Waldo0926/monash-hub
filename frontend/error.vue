<script setup lang="ts">
const props = defineProps<{ error: any }>()
const is404 = computed(() => props.error?.statusCode === 404)
</script>

<template>
  <div class="container narrow">
    <div class="card section">
      <h1>{{ is404 ? 'That page does not exist' : 'Something went wrong' }}</h1>
      <p class="muted">
        {{ is404
          ? 'The link may be out of date, or the unit or guide is not in the index yet.'
          : 'This is our problem, not your connection. Try again in a moment.' }}
      </p>
      <div class="actions">
        <NuxtLink to="/" class="btn">Go home</NuxtLink>
        <NuxtLink to="/search" class="btn btn--ghost">Search Monash Hub</NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.narrow { max-width: 620px; margin-top: var(--s7); }
.section { padding: var(--s6); text-align: center; }
.actions { display: flex; gap: var(--s3); justify-content: center; flex-wrap: wrap; }
</style>
