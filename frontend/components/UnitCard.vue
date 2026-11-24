<script setup lang="ts">
const props = defineProps<{ unit: any }>()
const { $t } = useNuxtApp()
const { cnReadonly } = useSiteMode()
const { withYear } = useHandbookYear()

// Older API responses have no exam_status; work it out from has_exam then.
const status = computed<string>(() => props.unit.exam_status
  || (props.unit.has_exam === true ? 'exam' : props.unit.has_exam === false ? 'none' : 'unknown'))
const statusTone = computed(() => (status.value === 'final' ? 'exam' : status.value))

// "60" from the Handbook reads as 60%; anything else ("Pass/Fail") as written.
const weight = (value: string | null) => (value && /^\d+(\.\d+)?$/.test(value.trim()) ? `${value.trim()}%` : value)
const items = computed(() => ((props.unit.assessment_items || []) as { name: string; weight: string | null }[]))
const moreItems = computed(() => Math.max(0, (props.unit.assessment_count || 0) - items.value.length))
</script>

<template>
  <NuxtLink :to="withYear(`/units/${unit.unit_code}`)" class="unit card">
    <div class="top">
      <span class="code mono">{{ unit.unit_code }}</span>
      <span
        class="status"
        :class="`status--${statusTone}`"
        :title="$t(`units.statusHint.${status === 'final' ? 'exam' : status}`)"
      >
        <span class="dot" aria-hidden="true" />{{ $t(`units.status.${status}`) }}
      </span>
    </div>
    <h3 class="title">{{ unit.title }}</h3>
    <p
      v-if="!cnReadonly && unit.rating?.count"
      class="rating tiny"
      :title="$t('reviews.cardTitle')"
    >
      <StarRating :value="unit.rating.average" size="sm" />
      <strong>{{ Number(unit.rating.average).toFixed(1) }}</strong>
      <span class="muted">({{ unit.rating.count }})</span>
      <span class="rating-source">{{ $t('badge.community') }}</span>
    </p>
    <p v-if="items.length" class="assessments small">
      <template v-for="(item, i) in items" :key="i">
        <span v-if="i" class="sep" aria-hidden="true"> · </span>
        <span class="item">{{ item.name }}<b v-if="item.weight" class="weight">{{ weight(item.weight) }}</b></span>
      </template>
      <span v-if="moreItems" class="muted"> · {{ $t('units.more', { count: moreItems }) }}</span>
    </p>
    <div class="chips">
      <span v-for="(offering, i) in unit.offerings.slice(0, 4)" :key="i" class="chip">
        {{ $term('campus', offering.campus) }} · {{ $term('period', offering.teaching_period) }}
      </span>
      <span v-if="unit.offerings.length > 4" class="chip">
        {{ $t('units.more', { count: unit.offerings.length - 4 }) }}
      </span>
      <span v-if="!unit.offerings.length" class="chip chip--quiet">
        {{ $t('units.noOfferings') }}
      </span>
    </div>
    <p class="meta tiny muted">
      <span>{{ unit.credit_points }} {{ $t('units.creditPoints') }}<span v-if="unit.level"> · {{ $term('level', unit.level) }}</span></span>
      <SourceBadge kind="handbook" />
    </p>
  </NuxtLink>
</template>

<style scoped>
.unit { display: flex; flex-direction: column; padding: var(--s4); color: inherit; }
.unit:hover { text-decoration: none; border-color: var(--border-strong); box-shadow: var(--shadow); }
.top { display: flex; align-items: center; justify-content: space-between; gap: var(--s3); }
.code { font-weight: 700; color: var(--navy); }
.title { margin: var(--s2) 0 var(--s2); font-size: 1.02rem; line-height: 1.35; }

/* The exam status in four colours, the same four the electives page filters on. */
.status {
  flex: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 10px;
  border-radius: var(--radius-pill);
  font-size: 0.76rem;
  font-weight: 600;
  white-space: nowrap;
}
.status .dot { width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.status--none { background: var(--success-bg); color: var(--success); }
.status--quiz { background: var(--warning-bg); color: var(--warning); }
.status--exam { background: var(--danger-bg); color: var(--danger); }
.status--unknown { background: var(--surface-2); color: var(--muted); }

/* Student ratings are community content, so they say so even on a card. */
.rating { display: flex; align-items: center; gap: 5px; margin: 0 0 var(--s2); }
.rating-source { color: var(--badge-community); font-weight: 600; }
.assessments { margin: 0 0 var(--s3); color: var(--muted); line-height: 1.5; }
.assessments .weight { margin-left: 0.3em; font-weight: 600; color: var(--text); }
.chips { display: flex; flex-wrap: wrap; gap: var(--s2); margin-bottom: var(--s3); }
.chip {
  padding: 2px 10px;
  border-radius: var(--radius-pill);
  background: var(--surface-2);
  color: var(--text);
  font-size: 0.76rem;
}
.chip--quiet { color: var(--muted); }
.meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--s2);
  margin: auto 0 0;
}
</style>
