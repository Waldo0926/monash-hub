<script setup lang="ts">
/**
 * One degree as a link. The full card is a single row for wide lists such as
 * search results; `compact` stacks the facts under the name so it fits the
 * narrower panels on the degree page.
 */
defineProps<{ course: any; compact?: boolean }>()

const { $t } = useNuxtApp()
const { withYear } = useHandbookYear()
</script>

<template>
  <NuxtLink
    class="course-card"
    :class="{ 'course-card--compact': compact }"
    :to="withYear(`/courses/${course.course_code}`)"
  >
    <span class="code">{{ course.course_code }}</span>
    <span class="name">{{ course.title }}</span>
    <span v-if="compact" class="meta">
      <span v-if="course.credit_points" class="fact">{{ course.credit_points }} cp</span>
      <span v-if="course.duration_years" class="fact">{{ $t('courses.years', { n: course.duration_years }) }}</span>
      <span v-for="campus in course.campuses" :key="campus" class="chip">{{ campus }}</span>
    </span>
    <span v-else class="facts">
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

/* Inside a panel the panel draws the box, so a row is just a hover band. */
.course-card--compact {
  grid-template-columns: 64px minmax(0, 1fr); row-gap: 2px;
  padding: var(--s2) var(--s4); border: 0; border-radius: 0; background: transparent;
}
.course-card--compact:hover { box-shadow: none; background: var(--blue-50); }
.course-card--compact:focus-visible { outline-offset: -2px; }
.course-card--compact .meta {
  grid-column: 2; display: flex; flex-wrap: wrap; align-items: center; gap: var(--s1) var(--s2);
  font-size: 0.8rem; color: var(--muted);
}
.course-card--compact .fact + .fact::before { content: '·'; margin-right: var(--s2); color: var(--muted-2); }
.course-card--compact .chip { font-size: 0.75rem; padding: 0 var(--s2); }

@media (max-width: 700px) {
  .course-card { grid-template-columns: minmax(0, 1fr); gap: var(--s1); }
  .course-card--compact { grid-template-columns: 56px minmax(0, 1fr); gap: 2px var(--s2); }
}
</style>
