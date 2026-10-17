<script setup lang="ts">
/**
 * "After this unit": the units that list it as a prerequisite or corequisite.
 *
 * The graph on /tree can show the same thing, but past twenty nodes it turns
 * into lines on a canvas you have to zoom around. Most of the time a student
 * only wants the names, so this is the list, with the campus mark the graph
 * uses and a link to the graph for when the depth matters.
 */
const props = withDefaults(defineProps<{
  code: string
  year?: number | null
  campus?: string | null
  /** Rows shown before "Show more". */
  limit?: number
  /** Hide the link to /tree, for when this already sits under the graph. */
  graphLink?: boolean
}>(), { year: null, campus: null, limit: 8, graphLink: true })

const { $t } = useNuxtApp()
const campusName = useCampusName()
const { withYear } = useHandbookYear()

const query = computed(() => {
  const params = new URLSearchParams()
  if (props.year) params.set('year', String(props.year))
  if (props.campus) params.set('campus', props.campus)
  const text = params.toString()
  return `/v1/units/${props.code}/unlocks${text ? `?${text}` : ''}`
})

const { data, pending, error } = await useLocalisedApiFetch<any>(
  () => query.value,
  { watch: [() => props.code, () => props.year, () => props.campus] }
)

const expanded = ref(false)
watch(() => props.code, () => { expanded.value = false })

const rows = computed<any[]>(() => data.value?.units ?? [])
const shown = computed(() => (expanded.value ? rows.value : rows.value.slice(0, props.limit)))
const hidden = computed(() => Math.max(0, rows.value.length - props.limit))
const awayCount = computed(() => rows.value.filter((r) => !r.offered_at_campus).length)
</script>

<template>
  <div class="unlocks">
    <Skeleton v-if="pending && !data" :lines="3" />
    <p v-else-if="error" class="tiny bad-text" role="alert">{{ $t('unlocks.error') }}</p>
    <template v-else-if="data">
      <p v-if="!rows.length" class="muted small">
        {{ $t('unlocks.none', { code: data.seed, year: data.academic_year }) }}
      </p>
      <template v-else>
        <p class="small summary">
          {{ $t(rows.length === 1 ? 'unlocks.countOne' : 'unlocks.count', { code: data.seed, count: rows.length }) }}
          <template v-if="data.total_downstream > rows.length">
            {{ $t(data.truncated ? 'unlocks.leadsOnAtLeast' : 'unlocks.leadsOn', { total: data.total_downstream }) }}
          </template>
        </p>
        <p v-if="campus && awayCount" class="tiny away-note">
          {{ $t('unlocks.awayNote', { count: awayCount, campus: campusName(campus) }) }}
        </p>

        <ul class="rows">
          <li v-for="row in shown" :key="row.unit_code">
            <NuxtLink class="row" :class="{ 'row--away': !row.offered_at_campus }" :to="withYear(`/units/${row.unit_code}`)">
              <span class="mono code">{{ row.unit_code }}</span>
              <span class="title">{{ row.title }}</span>
              <span class="tags">
                <span v-if="row.requisite_type === 'corequisite'" class="tag tag--coreq">{{ $t('unlocks.coreq') }}</span>
                <span v-if="!row.offered_at_campus" class="tag tag--away">
                  {{ $t('tree.keyAway', { campus: campusName(campus) }) }}
                </span>
                <template v-else>
                  <span v-for="p in row.periods" :key="p" class="tag">{{ p }}</span>
                </template>
              </span>
            </NuxtLink>
          </li>
        </ul>

        <div class="foot">
          <button v-if="hidden && !expanded" type="button" class="more" @click="expanded = true">
            {{ $t('unlocks.showMore', { count: hidden }) }}
          </button>
          <button v-else-if="hidden" type="button" class="more" @click="expanded = false">
            {{ $t('unlocks.showLess') }}
          </button>
          <NuxtLink
            v-if="graphLink"
            class="small"
            :to="`/tree?unit=${data.seed}&direction=downstream${campus ? `&campus=${campus}` : ''}`"
          >
            {{ $t('unlocks.asGraph') }}
          </NuxtLink>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.summary { margin-bottom: var(--s2); }
.away-note { color: var(--warning); margin-bottom: var(--s3); }
.rows {
  list-style: none; margin: 0; padding: 0;
  border: 1px solid var(--border); border-radius: var(--radius-sm); overflow: hidden;
}
.rows li + li { border-top: 1px solid var(--border); }
.row {
  display: grid; grid-template-columns: 82px minmax(0, 1fr) auto; gap: var(--s3);
  align-items: center; padding: var(--s2) var(--s3); color: var(--text);
}
.row:hover { background: var(--surface-2); text-decoration: none; }
.row--away .code, .row--away .title { color: var(--muted); }
.code { font-size: 0.85rem; font-weight: 600; color: var(--navy); }
.title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 0.92rem; }
.tags { display: flex; gap: var(--s1); flex-wrap: wrap; justify-content: flex-end; }
.tag {
  padding: 0 6px; border-radius: 4px; font-size: 0.72rem; line-height: 1.6;
  background: var(--surface-2); color: var(--muted); border: 1px solid var(--border);
}
.tag--coreq { background: var(--blue-50); color: var(--blue-700); border-color: transparent; }
.tag--away { background: var(--warning-bg); color: var(--warning); border-color: transparent; }
.foot { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: var(--s3); margin-top: var(--s3); }
.more {
  padding: 0; border: 0; background: none; font: inherit; font-size: 0.9rem;
  color: var(--blue-700); cursor: pointer;
}
.more:hover { text-decoration: underline; }

@media (max-width: 600px) {
  .row { grid-template-columns: 72px minmax(0, 1fr); }
  .tags { grid-column: 2; justify-content: flex-start; }
  .title { white-space: normal; }
}
</style>
