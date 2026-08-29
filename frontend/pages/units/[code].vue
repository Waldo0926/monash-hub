<script setup lang="ts">
/**
 * Unit detail - the first page that shows what the product is for. Everything
 * on it is a parsed Handbook field, with the source and the check date in
 * view, plus the zero-AI ask box and any related community threads.
 */
const route = useRoute()
const config = useRuntimeConfig()
const { $t } = useNuxtApp()
const { locale } = useLocale()
const code = computed(() => String(route.params.code).toUpperCase())

const { data: unit, error } = await useLocalisedApiFetch<any>(() => `/v1/units/${code.value}`)
const { data: discussions } = await useApiFetch<any>(
  () => `/v1/community/posts?unit_code=${code.value}&limit=5`
)

const question = ref('')
const answer = ref<any>(null)
const asking = ref(false)

async function ask(text?: string) {
  const q = (text ?? question.value).trim()
  if (!q) return
  question.value = q
  asking.value = true
  try {
    answer.value = await apiFetch<any>(`/v1/ask?locale=${locale.value}`, {
      method: 'POST',
      body: { query: q }
    })
  } finally {
    asking.value = false
  }
}

const suggestions = computed(() => [
  $t('unit.suggestExam', { code: code.value }),
  $t('unit.suggestPrereq', { code: code.value }),
  $t('unit.suggestMalaysia', { code: code.value })
])

const requisitesByType = computed(() => {
  const groups: Record<string, any[]> = {}
  for (const group of unit.value?.requisites || []) {
    ;(groups[group.requisite_type] ||= []).push(group)
  }
  return groups
})

useSeoMeta({
  title: () => (unit.value ? `${unit.value.unit_code} ${unit.value.title} — Monash Hub` : 'Unit — Monash Hub'),
  description: () =>
    unit.value
      ? `${unit.value.unit_code} ${unit.value.title}: assessment, requisites, offerings and workload from the ${unit.value.academic_year} Monash Handbook.`
      : '',
  ogTitle: () => (unit.value ? `${unit.value.unit_code} · ${unit.value.title}` : '')
})
useHead(() => ({
  link: [{ rel: 'canonical', href: `${config.public.siteUrl}/units/${code.value}` }]
}))
</script>

<template>
  <div class="container">
    <ErrorState v-if="error" :error="error" />

    <article v-else-if="unit" class="unit">
      <header class="head card">
        <div class="head-top">
          <div>
            <p class="tiny muted">
              <NuxtLink to="/units">{{ $t('nav.units') }}</NuxtLink> / {{ unit.unit_code }}
            </p>
            <h1><span class="mono">{{ unit.unit_code }}</span> · {{ unit.title }}</h1>
          </div>
          <SourceBadge kind="handbook" />
        </div>
        <p class="chips">
          <span class="chip">{{ $t('unit.handbookYear', { year: unit.academic_year }) }}</span>
          <span v-if="unit.credit_points" class="chip">
            {{ unit.credit_points }} {{ $t('units.creditPoints') }}
          </span>
          <span v-if="unit.level" class="chip">{{ $term('level', unit.level) }}</span>
          <span v-if="unit.faculty" class="chip">{{ $term('faculty', unit.faculty) }}</span>
        </p>
        <LastChecked :value="unit.last_checked" />
      </header>

      <div class="body">
        <div class="content stack">
          <section v-if="unit.overview" id="overview" class="card section">
            <h2>{{ $t('unit.overview') }}</h2>
            <TranslationNotice
              v-if="unit.translation"
              :translation="unit.translation"
              :source-url="unit.source_url"
              class="mb"
            />
            <p class="pre">{{ unit.overview }}</p>
            <p v-if="unit.areas_of_study" class="small muted">
              {{ $t('unit.areasOfStudy') }}: {{ unit.areas_of_study }}
            </p>
          </section>

          <section id="offerings" class="card section">
            <h2>{{ $t('unit.offerings') }}</h2>
            <div v-if="unit.offerings.length" class="scroll-x">
              <table>
                <thead>
                  <tr>
                    <th>{{ $t('unit.colCampus') }}</th>
                    <th>{{ $t('unit.colPeriod') }}</th>
                    <th>{{ $t('unit.colMode') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(offering, i) in unit.offerings" :key="i">
                    <td>{{ $term('campus', offering.campus) || '—' }}</td>
                    <td>{{ $term('period', offering.teaching_period) || '—' }}</td>
                    <td>{{ $term('mode', offering.attendance_mode) || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="muted small">{{ $t('unit.noOfferingsPublished') }}</p>
          </section>

          <section id="assessment" class="card section">
            <h2>{{ $t('unit.assessment') }}</h2>
            <p class="verdict small">
              <template v-if="unit.has_exam === true">{{ $t('unit.examYes') }}</template>
              <template v-else-if="unit.has_exam === false">{{ $t('unit.examNo') }}</template>
              <template v-else>{{ $t('unit.examUnknown') }}</template>
            </p>
            <div v-if="unit.assessments.length" class="scroll-x">
              <table>
                <thead>
                  <tr>
                    <th>{{ $t('unit.colNumber') }}</th>
                    <th>{{ $t('unit.colAssessment') }}</th>
                    <th>{{ $t('unit.colType') }}</th>
                    <th>{{ $t('unit.colWeight') }}</th>
                    <th>{{ $t('unit.colHurdle') }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in unit.assessments" :key="item.number">
                    <td>{{ item.number }}</td>
                    <td>{{ $assessmentName(item.name) }}</td>
                    <td>{{ $term('assessmentType', item.type) || '—' }}</td>
                    <td>{{ item.weight ? `${item.weight}%` : '—' }}</td>
                    <td>{{ $term('hurdle', item.hurdle) || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-if="unit.assessment_summary" class="small pre muted">{{ unit.assessment_summary }}</p>
            <p v-if="unit.assessment_static_text" class="tiny muted pre">{{ unit.assessment_static_text }}</p>
          </section>

          <section id="requisites" class="card section">
            <h2>{{ $t('unit.requisites') }}</h2>
            <template v-if="unit.requisites.length">
              <div v-for="(groups, type) in requisitesByType" :key="type" class="req">
                <h3 class="req-type">{{ $term('requisiteType', String(type)) }}</h3>
                <RequisiteRule
                  v-for="(group, gi) in groups"
                  :key="gi"
                  :rule="group"
                  class="req-group"
                />
              </div>
            </template>
            <p v-else class="muted small">{{ $t('unit.noRequisites') }}</p>
          </section>

          <section v-if="unit.learning_outcomes.length" id="outcomes" class="card section">
            <h2>{{ $t('unit.outcomes') }}</h2>
            <ol class="outcomes">
              <li v-for="outcome in unit.learning_outcomes" :key="outcome.code">
                {{ outcome.description }}
              </li>
            </ol>
          </section>

          <section id="workload" class="card section">
            <h2>{{ $t('unit.workload') }}</h2>
            <p v-if="unit.workload_requirements" class="pre">{{ unit.workload_requirements }}</p>
            <div v-if="unit.activities.length" class="scroll-x">
              <table>
                <thead>
                  <tr><th>{{ $t('unit.colActivity') }}</th><th>{{ $t('unit.colDuration') }}</th></tr>
                </thead>
                <tbody>
                  <tr v-for="(activity, i) in unit.activities" :key="i">
                    <td>{{ $term('activityType', activity.activity_type) }}</td>
                    <td>{{ activity.name || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-if="!unit.workload_requirements && !unit.activities.length" class="muted small">
              {{ $t('unit.noWorkload') }}
            </p>
          </section>

          <section id="ask" class="card section ask">
            <h2>{{ $t('unit.askAbout', { code: unit.unit_code }) }}</h2>
            <p class="tiny muted">{{ $t('unit.askHint') }}</p>
            <SearchInput
              v-model="question"
              :placeholder="$t('unit.askPlaceholder', { code: unit.unit_code })"
              @submit="ask"
            />
            <p class="suggestions tiny">
              <button v-for="s in suggestions" :key="s" class="chip-btn" @click="ask(s)">{{ s }}</button>
            </p>
            <Skeleton v-if="asking" :lines="3" />
            <AnswerBlocks v-else-if="answer" :answer="answer" class="answer" />
          </section>

          <section id="community" class="card section">
            <div class="section-head">
              <h2>{{ $t('unit.discussionsAbout', { code: unit.unit_code }) }}</h2>
              <SourceBadge kind="community" />
            </div>
            <p class="tiny muted">{{ $t('unit.discussionsNote') }}</p>
            <div v-if="discussions?.results?.length" class="grid">
              <PostCard v-for="post in discussions.results" :key="post.id" :post="post" />
            </div>
            <EmptyState
              v-else
              :title="$t('unit.noDiscussions')"
              :hint="$t('unit.noDiscussionsHint')"
            >
              <NuxtLink :to="`/community?unit=${unit.unit_code}`" class="btn">
                {{ $t('unit.startDiscussion') }}
              </NuxtLink>
            </EmptyState>
          </section>
        </div>

        <aside class="side">
          <nav class="card section nav" :aria-label="$t('unit.onThisPage')">
            <h2 class="small">{{ $t('unit.onThisPage') }}</h2>
            <a href="#overview">{{ $t('unit.overview') }}</a>
            <a href="#offerings">{{ $t('unit.offerings') }}</a>
            <a href="#assessment">{{ $t('unit.assessment') }}</a>
            <a href="#requisites">{{ $t('unit.requisites') }}</a>
            <a href="#outcomes">{{ $t('unit.outcomes') }}</a>
            <a href="#workload">{{ $t('unit.workload') }}</a>
            <a href="#ask">{{ $t('unit.askAbout', { code: unit.unit_code }) }}</a>
            <a href="#community">{{ $t('nav.community') }}</a>
          </nav>
          <div class="card section">
            <h2 class="small">{{ $t('unit.officialSource') }}</h2>
            <p class="small">
              <a :href="unit.source_url" rel="noopener external" target="_blank">
                Monash Handbook {{ unit.academic_year }} ↗
              </a>
            </p>
            <LastChecked :value="unit.last_checked" />
            <p class="tiny muted">
              {{ $t('unit.handbookVersion', { version: unit.handbook_version || '—' }) }}
              {{ $t('unit.moodleNote') }}
            </p>
          </div>
        </aside>
      </div>
    </article>
  </div>
</template>

<style scoped>
.mb { margin-bottom: var(--s5); }
.head { padding: var(--s5); margin-bottom: var(--s5); }
.head-top { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--s4); }
.head h1 { margin-bottom: var(--s3); }
.chips { display: flex; flex-wrap: wrap; gap: var(--s2); margin-bottom: var(--s2); }
.chip { padding: 2px 10px; border-radius: var(--radius-pill); background: var(--surface-2); font-size: 0.78rem; }

.body { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: var(--s5); align-items: start; }
/* A grid item defaults to min-width:auto, so a wide table inside .scroll-x
   stretches its own column instead of scrolling, and the whole page ends up
   scrolling sideways on a phone. This is the line that keeps the scroll inside
   the table where it belongs. */
.body > * { min-width: 0; }
.section { padding: var(--s5); }
.section-head { display: flex; align-items: center; justify-content: space-between; gap: var(--s3); }
.pre { white-space: pre-line; }
.verdict {
  padding: var(--s3) var(--s4);
  border-left: 3px solid var(--blue);
  background: var(--blue-50);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.req + .req { margin-top: var(--s5); }
.req-type { text-transform: capitalize; }
.req-group ul { margin: var(--s2) 0; padding-left: var(--s5); }
.outcomes { padding-left: var(--s5); }
.outcomes li + li { margin-top: var(--s2); }
.suggestions { display: flex; flex-wrap: wrap; gap: var(--s2); margin: var(--s3) 0; }
.chip-btn {
  padding: 4px 12px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  background: var(--surface);
  font: inherit;
  font-size: 0.78rem;
  cursor: pointer;
}
.chip-btn:hover { background: var(--surface-2); }
.answer { margin-top: var(--s4); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--s3); }
.side { position: sticky; top: calc(var(--header-h) + var(--s4)); display: grid; gap: var(--s4); }
.nav { display: grid; gap: var(--s2); }
.nav a { font-size: 0.9rem; }

@media (max-width: 900px) {
  .body { grid-template-columns: 1fr; }
  .side { position: static; }
  .nav { display: none; }
}
</style>
