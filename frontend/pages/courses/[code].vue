<script setup lang="ts">
/**
 * One degree, as the requirement outline the Handbook actually publishes.
 *
 * Not a graph. A prerequisite chain is a graph and is drawn as one on /tree; a
 * degree is a nested set of "complete N points from the following", and the
 * nesting is the meaning. C2001's Part D is five options of two units each,
 * and drawn flat it reads as ten units you must all pass - a different degree,
 * and one nobody could finish.
 *
 * Every unit named is resolved to its title and its offerings, and marked when
 * the chosen campus does not teach it. A requirement you cannot satisfy here
 * is the single most useful thing this page can tell a Malaysia student, and
 * it is the thing a list of bare codes hides completely.
 */
const route = useRoute()
const router = useRouter()
const { $t } = useNuxtApp()

const code = computed(() => String(route.params.code).toUpperCase())
const campus = ref(String(route.query.campus ?? 'Malaysia'))

const { data: course, error } = await useLocalisedApiFetch<any>(
  () => `/v1/courses/${code.value}${campus.value ? `?campus=${campus.value}` : ''}`,
  { watch: [campus] }
)

watch(campus, () => {
  router.replace({ query: campus.value ? { campus: campus.value } : {} })
})

const campusLabel = computed(() =>
  campus.value === 'Malaysia' ? $t('tree.campusMalaysia') : campus.value
)

const elsewhereTotal = computed(() => {
  const facts = course.value?.units || {}
  return Object.values(facts).filter((f: any) => f.in_year && !f.offered_at_campus).length
})

const open = reactive<Record<number, boolean>>({})
function toggle(id: number) {
  open[id] = !open[id]
}
function isOpen(id: number, depth: number) {
  return open[id] ?? depth === 0
}

useHead(() => ({ title: course.value ? `${code.value} ${course.value.title}` : code.value }))
</script>

<template>
  <div class="page">
    <ErrorState v-if="error" :error="error" />
    <template v-else-if="course">
      <header class="head">
        <p class="crumb"><NuxtLink to="/courses">{{ $t('courses.title') }}</NuxtLink></p>
        <h1>{{ course.title }}</h1>
        <p class="sub">
          <span class="code">{{ course.course_code }}</span>
          <span v-if="course.abbreviated_name">{{ course.abbreviated_name }}</span>
        </p>
        <dl class="facts">
          <div v-if="course.credit_points"><dt>{{ $t('courses.creditPoints') }}</dt><dd>{{ course.credit_points }}</dd></div>
          <div v-if="course.duration_years"><dt>{{ $t('courses.duration') }}</dt><dd>{{ $t('courses.years', { n: course.duration_years }) }}</dd></div>
          <div v-if="course.aqf_level"><dt>{{ $t('courses.aqf') }}</dt><dd>{{ course.aqf_level }}</dd></div>
          <div v-if="course.faculty"><dt>{{ $t('courses.faculty') }}</dt><dd>{{ course.faculty }}</dd></div>
          <div v-if="course.campuses?.length"><dt>{{ $t('tree.campus') }}</dt><dd>{{ course.campuses.join(' · ') }}</dd></div>
        </dl>
      </header>

      <div class="bar">
        <label class="campus">
          <span>{{ $t('courses.viewAs') }}</span>
          <select v-model="campus" class="input">
            <option value="Malaysia">{{ $t('tree.campusMalaysia') }}</option>
            <option value="Clayton">Clayton</option>
            <option value="">{{ $t('tree.campusAny') }}</option>
          </select>
        </label>
        <p v-if="campus && elsewhereTotal" class="warn">
          {{ $t('courses.notHere', { n: elsewhereTotal, campus: campusLabel }) }}
        </p>
      </div>

      <p v-if="course.overview" class="overview">{{ course.overview }}</p>

      <section class="structure">
        <h2>{{ $t('courses.structure') }}</h2>
        <CourseRequirement
          v-for="node in course.containers"
          :key="node.id"
          :node="node"
          :units="course.units"
          :campus="campus"
          :depth="0"
          :open="isOpen(node.id, 0)"
          @toggle="toggle"
        />
      </section>

      <section v-if="course.areas_of_study?.length" class="aos">
        <h2>{{ $t('courses.areasOfStudy') }}</h2>
        <ul>
          <li v-for="a in course.areas_of_study" :key="a.code">
            <NuxtLink :to="`/courses/aos/${a.code}`">
              <span class="code">{{ a.code }}</span>
              <span>{{ a.title }}</span>
              <span class="muted">{{ a.aos_type }}<template v-if="a.credit_points"> · {{ a.credit_points }} cp</template></span>
            </NuxtLink>
          </li>
        </ul>
      </section>

      <LastChecked v-if="course.last_checked" :at="course.last_checked" :url="course.source_url" />
    </template>
  </div>
</template>

<style scoped>
.page { max-width: 900px; margin: 0 auto; padding: var(--s5) var(--s4) var(--s7); }
.crumb { margin: 0 0 var(--s2); font-size: 0.85rem; }
.head h1 { margin: 0 0 var(--s2); }
.sub { display: flex; gap: var(--s3); align-items: baseline; margin: 0 0 var(--s4); color: var(--muted); }
.code { font: 600 0.9rem var(--font-mono); color: var(--navy); }

.facts { display: flex; flex-wrap: wrap; gap: var(--s4); margin: 0 0 var(--s4); }
.facts div { display: grid; gap: 2px; }
.facts dt { font-size: 0.75rem; color: var(--muted); }
.facts dd { margin: 0; font-weight: 500; }

.bar { display: flex; flex-wrap: wrap; gap: var(--s3); align-items: end; margin-bottom: var(--s4); }
.campus { display: grid; gap: var(--s1); font-size: 0.85rem; color: var(--muted); }
.input {
  padding: var(--s2) var(--s3); border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm); font: inherit; background: var(--surface); color: var(--text);
}
.warn {
  margin: 0; padding: var(--s2) var(--s3); border-radius: var(--radius-sm);
  background: var(--warning-bg); color: var(--warning); font-size: 0.85rem;
}
.overview { color: var(--text); white-space: pre-line; margin: 0 0 var(--s6); }

.structure h2, .aos h2 { font-size: 1.05rem; margin: 0 0 var(--s3); }
.structure { margin-bottom: var(--s6); }

.aos ul { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--s2); }
.aos a {
  display: flex; gap: var(--s3); align-items: baseline; padding: var(--s3);
  border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--surface); color: inherit; text-decoration: none;
}
.aos a:hover { border-color: var(--blue); }
.muted { color: var(--muted); font-size: 0.8rem; margin-left: auto; }
</style>
