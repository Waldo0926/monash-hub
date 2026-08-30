<script setup lang="ts">
/**
 * The degree picker.
 *
 * Campus filters this list rather than marking it, which is the opposite of
 * the unit tree. There a prerequisite Malaysia does not teach still has to be
 * shown, because the rule names it and the student has to satisfy it some
 * other way. Here there is no other way: a degree that is not taught at your
 * campus is not one you can enrol in, and listing it would be offering
 * something that does not exist.
 */
const route = useRoute()
const router = useRouter()
const { $t } = useNuxtApp()

const q = ref(String(route.query.q || ''))
const campus = ref(String(route.query.campus ?? 'Malaysia'))
const draft = ref(q.value)

const query = computed(() => {
  const params = new URLSearchParams({ limit: '200' })
  if (q.value) params.set('q', q.value)
  if (campus.value) params.set('campus', campus.value)
  return params.toString()
})

const { data, pending } = await useLocalisedApiFetch<any>(
  () => `/v1/courses?${query.value}`,
  { watch: [q, campus] }
)

watch([q, campus], () => {
  router.replace({
    query: { ...(q.value ? { q: q.value } : {}), ...(campus.value ? { campus: campus.value } : {}) }
  })
})

function search() {
  q.value = draft.value.trim()
}

const campusLabel = computed(() =>
  campus.value === 'Malaysia' ? $t('tree.campusMalaysia') : campus.value
)

/** Undergraduate before postgraduate, then research - how a student looks. */
const ORDER = [
  'UG specialist',
  'UG comprehensive',
  'UG double',
  'Vertical double',
  'Honours - 1 yr',
  'UG diploma',
  'PG Grad Cert / Grad Dip',
  'PG Masters',
  'PG coursework double',
  'Masters by research',
  'Doctorate by research',
  'Higher doctorate',
  'Non award pathway',
  'Other'
]

const TYPE_KEYS: Record<string, string> = {
  'UG specialist': 'courses.type.ugSpecialist',
  'UG comprehensive': 'courses.type.ugComprehensive',
  'UG double': 'courses.type.ugDouble',
  'Vertical double': 'courses.type.verticalDouble',
  'Honours - 1 yr': 'courses.type.honoursOneYear',
  'UG diploma': 'courses.type.ugDiploma',
  'PG Grad Cert / Grad Dip': 'courses.type.pgCertificateDiploma',
  'PG Masters': 'courses.type.pgMasters',
  'PG coursework double': 'courses.type.pgCourseworkDouble',
  'Masters by research': 'courses.type.mastersResearch',
  'Doctorate by research': 'courses.type.doctorateResearch',
  'Higher doctorate': 'courses.type.higherDoctorate',
  'Non award pathway': 'courses.type.nonAward',
  'Other': 'courses.otherType'
}

function typeLabel(type: string) {
  const key = TYPE_KEYS[type]
  return key ? $t(key) : type
}

const grouped = computed(() => {
  const buckets = new Map<string, any[]>()
  for (const course of data.value?.results || []) {
    const key = course.course_type_raw || course.course_type || 'Other'
    if (!buckets.has(key)) buckets.set(key, [])
    buckets.get(key)!.push(course)
  }
  return [...buckets.entries()].sort((a, b) => {
    const ia = ORDER.indexOf(a[0])
    const ib = ORDER.indexOf(b[0])
    return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib) || a[0].localeCompare(b[0])
  })
})

useHead({ title: $t('courses.title') })
</script>

<template>
  <div class="page">
    <header class="intro">
      <h1>{{ $t('courses.title') }}</h1>
      <p class="lede">{{ $t('courses.lede') }}</p>
    </header>

    <div class="controls">
      <form class="finder" @submit.prevent="search">
        <input
          v-model="draft"
          class="input"
          :placeholder="$t('courses.searchPlaceholder')"
          :aria-label="$t('courses.search')"
          autocomplete="off"
        />
        <button class="btn btn--primary" type="submit">{{ $t('courses.search') }}</button>
      </form>
      <label class="campus">
        <span>{{ $t('tree.campus') }}</span>
        <select v-model="campus" class="input">
          <option value="Malaysia">{{ $t('tree.campusMalaysia') }}</option>
          <option value="Clayton">Clayton</option>
          <option value="">{{ $t('tree.campusAny') }}</option>
        </select>
      </label>
    </div>

    <p v-if="!pending" class="count">
      {{ campus ? $t('courses.countAt', { n: data?.total ?? 0, campus: campusLabel }) : $t('courses.count', { n: data?.total ?? 0 }) }}
    </p>

    <Skeleton v-if="pending" :lines="8" />
    <EmptyState v-else-if="!data?.total" :title="$t('courses.noneTitle')" :body="$t('courses.noneBody')" />

    <section v-for="[type, courses] in grouped" v-else :key="type" class="group">
      <h2>{{ typeLabel(type) }}</h2>
      <ul class="cards">
        <li v-for="course in courses" :key="course.course_code">
          <CourseCard :course="course" />
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.page { max-width: var(--container); margin: 0 auto; padding: var(--s5) var(--s4) var(--s7); }
.intro h1 { margin: 0 0 var(--s2); }
.lede { color: var(--muted); margin: 0 0 var(--s5); max-width: var(--measure-lede); }

.controls { display: flex; flex-wrap: wrap; gap: var(--s3); align-items: end; margin-bottom: var(--s3); }
.finder { display: flex; gap: var(--s2); flex: 1 1 320px; }
.campus { display: grid; gap: var(--s1); font-size: 0.85rem; color: var(--muted); }
.input {
  width: 100%; padding: var(--s2) var(--s3); border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm); font: inherit; background: var(--surface); color: var(--text);
}
.count { color: var(--muted); font-size: 0.9rem; margin: 0 0 var(--s5); }

.group { margin-bottom: var(--s6); }
.group h2 { font-size: 1rem; color: var(--muted); font-weight: 600; margin: 0 0 var(--s3); }
.cards { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--s2); }
</style>
