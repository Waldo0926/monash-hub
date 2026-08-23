<script setup lang="ts">
defineProps<{ page: any }>()
const { $t } = useNuxtApp()
</script>

<template>
  <NuxtLink :to="`/guides/${page.slug}`" class="guide card">
    <div class="top">
      <SourceBadge kind="official" />
      <span class="tiny muted">{{ $t(`category.${page.category}`) }}</span>
    </div>
    <h3>{{ page.title }}</h3>
    <p class="small muted summary">{{ page.summary }}</p>
    <LastChecked :value="page.last_checked" />
  </NuxtLink>
</template>

<style scoped>
.guide { display: block; padding: var(--s4); color: inherit; }
.guide:hover { text-decoration: none; border-color: var(--border-strong); box-shadow: var(--shadow); }
.top { display: flex; align-items: center; justify-content: space-between; gap: var(--s3); margin-bottom: var(--s2); }
.guide h3 { font-size: 1rem; }
.summary {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
