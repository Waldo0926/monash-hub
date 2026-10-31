<script setup lang="ts">
/**
 * The Monash Malaysia fee for one degree, read from the official fee page.
 *
 * Two things a reader gets wrong most often are written next to every number
 * rather than once in a heading: whether it is for one year or the whole
 * course, and that it is tuition only. A number we could not read stays as
 * Monash printed it, with a line saying so.
 */
import { deltaAt, feeNote, feeTitle, formatAmount, type FeeRow } from '~/utils/tuition'

type Source = { title: string; url: string; last_checked: string | null }

const props = defineProps<{
  fee: {
    year: number | null
    rows: FeeRow[]
    not_listed: { en: string; zh: string; url?: string } | null
    sources: Record<string, Source>
    previous?: { year: number; sources: Record<string, { title: string; url: string }> } | null
  }
}>()

const { locale } = useLocale()

// One row needs no label. Two or more (the DHES streams, Monash English
// lengths) need one each.
const labelled = computed(() => props.fee.rows.length > 1)

function rowLabel(row: FeeRow) {
  return row.variant || feeTitle(row, locale.value)
}
</script>

<template>
  <section class="fee card" aria-labelledby="fee-title">
    <h2 id="fee-title">
      {{ fee.year ? $t('fees.cardTitle', { year: fee.year }) : $t('fees.cardTitleNoYear') }}
    </h2>

    <p v-if="fee.not_listed" class="small">
      {{ feeNote(fee.not_listed, locale) }}
      <a v-if="fee.not_listed.url" :href="fee.not_listed.url" rel="noopener external" target="_blank">{{ $t('fees.coursePage') }}</a>
    </p>

    <div v-for="(row, i) in fee.rows" :key="i" class="row">
      <p v-if="labelled" class="label">{{ rowLabel(row) }}</p>
      <dl class="amounts">
        <div>
          <dt>{{ $t('fees.domestic') }}</dt>
          <dd>
            <span v-for="(a, n) in row.domestic" :key="n" class="amount">
              {{ formatAmount(a) }}<span v-if="a.label" class="tiny muted stream">{{ a.label }}</span>
              <FeeDelta :delta="deltaAt(row.change, 'domestic', n)" :year="row.change?.year" />
            </span>
          </dd>
        </div>
        <div>
          <dt>{{ $t('fees.international') }}</dt>
          <dd>
            <span v-for="(a, n) in row.international" :key="n" class="amount">
              {{ formatAmount(a) }}<span v-if="a.label" class="tiny muted stream">{{ a.label }}</span>
              <FeeDelta :delta="deltaAt(row.change, 'international', n)" :year="row.change?.year" />
            </span>
          </dd>
        </div>
        <div v-if="row.basis">
          <dt>{{ $t('fees.basis') }}</dt>
          <dd><span class="basis" :class="`basis--${row.basis}`">{{ $t(`fees.basis.${row.basis}`) }}</span></dd>
        </div>
      </dl>
      <p v-if="row.unreadable" class="small warn" role="note">{{ $t('fees.unreadable') }}</p>
      <p v-if="row.note" class="small note">
        {{ feeNote(row.note, locale) }}
        <a v-if="row.note.url" :href="row.note.url" rel="noopener external" target="_blank">{{ $t('fees.coursePage') }}</a>
      </p>
    </div>

    <p class="tiny muted">{{ $t('fees.excludes') }}</p>
    <p class="tiny muted sources">
      {{ $t('fees.source') }}
      <template v-for="([slug, source], n) in Object.entries(fee.sources)" :key="slug">
        <template v-if="n">, </template>
        <a :href="source.url" rel="noopener external" target="_blank">{{ source.title }}</a>
        <template v-if="source.last_checked"> · <LastChecked :value="source.last_checked" /></template>
      </template>
      · <NuxtLink to="/fees">{{ $t('fees.all') }}</NuxtLink>
    </p>
    <p v-if="fee.previous" class="tiny muted sources">
      {{ $t('fees.previousSource', { year: fee.previous.year }) }}
      <template v-for="([key, source], n) in Object.entries(fee.previous.sources)" :key="key">
        <template v-if="n">, </template>
        <a :href="source.url" rel="noopener external" target="_blank">{{ source.title }}</a>
      </template>
    </p>
  </section>
</template>

<style scoped>
.fee { margin: 0 0 var(--s5); padding: var(--s4) var(--s5); }
.fee h2 { margin: 0 0 var(--s3); font-size: 1.05rem; }
.row { padding: var(--s3) 0; border-top: 1px solid var(--border); }
.row:first-of-type { border-top: 0; padding-top: 0; }
.label { margin: 0 0 var(--s2); font-weight: 600; }
.amounts { display: flex; flex-wrap: wrap; gap: var(--s4) var(--s6); margin: 0; }
.amounts div { display: grid; gap: 2px; }
.amounts dt { font-size: 0.75rem; color: var(--muted); }
.amounts dd { margin: 0; display: grid; gap: 2px; }
.amount { font: 600 1.05rem var(--font-mono); color: var(--navy); }
.stream { display: block; font-family: var(--font); font-weight: 400; }
.basis {
  display: inline-block; padding: 0 var(--s2); border-radius: 999px;
  font-size: 0.85rem; font-weight: 600; border: 1px solid currentColor;
}
.basis--full_course { color: var(--warning); }
.basis--per_year { color: var(--blue); }
.warn { margin: var(--s2) 0 0; color: var(--warning); }
.note { margin: var(--s2) 0 0; }
.fee .tiny { margin: var(--s2) 0 0; overflow-wrap: anywhere; }
</style>
