<script setup lang="ts">
/**
 * Every Monash Malaysia tuition fee on one page.
 *
 * The rows are the official /ugfees and /pgfees tables as last read, grouped the
 * way Monash groups them: by level, then by school. A degree page shows its own
 * row; this page is for comparing, and for the rows that are not one degree
 * (Monash English, a PhD in each school, the two DHES streams).
 */
import { feeNote, feeTitle, filterFees, formatAmount, type FeeRow } from '~/utils/tuition'

type Source = { title: string; url: string; level: string; last_checked: string | null }
type Table = {
  year: number | null
  sections: { source: string; level: string; schools: { school: string; rows: FeeRow[] }[] }[]
  general: string[]
  sources: Record<string, Source>
}

const { $t } = useNuxtApp()
const { locale } = useLocale()
const route = useRoute()
const router = useRouter()

const { data, error } = await useApiFetch<Table>('/v1/fees')
useErrorStatus(error)

const query = ref(String(route.query.q || ''))
watch(query, (q) => {
  router.replace({ query: q.trim() ? { q: q.trim() } : {} })
})

const sections = computed(() =>
  (data.value?.sections || [])
    .map(section => ({
      ...section,
      schools: section.schools
        .map(group => ({ ...group, rows: filterFees(group.rows, query.value) }))
        .filter(group => group.rows.length)
    }))
    .filter(section => section.schools.length)
)

const empty = computed(() => !data.value?.sections?.length)

function label(row: FeeRow) {
  const title = feeTitle(row, locale.value)
  return row.variant ? `${title} · ${row.variant}` : title
}

/** The undergraduate table gives a bare number of years ("3"). */
function duration(text: string) {
  return /^\d+(\.\d+)?$/.test(text) ? $t('courses.years', { n: text }) : text
}

function schoolName(key: string) {
  const text = $t(`fees.school.${key}`)
  return text === `fees.school.${key}` ? key : text
}

function modeName(mode: string | null) {
  if (!mode) return ''
  const key = `fees.mode.${mode.toLowerCase().replace(/\s+/g, '')}`
  const text = $t(key)
  return text === key ? mode : text
}

const title = computed(() =>
  data.value?.year ? $t('fees.title', { year: data.value.year }) : $t('fees.titleNoYear')
)
useSeoMeta({ title, description: () => $t('fees.lede') })
</script>

<template>
  <div class="page">
    <ErrorState v-if="error" :error="error" />
    <template v-else>
      <header class="intro">
        <p class="crumb"><NuxtLink to="/courses">{{ $t('courses.title') }}</NuxtLink></p>
        <h1>{{ title }}</h1>
        <p class="lede">{{ $t('fees.lede') }}</p>
      </header>

      <EmptyState v-if="empty" :title="$t('fees.emptyTitle')" :hint="$t('fees.emptyBody')" />
      <template v-else>
        <input
          v-model="query"
          class="field filter"
          type="search"
          :placeholder="$t('fees.filter')"
          :aria-label="$t('fees.filter')"
          autocomplete="off"
        />

        <ul class="keys small">
          <li>{{ $t('fees.keyBasis') }}</li>
          <li>{{ $t('fees.excludes') }}</li>
          <li>{{ $t('fees.noTotal') }}</li>
        </ul>

        <p v-if="!sections.length" class="small muted">{{ $t('fees.noMatch', { q: query }) }}</p>

        <section v-for="section in sections" :key="section.source" class="level">
          <h2>{{ $t(`fees.level.${section.level}`) }}</h2>
          <p class="tiny muted">
            <a :href="data!.sources[section.source]?.url" rel="noopener external" target="_blank">{{ data!.sources[section.source]?.title }}</a>
            <template v-if="data!.sources[section.source]?.last_checked">
              · <LastChecked :value="data!.sources[section.source]!.last_checked" />
            </template>
          </p>

          <div v-for="group in section.schools" :key="group.school" class="school">
            <h3>{{ schoolName(group.school) }}</h3>
            <div class="table" role="table" :aria-label="schoolName(group.school)">
              <div class="tr th" role="row">
                <span role="columnheader">{{ $t('fees.course') }}</span>
                <span role="columnheader">{{ $t('fees.domestic') }}</span>
                <span role="columnheader">{{ $t('fees.international') }}</span>
                <span role="columnheader">{{ $t('fees.basis') }}</span>
              </div>
              <div v-for="(row, i) in group.rows" :key="i" class="tr" role="row">
                <span class="name" role="cell">
                  <b>{{ label(row) }}</b>
                  <span v-if="locale === 'zh' && row.title_zh" class="tiny muted en">{{ row.title }}</span>
                  <span class="tiny muted">
                    <template v-if="row.duration && !row.variant">{{ duration(row.duration) }}</template>
                    <template v-if="row.mode"> · {{ modeName(row.mode) }}</template>
                  </span>
                  <span v-if="row.covers.length" class="tiny muted covers">
                    {{ $t('fees.covers') }}: {{ row.covers.join(', ') }}
                  </span>
                  <span v-if="row.note" class="tiny note">{{ feeNote(row.note, locale) }}</span>
                  <span v-if="row.unreadable" class="tiny warn">{{ $t('fees.unreadable') }}</span>
                </span>
                <span class="money" role="cell" :data-label="$t('fees.domestic')">
                  <span v-for="(a, n) in row.domestic" :key="n">
                    {{ formatAmount(a) }}<small v-if="a.label"> {{ a.label }}</small>
                  </span>
                </span>
                <span class="money" role="cell" :data-label="$t('fees.international')">
                  <span v-for="(a, n) in row.international" :key="n">
                    {{ formatAmount(a) }}<small v-if="a.label"> {{ a.label }}</small>
                  </span>
                </span>
                <span role="cell" :data-label="$t('fees.basis')">
                  <span v-if="row.basis" class="basis" :class="`basis--${row.basis}`">{{ $t(`fees.basis.${row.basis}`) }}</span>
                </span>
              </div>
            </div>
          </div>
        </section>

        <section v-if="data?.general?.length" class="general">
          <h2>{{ $t('fees.general') }}</h2>
          <ul class="small">
            <li v-for="line in data.general" :key="line">{{ line }}</li>
          </ul>
        </section>
      </template>
    </template>
  </div>
</template>

<style scoped>
.page { max-width: 960px; margin: 0 auto; padding: var(--s5) var(--s4) var(--s7); }
.crumb { margin: 0 0 var(--s2); font-size: 0.85rem; }
.intro h1 { margin: 0 0 var(--s2); }
.lede { margin: 0 0 var(--s4); color: var(--muted); }
.filter {
  width: 100%; max-width: 28rem; margin-bottom: var(--s3);
  padding: var(--s2) var(--s3); border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm); font: inherit; background: var(--surface); color: var(--text);
}
.keys { margin: 0 0 var(--s5); padding-left: 1.2em; color: var(--muted); display: grid; gap: var(--s1); }

.level { margin-bottom: var(--s6); }
.level h2 { margin: 0 0 var(--s1); font-size: 1.15rem; }
.level > .tiny { margin: 0 0 var(--s3); overflow-wrap: anywhere; }
.school { margin-bottom: var(--s4); }
.school h3 { margin: 0 0 var(--s2); font-size: 0.95rem; color: var(--navy); }

.table { border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); }
.tr {
  display: grid; grid-template-columns: minmax(0, 2.4fr) minmax(0, 1fr) minmax(0, 1fr) 6.5rem;
  gap: var(--s3); padding: var(--s3); border-top: 1px solid var(--border); align-items: start;
}
.tr:first-child { border-top: 0; }
.th { font-size: 0.75rem; color: var(--muted); padding-block: var(--s2); }
.name { display: grid; gap: 2px; min-width: 0; }
.en { font-style: italic; }
.covers, .note, .warn { overflow-wrap: anywhere; }
.warn { color: var(--warning); }
.money { display: grid; gap: 2px; font: 600 0.95rem var(--font-mono); color: var(--navy); }
.money small { display: block; font: 400 0.75rem var(--font-body, inherit); color: var(--muted); }
.basis {
  display: inline-block; padding: 0 var(--s2); border-radius: 999px;
  font-size: 0.8rem; font-weight: 600; border: 1px solid currentColor; white-space: nowrap;
}
.basis--full_course { color: var(--warning); }
.basis--per_year { color: var(--blue); }

.general h2 { font-size: 1.05rem; margin: 0 0 var(--s2); }
.general ul { margin: 0; padding-left: 1.2em; display: grid; gap: var(--s1); }

/* On a phone each row becomes a small card, with the fee labels written out. */
@media (max-width: 640px) {
  .th { display: none; }
  .tr { grid-template-columns: 1fr 1fr; }
  .name { grid-column: 1 / -1; }
  .tr > [data-label]::before {
    content: attr(data-label); display: block;
    font: 400 0.7rem var(--font-body, inherit); color: var(--muted);
  }
}
</style>
