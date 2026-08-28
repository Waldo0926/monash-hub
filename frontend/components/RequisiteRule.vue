<script setup lang="ts">
/**
 * One requisite rule, drawn the way the Handbook draws it.
 *
 * Recursive, because the rule is: FIT2099 asks for one of six programming
 * units *or* an engineering pair, and the pair is itself two choices joined by
 * AND. Rendered as a flat list of groups - which is what this page did before
 * the nesting was kept - it reads as "all of the above", which is a different
 * and much harder rule than the one the Handbook states.
 *
 * The connector is shown between the operands rather than as a footnote, so
 * that "or" is read as part of the rule instead of as a remark about it.
 */
const props = defineProps<{
  rule: any
  depth?: number
}>()
const { $t, $term } = useNuxtApp() as any

const depth = computed(() => props.depth ?? 0)

/** Items and nested groups are the operands, in the order they are published. */
const operands = computed(() => [
  ...(props.rule.items || []).map((item: any) => ({ kind: 'unit', item })),
  ...(props.rule.groups || []).map((group: any) => ({ kind: 'group', group }))
])

const joiner = computed(() => {
  const raw = (props.rule.connector || 'AND').toUpperCase()
  return $term('connector', raw) || raw
})
</script>

<template>
  <div class="rule" :class="{ 'rule--nested': depth > 0 }">
    <p v-if="rule.description" class="small pre">{{ rule.description }}</p>

    <template v-for="(operand, index) in operands" :key="index">
      <p v-if="index > 0" class="joiner"><span>{{ joiner }}</span></p>

      <NuxtLink v-if="operand.kind === 'unit'" class="unit" :to="`/units/${operand.item.code}`">
        <span class="mono">{{ operand.item.code }}</span>
        <span class="muted">{{ operand.item.name }}</span>
        <span v-if="operand.item.credit_points" class="tiny muted">
          {{ operand.item.credit_points }} cp
        </span>
      </NuxtLink>

      <RequisiteRule v-else :rule="operand.group" :depth="depth + 1" />
    </template>

    <p v-if="!operands.length && !rule.description" class="muted small">
      {{ $t('unit.noRequisites') }}
    </p>
  </div>
</template>

<style scoped>
.rule { display: grid; gap: var(--s1); }
.rule--nested {
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  padding: var(--s3); background: var(--surface-2);
}

.joiner {
  display: flex; align-items: center; gap: var(--s2); margin: var(--s1) 0;
  color: var(--muted); font-size: 0.75rem; font-weight: 600;
}
.joiner span {
  background: var(--surface-2); border: 1px solid var(--border);
  border-radius: var(--radius-pill); padding: 1px var(--s2);
}
.rule--nested .joiner span { background: var(--surface); }
/* The rule between the chip and the edge, so the join reads as a join. */
.joiner::after { content: ''; flex: 1; height: 1px; background: var(--border); }

.unit {
  display: grid; grid-template-columns: 82px minmax(0, 1fr) auto; gap: var(--s3);
  align-items: baseline; padding: var(--s2) var(--s3); border-radius: var(--radius-sm);
  border: 1px solid var(--border); background: var(--surface);
  color: inherit; text-decoration: none;
}
.unit:hover { border-color: var(--blue); }
.mono { font: 600 0.82rem var(--font-mono); color: var(--navy); }
.muted { color: var(--muted); font-size: 0.88rem; }
.tiny { font-size: 0.75rem; white-space: nowrap; }
.pre { white-space: pre-line; margin: 0 0 var(--s2); }
.small { font-size: 0.85rem; }

@media (max-width: 700px) {
  .unit { grid-template-columns: minmax(0, 1fr); gap: 2px; }
}
</style>
