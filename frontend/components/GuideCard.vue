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
    <!-- The campus goes on the card, not only inside the page: a reader who
         never opens an Australian visa page cannot be misled by it. -->
    <CampusNotice :applies-to="page.applies_to" compact class="scope" />
    <span v-if="page.requires_sign_in" class="chip-signin">{{ $t('guides.signIn.label') }}</span>
    <p class="small muted summary">{{ page.summary }}</p>
  </NuxtLink>
</template>

<style scoped>
.guide { display: block; padding: var(--s4); color: inherit; }
.guide:hover { text-decoration: none; border-color: var(--border-strong); box-shadow: var(--shadow); }
.top { display: flex; align-items: center; justify-content: space-between; gap: var(--s3); margin-bottom: var(--s2); }
.guide h3 { font-size: 1rem; }
.scope { margin-bottom: var(--s2); }
.chip-signin {
  display: inline-block;
  margin: 0 0 var(--s2) var(--s1);
  padding: 2px var(--s2);
  border-radius: var(--radius-pill);
  font-size: 0.72rem;
  font-weight: 600;
  background: #f1ecf8;
  color: #4b2a7a;
}
.summary {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
