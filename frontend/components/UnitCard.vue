<script setup lang="ts">
defineProps<{ unit: any }>()
const { $t } = useNuxtApp()
</script>

<template>
  <NuxtLink :to="`/units/${unit.unit_code}`" class="unit card">
    <div class="top">
      <span class="code mono">{{ unit.unit_code }}</span>
      <SourceBadge kind="handbook" />
    </div>
    <h3 class="title">{{ unit.title }}</h3>
    <div class="chips">
      <span v-for="(offering, i) in unit.offerings.slice(0, 4)" :key="i" class="chip">
        {{ offering.campus }} · {{ offering.teaching_period }}
      </span>
      <span v-if="unit.offerings.length > 4" class="chip">
        {{ $t('units.more', { count: unit.offerings.length - 4 }) }}
      </span>
      <span v-if="!unit.offerings.length" class="chip chip--quiet">
        {{ $t('units.noOfferings') }}
      </span>
    </div>
    <p class="meta tiny muted">
      {{ unit.credit_points }} {{ $t('units.creditPoints') }}<span v-if="unit.level"> · {{ unit.level }}</span>
      · {{ unit.assessment_count }} {{ $t('units.assessmentItems') }}
      <span v-if="unit.has_exam === true"> · {{ $t('units.examListed') }}</span>
      <span v-else-if="unit.has_exam === false"> · {{ $t('units.noExamListed') }}</span>
    </p>
  </NuxtLink>
</template>

<style scoped>
.unit { display: block; padding: var(--s4); color: inherit; }
.unit:hover { text-decoration: none; border-color: var(--border-strong); box-shadow: var(--shadow); }
.top { display: flex; align-items: center; justify-content: space-between; gap: var(--s3); }
.code { font-weight: 700; color: var(--navy); }
.title { margin: var(--s2) 0 var(--s3); font-size: 1.02rem; }
.chips { display: flex; flex-wrap: wrap; gap: var(--s2); margin-bottom: var(--s3); }
.chip {
  padding: 2px 10px;
  border-radius: var(--radius-pill);
  background: var(--surface-2);
  color: var(--text);
  font-size: 0.76rem;
}
.chip--quiet { color: var(--muted); }
.meta { margin: 0; }
</style>
