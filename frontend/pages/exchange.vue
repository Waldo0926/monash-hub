<script setup lang="ts">
const { $t } = useNuxtApp()
const { data } = await useLocalisedApiFetch<any>('/v1/exchange')

useSeoMeta({
  title: () => $t('exchange.metaTitle'),
  description:
    'Monash exchange and study abroad information. Integration with the Monash Abroad Tracker is planned.'
})
</script>

<template>
  <div class="container narrow">
    <h1>{{ $t('exchange.title') }}</h1>
    <div class="card section">
      <p>{{ data?.summary }}</p>
      <p class="tiny muted">{{ $t('exchange.planned', { stage: data?.stage || '' }) }}</p>
      <ul>
        <li v-for="topic in data?.topics || []" :key="topic.key">{{ topic.label }}</li>
      </ul>
      <p class="small">
        {{ $t('exchange.note') }}
      </p>
      <p class="small">
        <NuxtLink to="/guides?category=exchange">{{ $t('nav.guides') }}</NuxtLink> ·
        <NuxtLink to="/community?category=exchange">{{ $t('nav.community') }}</NuxtLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.narrow { max-width: 720px; }
.section { padding: var(--s5); }
</style>
