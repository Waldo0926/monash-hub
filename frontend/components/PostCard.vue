<script setup lang="ts">
defineProps<{ post: any }>()
</script>

<template>
  <NuxtLink :to="`/community/post/${post.id}`" class="post card">
    <div class="top">
      <SourceBadge kind="community" />
      <span v-if="post.is_solved" class="solved tiny">Marked helpful</span>
    </div>
    <h3>{{ post.title }}</h3>
    <p class="tiny muted">
      {{ post.author || 'unknown' }} · {{ post.answer_count }} answers
      <span v-if="post.unit_code"> · <span class="mono">{{ post.unit_code }}</span></span>
    </p>
  </NuxtLink>
</template>

<style scoped>
.post { display: block; padding: var(--s4); color: inherit; }
.post:hover { text-decoration: none; border-color: var(--border-strong); box-shadow: var(--shadow); }
.top { display: flex; align-items: center; gap: var(--s3); margin-bottom: var(--s2); }
.post h3 { font-size: 1rem; margin-bottom: var(--s2); }
.solved { color: var(--success); font-weight: 600; }
</style>
