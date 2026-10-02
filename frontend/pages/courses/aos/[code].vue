<script setup lang="ts">
import { CAMPUS_CHOICES } from '~/composables/useCampuses'
/**
 * One major, minor or specialisation.
 *
 * The same outline as a degree, one level down, so it reuses the same
 * component. It is a page of its own because a course points at these by code:
 * C2001's Part C is four specialisations and nothing else, and without
 * somewhere to follow that to, Part C is a dead end.
 */
const route = useRoute()
const router = useRouter()
const { $t } = useNuxtApp()

const code = computed(() => String(route.params.code).toUpperCase())
const campus = ref(String(route.query.campus ?? 'Malaysia'))
const { year, withYear, setYear } = useHandbookYear()

const { data: aos, error } = await useLocalisedApiFetch<any>(
  () => withYear(`/v1/courses/aos/${code.value}${campus.value ? `?campus=${campus.value}` : ''}`),
  { watch: [campus, year] }
)

watch(campus, () => {
  // Kept apart from the year: changing campus must not drop `?year=`.
  const query = { ...route.query }
  if (campus.value) query.campus = campus.value
  else delete query.campus
  router.replace({ query })
})

/** The newest year that lists it is the default, so choosing it clears `?year=`. */
function pickYear(y: number) {
  setYear(y === aos.value?.available_years?.[0] ? null : y)
}

const campusName = useCampusName()
const campusLabel = computed(() => campusName(campus.value))

const elsewhereTotal = computed(() =>
  Object.values(aos.value?.units || {}).filter(
    (f: any) => f.in_year && !f.offered_at_campus
  ).length
)

useHead(() => ({ title: aos.value ? `${code.value} ${aos.value.title}` : code.value }))
</script>

<template>
  <div class="page">
    <ErrorState v-if="error" :error="error" />
    <template v-else-if="aos">
      <YearNotice v-if="aos.not_in_year" :code="aos.aos_code" :year="aos.academic_year" :missing="aos.not_in_year" />
      <header class="head">
        <p class="crumb"><NuxtLink to="/courses">{{ $t('courses.title') }}</NuxtLink></p>
        <h1>{{ aos.title }}</h1>
        <p class="sub">
          <span class="code">{{ aos.aos_code }}</span>
          <span v-if="aos.aos_type">{{ aos.aos_type }}</span>
          <span v-if="aos.credit_points">{{ aos.credit_points }} cp</span>
        </p>
      </header>

      <div class="bar">
        <label class="campus">
          <span>{{ $t('courses.viewAs') }}</span>
          <select v-model="campus" class="input">
            <option v-for="choice in CAMPUS_CHOICES" :key="choice" :value="choice">{{ campusName(choice) }}</option>
            <option value="">{{ $t('tree.campusAny') }}</option>
          </select>
        </label>
        <YearPicker
          v-if="(aos.available_years || []).length > 1"
          :model-value="aos.academic_year"
          :years="aos.available_years"
          @update:model-value="pickYear"
        />
        <p v-if="campus && elsewhereTotal" class="warn">
          {{ $t('courses.notHere', { n: elsewhereTotal, campus: campusLabel }) }}
        </p>
      </div>

      <p v-if="aos.overview" class="overview">{{ aos.overview }}</p>

      <section class="structure">
        <h2>{{ $t('courses.structure') }}</h2>
        <CourseRequirement
          v-for="node in aos.containers"
          :key="node.id"
          :node="node"
          :units="aos.units"
          :campus="campus"
          :depth="0"
        />
      </section>

      <LastChecked v-if="aos.last_checked" :at="aos.last_checked" :url="aos.source_url" />
    </template>
  </div>
</template>

<style scoped>
.page { max-width: 900px; margin: 0 auto; padding: var(--s5) var(--s4) var(--s7); }
.crumb { margin: 0 0 var(--s2); font-size: 0.85rem; }
.head h1 { margin: 0 0 var(--s2); }
.sub { display: flex; gap: var(--s3); align-items: baseline; margin: 0 0 var(--s4); color: var(--muted); }
.code { font: 600 0.9rem var(--font-mono); color: var(--navy); }
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
.overview { white-space: pre-line; margin: 0 0 var(--s6); }
.structure h2 { font-size: 1.05rem; margin: 0 0 var(--s3); }
</style>
