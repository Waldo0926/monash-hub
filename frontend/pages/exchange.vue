<script setup lang="ts">
const { data } = await useApiFetch<any>('/v1/exchange')
useSeoMeta({
  title: 'Exchange — Monash Hub',
  description: 'Monash exchange and study abroad information. Integration with the Monash Abroad Tracker is planned.'
})
</script>

<template>
  <div class="container narrow">
    <h1>Exchange</h1>
    <div class="card section">
      <p>{{ data?.summary }}</p>
      <p class="tiny muted">Planned for {{ data?.stage }}.</p>
      <ul>
        <li v-for="topic in data?.topics || []" :key="topic.key">{{ topic.label }}</li>
      </ul>
      <p class="small">
        In the meantime, the official Monash exchange page is indexed under
        <NuxtLink to="/guides?category=exchange">Official guides</NuxtLink>, and exchange questions
        belong in <NuxtLink to="/community?category=exchange">Community</NuxtLink>.
      </p>
    </div>
  </div>
</template>

<style scoped>
.narrow { max-width: 720px; }
.section { padding: var(--s5); }
</style>
