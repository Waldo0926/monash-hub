<script setup lang="ts">
defineProps<{ course: any }>()

const { $t } = useNuxtApp()
</script>

<template>
  <NuxtLink class="course-card" :to="`/courses/${course.course_code}`">
    <span class="code">{{ course.course_code }}</span>
    <span class="name">{{ course.title }}</span>
    <span class="facts">
      <span v-if="course.credit_points">{{ course.credit_points }} cp</span>
      <span v-if="course.duration_years">{{ $t('courses.years', { n: course.duration_years }) }}</span>
      <span v-for="campus in course.campuses" :key="campus" class="chip">{{ campus }}</span>
    </span>
  </NuxtLink>
</template>

<style scoped>
.course-card {
  display: grid; grid-template-columns: 72px minmax(12rem, 1fr) minmax(0, 2fr); gap: var(--s3);
  align-items: baseline; padding: var(--s3) var(--s4); background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--radius); color: inherit;
  text-decoration: none;
}
.course-card:hover { border-color: var(--blue); box-shadow: var(--shadow-sm); }
.code { font: 600 0.85rem var(--font-mono); color: var(--navy); }
.name { font-weight: 500; }
.facts {
  display: flex; flex-wrap: wrap; justify-content: flex-end; gap: var(--s2);
  align-items: center; min-width: 0; font-size: 0.8rem; color: var(--muted);
}
.chip {
  background: var(--surface-2); border-radius: var(--radius-pill);
  padding: 2px var(--s2); white-space: nowrap;
}

@media (max-width: 700px) {
  .course-card { grid-template-columns: minmax(0, 1fr); gap: var(--s1); }
}
</style>
