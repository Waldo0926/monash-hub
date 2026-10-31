<script setup lang="ts">
/**
 * Every upcoming key date for one campus, by month: the full list behind the
 * home-page card.
 *
 * Same source as the card, /v1/key-dates, which reads the census, final
 * assessment and principal dates pages the index already holds. Only the main
 * teaching periods are listed (the API decides which); the page says so and
 * links the official pages for the rest, so nobody reads a missing summer
 * term as "no dates".
 *
 * The campus choice is the home page's cookie, so switching on one switches
 * the other.
 */
import {
  KEY_DATE_TEXT, checkedOnLabel, dayNumber, keyDateLabel, keyDateRange,
  type KeyDate, type KeyDateLang, type KeyDates
} from '~/utils/keyDates'

const config = useRuntimeConfig()
const { locale } = useLocale()
const lang = computed(() => (['zh', 'ja', 'ko'].includes(locale.value) ? locale.value : 'en') as KeyDateLang)
const t = computed(() => KEY_DATE_TEXT[lang.value])

const campus = useCookie<'malaysia' | 'australia'>('mh_home_campus', {
  default: () => 'malaysia',
  maxAge: 60 * 60 * 24 * 365,
  sameSite: 'lax',
  path: '/'
})
if (campus.value !== 'malaysia' && campus.value !== 'australia') campus.value = 'malaysia'

const { data, error, status } = await useLocalisedApiFetch<KeyDates>(
  () => `/v1/key-dates?campus=${campus.value}&limit=60`,
  { watch: [campus] }
)

const showHolidays = ref(true)

function when(item: KeyDate): string {
  const today = dayNumber(data.value!.today)
  if (dayNumber(item.date) <= today) return t.value.underway
  return t.value.inDays(dayNumber(item.date) - today)
}

// The next academic date gets the same emphasis the card gives it.
const nextAcademic = computed(() => data.value?.items.find(i => i.kind !== 'holiday') ?? null)

const months = computed(() => {
  const groups: { key: string; heading: string; rows: any[] }[] = []
  for (const item of data.value?.items ?? []) {
    if (!showHolidays.value && item.kind === 'holiday') continue
    const [y, m] = item.date.split('-').map(Number) as [number, number]
    const key = `${y}-${m}`
    let group = groups.at(-1)
    if (!group || group.key !== key) {
      group = { key, heading: t.value.month(y, m), rows: [] }
      groups.push(group)
    }
    group.rows.push({
      item,
      ...keyDateLabel(item, lang.value),
      range: keyDateRange(item, lang.value, data.value?.today),
      when: when(item),
      next: item === nextAcademic.value
    })
  }
  return groups
})
const shown = computed(() => months.value.reduce((n, g) => n + g.rows.length, 0))

const sources = computed(() => Object.values(data.value?.sources ?? {}))
const checkedOn = computed(() => checkedOnLabel(sources.value, lang.value))
const options = ['malaysia', 'australia'] as const

useSeoMeta({
  title: () => t.value.pageTitle,
  description: () => t.value.pageLead
})
useHead({ link: [{ rel: 'canonical', href: `${config.public.siteUrl}/dates` }] })
</script>

<template>
  <div class="container dates-page">
    <header class="head">
      <h1>{{ t.pageTitle }}</h1>
      <p class="lead">{{ t.pageLead }}</p>
    </header>

    <div class="controls">
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
      <label class="toggle small">
        <input v-model="showHolidays" type="checkbox">
        {{ t.showHolidays }}
      </label>
    </div>
    <p class="periods small muted">
      {{ t.periodsLabel }}{{ t.periods[campus] }}
      <template v-if="data?.items?.length"> · {{ t.count(shown) }}</template>
    </p>

    <div v-if="status === 'pending' && !data" class="loading">
      <Skeleton :lines="6" height="44px" />
    </div>
    <EmptyState v-else-if="error || !months.length" :title="t.empty" />
    <div v-else class="months">
      <section v-for="group in months" :key="group.key" class="month" :aria-label="group.heading">
        <h2>{{ group.heading }}</h2>
        <ol class="list">
          <li
            v-for="row in group.rows"
            :key="`${row.item.date}-${row.item.kind}-${row.item.period}-${row.item.name}`"
            :class="{ next: row.next, holiday: row.item.kind === 'holiday' }"
          >
            <span class="d mono">{{ row.range }}</span>
            <span class="what">
              {{ row.main }}
              <small v-if="row.sub">{{ row.sub }}</small>
            </span>
            <span class="when">{{ row.when }}</span>
          </li>
        </ol>
      </section>
    </div>

    <footer class="foot small muted">
      <p>{{ t.otherPeriods }}</p>
      <p v-if="sources.length">
        {{ t.source }}:
        <template v-for="(s, i) in sources" :key="s.url">
          <a :href="s.url" rel="noopener external" target="_blank">{{ s.title }} ↗</a><template v-if="i < sources.length - 1"> · </template>
        </template>
        <template v-if="checkedOn"> · {{ t.checked }} {{ checkedOn }}</template>
      </p>
    </footer>
  </div>
</template>

<style scoped>
.dates-page { max-width: 820px; padding-block: var(--s6) var(--s8); }
.head h1 { margin: 0 0 var(--s3); }
.lead { max-width: 40em; margin: 0 0 var(--s5); color: var(--muted); }

.controls { display: flex; flex-wrap: wrap; align-items: center; gap: var(--s3) var(--s5); }
.seg { display: inline-flex; padding: 2px; border: 1px solid var(--border-strong); border-radius: var(--radius-pill); }
.seg button {
  min-height: 36px;
  padding: 0 var(--s4);
  border: 0;
  border-radius: var(--radius-pill);
  background: none;
  color: var(--muted);
  font: inherit;
  font-size: 0.875rem;
  cursor: pointer;
}
.seg button[aria-pressed='true'] { background: var(--ink); color: var(--text-inverse); }
.toggle { display: inline-flex; align-items: center; gap: var(--s2); min-height: 44px; cursor: pointer; }
.toggle input { width: 18px; height: 18px; accent-color: var(--brand); }
.periods { margin: var(--s2) 0 var(--s5); }

.loading { display: grid; gap: var(--s2); }

.month + .month { margin-top: var(--s6); }
.month h2 {
  margin: 0 0 var(--s2);
  font-family: var(--font);
  font-size: 0.95rem;
  font-weight: 600;
}
.list { margin: 0; padding: 0; list-style: none; border-top: 1px solid var(--ink); }
.list li {
  display: grid;
  grid-template-columns: 9em minmax(0, 1fr) auto;
  gap: var(--s4);
  align-items: baseline;
  padding: 12px var(--s2);
  border-bottom: 1px solid var(--border);
}
.d { color: var(--muted); font-size: 0.85rem; font-variant-numeric: tabular-nums; }
.what small { display: block; color: var(--muted-2); font-size: 0.8rem; }
.when { color: var(--muted-2); font-size: 0.8rem; white-space: nowrap; font-variant-numeric: tabular-nums; }
.list li.holiday .what { color: var(--muted); }
/* The next academic date: a tinted row and bold label, not colour alone. */
.list li.next { background: var(--blue-50); }
.list li.next .what { font-weight: 600; }
.list li.next .when { color: var(--soon); font-weight: 500; }

.foot { margin-top: var(--s7); padding-top: var(--s4); border-top: 1px solid var(--border); }
.foot p { margin: 0 0 var(--s2); }
.foot a { color: inherit; border-bottom: 1px solid var(--border-strong); }
.foot a:hover { color: var(--text); text-decoration: none; }

@media (max-width: 560px) {
  .list li { grid-template-columns: 1fr auto; row-gap: 2px; padding-inline: var(--s1); }
  .d { grid-column: 1; }
  .when { grid-column: 2; grid-row: 1; }
  .what { grid-column: 1 / -1; }
}
</style>
