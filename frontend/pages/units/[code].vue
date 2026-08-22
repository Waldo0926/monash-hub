<script setup lang="ts">
/**
 * Unit detail - the first page that shows what the product is for. Everything
 * on it is a parsed Handbook field, with the source and the check date in
 * view, plus the zero-AI ask box and any related community threads.
 */
const route = useRoute()
const config = useRuntimeConfig()
const code = computed(() => String(route.params.code).toUpperCase())

const { data: unit, error } = await useApiFetch<any>(() => `/v1/units/${code.value}`)
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
    answer.value = await apiFetch<any>('/v1/ask', { method: 'POST', body: { query: q } })
  } finally {
    asking.value = false
  }
}

const suggestions = computed(() => [
  `Does ${code.value} have a final exam?`,
  `What are the prerequisites for ${code.value}?`,
  `Is ${code.value} offered in Malaysia?`
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
            <p class="tiny muted"><NuxtLink to="/units">Units</NuxtLink> / {{ unit.unit_code }}</p>
            <h1><span class="mono">{{ unit.unit_code }}</span> · {{ unit.title }}</h1>
          </div>
          <SourceBadge kind="handbook" />
        </div>
        <p class="chips">
          <span class="chip">{{ unit.academic_year }} Handbook</span>
          <span v-if="unit.credit_points" class="chip">{{ unit.credit_points }} credit points</span>
          <span v-if="unit.level" class="chip">{{ unit.level }}</span>
          <span v-if="unit.faculty" class="chip">{{ unit.faculty }}</span>
        </p>
        <LastChecked :value="unit.last_checked" />
      </header>

      <div class="body">
        <div class="content stack">
          <section v-if="unit.overview" id="overview" class="card section">
            <h2>Overview</h2>
            <p class="pre">{{ unit.overview }}</p>
            <p v-if="unit.areas_of_study" class="small muted">Areas of study: {{ unit.areas_of_study }}</p>
          </section>

          <section id="offerings" class="card section">
            <h2>Offerings</h2>
            <div v-if="unit.offerings.length" class="scroll-x">
              <table>
                <thead>
                  <tr><th>Campus</th><th>Teaching period</th><th>Mode</th></tr>
                </thead>
                <tbody>
                  <tr v-for="(offering, i) in unit.offerings" :key="i">
                    <td>{{ offering.campus || '—' }}</td>
                    <td>{{ offering.teaching_period || '—' }}</td>
                    <td>{{ offering.attendance_mode || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="muted small">The Handbook publishes no offerings for this unit.</p>
          </section>

          <section id="assessment" class="card section">
            <h2>Assessment</h2>
            <p class="verdict small">
              <template v-if="unit.has_exam === true">The Handbook lists an examination for this unit.</template>
              <template v-else-if="unit.has_exam === false">
                The Handbook does not list a final examination among the assessment items. That is
                not a guarantee there is none.
              </template>
              <template v-else>The Handbook publishes no assessment items for this unit yet.</template>
            </p>
            <div v-if="unit.assessments.length" class="scroll-x">
              <table>
                <thead>
                  <tr><th>#</th><th>Assessment</th><th>Type</th><th>Weight</th><th>Hurdle</th></tr>
                </thead>
                <tbody>
                  <tr v-for="item in unit.assessments" :key="item.number">
                    <td>{{ item.number }}</td>
                    <td>{{ item.name }}</td>
                    <td>{{ item.type || '—' }}</td>
                    <td>{{ item.weight ? `${item.weight}%` : '—' }}</td>
                    <td>{{ item.hurdle || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-if="unit.assessment_summary" class="small pre muted">{{ unit.assessment_summary }}</p>
            <p v-if="unit.assessment_static_text" class="tiny muted pre">{{ unit.assessment_static_text }}</p>
          </section>

          <section id="requisites" class="card section">
            <h2>Requisites</h2>
            <template v-if="unit.requisites.length">
              <div v-for="(groups, type) in requisitesByType" :key="type" class="req">
                <h3 class="req-type">{{ type }}</h3>
                <div v-for="(group, gi) in groups" :key="gi" class="req-group">
                  <p v-if="group.description" class="small pre">{{ group.description }}</p>
                  <ul v-if="group.items.length">
                    <li v-for="item in group.items" :key="item.code">
                      <NuxtLink :to="`/units/${item.code}`" class="mono">{{ item.code }}</NuxtLink>
                      <span class="muted"> — {{ item.name }}</span>
                    </li>
                  </ul>
                  <p v-if="group.connector && group.items.length > 1" class="tiny muted">
                    Joined by {{ group.connector }}.
                  </p>
                </div>
              </div>
            </template>
            <p v-else class="muted small">
              The Handbook lists no prerequisite, corequisite or prohibition for this unit.
            </p>
          </section>

          <section v-if="unit.learning_outcomes.length" id="outcomes" class="card section">
            <h2>Learning outcomes</h2>
            <ol class="outcomes">
              <li v-for="outcome in unit.learning_outcomes" :key="outcome.code">
                {{ outcome.description }}
              </li>
            </ol>
          </section>

          <section id="workload" class="card section">
            <h2>Workload</h2>
            <p v-if="unit.workload_requirements" class="pre">{{ unit.workload_requirements }}</p>
            <div v-if="unit.activities.length" class="scroll-x">
              <table>
                <thead><tr><th>Activity</th><th>Duration</th></tr></thead>
                <tbody>
                  <tr v-for="(activity, i) in unit.activities" :key="i">
                    <td>{{ activity.activity_type }}</td>
                    <td>{{ activity.name || '—' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-if="!unit.workload_requirements && !unit.activities.length" class="muted small">
              No workload detail published.
            </p>
          </section>

          <section id="ask" class="card section ask">
            <h2>Ask about {{ unit.unit_code }}</h2>
            <p class="tiny muted">
              Answered from the Handbook fields above - no AI, no guessing. Every answer links back
              to the source.
            </p>
            <SearchInput
              v-model="question"
              :placeholder="`${unit.unit_code} 有考试吗？`"
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
              <h2>Community discussions about {{ unit.unit_code }}</h2>
              <SourceBadge kind="community" />
            </div>
            <p class="tiny muted">
              Student experience, not official rules. Nothing here changes what the Handbook says.
            </p>
            <div v-if="discussions?.results?.length" class="grid">
              <PostCard v-for="post in discussions.results" :key="post.id" :post="post" />
            </div>
            <EmptyState
              v-else
              title="No discussions yet"
              hint="Be the first to share what this unit was actually like."
            >
              <NuxtLink :to="`/community?unit=${unit.unit_code}`" class="btn">Start a discussion</NuxtLink>
            </EmptyState>
          </section>
        </div>

        <aside class="side">
          <nav class="card section nav" aria-label="On this page">
            <h2 class="small">On this page</h2>
            <a href="#overview">Overview</a>
            <a href="#offerings">Offerings</a>
            <a href="#assessment">Assessment</a>
            <a href="#requisites">Requisites</a>
            <a href="#outcomes">Learning outcomes</a>
            <a href="#workload">Workload</a>
            <a href="#ask">Ask about this unit</a>
            <a href="#community">Community</a>
          </nav>
          <div class="card section">
            <h2 class="small">Official source</h2>
            <p class="small">
              <a :href="unit.source_url" rel="noopener external" target="_blank">
                Monash Handbook {{ unit.academic_year }} ↗
              </a>
            </p>
            <LastChecked :value="unit.last_checked" />
            <p class="tiny muted">
              Handbook version {{ unit.handbook_version || 'unknown' }}. Assessment detail for a
              specific teaching period is confirmed in Moodle.
            </p>
          </div>
        </aside>
      </div>
    </article>
  </div>
</template>

<style scoped>
.head { padding: var(--s5); margin-bottom: var(--s5); }
.head-top { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--s4); }
.head h1 { margin-bottom: var(--s3); }
.chips { display: flex; flex-wrap: wrap; gap: var(--s2); margin-bottom: var(--s2); }
.chip { padding: 2px 10px; border-radius: var(--radius-pill); background: var(--surface-2); font-size: 0.78rem; }

.body { display: grid; grid-template-columns: 1fr 280px; gap: var(--s5); align-items: start; }
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
