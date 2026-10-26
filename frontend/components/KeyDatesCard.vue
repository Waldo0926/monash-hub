<script setup lang="ts">
/**
 * What is coming up at the student's campus: census and withdrawal deadlines,
 * the end of teaching, swot vac, exams, results and public holidays.
 *
 * Every row comes from /v1/key-dates, which reads the official date pages the
 * index already holds. Nothing here is typed in by hand except the wording, and
 * the card says which pages the dates came from and when they were checked -
 * a deadline without a source is a rumour.
 *
 * Days remaining are counted from the date the API reports for the campus, not
 * from the browser's clock, so the server and the client render the same number
 * and a student abroad sees the campus's today.
 *
 * The big number is the next academic date (census, withdrawal, swot vac, exams,
 * results), not a public holiday, and that date is not listed again below it.
 * Holidays stay in the list because a closed campus still changes a week, they
 * just do not take the headline.
 */
import {
  KEY_DATE_TEXT, checkedOnLabel, dayNumber, keyDateLabel, keyDateRange,
  type KeyDateLang, type KeyDates, type KeyDate
} from '~/utils/keyDates'

const campus = defineModel<'malaysia' | 'australia'>('campus', { required: true })

// Enough rows that a run of holidays cannot leave the headline without an
// academic date, but only LISTED of them are shown under it.
const FETCHED = 8
const LISTED = 4
const { locale } = useLocale()
const lang = computed(() => (['zh', 'ja', 'ko'].includes(locale.value) ? locale.value : 'en') as KeyDateLang)

// The source titles come back in the page's language, so the fetch carries it.
const { data, error } = await useLocalisedApiFetch<KeyDates>(
  () => `/v1/key-dates?campus=${campus.value}&limit=${FETCHED}`,
  { watch: [campus] }
)

const t = computed(() => KEY_DATE_TEXT[lang.value])
const label = (item: KeyDate) => keyDateLabel(item, lang.value)
const range = (item: KeyDate) => keyDateRange(item, lang.value, data.value?.today)

function when(item: KeyDate): string {
  const today = dayNumber(data.value!.today)
  if (dayNumber(item.date) <= today) return t.value.underway
  const n = dayNumber(item.date) - today
  return t.value.inDays(n)
}

const headline = computed(() => {
  const items = data.value?.items ?? []
  return items.find(item => item.kind !== 'holiday') ?? items[0] ?? null
})
const rows = computed(() =>
  (data.value?.items ?? [])
    .filter(item => item !== headline.value)
    .slice(0, LISTED)
    .map(item => ({ item, ...label(item), range: range(item), when: when(item) }))
)
const next = computed(() => {
  const first = headline.value
  if (!first) return null
  const today = dayNumber(data.value!.today)
  const n = dayNumber(first.date) - today
  return { n: Math.max(n, 0), underway: n <= 0, ...label(first), range: range(first) }
})

const sources = computed(() => Object.values(data.value?.sources ?? {}))
const checkedOn = computed(() => checkedOnLabel(sources.value, lang.value))

const options = ['malaysia', 'australia'] as const
</script>

<template>
  <aside class="dates" aria-labelledby="dates-title">
    <div class="head">
      <h2 id="dates-title">{{ t.title }}</h2>
      <div class="seg" role="group" :aria-label="t.switcher">
        <button
          v-for="option in options"
          :key="option"
          type="button"
          :aria-pressed="campus === option"
          @click="campus = option"
        >
          {{ t.campus[option] }}
        </button>
      </div>
    </div>

    <template v-if="next && !error">
      <p class="count">
        <b v-if="!next.underway">{{ next.n }}</b>
        <b v-else class="now">{{ t.underway }}</b>
        <span class="count-text">
          <template v-if="!next.underway">{{ t.daysAway(next.n) }}</template>
          <small>{{ next.main }}<template v-if="next.sub"> · {{ next.sub }}</template></small>
          <span class="count-date mono">{{ next.range }}</span>
        </span>
      </p>

      <ol v-if="rows.length" class="list">
        <li v-for="row in rows" :key="`${row.item.date}-${row.item.kind}-${row.item.period}-${row.item.name}`" :class="{ holiday: row.item.kind === 'holiday' }">
          <span class="d mono">{{ row.range }}</span>
          <span class="what">
            {{ row.main }}
            <small v-if="row.sub">{{ row.sub }}</small>
          </span>
          <span class="when">{{ row.when }}</span>
        </li>
      </ol>
    </template>
    <p v-else class="muted small empty">{{ t.empty }}</p>

    <NuxtLink to="/dates" class="all small">{{ t.viewAll }} →</NuxtLink>

    <p class="src tiny muted">
      <template v-if="sources.length">{{ t.source }}:
        <template v-for="(s, i) in sources" :key="s.url">
          <a :href="s.url" rel="noopener external" target="_blank">{{ s.title }}</a><template v-if="i < sources.length - 1"> · </template>
        </template>
        <template v-if="checkedOn"> · {{ t.checked }} {{ checkedOn }}</template>
      </template>
    </p>
  </aside>
</template>

<style scoped>
.dates {
  padding: var(--s5) var(--s5) var(--s4);
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--surface);
}
.head { display: flex; align-items: center; justify-content: space-between; gap: var(--s3); flex-wrap: wrap; }
.head h2 { margin: 0; font-family: var(--font); font-size: 0.95rem; font-weight: 600; }
.seg { display: inline-flex; padding: 2px; border: 1px solid var(--border-strong); border-radius: var(--radius-pill); }
.seg button {
  min-height: 28px;
  padding: 0 var(--s3);
  border: 0;
  border-radius: var(--radius-pill);
  background: none;
  color: var(--muted);
  font: inherit;
  font-size: 0.8rem;
  cursor: pointer;
}
.seg button[aria-pressed='true'] { background: var(--ink); color: var(--text-inverse); }

.count { display: flex; align-items: baseline; gap: var(--s3); margin: var(--s4) 0 var(--s3); }
.count b {
  font-family: var(--font-display);
  font-size: 3.2rem;
  font-weight: 600;
  line-height: 1;
  letter-spacing: -0.03em;
  font-variant-numeric: tabular-nums;
}
/* A date already underway has no number to count down, so the word takes its
   place at a size that still reads as the headline. */
.count b.now { font-size: 1.9rem; color: var(--soon); letter-spacing: 0; }
.count-text { display: grid; color: var(--muted); }
.count-text small { color: var(--text); font-size: 0.9rem; font-weight: 500; }
.count-date { color: var(--muted-2); font-size: 0.8rem; font-variant-numeric: tabular-nums; }

.list { list-style: none; margin: 0; padding: 0; }
.list li {
  display: grid;
  grid-template-columns: 8.8em minmax(0, 1fr) auto;
  gap: var(--s3);
  align-items: baseline;
  padding: 10px 0;
  border-top: 1px solid var(--border);
  font-size: 0.92rem;
}
.d { color: var(--muted); font-size: 0.8rem; font-variant-numeric: tabular-nums; }
.what small { display: block; color: var(--muted-2); font-size: 0.78rem; }
.when { color: var(--muted-2); font-size: 0.78rem; white-space: nowrap; font-variant-numeric: tabular-nums; }
.list li.holiday .what { color: var(--muted); }

.empty { margin: var(--s4) 0 0; }
.all { display: inline-block; margin-top: var(--s3); color: var(--brand); font-weight: 500; }
.src { margin: var(--s3) 0 0; }
.src a { color: inherit; border-bottom: 1px solid var(--border-strong); }
.src a:hover { color: var(--text); text-decoration: none; }

@media (max-width: 520px) {
  .dates { padding: var(--s4); }
  .list li { grid-template-columns: 1fr auto; row-gap: 0; }
  .d { grid-column: 1; }
  .when { grid-column: 2; grid-row: 1; }
  .what { grid-column: 1 / -1; }
}
</style>
